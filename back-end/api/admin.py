"""管理员接口 — 系统面板、用户管理、课程管理"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import User, Course, UserCourse, Courseware
from utils.errors import NotFoundError, ForbiddenError

admin_bp = Blueprint('admin', __name__)


def _require_admin():
    """验证当前用户是否为管理员，返回 user 对象"""
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if not user or user.role != 'admin':
        return None
    return user


# ─── 系统面板 ────────────────────────────────────────────

@admin_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    """获取系统统计数据"""
    admin = _require_admin()
    if not admin:
        return jsonify({'code': 403, 'message': '需要管理员权限', 'data': None}), 403

    total_users = User.query.count()
    total_courses = Course.query.count()
    total_courseware = Courseware.query.count()

    return jsonify({
        'code': 200,
        'message': 'success',
        'data': {
            'users': total_users,
            'courses': total_courses,
            'courseware': total_courseware,
        }
    }), 200


# ─── 用户管理 ────────────────────────────────────────────

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def list_users():
    """获取所有用户列表"""
    admin = _require_admin()
    if not admin:
        return jsonify({'code': 403, 'message': '需要管理员权限', 'data': None}), 403

    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': {'users': [u.to_dict() for u in users]}
    }), 200


@admin_bp.route('/users/<int:user_id>/role', methods=['PUT'])
@jwt_required()
def change_user_role(user_id):
    """修改用户角色"""
    admin = _require_admin()
    if not admin:
        return jsonify({'code': 403, 'message': '需要管理员权限', 'data': None}), 403

    target_user = db.session.get(User, user_id)
    if not target_user:
        raise NotFoundError('用户不存在')

    if target_user.role == 'admin':
        return jsonify({'code': 403, 'message': '不能修改其他管理员的角色', 'data': None}), 403

    data = request.get_json()
    new_role = data.get('role') if data else None
    if new_role not in ('student', 'teacher'):
        return jsonify({'code': 400, 'message': '角色只能是 student 或 teacher', 'data': None}), 400

    target_user.role = new_role
    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '角色已更新',
        'data': target_user.to_dict()
    }), 200


@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """删除用户"""
    admin = _require_admin()
    if not admin:
        return jsonify({'code': 403, 'message': '需要管理员权限', 'data': None}), 403

    target_user = db.session.get(User, user_id)
    if not target_user:
        raise NotFoundError('用户不存在')

    if target_user.role == 'admin':
        return jsonify({'code': 403, 'message': '不能删除其他管理员', 'data': None}), 403

    # 清理关联数据
    # 1. 用户上传的课件及分块
    from models import DocumentChunk
    cws = Courseware.query.filter_by(uploader_id=user_id).all()
    for cw in cws:
        DocumentChunk.query.filter_by(courseware_id=cw.id).delete()
        db.session.delete(cw)

    # 2. 用户创建的课程：清理课程下的选课记录、课件、分块
    created_courses = Course.query.filter_by(teacher_id=user_id).all()
    for course in created_courses:
        UserCourse.query.filter_by(course_id=course.id).delete()
        cw_list = Courseware.query.filter_by(course_id=course.id).all()
        for cw in cw_list:
            DocumentChunk.query.filter_by(courseware_id=cw.id).delete()
            db.session.delete(cw)
        db.session.delete(course)

    # 3. 用户的选课记录
    UserCourse.query.filter_by(user_id=user_id).delete()

    # 4. 删除用户
    db.session.delete(target_user)
    db.session.commit()

    return jsonify({'code': 200, 'message': '用户已删除', 'data': None}), 200


# ─── 课程管理 ────────────────────────────────────────────

@admin_bp.route('/courses', methods=['GET'])
@jwt_required()
def list_all_courses():
    """获取系统所有课程列表（管理员视图）"""
    admin = _require_admin()
    if not admin:
        return jsonify({'code': 403, 'message': '需要管理员权限', 'data': None}), 403

    courses = Course.query.order_by(Course.created_at.desc()).all()
    courses_data = []
    for course in courses:
        info = course.to_dict(include_teacher=True)
        info['student_count'] = UserCourse.query.filter_by(
            course_id=course.id, role='student'
        ).count()
        info['courseware_count'] = course.coursewares.count()
        courses_data.append(info)

    return jsonify({
        'code': 200,
        'message': 'success',
        'data': {'courses': courses_data}
    }), 200


@admin_bp.route('/courses/<int:course_id>', methods=['DELETE'])
@jwt_required()
def delete_any_course(course_id):
    """管理员删除任意课程"""
    admin = _require_admin()
    if not admin:
        return jsonify({'code': 403, 'message': '需要管理员权限', 'data': None}), 403

    course = db.session.get(Course, course_id)
    if not course:
        raise NotFoundError('课程不存在')

    from models import DocumentChunk
    # 删除选课记录
    UserCourse.query.filter_by(course_id=course_id).delete()
    # 删除课件及分块
    cws = Courseware.query.filter_by(course_id=course_id).all()
    for cw in cws:
        DocumentChunk.query.filter_by(courseware_id=cw.id).delete()
        db.session.delete(cw)
    # 删除课程
    db.session.delete(course)
    db.session.commit()

    return jsonify({'code': 200, 'message': '课程已删除', 'data': None}), 200
