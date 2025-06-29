from app import db
from datetime import datetime
from sqlalchemy import Text, Boolean, Integer, String, DateTime

class ApiToken(db.Model):
    """Model for storing API tokens"""
    __tablename__ = 'api_tokens'
    
    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(100), unique=True, nullable=False)
    token = db.Column(Text, nullable=False)
    is_active = db.Column(Boolean, default=True, nullable=False)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    last_used = db.Column(DateTime)
    
    def __repr__(self):
        return f'<ApiToken {self.name}>'

class DataRecord(db.Model):
    """Generic model for storing data records"""
    __tablename__ = 'data_records'
    
    id = db.Column(Integer, primary_key=True)
    title = db.Column(String(200), nullable=False)
    content = db.Column(Text)
    category = db.Column(String(100))
    is_active = db.Column(Boolean, default=True, nullable=False)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'category': self.category,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<DataRecord {self.title}>'
