"""提问模型 — 学生向老师提问"""
from extensions import db
from datetime import datetime


class Question(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=True, index=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=True)
    answered_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    status = db.Column(
        db.Enum('pending', 'answered', name='question_status'),
        nullable=False,
        default='pending',
        index=True
    )
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    answered_at = db.Column(db.DateTime, nullable=True)

    # 关系
    student = db.relationship('User', foreign_keys=[student_id], backref='questions')
    course = db.relationship('Course', foreign_keys=[course_id], backref='questions')
    teacher = db.relationship('User', foreign_keys=[answered_by])

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'course_id': self.course_id,
            'title': self.title,
            'content': self.content,
            'answer': self.answer,
            'answered_by': self.answered_by,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'answered_at': self.answered_at.strftime('%Y-%m-%d %H:%M:%S') if self.answered_at else None,
            'student_name': self.student.username if self.student else None,
            'course_name': self.course.course_name if self.course else None,
        }
