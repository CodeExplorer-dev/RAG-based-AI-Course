"""认证服务 — 注册、登录、Token管理"""

from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token
from extensions import db
from models import User
from utils.errors import ConflictError, AuthenticationError


class AuthService:

    def register(self, username: str, password: str, email: str = None, role: str = 'student') -> dict:
        """注册新用户"""
        # 检查用户名唯一
        if User.query.filter_by(username=username).first():
            raise ConflictError('用户名已存在')

        # 检查邮箱唯一
        if email and User.query.filter_by(email=email).first():
            raise ConflictError('邮箱已被注册')

        user = User(
            username=username,
            password=generate_password_hash(password),
            email=email,
            role=role,
        )
        db.session.add(user)
        db.session.commit()

        return user.to_dict()

    def login(self, username: str, password: str) -> dict:
        """登录，返回 JWT token"""
        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password, password):
            raise AuthenticationError('用户名或密码错误')

        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))

        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict(),
        }

    def refresh_token(self, identity: str) -> dict:
        """用 refresh_token 换取新的 access_token"""
        access_token = create_access_token(identity=identity)
        return {'access_token': access_token}


auth_service = AuthService()
