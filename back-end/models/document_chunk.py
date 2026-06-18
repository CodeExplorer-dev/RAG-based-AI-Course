from extensions import db
from datetime import datetime


class DocumentChunk(db.Model):
    __tablename__ = 'document_chunks'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    courseware_id = db.Column(db.Integer, db.ForeignKey('courseware.id'), nullable=False)
    chunk_index = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    vector_id = db.Column(db.Text, nullable=True)
    token_count = db.Column(db.Integer, nullable=False, default=0)
    page_ref = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # 关系
    courseware = db.relationship('Courseware', back_populates='chunks', foreign_keys=[courseware_id])

    __table_args__ = (
        db.UniqueConstraint('courseware_id', 'chunk_index', name='idx_cw_chunk'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'courseware_id': self.courseware_id,
            'chunk_index': self.chunk_index,
            'content': self.content,
            'vector_id': self.vector_id,
            'token_count': self.token_count,
            'page_ref': self.page_ref,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
        }
