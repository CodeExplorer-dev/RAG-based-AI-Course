"""知识点关系模型 — knowledge_point_relations 表"""
from extensions import db
from datetime import datetime


class KnowledgePointRelation(db.Model):
    __tablename__ = 'knowledge_point_relations'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    source_kp_id = db.Column(db.Integer, db.ForeignKey('knowledge_points.id', ondelete='CASCADE'), nullable=False)
    target_kp_id = db.Column(db.Integer, db.ForeignKey('knowledge_points.id', ondelete='CASCADE'), nullable=False)
    relation_type = db.Column(
        db.Enum('prerequisite', 'contains', 'related', 'extends', 'applies', name='relation_type_enum'),
        nullable=False, default='related'
    )
    weight = db.Column(db.Float, nullable=False, default=1.0)
    description = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'source_kp_id': self.source_kp_id,
            'target_kp_id': self.target_kp_id,
            'relation_type': self.relation_type,
            'weight': self.weight,
            'description': self.description,
        }
