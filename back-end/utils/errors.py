"""自定义异常类与全局错误处理器"""


class APIException(Exception):
    """API 基础异常"""
    status_code = 400

    def __init__(self, message, status_code=None, data=None):
        super().__init__(message)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.data = data


class AuthenticationError(APIException):
    """401 - 未登录或 Token 过期"""
    status_code = 401


class ForbiddenError(APIException):
    """403 - 权限不足"""
    status_code = 403


class NotFoundError(APIException):
    """404 - 资源不存在"""
    status_code = 404


class ConflictError(APIException):
    """409 - 资源冲突（如用户名已存在、已选课）"""
    status_code = 409


def register_error_handlers(app):
    """注册全局错误处理器"""

    from flask import jsonify

    @app.errorhandler(APIException)
    def handle_api_exception(error):
        response = {
            'code': error.status_code,
            'message': error.message,
            'data': error.data
        }
        return jsonify(response), error.status_code

    @app.errorhandler(400)
    def handle_400(error):
        return jsonify({
            'code': 400,
            'message': '请求参数错误',
            'data': None
        }), 400

    @app.errorhandler(404)
    def handle_404(error):
        return jsonify({
            'code': 404,
            'message': '资源不存在',
            'data': None
        }), 404

    @app.errorhandler(405)
    def handle_405(error):
        return jsonify({
            'code': 405,
            'message': '请求方法不允许',
            'data': None
        }), 405

    @app.errorhandler(500)
    def handle_500(error):
        return jsonify({
            'code': 500,
            'message': '服务器内部错误',
            'data': None
        }), 500
