"""用户反馈模型 — 用户对 AI 回答的评价"""
from extensions import db
from datetime import datetime


class Feedback(db.Model):
    __tablename__ = "feedback"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    message_id = db.Column(db.Integer, db.ForeignKey("qa_messages.id"), nullable=False, index=True)
    rating = db.Column(db.Integer, nullable=False, comment="评分 1-5")
    comment = db.Column(db.Text, nullable=True)
    feedback_type = db.Column(
        db.Enum("helpful", "not_helpful", "inaccurate", "incomplete", "other", name="feedback_type_enum"),
        nullable=True,
    )
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # 关系
    user = db.relationship("User", foreign_keys=[user_id], backref="feedbacks")
    message = db.relationship("QaMessage", foreign_keys=[message_id], backref="feedbacks")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "message_id": self.message_id,
            "rating": self.rating,
            "comment": self.comment,
            "feedback_type": self.feedback_type,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None,
        }
