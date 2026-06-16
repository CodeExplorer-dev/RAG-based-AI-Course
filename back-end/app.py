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

    return app


if __name__ == '__main__':
    application = create_app()
    application.run(debug=True, port=5000)
