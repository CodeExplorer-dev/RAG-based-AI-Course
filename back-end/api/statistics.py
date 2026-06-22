"""统计接口 — 增强版：按课程/角色的多维度统计数据"""
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import User, Course, UserCourse, Courseware, Question, KnowledgePoint, QaConversation

stats_bp = Blueprint("statistics", __name__)


def _student_stats(user_id):
    """学生视角的统计数据"""
    enrollments = UserCourse.query.filter_by(user_id=user_id, role="student").all()
    course_ids = [e.course_id for e in enrollments]

    total_courses = len(course_ids)
    total_convs = QaConversation.query.filter_by(user_id=user_id).count()
    questions = Question.query.filter_by(student_id=user_id).all()
    total_q = len(questions)
    answered_q = sum(1 for q in questions if q.status == "answered")

    return {
        "total_courses": total_courses,
        "total_conversations": total_convs,
        "total_questions": total_q,
        "answered_questions": answered_q,
        "pending_questions": total_q - answered_q,
    }


def _teacher_stats(user_id):
    """教师视角的统计数据"""
    my_courses = Course.query.filter_by(teacher_id=user_id).all()
    course_ids = [c.id for c in my_courses]

    total_courses = len(course_ids)
    total_students = UserCourse.query.filter(
        UserCourse.course_id.in_(course_ids), UserCourse.role == "student"
    ).count()
    total_courseware = Courseware.query.filter(Courseware.course_id.in_(course_ids)).count()
    total_kps = KnowledgePoint.query.filter(KnowledgePoint.course_id.in_(course_ids)).count()

    # 所有课程的提问
    all_questions = Question.query.filter(Question.course_id.in_(course_ids)).all()
    total_q = len(all_questions)
    answered_q = sum(1 for q in all_questions if q.status == "answered")

    # 按课程统计
    course_stats = []
    for c in my_courses:
        c_qs = [q for q in all_questions if q.course_id == c.id]
        c_students = UserCourse.query.filter_by(course_id=c.id, role="student").count()
        c_cw = Courseware.query.filter_by(course_id=c.id).count()
        c_kps = KnowledgePoint.query.filter_by(course_id=c.id).count()
        course_stats.append({
            "course_id": c.id,
            "course_name": c.course_name,
            "students": c_students,
            "courseware": c_cw,
            "knowledge_points": c_kps,
            "total_questions": len(c_qs),
            "pending_questions": sum(1 for q in c_qs if q.status == "pending"),
        })

    # 高频提问知识点（取所有提问的标题/内容做简单词频）
    top_questions = sorted(
        all_questions, key=lambda q: q.created_at, reverse=True
    )[:10]

    return {
        "total_courses": total_courses,
        "total_students": total_students,
        "total_courseware": total_courseware,
        "total_knowledge_points": total_kps,
        "total_questions": total_q,
        "answered_questions": answered_q,
        "pending_questions": total_q - answered_q,
        "course_stats": course_stats,
        "recent_questions": [
            {"id": q.id, "title": q.title, "course_name": q.course.course_name if q.course else "",
             "status": q.status, "created_at": q.created_at.strftime("%Y-%m-%d %H:%M:%S") if q.created_at else None}
            for q in top_questions
        ],
    }


def _admin_stats(user_id):
    """管理员视角的系统级统计数据"""
    total_users = User.query.count()
    total_courses = Course.query.count()
    total_courseware = Courseware.query.count()
    total_kps = KnowledgePoint.query.count()
    total_questions = Question.query.count()

    # 角色分布
    student_count = User.query.filter_by(role="student").count()
    teacher_count = User.query.filter_by(role="teacher").count()
    admin_count = User.query.filter_by(role="admin").count()

    return {
        "users": total_users,
        "students": student_count,
        "teachers": teacher_count,
        "admins": admin_count,
        "courses": total_courses,
        "courseware": total_courseware,
        "knowledge_points": total_kps,
        "total_questions": total_questions,
    }


@stats_bp.route("", methods=["GET"])
@jwt_required()
def get_stats():
    """根据用户角色返回统计数据"""
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"code": 404, "message": "用户不存在", "data": None}), 404

    if user.role == "teacher":
        data = _teacher_stats(user_id)
    elif user.role == "admin":
        data = _admin_stats(user_id)
    else:
        data = _student_stats(user_id)

    data["role"] = user.role
    return jsonify({"code": 200, "message": "success", "data": data}), 200


@stats_bp.route("/knowledge-points", methods=["GET"])
@jwt_required()
def knowledge_point_stats():
    """知识点统计数据（教师/管理员）"""
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)

    if user.role == "teacher":
        course_ids = [c.id for c in Course.query.filter_by(teacher_id=user_id).all()]
    elif user.role == "admin":
        course_ids = [c.id for c in Course.query.all()]
    else:
        return jsonify({"code": 403, "message": "无权限", "data": None}), 403

    if not course_ids:
        return jsonify({
            "code": 200, "message": "success",
            "data": {"total": 0, "by_level": {}, "by_difficulty": {}, "by_course": []}
        }), 200

    kps = KnowledgePoint.query.filter(KnowledgePoint.course_id.in_(course_ids)).all()

    by_level = {1: 0, 2: 0, 3: 0}
    by_difficulty = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for kp in kps:
        by_level[kp.level] = by_level.get(kp.level, 0) + 1
        by_difficulty[kp.difficulty] = by_difficulty.get(kp.difficulty, 0) + 1

    by_course = []
    for cid in course_ids:
        c = db.session.get(Course, cid)
        c_kps = [kp for kp in kps if kp.course_id == cid]
        by_course.append({
            "course_id": cid,
            "course_name": c.course_name if c else f"课程{cid}",
            "count": len(c_kps),
        })

    return jsonify({
        "code": 200, "message": "success",
        "data": {
            "total": len(kps),
            "by_level": by_level,
            "by_difficulty": by_difficulty,
            "by_course": by_course,
        }
    }), 200
