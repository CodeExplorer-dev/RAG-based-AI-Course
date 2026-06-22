"""问答会话模型 — 存储 AI 问答对话会话"""
from extensions import db
from datetime import datetime


class QaConversation(db.Model):
    __tablename__ = "qa_conversations"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=True, index=True)
    title = db.Column(db.String(300), nullable=False, default="新对话")
    message_count = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    user = db.relationship("User", foreign_keys=[user_id], backref="qa_conversations")
    course = db.relationship("Course", foreign_keys=[course_id], backref="qa_conversations")
    messages = db.relationship("QaMessage", back_populates="conversation", lazy="dynamic",
                                cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "course_id": self.course_id,
            "title": self.title,
            "message_count": self.message_count,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None,
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S") if self.updated_at else None,
            "course_name": self.course.course_name if self.course else None,
        }
