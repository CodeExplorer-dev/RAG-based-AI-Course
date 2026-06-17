"""AI 问答接口 — RAG 检索 + LLM 生成"""
import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import Course, Courseware, DocumentChunk, UserCourse
from utils.llm_client import llm_client

chat_bp = Blueprint('chat', __name__)
logger = logging.getLogger(__name__)

# 默认检索的 chunk 数量
DEFAULT_TOP_K = 5


def keyword_search(query: str, course_id: int = None, top_k: int = DEFAULT_TOP_K) -> list:
    """
    关键词检索：基于 MySQL 的 LIKE 查询在 document_chunks 中检索相关文本。
    后期可替换为 ChromaDB 向量检索。
    """
    # 拆分查询关键词
    keywords = [kw.strip() for kw in query.split() if len(kw.strip()) >= 1]

    if course_id:
        # 限定课程范围：通过 courseware 关联
        chunk_query = DocumentChunk.query.join(
            Courseware, DocumentChunk.courseware_id == Courseware.id
        ).filter(Courseware.course_id == course_id)
    else:
        chunk_query = DocumentChunk.query

    # 构建 OR 条件的关键词匹配
    from sqlalchemy import or_
    conditions = []
    for kw in keywords:
        conditions.append(DocumentChunk.content.like(f'%{kw}%'))

    if conditions:
        chunk_query = chunk_query.filter(or_(*conditions))

    chunks = chunk_query.limit(top_k * 2).all()

    # 简单的相关性排序：按关键词命中次数
    scored = []
    for chunk in chunks:
        score = sum(1 for kw in keywords if kw.lower() in chunk.content.lower())
        scored.append((score, chunk))

    scored.sort(key=lambda x: x[0], reverse=True)

    return [chunk.content for _, chunk in scored[:top_k]]


def build_context(chunks: list, max_chars: int = 4000) -> str:
    """将检索到的分块拼接为上下文，控制总长度"""
    context = ''
    for i, chunk in enumerate(chunks):
        if len(context) + len(chunk) > max_chars:
            break
        context += f'\n[资料{i+1}]\n{chunk}\n'
    return context.strip()


@chat_bp.route('', methods=['POST'])
@jwt_required()
def chat():
    """AI 问答接口"""
    user_id = int(get_jwt_identity())

    data = request.get_json() or {}
    message = data.get('message', '').strip()
    course_id = data.get('course_id')

    if not message:
        return jsonify({'code': 400, 'message': '请输入问题', 'data': None}), 400

    # 验证课程访问权限（如果指定了课程）
    if course_id:
        course = db.session.get(Course, int(course_id))
        if not course:
            return jsonify({'code': 404, 'message': '课程不存在', 'data': None}), 404
        # 检查用户是否已加入课程
        enrollment = UserCourse.query.filter_by(user_id=user_id, course_id=int(course_id)).first()
        if not enrollment and course.teacher_id != user_id:
            return jsonify({'code': 403, 'message': '请先加入课程', 'data': None}), 403

    try:
        # 1. 关键词检索相关分块
        chunks = keyword_search(message, course_id=int(course_id) if course_id else None)

        if not chunks:
            return jsonify({
                'code': 200,
                'message': 'success',
                'data': {
                    'answer': '抱歉，没有在课件中找到与您问题相关的内容。请尝试换个问法，或联系老师上传更多课件。',
                    'sources': [],
                    'chunk_count': 0,
                }
            }), 200

        # 2. 构造上下文 + 调用 LLM
        context_text = build_context(chunks)
        answer = llm_client.chat_with_context(message, chunks)

        # 3. 生成来源摘要
        sources = []
        for i, chunk in enumerate(chunks[:3]):
            preview = chunk[:80].replace('\n', ' ') + ('...' if len(chunk) > 80 else '')
            sources.append(f'片段{i+1}: {preview}')

        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {
                'answer': answer,
                'sources': sources,
                'chunk_count': len(chunks),
            }
        }), 200

    except RuntimeError as e:
        # LLM 调用失败
        logger.error(f'LLM 调用失败: {e}')
        # 降级：返回检索到的原文摘要
        context_text = build_context(chunks, max_chars=2000)
        return jsonify({
            'code': 200,
            'message': 'LLM 暂不可用，以下为课件原文摘要',
            'data': {
                'answer': f'（AI 助手暂不可用，以下是课件中与您问题相关的内容摘要）\n\n{context_text}',
                'sources': [],
                'chunk_count': len(chunks),
            }
        }), 200


@chat_bp.route('/feedback', methods=['POST'])
@jwt_required()
def chat_feedback():
    """用户对 AI 回答的反馈"""
    data = request.get_json() or {}
    # message_id 和 type 先记录日志，后续可存入 feedback 表
    logger.info(f'Chat feedback: user={get_jwt_identity()}, type={data.get("type")}, message_id={data.get("message_id")}')
    return jsonify({'code': 200, 'message': '反馈已记录', 'data': None}), 200
