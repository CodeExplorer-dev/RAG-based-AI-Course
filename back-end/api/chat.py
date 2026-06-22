"""AI 问答接口 — RAG 检索增强生成 + 对话持久化"""
import time
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import Course, UserCourse, QaConversation, QaMessage, Feedback
from services.rag_service import generate_answer, search, index_courseware

chat_bp = Blueprint("chat", __name__)
logger = logging.getLogger(__name__)


# ─── 会话管理 ────────────────────────────────────────────

@chat_bp.route("/conversations", methods=["GET"])
@jwt_required()
def list_conversations():
    """获取当前用户的所有会话列表（按最后更新时间倒序）"""
    user_id = int(get_jwt_identity())
    convs = QaConversation.query.filter_by(user_id=user_id)\
        .order_by(QaConversation.updated_at.desc()).all()
    return jsonify({
        "code": 200,
        "message": "success",
        "data": {"conversations": [c.to_dict() for c in convs]}
    }), 200


@chat_bp.route("/conversations/<int:conv_id>", methods=["GET"])
@jwt_required()
def get_conversation(conv_id):
    """获取指定会话的详情（含消息列表）"""
    user_id = int(get_jwt_identity())
    conv = QaConversation.query.filter_by(id=conv_id, user_id=user_id).first()
    if not conv:
        return jsonify({"code": 404, "message": "会话不存在", "data": None}), 404

    data = conv.to_dict()
    data["messages"] = [m.to_dict() for m in
                        QaMessage.query.filter_by(conversation_id=conv_id)
                        .order_by(QaMessage.created_at).all()]
    return jsonify({"code": 200, "message": "success", "data": data}), 200


@chat_bp.route("/conversations/<int:conv_id>", methods=["DELETE"])
@jwt_required()
def delete_conversation(conv_id):
    """删除指定会话（级联删除所有消息）"""
    user_id = int(get_jwt_identity())
    conv = QaConversation.query.filter_by(id=conv_id, user_id=user_id).first()
    if not conv:
        return jsonify({"code": 404, "message": "会话不存在", "data": None}), 404
    db.session.delete(conv)
    db.session.commit()
    return jsonify({"code": 200, "message": "会话已删除", "data": None}), 200


# ─── AI 问答（RAG + 持久化） ──────────────────────────

@chat_bp.route("", methods=["POST"])
@jwt_required()
def chat():
    """AI 问答接口：RAG 检索 → 对话持久化 → 返回结果"""
    user_id = int(get_jwt_identity())

    data = request.get_json() or {}
    message = data.get("message", "").strip()
    course_id = data.get("course_id")
    conversation_id = data.get("conversation_id")

    if not message:
        return jsonify({"code": 400, "message": "请输入问题", "data": None}), 400

    # ── 验证课程访问权限 ──
    if course_id:
        cid = int(course_id)
        course = db.session.get(Course, cid)
        if not course:
            return jsonify({"code": 404, "message": "课程不存在", "data": None}), 404
        enrollment = UserCourse.query.filter_by(user_id=user_id, course_id=cid).first()
        if not enrollment and course.teacher_id != user_id:
            return jsonify({"code": 403, "message": "请先加入课程", "data": None}), 403

    # ── 查找或创建会话 ──
    t0 = time.time()

    if conversation_id:
        conv = QaConversation.query.filter_by(id=int(conversation_id), user_id=user_id).first()
        if not conv:
            return jsonify({"code": 404, "message": "会话不存在或无权访问", "data": None}), 404
    else:
        # 自动命名会话：取用户第一条消息的前 30 个字
        title = (message[:30] + "...") if len(message) > 30 else message
        conv = QaConversation(
            user_id=user_id,
            course_id=int(course_id) if course_id else None,
            title=title,
        )
        db.session.add(conv)
        db.session.flush()  # 获得 conv.id

    # ── 保存用户消息 ──
    user_msg = QaMessage(
        conversation_id=conv.id,
        role="user",
        content=message,
    )
    db.session.add(user_msg)
    db.session.flush()

    # ── 执行 RAG 管线 ──
    try:
        result = generate_answer(message, course_id=int(course_id) if course_id else None)
        response_time_ms = int((time.time() - t0) * 1000)
    except Exception as e:
        logger.error(f"RAG 管线异常: {e}")
        result = {
            "answer": "抱歉，回答生成过程中出现错误，请稍后再试。",
            "sources": [],
            "chunk_count": 0,
            "search_mode": "none",
        }
        response_time_ms = int((time.time() - t0) * 1000)

    answer_text = result.get("answer", "")

    # ── 保存 AI 回复 ──
    ai_msg = QaMessage(
        conversation_id=conv.id,
        role="assistant",
        content=answer_text,
        referenced_chunks=result.get("sources", [])[:5] if result.get("sources") else None,
        token_usage=None,
        response_time_ms=response_time_ms,
    )
    db.session.add(ai_msg)

    # ── 更新会话状态 ──
    previous_count = conv.message_count or 0
    conv.message_count = previous_count + 2  # user + assistant
    conv.updated_at = datetime.utcnow()
    db.session.commit()

    # ── 返回结果（含 conversation_id） ──
    return jsonify({
        "code": 200,
        "message": "success",
        "data": {
            "conversation_id": conv.id,
            "conversation_title": conv.title,
            "answer": answer_text,
            "sources": result.get("sources", [])[:5],
            "chunk_count": result.get("chunk_count", 0),
            "search_mode": result.get("search_mode", "none"),
            "response_time_ms": response_time_ms,
        }
    }), 200


# ─── 检索（不生成回答） ──────────────────────────────────

@chat_bp.route("/search", methods=["POST"])
@jwt_required()
def search_chunks():
    """仅检索课件分块，不生成回答"""
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


# ─── 重新索引 Embeddings ─────────────────────────────────

@chat_bp.route("/reindex", methods=["POST"])
@jwt_required()
def reindex():
    """手动重新索引指定课件的 Embeddings"""
    data = request.get_json() or {}
    courseware_id = data.get("courseware_id")
    if not courseware_id:
        return jsonify({"code": 400, "message": "请指定 courseware_id", "data": None}), 400
    result = index_courseware(int(courseware_id))
    return jsonify({"code": 200, "message": "索引完成", "data": result}), 200


# ─── 用户反馈 ────────────────────────────────────────────

@chat_bp.route("/feedback", methods=["POST"])
@jwt_required()
def chat_feedback():
    """用户对 AI 回答进行评价（赞/踩）并持久化"""
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    message_id = data.get("message_id")
    feedback_type = data.get("type")  # like / dislike

    if not message_id:
        return jsonify({"code": 400, "message": "请指定 message_id", "data": None}), 400

    # 验证消息存在且属于当前用户
    msg = QaMessage.query.filter_by(id=int(message_id)).first()
    if not msg:
        return jsonify({"code": 404, "message": "消息不存在", "data": None}), 404

    conv = QaConversation.query.get(msg.conversation_id)
    if not conv or conv.user_id != user_id:
        return jsonify({"code": 403, "message": "无权评价此消息", "data": None}), 403

    rating = 1 if feedback_type == "like" else 0
    fb_type = "helpful" if feedback_type == "like" else "not_helpful"

    feedback = Feedback(
        user_id=user_id,
        message_id=int(message_id),
        rating=rating,
        feedback_type=fb_type,
    )
    db.session.add(feedback)
    db.session.commit()

    logger.info(f"Chat feedback saved: user={user_id}, message={message_id}, type={feedback_type}")
    return jsonify({"code": 200, "message": "反馈已记录", "data": None}), 200
