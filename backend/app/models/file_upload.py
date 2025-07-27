from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON
from sqlalchemy.sql import func
from app.core.database import Base
from datetime import datetime

class FileUpload(Base):
    __tablename__ = "file_uploads"
    
    id = Column(String(36), primary_key=True, index=True)
    file_id = Column(String(255), unique=True, index=True, nullable=False)
    user_id = Column(String(255), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_type = Column(String(50), nullable=False)
    
    schema = Column(JSON, nullable=True)  
    total_rows = Column(Integer, nullable=True)
    total_columns = Column(Integer, nullable=True)
    
    is_processed = Column(Boolean, default=False)
    is_normalized = Column(Boolean, default=False)
    is_aggregated = Column(Boolean, default=False)
    
    upload_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    processed_timestamp = Column(DateTime(timezone=True), nullable=True)
    
    normalization_log = Column(Text, nullable=True)
    aggregation_config = Column(JSON, nullable=True)
    preview_data = Column(JSON, nullable=True) 
    
    tags = Column(JSON, nullable=True)
    category = Column(String(100), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<FileUpload(id={self.id}, filename='{self.filename}', user_id='{self.user_id}')>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "file_id": self.file_id,
            "user_id": self.user_id,
            "filename": self.filename,
            "original_filename": self.original_filename,
            "file_size": self.file_size,
            "file_type": self.file_type,
            "schema": self.schema,
            "total_rows": self.total_rows,
            "total_columns": self.total_columns,
            "is_processed": self.is_processed,
            "is_normalized": self.is_normalized,
            "is_aggregated": self.is_aggregated,
            "upload_timestamp": self.upload_timestamp.isoformat() if self.upload_timestamp else None,
            "processed_timestamp": self.processed_timestamp.isoformat() if self.processed_timestamp else None,
            "normalization_log": self.normalization_log,
            "aggregation_config": self.aggregation_config,
            "preview_data": self.preview_data,
            "tags": self.tags,
            "category": self.category,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        } 