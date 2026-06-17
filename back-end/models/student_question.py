from extensions import db
from datetime import datetime


class StudentQuestion(db.Model):
    __tablename__ = 'student_questions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    student_name = db.Column(db.String(80), nullable=False)
    course_id = db.Column(db.Integer, nullable=True)
    course_name = db.Column(db.String(200), nullable=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    student = db.relationship('User', foreign_keys=[student_id])

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'student_name': self.student_name,
            'course_id': self.course_id,
            'course_name': self.course_name,
            'title': self.title,
            'content': self.content,
            'answer': self.answer,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
        }
