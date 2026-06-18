"""RAG 检索增强生成服务
功能：文档嵌入 → 语义检索 → Prompt 组装 → LLM 调用 → 引用标注
"""
import os
import re
import json
import math
import logging
from typing import List, Optional
from collections import Counter

from extensions import db
from models import Courseware, DocumentChunk
from utils.llm_client import llm_client
import jieba
from utils.text_utils import extract_keywords

logger = logging.getLogger(__name__)

# ─── 配置 ───────────────────────────────────────────
EMBEDDING_MODEL = os.environ.get('EMBEDDING_MODEL', 'text-embedding-3-small')
TOP_K_RETRIEVAL = int(os.environ.get('RAG_TOP_K', '5'))
MAX_CONTEXT_CHARS = int(os.environ.get('RAG_MAX_CONTEXT', '4000'))
SIMILARITY_THRESHOLD = float(os.environ.get('RAG_SIMILARITY', '0.0'))


# ═══════════════════════════════════════════════════
# 第一部分：嵌入生成
# ═══════════════════════════════════════════════════

def _get_openai_embedding(texts: List[str]) -> List[List[float]]:
    """调用 OpenAI Embedding API"""
    import requests
    api_key = os.environ.get('LLM_API_KEY', '')
    if not api_key:
        raise RuntimeError('LLM_API_KEY 未配置，无法使用语义嵌入')

    url = f'{os.environ.get("LLM_API_BASE", "https://api.openai.com/v1").rstrip("/")}/embeddings'
    headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
    payload = {'model': EMBEDDING_MODEL, 'input': texts}

    resp = requests.post(url, json=payload, headers=headers, timeout=60)
    resp.raise_for_status()
    data = resp.json()

    # 按输入顺序排列
    sorted_data = sorted(data['data'], key=lambda x: x['index'])
    return [item['embedding'] for item in sorted_data]


def _tfidf_vectorize(text: str, all_keywords: List[str]) -> List[float]:
    """基于 jieba 关键词的简单 TF-IDF 向量化（OpenAI Embedding 不可用时的 fallback）"""
    kws = extract_keywords(text, max_count=50)
    kw_set = set(kws)
    vec = []
    for kw in all_keywords:
        # TF 分量：词在当前文本中的出现次数
        tf = text.count(kw)
        # IDF 分量（简化版）：假设每个词在 1/len(all_keywords) 的文档中出现
        idf = math.log(len(all_keywords) / (sum(1 for k in all_keywords if k in kw_set) + 1) + 1)
        vec.append(tf * idf if tf > 0 else 0.0)
    return vec


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """余弦相似度"""
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


# ═══════════════════════════════════════════════════
# 第二部分：索引构建
# ═══════════════════════════════════════════════════

def index_courseware(courseware_id: int) -> dict:
    """为课件的所有 chunk 生成嵌入向量并存储"""
    chunks = DocumentChunk.query.filter_by(courseware_id=courseware_id).order_by(DocumentChunk.chunk_index).all()
    if not chunks:
        return {'indexed': 0}

    texts = [c.content for c in chunks]

    # 尝试 OpenAI Embedding
    embeddings = None
    try:
        embeddings = _get_openai_embedding(texts)
        logger.info(f'OpenAI Embedding 成功: {len(texts)} chunks')
    except Exception as e:
        logger.warning(f'OpenAI Embedding 不可用，回退 TF-IDF: {e}')

    # 如果是 TF-IDF 方式，需要先收集全局关键词
    all_keywords = []
    if embeddings is None:
        for t in texts:
            all_keywords.extend(extract_keywords(t, max_count=50))
        # 去重，按频率排序取前 500 个
        kw_counter = Counter(all_keywords)
        all_keywords = [kw for kw, _ in kw_counter.most_common(500)]

    updated = 0
    for i, chunk in enumerate(chunks):
        if embeddings:
            vec = embeddings[i]
        else:
            vec = _tfidf_vectorize(chunk.content, all_keywords)

        # 存储为 JSON
        chunk.vector_id = json.dumps(vec, ensure_ascii=False)
        db.session.add(chunk)
        updated += 1

    db.session.commit()
    return {'indexed': updated, 'mode': 'openai' if embeddings else 'tfidf', 'keywords_count': len(all_keywords) if embeddings is None else 0}


# ═══════════════════════════════════════════════════
# 第三部分：语义检索
# ═══════════════════════════════════════════════════

def _extract_heading(content: str) -> str:
    """从 chunk 内容中提取章节标题，格式 【xxx】"""
    m = re.match(r'^【([^】]+)】', content)
    if m:
        return m.group(1)
    return ''


def _get_chunk_source(chunk: DocumentChunk) -> dict:
    """获取 chunk 的源信息"""
    heading = _extract_heading(chunk.content)
    courseware = db.session.get(Courseware, chunk.courseware_id)
    return {
        'chunk_index': chunk.chunk_index,
        'courseware_title': courseware.title if courseware else '',
        'heading': heading,
        'page_ref': chunk.page_ref,
        'token_count': chunk.token_count,
    }


def search(query: str, course_id: int = None, top_k: int = TOP_K_RETRIEVAL) -> list:
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
        results.append({'chunk': chunk, 'score': round(score, 4), 'source': _get_chunk_source(chunk)})
    return results

def generate_answer(question: str, course_id: int = None) -> dict:
    """完整的 RAG 问答管线

    Args:
        question: 用户问题
        course_id: 限定课程范围

    Returns:
        {
            'answer': str,           # LLM 生成的回答
            'sources': [...],        # 引用的 chunk 源信息
            'chunk_count': int,      # 检索到的相关 chunk 数
            'search_mode': str,      # 检索模式: openai / tfidf / none
        }
    """
    # 1. 语义检索
    results = search(question, course_id)

    if not results:
        return {
            'answer': '抱歉，没有在课件中找到与您问题相关的内容。请尝试换个问法，或联系老师上传更多课件。',
            'sources': [],
            'chunk_count': 0,
            'search_mode': 'none',
        }

    # 2. 构建上下文（带章节标注）
    context_parts = []
    sources = []
    total_chars = 0

    for i, r in enumerate(results):
        chunk = r['chunk']
        source = r['source']
        heading = source['heading'] or '（未分段）'

        # 带章节来源的片段标注
        labeled = f'【资料{i+1}·{heading}】\n{chunk.content}'
        if total_chars + len(labeled) > MAX_CONTEXT_CHARS:
            break

        context_parts.append(labeled)
        total_chars += len(labeled)
        sources.append(source)

    context_text = '\n\n---\n\n'.join(context_parts)

    # 3. 调用 LLM
    try:
        answer = llm_client.chat_with_context(question, [p['chunk'].content for p in results[:3]])
    except RuntimeError as e:
        logger.error(f'LLM 调用失败，返回检索摘要: {e}')
        # 降级：返回检索到的原文摘要
        answer = (
            '（AI 助手暂时不可用，以下是课件中与您问题相关的内容摘要）\n\n'
            f'{context_text[:2000]}'
        )
    except Exception as e:
        logger.error(f'RAG 生成失败: {e}')
        answer = '抱歉，回答生成过程中出现错误，请稍后再试。'

    # 4. 确定搜索模式
    has_embedding = any(r['chunk'].vector_id for r in results)
    search_mode = 'openai' if has_embedding and len(results[0]['chunk'].vector_id) > 200 else 'tfidf'

    return {
        'answer': answer,
        'sources': sources[:5],  # 最多返回 5 个来源
        'chunk_count': len(results),
        'search_mode': search_mode,
    }


# 全局单例
rag_service = {
    'index_courseware': index_courseware,
    'search': search,
    'generate_answer': generate_answer,
}




