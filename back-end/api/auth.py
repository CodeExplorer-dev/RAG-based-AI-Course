"""认证相关接口"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from services.auth_service import auth_service

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'code': 400, 'message': '用户名和密码不能为空', 'data': None}), 400

    result = auth_service.register(
        username=data['username'],
        password=data['password'],
        email=data.get('email'),
        role=data.get('role', 'student'),
    )
    return jsonify({'code': 200, 'message': '注册成功', 'data': result}), 200


@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'code': 400, 'message': '用户名和密码不能为空', 'data': None}), 400

    result = auth_service.login(data['username'], data['password'])
    return jsonify({'code': 200, 'message': '登录成功', 'data': result}), 200


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """刷新 access_token"""
    identity = get_jwt_identity()
    result = auth_service.refresh_token(identity)
    return jsonify({'code': 200, 'message': '刷新成功', 'data': result}), 200
