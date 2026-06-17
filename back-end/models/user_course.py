from extensions import db
from datetime import datetime


class UserCourse(db.Model):
    __tablename__ = 'user_courses'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    role = db.Column(
        db.Enum('student', 'teacher', name='user_course_role'),
        nullable=False,
        default='student'
    )
    enrolled_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # 关系
    user = db.relationship('User', back_populates='enrollments', foreign_keys=[user_id])
    course = db.relationship('Course', back_populates='enrollments', foreign_keys=[course_id])

    __table_args__ = (
        db.UniqueConstraint('user_id', 'course_id', 'role', name='idx_user_course_role'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'course_id': self.course_id,
            'role': self.role,
            'enrolled_at': self.enrolled_at.strftime('%Y-%m-%d %H:%M:%S') if self.enrolled_at else None,
        }
