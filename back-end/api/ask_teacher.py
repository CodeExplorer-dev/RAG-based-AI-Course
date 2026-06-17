"""提问接口 — 学生向老师提问"""
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import User, Course, UserCourse, Question
from utils.errors import NotFoundError, ForbiddenError

ask_teacher_bp = Blueprint('ask_teacher', __name__)


# ─── 学生提问 ────────────────────────────────────────────

@ask_teacher_bp.route('', methods=['POST'])
@jwt_required()
def submit_question():
    """学生提交问题"""
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if not user or user.role not in ('student', 'teacher'):
        return jsonify({'code': 403, 'message': '仅学生和教师可以提问', 'data': None}), 403

    data = request.get_json() or {}
    title = data.get('title', '').strip()
    content = data.get('content', '').strip()
    course_id = data.get('course_id')

    if not title or not content:
        return jsonify({'code': 400, 'message': '请填写问题标题和内容', 'data': None}), 400

    if course_id:
        course = db.session.get(Course, int(course_id))
        if not course:
            return jsonify({'code': 404, 'message': '课程不存在', 'data': None}), 404

    question = Question(
        student_id=user_id,
        course_id=int(course_id) if course_id else None,
        title=title,
        content=content,
        status='pending',
    )
    db.session.add(question)
    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '问题已提交',
        'data': question.to_dict()
    }), 200


# ─── 我的提问 ────────────────────────────────────────────

@ask_teacher_bp.route('/mine', methods=['GET'])
@jwt_required()
def my_questions():
    """获取当前用户的提问列表"""
    user_id = int(get_jwt_identity())
    questions = Question.query.filter_by(student_id=user_id)\
        .order_by(Question.created_at.desc()).all()

    return jsonify({
        'code': 200,
        'message': 'success',
        'data': {'questions': [q.to_dict() for q in questions]}
    }), 200


# ─── 课程提问列表（教师查看） ─────────────────────────────

@ask_teacher_bp.route('/course/<int:course_id>', methods=['GET'])
@jwt_required()
def course_questions(course_id):
    """教师查看某课程下的所有提问"""
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if not user or user.role not in ('teacher', 'admin'):
        return jsonify({'code': 403, 'message': '权限不足', 'data': None}), 403

    course = db.session.get(Course, course_id)
    if not course:
        raise NotFoundError('课程不存在')

    # 验证是课程教师或管理员
    if user.role != 'admin' and course.teacher_id != user_id:
        raise ForbiddenError('仅课程教师可以查看')

    questions = Question.query.filter_by(course_id=course_id)\
        .order_by(Question.created_at.desc()).all()

    return jsonify({
        'code': 200,
        'message': 'success',
        'data': {'questions': [q.to_dict() for q in questions]}
    }), 200


# ─── 教师待回答问题 ─────────────────────────────────────

@ask_teacher_bp.route('/pending', methods=['GET'])
@jwt_required()
def pending_questions():
    """获取教师名下所有课程的待回答问题"""
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if not user or user.role not in ('teacher', 'admin'):
        return jsonify({'code': 403, 'message': '权限不足', 'data': None}), 403

    # 获取教师的所有课程 ID
    if user.role == 'admin':
        course_ids = [c.id for c in Course.query.all()]
    else:
        course_ids = [c.id for c in Course.query.filter_by(teacher_id=user_id).all()]

    if not course_ids:
        return jsonify({'code': 200, 'message': 'success', 'data': {'questions': [], 'pending_count': 0}}), 200

    questions = Question.query.filter(
        Question.course_id.in_(course_ids),
        Question.status == 'pending'
    ).order_by(Question.created_at.desc()).all()

    return jsonify({
        'code': 200,
        'message': 'success',
        'data': {
            'questions': [q.to_dict() for q in questions],
            'pending_count': len(questions),
        }
    }), 200


# ─── 回答问题 ────────────────────────────────────────────

@ask_teacher_bp.route('/<int:question_id>/answer', methods=['PUT'])
@jwt_required()
def answer_question(question_id):
    """教师回答问题"""
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if not user or user.role not in ('teacher', 'admin'):
        return jsonify({'code': 403, 'message': '仅教师和管理员可以回答', 'data': None}), 403

    question = db.session.get(Question, question_id)
    if not question:
        raise NotFoundError('问题不存在')

    data = request.get_json() or {}
    answer = data.get('answer', '').strip()
    if not answer:
        return jsonify({'code': 400, 'message': '请输入回答内容', 'data': None}), 400

    question.answer = answer
    question.answered_by = user_id
    question.status = 'answered'
    question.answered_at = datetime.utcnow()
    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '回答成功',
        'data': question.to_dict()
    }), 200

