"""用户相关接口"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import User

user_bp = Blueprint('user', __name__)


@user_bp.route('/me', methods=['GET'])
@jwt_required()
def get_me():
    """获取当前用户信息"""
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'code': 404, 'message': '用户不存在', 'data': None}), 404
    return jsonify({'code': 200, 'message': 'success', 'data': user.to_dict()}), 200


@user_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_me():
    """更新当前用户信息"""
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'code': 404, 'message': '用户不存在', 'data': None}), 404

    data = request.get_json()
    if not data:
        return jsonify({'code': 400, 'message': '请提供要更新的字段', 'data': None}), 400

    if 'email' in data:
        if User.query.filter(User.email == data['email'], User.id != user_id).first():
            return jsonify({'code': 409, 'message': '邮箱已被使用', 'data': None}), 409
        user.email = data['email']

    if 'password' in data:
        from werkzeug.security import generate_password_hash
        user.password = generate_password_hash(data['password'])

    db.session.commit()
    return jsonify({'code': 200, 'message': '更新成功', 'data': user.to_dict()}), 200
