"""Flask 应用入口"""
import os
from flask import Flask
from config import config_map
from extensions import init_extensions


def create_app(config_name=None):
    """应用工厂函数"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config_map[config_name])

    # 初始化扩展
    init_extensions(app)

    # 注册蓝图
    from api import register_blueprints
    register_blueprints(app)

    # 注册错误处理
    from utils.errors import register_error_handlers
    register_error_handlers(app)

    # 确保上传目录存在
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database'), exist_ok=True)

    # 自动建表 + 种子用户
    with app.app_context():
        from extensions import db
        from werkzeug.security import generate_password_hash
        from models import User
        db.create_all()
        for uname, pwd, role in [
            ('admin', 'admin123', 'admin'),
            ('teacher1', 'teacher123', 'teacher'),
            ('student1', 'student123', 'student'),
        ]:
            if not User.query.filter_by(username=uname).first():
                db.session.add(User(username=uname, password=generate_password_hash(pwd), role=role))
        db.session.commit()

    return app


if __name__ == '__main__':
    application = create_app()
    application.run(debug=True, host='0.0.0.0', port=5000)
