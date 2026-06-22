"""课件相关接口"""
import os
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import User, UserCourse, Courseware, DocumentChunk, Course, KpCourseware
from services.document_service import document_service
from utils.errors import ForbiddenError, NotFoundError

courseware_bp = Blueprint('courseware', __name__)


@courseware_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload():
    """上传课件"""
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)

    if user.role not in ('teacher', 'admin'):
        return jsonify({'code': 403, 'message': '仅教师可上传课件', 'data': None}), 403

    if 'file' not in request.files:
        return jsonify({'code': 400, 'message': '请选择文件', 'data': None}), 400

    file = request.files['file']
    if not file.filename:
        return jsonify({'code': 400, 'message': '请选择文件', 'data': None}), 400

    course_id = request.form.get('course_id')
    if not course_id:
        return jsonify({'code': 400, 'message': '请指定课程', 'data': None}), 400

    try:
        course_id = int(course_id)
    except ValueError:
        return jsonify({'code': 400, 'message': '课程ID无效', 'data': None}), 400

    # 检查权限
    enrollment = UserCourse.query.filter_by(
        user_id=user_id, course_id=course_id, role='teacher'
    ).first()
    if not enrollment:
        course = db.session.get(Course, course_id)
        if course and course.teacher_id == user_id:
            enrollment = course
        return jsonify({'code': 403, 'message': '仅该课程的教师可上传课件', 'data': None}), 403

    title = request.form.get('title')

    try:
        courseware = document_service.save_upload(file, course_id, user_id, title)
    except ValueError as e:
        return jsonify({'code': 400, 'message': str(e), 'data': None}), 400

    # 异步处理文档（简单版：同步处理，以后可改用后台任务）
    try:
        document_service.process_document(
            courseware.id,
            chunk_size=current_app.config.get('CHUNK_SIZE', 500),
            chunk_overlap=current_app.config.get('CHUNK_OVERLAP', 50),
        )
    except Exception as e:
        return jsonify({
            'code': 200,
            'message': f'上传成功，但文档解析失败: {e}',
            'data': courseware.to_dict(include_uploader=True)
        }), 200

    return jsonify({
        'code': 200,
        'message': '上传成功，解析完成',
        'data': courseware.to_dict(include_uploader=True)
    }), 200


@courseware_bp.route('', methods=['GET'])
@jwt_required()
def list_courseware():
    """获取课件列表"""
    course_id = request.args.get('course_id')
    if not course_id:
        return jsonify({'code': 400, 'message': '请指定课程', 'data': None}), 400

    coursewares = Courseware.query.filter_by(course_id=int(course_id))\
        .order_by(Courseware.uploaded_at.desc()).all()

    return jsonify({
        'code': 200,
        'message': 'success',
        'data': {
            'courseware': [cw.to_dict(include_uploader=True) for cw in coursewares]
        }
    }), 200


@courseware_bp.route('/<int:courseware_id>', methods=['GET'])
@jwt_required()
def get_courseware(courseware_id):
    """获取课件详情"""
    cw = db.session.get(Courseware, courseware_id)
    if not cw:
        raise NotFoundError('课件不存在')

    data = cw.to_dict(include_uploader=True)
    data['course_name'] = cw.course.course_name if cw.course else ''
    return jsonify({'code': 200, 'message': 'success', 'data': data}), 200


@courseware_bp.route('/<int:courseware_id>/chunks', methods=['GET'])
@jwt_required()
def get_chunks(courseware_id):
    """获取课件分块列表"""
    cw = db.session.get(Courseware, courseware_id)
    if not cw:
        raise NotFoundError('课件不存在')

    chunks = DocumentChunk.query.filter_by(courseware_id=courseware_id)\
        .order_by(DocumentChunk.chunk_index).all()

    return jsonify({
        'code': 200,
        'message': 'success',
        'data': {
            'courseware_id': courseware_id,
            'total': len(chunks),
            'chunks': [c.to_dict() for c in chunks],
        }
    }), 200


@courseware_bp.route('/<int:courseware_id>', methods=['DELETE'])
@jwt_required()
def delete_courseware(courseware_id):
    """删除课件"""
    user_id = int(get_jwt_identity())
    cw = db.session.get(Courseware, courseware_id)
    if not cw:
        raise NotFoundError('课件不存在')

    if cw.uploader_id != user_id:
        user = db.session.get(User, user_id)
        if user.role != 'admin':
            return jsonify({'code': 403, 'message': '无权限删除', 'data': None}), 403

    # 删除文件
    if os.path.exists(cw.file_path):
        try:
            os.remove(cw.file_path)
        except OSError:
            pass

    # 删除知识点-课件关联记录
    KpCourseware.query.filter_by(courseware_id=courseware_id).delete()

    # 删除分块记录（数据库 ON DELETE SET NULL 会将 kp_courseware.chunk_id 置空）
    DocumentChunk.query.filter_by(courseware_id=courseware_id).delete()

    # 删除课件记录
    db.session.delete(cw)
    db.session.commit()

    return jsonify({'code': 200, 'message': '课件已删除', 'data': None}), 200





