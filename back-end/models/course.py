import random
import string
from extensions import db
from datetime import datetime


class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    join_code = db.Column(db.String(20), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    teacher = db.relationship('User', foreign_keys=[teacher_id])
    enrollments = db.relationship('UserCourse', back_populates='course', lazy='dynamic')
    coursewares = db.relationship('Courseware', back_populates='course', lazy='dynamic')

    @staticmethod
    def generate_join_code():
        """生成6位随机选课码（大写字母+数字）"""
        chars = string.ascii_uppercase + string.digits
        while True:
            code = ''.join(random.choices(chars, k=6))
            if not Course.query.filter_by(join_code=code).first():
                return code

    def to_dict(self, include_teacher=False):
        data = {
            'id': self.id,
            'course_name': self.course_name,
            'description': self.description,
            'teacher_id': self.teacher_id,
            'join_code': self.join_code,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None,
        }
        if include_teacher and self.teacher:
            data['teacher'] = self.teacher.to_dict()
        return data
