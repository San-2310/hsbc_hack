from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON
from sqlalchemy.sql import func
from app.core.database import Base
from datetime import datetime

class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    session_id = Column(String(255), unique=True, index=True, nullable=False)
    
    # Session details
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(Text, nullable=True)
    device_info = Column(JSON, nullable=True)  # Browser, OS, etc.
    
    # Session status
    is_active = Column(Boolean, default=True)
    last_activity = Column(DateTime(timezone=True), server_default=func.now())
    
    # Session metadata
    login_method = Column(String(50), nullable=True)  # google, email, etc.
    session_data = Column(JSON, nullable=True)  # Additional session data
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<UserSession(id={self.id}, user_id='{self.user_id}', session_id='{self.session_id}')>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "device_info": self.device_info,
            "is_active": self.is_active,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None,
            "login_method": self.login_method,
            "session_data": self.session_data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None
        }
    
    @classmethod
    def create_session(cls, db, user_id: str, session_id: str, ip_address: str = None, 
                      user_agent: str = None, login_method: str = None, device_info: dict = None):
        """Create a new user session"""
        session = cls(
            user_id=user_id,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent,
            login_method=login_method,
            device_info=device_info
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session
    
    def update_activity(self, db):
        """Update last activity timestamp"""
        self.last_activity = func.now()
        db.commit()
        db.refresh(self)
    
    def deactivate(self, db):
        """Deactivate session"""
        self.is_active = False
        db.commit()
        db.refresh(self) 