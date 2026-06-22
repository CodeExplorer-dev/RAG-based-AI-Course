"""知识点模型 — knowledge_points 表"""
from extensions import db
from datetime import datetime


class KnowledgePoint(db.Model):
    __tablename__ = 'knowledge_points'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text, nullable=True)
    level = db.Column(db.SmallInteger, nullable=False, default=1)
    parent_id = db.Column(db.Integer, db.ForeignKey('knowledge_points.id', ondelete='SET NULL'), nullable=True)
    importance = db.Column(db.SmallInteger, nullable=False, default=3)
    difficulty = db.Column(db.SmallInteger, nullable=False, default=3)
    keywords = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    course = db.relationship('Course', backref=db.backref('knowledge_points', lazy='dynamic'))
    parent = db.relationship('KnowledgePoint', remote_side=[id], backref=db.backref('children', lazy='dynamic'))
    kp_coursewares = db.relationship('KpCourseware', backref='knowledge_point', lazy='dynamic',
                                     cascade='all, delete-orphan')
    source_relations = db.relationship('KnowledgePointRelation', foreign_keys='KnowledgePointRelation.source_kp_id',
                                       backref='source_kp', lazy='dynamic', cascade='all, delete-orphan')
    target_relations = db.relationship('KnowledgePointRelation', foreign_keys='KnowledgePointRelation.target_kp_id',
                                       backref='target_kp', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'course_id': self.course_id,
            'name': self.name,
            'description': self.description,
            'level': self.level,
            'parent_id': self.parent_id,
            'importance': self.importance,
            'difficulty': self.difficulty,
            'keywords': self.keywords.split(',') if self.keywords else [],
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
