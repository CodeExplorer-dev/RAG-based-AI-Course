"""注册所有 API 蓝图"""


def register_blueprints(app):
    from api.auth import auth_bp
    from api.user import user_bp
    from api.course import course_bp
    from api.courseware import courseware_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/user')
    app.register_blueprint(course_bp, url_prefix='/api/courses')
    app.register_blueprint(courseware_bp, url_prefix='/api/courseware')
