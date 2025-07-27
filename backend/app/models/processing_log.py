from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime

class ProcessingLog(Base):
    __tablename__ = "processing_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(String(255), nullable=False, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    
    # Operation details
    operation_type = Column(String(100), nullable=False)  # upload, normalize, aggregate, export
    operation_status = Column(String(50), nullable=False)  # success, failed, in_progress
    operation_details = Column(Text, nullable=True)  # Detailed description
    
    # Processing metadata
    input_data = Column(JSON, nullable=True)  # Input parameters
    output_data = Column(JSON, nullable=True)  # Output results
    error_message = Column(Text, nullable=True)  # Error details if failed
    
    # Performance metrics
    processing_time_ms = Column(Integer, nullable=True)  # Processing time in milliseconds
    rows_processed = Column(Integer, nullable=True)  # Number of rows processed
    
    # Timestamps
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<ProcessingLog(id={self.id}, operation='{self.operation_type}', status='{self.operation_status}')>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "file_id": self.file_id,
            "user_id": self.user_id,
            "operation_type": self.operation_type,
            "operation_status": self.operation_status,
            "operation_details": self.operation_details,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "error_message": self.error_message,
            "processing_time_ms": self.processing_time_ms,
            "rows_processed": self.rows_processed,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def create_log(cls, db, file_id: str, user_id: str, operation_type: str, 
                   operation_details: str = None, input_data: dict = None):
        """Create a new processing log entry"""
        log = cls(
            file_id=file_id,
            user_id=user_id,
            operation_type=operation_type,
            operation_status="in_progress",
            operation_details=operation_details,
            input_data=input_data
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log
    
    def complete_success(self, db, output_data: dict = None, processing_time_ms: int = None, 
                        rows_processed: int = None):
        """Mark log as successfully completed"""
        self.operation_status = "success"
        self.completed_at = func.now()
        self.output_data = output_data
        self.processing_time_ms = processing_time_ms
        self.rows_processed = rows_processed
        db.commit()
        db.refresh(self)
    
    def complete_failure(self, db, error_message: str):
        """Mark log as failed"""
        self.operation_status = "failed"
        self.completed_at = func.now()
        self.error_message = error_message
        db.commit()
        db.refresh(self) 