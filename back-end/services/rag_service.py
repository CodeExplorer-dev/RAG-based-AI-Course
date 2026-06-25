"""RAG 检索增强生成服务（ChromaDB 向量版）
功能：ChromaDB 向量索引 → 语义检索 → Prompt 组装 → LLM 调用 → 引用标注
"""
import os
import re
import json
import math
import logging
from typing import List, Optional

import chromadb
from chromadb.config import Settings
from extensions import db
from models import Courseware, DocumentChunk
from utils.llm_client import llm_client
import jieba
from utils.text_utils import extract_keywords

logger = logging.getLogger(__name__)

# ─── 配置 ───────────────────────────────────────────
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "text-embedding-3-small")
TOP_K_RETRIEVAL = int(os.environ.get("RAG_TOP_K", "5"))
MAX_CONTEXT_CHARS = int(os.environ.get("RAG_MAX_CONTEXT", "4000"))
SIMILARITY_THRESHOLD = float(os.environ.get("RAG_SIMILARITY", "0.15"))
VECTOR_DB_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "storage", "vector_db"
)

# ── ChromaDB 客户端（延迟初始化） ──────────────────────────

_chroma_client = None
_chroma_collection = None
_COLLECTION_NAME = "rag_course_chunks"


def _get_chroma_client():
    global _chroma_client
    if _chroma_client is None:
        os.makedirs(VECTOR_DB_DIR, exist_ok=True)
        _chroma_client = chromadb.PersistentClient(
            path=VECTOR_DB_DIR,
            settings=Settings(anonymized_telemetry=False),
        )
    return _chroma_client


def _get_collection():
    global _chroma_collection
    if _chroma_collection is None:
        client = _get_chroma_client()
        try:
            _chroma_collection = client.get_collection(_COLLECTION_NAME)
        except ValueError:
            _chroma_collection = client.create_collection(
                _COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"},
            )
    return _chroma_collection


# ═══════════════════════════════════════════════════
# 第一部分：嵌入生成
# ═══════════════════════════════════════════════════

def _get_openai_embedding(texts: List[str]) -> List[List[float]]:
    """调用 OpenAI Embedding API"""
    import requests
    api_key = os.environ.get("LLM_API_KEY", "")
    if not api_key:
        raise RuntimeError("LLM_API_KEY \u672a\u914d\u7f6e\uff0c\u65e0\u6cd5\u4f7f\u7528\u8bed\u4e49\u5d4c\u5165")

    base = os.environ.get("LLM_API_BASE", "https://api.openai.com/v1").rstrip("/")
    url = f"{base}/embeddings"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"model": EMBEDDING_MODEL, "input": texts}

    resp = requests.post(url, json=payload, headers=headers, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    sorted_data = sorted(data["data"], key=lambda x: x["index"])
    return [item["embedding"] for item in sorted_data]


# ═══════════════════════════════════════════════════
# 第二部分：索引构建（ChromaDB）
# ═══════════════════════════════════════════════════

def index_courseware(courseware_id: int) -> dict:
    """为课件的所有 chunk 生成向量嵌入并存入 ChromaDB"""
    chunks = DocumentChunk.query.filter_by(courseware_id=courseware_id)\
        .order_by(DocumentChunk.chunk_index).all()
    if not chunks:
        return {"indexed": 0}

    texts = [c.content for c in chunks]
    chunk_ids = [f"chunk_{c.id}" for c in chunks]
    metadatas = [
        {
            "chunk_id": c.id,
            "courseware_id": c.courseware_id,
            "chunk_index": c.chunk_index,
            "course_id": _get_courseware_course_id(c.courseware_id),
        }
        for c in chunks
    ]

    # 尝试 OpenAI Embedding → ChromaDB
    try:
        embeddings = _get_openai_embedding(texts)
        collection = _get_collection()
        # 先删除该课件的旧向量
        existing_ids = collection.get(
            where={"courseware_id": courseware_id},
            include=[],
        )["ids"]
        if existing_ids:
            collection.delete(ids=existing_ids)

        collection.add(
            ids=chunk_ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=texts,
        )
        # 更新 vector_id 字段（记录 ChromaDB id）
        for c, cid in zip(chunks, chunk_ids):
            c.vector_id = cid
            db.session.add(c)
        db.session.commit()
        logger.info(f"ChromaDB indexed {len(chunks)} chunks for courseware {courseware_id}")
        return {"indexed": len(chunks), "mode": "chromadb"}

    except Exception as e:
        logger.warning(f"ChromaDB \u7d22\u5f15\u5931\u8d25\uff0c\u56de\u9000 TF-IDF: {e}")

    # ── Fallback: TF-IDF ──
    all_keywords = []
    for t in texts:
        all_keywords.extend(extract_keywords(t, max_count=50))
    from collections import Counter
    kw_counter = Counter(all_keywords)
    all_keywords = [kw for kw, _ in kw_counter.most_common(500)]

    updated = 0
    for i, chunk in enumerate(chunks):
        kws = extract_keywords(chunk.content, max_count=50)
        kw_set = set(kws)
        vec = []
        for kw in all_keywords:
            tf = chunk.content.count(kw)
            idf = math.log(len(all_keywords) / (sum(1 for k in all_keywords if k in kw_set) + 1) + 1)
            vec.append(tf * idf if tf > 0 else 0.0)
        # ????????? JSON ??? MySQL TEXT ??
        # ?? TF-IDF ????? vector_id???? jieba ?? content
        chunk.vector_id = "tfidf"
        db.session.add(chunk)
        updated += 1

    db.session.commit()
    return {"indexed": updated, "mode": "tfidf", "keywords_count": len(all_keywords)}


def _get_courseware_course_id(courseware_id):
    cw = db.session.get(Courseware, courseware_id)
    return cw.course_id if cw else 0


# ═══════════════════════════════════════════════════
# 第三部分：语义检索（ChromaDB + Fallback）
# ═══════════════════════════════════════════════════

_last_search_mode = "none"
def _extract_heading(content: str) -> str:
    m = re.match(r"^\u3010([^\u3011]+)\u3011", content)
    if m:
        return m.group(1)
    return ""


def _get_chunk_source(chunk: DocumentChunk) -> dict:
    heading = _extract_heading(chunk.content)
    courseware = db.session.get(Courseware, chunk.courseware_id)
    return {
        "chunk_index": chunk.chunk_index,
        "courseware_title": courseware.title if courseware else "",
        "heading": heading,
        "page_ref": chunk.page_ref,
        "token_count": chunk.token_count,
    }


def _chroma_search(query: str, course_id: int = None, top_k: int = TOP_K_RETRIEVAL) -> list:
    """ChromaDB 语义检索"""
    try:
        collection = _get_collection()
        query_embedding = _get_openai_embedding([query])[0]
    except Exception as e:
        logger.warning(f"ChromaDB \u68c0\u7d22\u5931\u8d25: {e}")
        return None  # \u8868\u793a\u9700\u8981\u964d\u7ea7

    where = {}
    if course_id:
        where["course_id"] = course_id

    try:
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k * 2,
            where=where if where else None,
            include=["metadatas", "documents", "distances"],
        )
    except Exception as e:
        logger.warning(f"ChromaDB query failed: {e}")
        return None

    if not results or not results["ids"][0]:
        return []

    output = []
    for i, chunk_id in enumerate(results["ids"][0]):
        meta = results["metadatas"][0][i]
        distance = results["distances"][0][i]
        score = 1.0 - distance  # cosine similarity from distance

        if score < SIMILARITY_THRESHOLD:
            continue

        chunk = db.session.get(DocumentChunk, meta["chunk_id"])
        if not chunk:
            continue

        output.append({
            "chunk": chunk,
            "score": round(score, 4),
            "source": _get_chunk_source(chunk),
        })

    # \u6309\u76f8\u4f3c\u5ea6\u6392\u5e8f
    output.sort(key=lambda x: x["score"], reverse=True)
    return output[:top_k]


def _keyword_search(query: str, course_id: int = None, top_k: int = TOP_K_RETRIEVAL) -> list:
    """\u5173\u952e\u8bcd\u5339\u914d\u5668\uff08ChromaDB \u4e0d\u53ef\u7528\u65f6\u7684\u964d\u7ea7\u5907\u4efd\uff09"""
    import jieba
    chunk_query = DocumentChunk.query.join(Courseware, DocumentChunk.courseware_id == Courseware.id)
    if course_id:
        chunk_query = chunk_query.filter(Courseware.course_id == course_id)
    candidates = chunk_query.order_by(DocumentChunk.chunk_index).all()
    if not candidates:
        return []

    query_kws = set(w for w in jieba.lcut(query) if len(w) >= 2)
    if not query_kws:
        return []

    scored = []
    for chunk in candidates:
        if not chunk.content:
            continue
        matches = sum(1 for kw in query_kws if kw in chunk.content)
        if matches > 0:
            scored.append((matches / len(query_kws), chunk))

    scored.sort(key=lambda x: x[0], reverse=True)
    results = []
    for score, chunk in scored[:top_k]:
        results.append({"chunk": chunk, "score": round(score, 4), "source": _get_chunk_source(chunk)})
    return results


def search(query: str, course_id: int = None, top_k: int = TOP_K_RETRIEVAL) -> list:
    global _last_search_mode
    """\u901a\u7528\u68c0\u7d22 API\uff1a\u4f18\u5148 ChromaDB\uff0c\u5931\u8d25\u964d\u7ea7\u4e3a\u5173\u952e\u8bcd"""
    results = _chroma_search(query, course_id, top_k)
    if results is not None:
        _last_search_mode = "chromadb"
        return results
    _last_search_mode = "keyword"
    return _keyword_search(query, course_id, top_k)


def generate_answer(question: str, course_id: int = None, detailed: bool = False) -> dict:
    """\u5b8c\u6574\u7684 RAG \u95ee\u7b54\u7ba1\u7ebf

    Returns:
        { "answer": str, "sources": [...], "chunk_count": int, "search_mode": str }
    """
    results = search(question, course_id)

    if not results:
        return {
            "answer": "\u62b1\u6b49\uff0c\u6ca1\u6709\u5728\u8bfe\u4ef6\u4e2d\u627e\u5230\u4e0e\u60a8\u95ee\u9898\u76f8\u5173\u7684\u5185\u5bb9\u3002\u8bf7\u5c1d\u8bd5\u6362\u4e2a\u95ee\u6cd5\uff0c\u6216\u8054\u7cfb\u8001\u5e08\u4e0a\u4f20\u66f4\u591a\u8bfe\u4ef6\u3002",
            "sources": [],
            "chunk_count": 0,
            "search_mode": "none",
        }

    context_parts = []
    sources = []
    total_chars = 0

    for i, r in enumerate(results):
        chunk = r["chunk"]
        source = r["source"]
        heading = source["heading"] or "\uff08\u672a\u5206\u6bb5\uff09"
        labeled = f"\u3010\u8d44\u6599{i+1}\u00b7{heading}\u3011\n{chunk.content}"
        if total_chars + len(labeled) > MAX_CONTEXT_CHARS:
            break
        context_parts.append(labeled)
        total_chars += len(labeled)
        sources.append(source)

    context_text = "\n\n---\n\n".join(context_parts)

    # \u8c03\u7528 LLM
    try:
        if detailed:
            detailed_prompt =   "你是一个 AI 课程助教。用户对之前的回答不满意，请给出更详细、更深入的解释，包含具体例子和更多细节。尽量全面覆盖相关知识点。"

            answer = llm_client.chat_with_context(question, [p["chunk"].content for p in results[:3]], system_prompt=detailed_prompt)
        else:
            answer = llm_client.chat_with_context(question, [p["chunk"].content for p in results[:3]])
        search_mode = _last_search_mode
    except RuntimeError as e:
        logger.error(f"LLM \u8c03\u7528\u5931\u8d25: {e}")
        answer = (
            "\uff08AI \u52a9\u624b\u6682\u65f6\u4e0d\u53ef\u7528\uff0c\u4ee5\u4e0b\u662f\u8bfe\u4ef6\u4e2d\u4e0e\u60a8\u95ee\u9898\u76f8\u5173\u7684\u5185\u5bb9\u6458\u8981\uff09\n\n"
            f"{context_text[:2000]}"
        )
        search_mode = "chromadb_fallback"
    except Exception as e:
        logger.error(f"RAG \u751f\u6210\u5931\u8d25: {e}")
        answer = "\u62b1\u6b49\uff0c\u56de\u7b54\u751f\u6210\u8fc7\u7a0b\u4e2d\u51fa\u73b0\u9519\u8bef\uff0c\u8bf7\u7a0d\u540e\u518d\u8bd5\u3002"
        search_mode = "error"

    return {
        "answer": answer,
        "sources": sources[:5],
        "chunk_count": len(results),
        "search_mode": search_mode,
    }


# \u5168\u5c40\u5355\u4f8b
rag_service = {
    "index_courseware": index_courseware,
    "search": search,
    "generate_answer": generate_answer,
}
