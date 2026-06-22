"""知识点-课件关联模型 — kp_courseware 表"""
from extensions import db
from datetime import datetime


class KpCourseware(db.Model):
    __tablename__ = 'kp_courseware'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    knowledge_point_id = db.Column(db.Integer, db.ForeignKey('knowledge_points.id', ondelete='CASCADE'), nullable=False)
    courseware_id = db.Column(db.Integer, db.ForeignKey('courseware.id', ondelete='CASCADE'), nullable=False)
    chunk_id = db.Column(db.Integer, db.ForeignKey('document_chunks.id', ondelete='SET NULL'), nullable=True)
    relevance_score = db.Column(db.Float, nullable=False, default=1.0)

    # Relationships
    courseware = db.relationship('Courseware', backref=db.backref('kp_associations', lazy='dynamic'))
    chunk = db.relationship('DocumentChunk', backref=db.backref('kp_associations', lazy='dynamic'))

    def to_dict(self):
        return {
            'id': self.id,
            'knowledge_point_id': self.knowledge_point_id,
            'courseware_id': self.courseware_id,
            'chunk_id': self.chunk_id,
            'relevance_score': self.relevance_score,
        }
