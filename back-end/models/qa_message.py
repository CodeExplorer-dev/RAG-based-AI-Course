"""问答消息模型 — 存储每条具体的问答消息"""
from extensions import db
from datetime import datetime


class QaMessage(db.Model):
    __tablename__ = "qa_messages"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey("qa_conversations.id"), nullable=False, index=True)
    role = db.Column(db.Enum("user", "assistant", "system", name="message_role"), nullable=False)
    content = db.Column(db.Text, nullable=False)
    referenced_chunks = db.Column(db.JSON, nullable=True)
    token_usage = db.Column(db.JSON, nullable=True)
    response_time_ms = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # 关系
    conversation = db.relationship("QaConversation", back_populates="messages", foreign_keys=[conversation_id])

    def to_dict(self):
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "role": self.role,
            "content": self.content,
            "referenced_chunks": self.referenced_chunks,
            "token_usage": self.token_usage,
            "response_time_ms": self.response_time_ms,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None,
        }
