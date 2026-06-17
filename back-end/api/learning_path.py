"""学习路径推荐 API"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import Course, Courseware, UserCourse, DocumentChunk

learning_path_bp = Blueprint('learning_path', __name__)


@learning_path_bp.route('/<int:course_id>', methods=['GET'])
@jwt_required()
def get_learning_path(course_id):
    """生成学习路径推荐：基于课件内容结构，推荐学习顺序"""
    user_id = int(get_jwt_identity())

    enrollment = UserCourse.query.filter_by(user_id=user_id, course_id=course_id).first()
    if not enrollment:
        return jsonify({'code': 403, 'message': '请先加入课程', 'data': None}), 403

    course = db.session.get(Course, course_id)
    if not course:
        return jsonify({'code': 404, 'message': '课程不存在', 'data': None}), 404

    coursewares = Courseware.query.filter_by(course_id=course_id)\
        .order_by(Courseware.uploaded_at.asc()).all()

    learning_path = []
    for i, cw in enumerate(coursewares):
        chunks = DocumentChunk.query.filter_by(courseware_id=cw.id)\
            .order_by(DocumentChunk.chunk_index).limit(3).all()
        key_points = []
        for ch in chunks:
            lines = [l.strip() for l in ch.content.split('\n') if l.strip()]
            for line in lines[:5]:
                if len(line) > 5 and len(line) < 80 and not line.endswith(('。', '？', '！')):
                    key_points.append(line[:50])
                    if len(key_points) >= 3:
                        break
            if len(key_points) >= 3:
                break

        learning_path.append({
            'step': i + 1,
            'courseware_id': cw.id,
            'title': cw.title,
            'file_type': cw.file_type,
            'key_points': key_points[:3],
            'estimated_time': '{}分钟'.format(
                cw.page_count * 2 if cw.page_count else
                max(5, int(cw.file_size / 50000)) if cw.file_size else
                max(5, cw.chunk_count) if cw.chunk_count else
                10
            ),
            'uploaded_at': cw.uploaded_at.strftime('%Y-%m-%d %H:%M:%S') if cw.uploaded_at else None,
        })

    has_progress = len(coursewares) > 0
    from models import Question
    asked_count = Question.query.filter_by(
        student_id=user_id, course_id=course_id
    ).count()

    return jsonify({
        'code': 200,
        'message': 'success',
        'data': {
            'course_name': course.course_name,
            'total_courseware': len(coursewares),
            'learnt_count': min(asked_count, len(coursewares)),
            'progress_percent': round(asked_count / max(1, len(coursewares)) * 100) if has_progress else 0,
            'steps': learning_path,
        }
    }), 200


