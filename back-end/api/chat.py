"""AI 问答接口 — RAG 检索增强生成管线"""
import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import Course, Courseware, DocumentChunk, UserCourse
from services.rag_service import generate_answer, search, index_courseware

chat_bp = Blueprint("chat", __name__)
logger = logging.getLogger(__name__)


@chat_bp.route("", methods=["POST"])
@jwt_required()
def chat():
    """AI 问答接口：RAG 检索 → Prompt 组装 → LLM 生成 → 引用标注"""
    user_id = int(get_jwt_identity())

    data = request.get_json() or {}
    message = data.get("message", "").strip()
    course_id = data.get("course_id")

    if not message:
        return jsonify({"code": 400, "message": "请输入问题", "data": None}), 400

    # 验证课程访问权限
    if course_id:
        course = db.session.get(Course, int(course_id))
        if not course:
            return jsonify({"code": 404, "message": "课程不存在", "data": None}), 404
        enrollment = UserCourse.query.filter_by(user_id=user_id, course_id=int(course_id)).first()
        if not enrollment and course.teacher_id != user_id:
            return jsonify({"code": 403, "message": "请先加入课程", "data": None}), 403

    # 执行 RAG 管线
    result = generate_answer(message, course_id=int(course_id) if course_id else None)

    return jsonify({
        "code": 200,
        "message": "success",
        "data": result,
    }), 200


@chat_bp.route("/search", methods=["POST"])
@jwt_required()
def search_chunks():
    """仅检索，不生成回答（前端可用来展示相关课件片段）"""
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    query = data.get("query", "").strip()
    course_id = data.get("course_id")
    top_k = int(data.get("top_k", 5))

    if not query:
        return jsonify({"code": 400, "message": "请输入搜索内容", "data": None}), 400

    results = search(query, course_id=int(course_id) if course_id else None, top_k=top_k)

    return jsonify({
        "code": 200,
        "message": "success",
        "data": {
            "total": len(results),
            "results": [
                {
                    "chunk_index": r["chunk"].chunk_index,
                    "score": r["score"],
                    "content": r["chunk"].content,
                    "source": r["source"],
                }
                for r in results
            ],
        }
    }), 200


@chat_bp.route("/reindex", methods=["POST"])
@jwt_required()
def reindex():
    """手动重新索引课件的 embeddings"""
    data = request.get_json() or {}
    courseware_id = data.get("courseware_id")
    if not courseware_id:
        return jsonify({"code": 400, "message": "请指定 courseware_id", "data": None}), 400

    result = index_courseware(int(courseware_id))

    return jsonify({
        "code": 200,
        "message": "索引完成",
        "data": result,
    }), 200


@chat_bp.route("/feedback", methods=["POST"])
@jwt_required()
def chat_feedback():
    """用户对 AI 回答的反馈"""
    data = request.get_json() or {}
    logger.info(
        f"Chat feedback: user={get_jwt_identity()}, "
        f"type={data.get('type')}, message_id={data.get('message_id')}"
    )
    return jsonify({"code": 200, "message": "反馈已记录", "data": None}), 200
