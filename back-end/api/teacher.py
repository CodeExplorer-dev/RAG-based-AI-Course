from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Course, Courseware, StudentQuestion
teacher_bp = Blueprint('teacher', __name__)
@teacher_bp.route('/stats', methods=['GET'])
@jwt_required()
def stats():
    uid = int(get_jwt_identity())
    cnt = Course.query.filter_by(teacher_id=uid).count()
    ids = [c.id for c in Course.query.filter_by(teacher_id=uid).all()]
    cw = Courseware.query.filter(Courseware.course_id.in_(ids)).count() if ids else 0
    q = StudentQuestion.query.count()
    return jsonify({'code': 200, 'message': 'success', 'data': {'courses': cnt, 'courseware': cw, 'questions': q, 'knowledge_points': 0}}), 200
