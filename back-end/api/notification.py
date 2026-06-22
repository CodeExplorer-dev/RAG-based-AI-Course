"""通知接口 — 站内通知管理"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import Notification

notification_bp = Blueprint("notification", __name__)


@notification_bp.route("", methods=["GET"])
@jwt_required()
def list_notifications():
    """获取当前用户的通知列表（未读在前）"""
    user_id = int(get_jwt_identity())
    notis = Notification.query.filter_by(user_id=user_id)\
        .order_by(Notification.is_read.asc(), Notification.created_at.desc()).limit(50).all()
    return jsonify({
        "code": 200, "message": "success",
        "data": {"notifications": [n.to_dict() for n in notis]}
    }), 200


@notification_bp.route("/unread-count", methods=["GET"])
@jwt_required()
def unread_count():
    """获取未读通知数量"""
    user_id = int(get_jwt_identity())
    count = Notification.query.filter_by(user_id=user_id, is_read=False).count()
    return jsonify({"code": 200, "message": "success", "data": {"count": count}}), 200


@notification_bp.route("/<int:noti_id>/read", methods=["PUT"])
@jwt_required()
def mark_read(noti_id):
    """标记单条通知为已读"""
    user_id = int(get_jwt_identity())
    noti = Notification.query.filter_by(id=noti_id, user_id=user_id).first()
    if not noti:
        return jsonify({"code": 404, "message": "通知不存在", "data": None}), 404
    noti.is_read = True
    db.session.commit()
    return jsonify({"code": 200, "message": "success", "data": noti.to_dict()}), 200


@notification_bp.route("/read-all", methods=["PUT"])
@jwt_required()
def mark_all_read():
    """标记当前用户所有通知为已读"""
    user_id = int(get_jwt_identity())
    Notification.query.filter_by(user_id=user_id, is_read=False).update({"is_read": True})
    db.session.commit()
    return jsonify({"code": 200, "message": "全部标记已读", "data": None}), 200
