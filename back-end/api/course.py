"""课程相关接口"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import User, Course, UserCourse
from utils.errors import ForbiddenError, NotFoundError, ConflictError

course_bp = Blueprint('course', __name__)


@course_bp.route('', methods=['GET'])
@jwt_required()
def list_courses():
    """获取当前用户的课程列表"""
    user_id = int(get_jwt_identity())
    enrollments = UserCourse.query.filter_by(user_id=user_id).all()

    courses_data = []
    for enrollment in enrollments:
        course = enrollment.course
        if course:
            info = course.to_dict(include_teacher=True)
            info['role'] = enrollment.role
            info['enrolled_at'] = enrollment.enrolled_at.strftime('%Y-%m-%d %H:%M:%S')
            info['student_count'] = UserCourse.query.filter_by(
                course_id=course.id, role='student'
            ).count()
            info['courseware_count'] = course.coursewares.count()
            courses_data.append(info)

    return jsonify({'code': 200, 'message': 'success', 'data': {'courses': courses_data}}), 200


@course_bp.route('', methods=['POST'])
@jwt_required()
def create_course():
    """创建课程（教师/管理员）"""
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)

    if user.role not in ('teacher', 'admin'):
        return jsonify({'code': 403, 'message': '仅教师和管理员可创建课程', 'data': None}), 403

    data = request.get_json()
    if not data or not data.get('course_name'):
        return jsonify({'code': 400, 'message': '课程名称不能为空', 'data': None}), 400

    course = Course(
        course_name=data['course_name'],
        description=data.get('description', ''),
        teacher_id=user_id,
        join_code=Course.generate_join_code(),
    )
    db.session.add(course)
    db.session.commit()

    # 创建者自动加入课程
    enrollment = UserCourse(user_id=user_id, course_id=course.id, role='teacher')
    db.session.add(enrollment)
    db.session.commit()

    result = course.to_dict()
    return jsonify({'code': 200, 'message': '课程创建成功', 'data': result}), 200


@course_bp.route('/join', methods=['POST'])
@jwt_required()
def join_course():
    """通过选课码加入课程（学生）"""
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)

    data = request.get_json()
    if not data or not data.get('join_code'):
        return jsonify({'code': 400, 'message': '请输入选课码', 'data': None}), 400

    join_code = data['join_code'].strip().upper()
    course = Course.query.filter_by(join_code=join_code).first()
    if not course:
        return jsonify({'code': 404, 'message': '选课码无效', 'data': None}), 404

    # 检查是否已加入
    existing = UserCourse.query.filter_by(user_id=user_id, course_id=course.id).first()
    if existing:
        return jsonify({'code': 409, 'message': '你已加入该课程', 'data': None}), 409

    enrollment = UserCourse(user_id=user_id, course_id=course.id, role='student')
    db.session.add(enrollment)
    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '加入课程成功',
        'data': {
            'course_id': course.id,
            'course_name': course.course_name,
            'teacher_name': course.teacher.username if course.teacher else '',
            'enrolled_at': enrollment.enrolled_at.strftime('%Y-%m-%d %H:%M:%S'),
        }
    }), 200


@course_bp.route('/<int:course_id>', methods=['GET'])
@jwt_required()
def get_course(course_id):
    """获取课程详情"""
    user_id = int(get_jwt_identity())

    # 检查是否选课
    enrollment = UserCourse.query.filter_by(user_id=user_id, course_id=course_id).first()
    if not enrollment:
        return jsonify({'code': 403, 'message': '你未加入该课程', 'data': None}), 403

    course = db.session.get(Course, course_id)
    if not course:
        raise NotFoundError('课程不存在')

    data = course.to_dict(include_teacher=True)
    data['student_count'] = UserCourse.query.filter_by(course_id=course_id, role='student').count()
    data['courseware_count'] = course.coursewares.count()
    return jsonify({'code': 200, 'message': 'success', 'data': data}), 200


@course_bp.route('/<int:course_id>/students', methods=['GET'])
@jwt_required()
def list_students(course_id):
    """获取课程学生列表（教师）"""
    user_id = int(get_jwt_identity())

    # 检查权限
    enrollment = UserCourse.query.filter_by(
        user_id=user_id, course_id=course_id, role='teacher'
    ).first()
    if not enrollment:
        return jsonify({'code': 403, 'message': '仅授课教师可查看学生列表', 'data': None}), 403

    student_enrollments = UserCourse.query.filter_by(
        course_id=course_id, role='student'
    ).all()

    students = []
    for se in student_enrollments:
        students.append({
            'id': se.user_id,
            'username': se.user.username,
            'email': se.user.email,
            'enrolled_at': se.enrolled_at.strftime('%Y-%m-%d %H:%M:%S'),
        })

    return jsonify({'code': 200, 'message': 'success', 'data': {'students': students}}), 200


@course_bp.route('/<int:course_id>', methods=['DELETE'])
@jwt_required()
def delete_course(course_id):
    """删除课程（仅创建者/管理员）"""
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    course = db.session.get(Course, course_id)

    if not course:
        raise NotFoundError('课程不存在')

    # 仅课程创建者或管理员可删除
    if course.teacher_id != user_id and user.role != 'admin':
        return jsonify({'code': 403, 'message': '无权限删除该课程', 'data': None}), 403

    # 删除关联数据：选课记录、课件（含分块）、课程
    UserCourse.query.filter_by(course_id=course_id).delete()
    from models import Courseware, DocumentChunk
    coursewares = Courseware.query.filter_by(course_id=course_id).all()
    for cw in coursewares:
        DocumentChunk.query.filter_by(courseware_id=cw.id).delete()
        db.session.delete(cw)
    db.session.delete(course)
    db.session.commit()

    return jsonify({'code': 200, 'message': '课程已删除', 'data': None}), 200
