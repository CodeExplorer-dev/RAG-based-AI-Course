from extensions import db
from datetime import datetime


class Courseware(db.Model):
    __tablename__ = 'courseware'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    title = db.Column(db.String(300), nullable=False)
    file_type = db.Column(
        db.Enum('pdf', 'ppt', 'pptx', 'doc', 'docx', 'txt', 'md', name='file_type_enum'),
        nullable=False
    )
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.BigInteger, nullable=False, default=0)
    page_count = db.Column(db.Integer, nullable=True)
    uploader_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    chunk_count = db.Column(db.Integer, nullable=False, default=0)
    status = db.Column(
        db.Enum('uploading', 'processing', 'completed', 'failed', name='courseware_status'),
        nullable=False,
        default='uploading'
    )
    uploaded_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    course = db.relationship('Course', back_populates='coursewares', foreign_keys=[course_id])
    uploader = db.relationship('User', back_populates='uploaded_courseware', foreign_keys=[uploader_id])
    chunks = db.relationship('DocumentChunk', back_populates='courseware', lazy='dynamic')

    def to_dict(self, include_uploader=False):
        data = {
            'id': self.id,
            'course_id': self.course_id,
            'title': self.title,
            'file_type': self.file_type,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'page_count': self.page_count,
            'uploader_id': self.uploader_id,
            'chunk_count': self.chunk_count,
            'status': self.status,
            'uploaded_at': self.uploaded_at.strftime('%Y-%m-%d %H:%M:%S') if self.uploaded_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None,
        }
        if include_uploader and self.uploader:
            data['uploader'] = self.uploader.to_dict()
        return data
