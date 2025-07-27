from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import Dict, Any
import uuid
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.auth import verify_firebase_token, update_user_last_login, User
from app.models.user_session import UserSession
from app.core.config import settings

router = APIRouter()
security = HTTPBearer()

@router.post("/login")
async def login(
    request: Request,
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    try:
        user = await verify_firebase_token(token.credentials)
        
        update_user_last_login(user.uid)
        
        session_id = str(uuid.uuid4())
        session = UserSession.create_session(
            db=db,
            user_id=user.uid,
            session_id=session_id,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            login_method="firebase",
            device_info={
                "browser": request.headers.get("user-agent", ""),
                "ip": request.client.host if request.client else None
            }
        )
        
        return {
            "success": True,
            "user": {
                "uid": user.uid,
                "email": user.email,
                "display_name": user.display_name,
                "role": user.role
            },
            "session_id": session_id,
            "message": "Login successful"
        }
        
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")

@router.post("/logout")
async def logout(
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    try:
        user = await verify_firebase_token(token.credentials)
        
        active_sessions = db.query(UserSession).filter(
            UserSession.user_id == user.uid,
            UserSession.is_active == True
        ).all()
        
        for session in active_sessions:
            session.deactivate(db)
        
        return {
            "success": True,
            "message": "Logout successful"
        }
        
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Logout failed: {str(e)}")

@router.get("/me")
async def get_current_user_info(
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    try:
        user = await verify_firebase_token(token.credentials)
        
        active_sessions = db.query(UserSession).filter(
            UserSession.user_id == user.uid,
            UserSession.is_active == True
        ).count()
        
        return {
            "user": {
                "uid": user.uid,
                "email": user.email,
                "display_name": user.display_name,
                "role": user.role
            },
            "active_sessions": active_sessions,
            "last_login": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")

@router.get("/sessions")
async def get_user_sessions(
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    try:
        user = await verify_firebase_token(token.credentials)
        
        sessions = db.query(UserSession).filter(
            UserSession.user_id == user.uid,
            UserSession.is_active == True
        ).all()
        
        return {
            "sessions": [session.to_dict() for session in sessions]
        }
        
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")

@router.delete("/sessions/{session_id}")
async def revoke_session(
    session_id: str,
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    try:
        user = await verify_firebase_token(token.credentials)
        
        session = db.query(UserSession).filter(
            UserSession.session_id == session_id,
            UserSession.user_id == user.uid
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session.deactivate(db)
        
        return {
            "success": True,
            "message": "Session revoked successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Session revocation failed: {str(e)}")

@router.post("/refresh")
async def refresh_session(
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    try:
        user = await verify_firebase_token(token.credentials)
        
        active_sessions = db.query(UserSession).filter(
            UserSession.user_id == user.uid,
            UserSession.is_active == True
        ).all()
        
        for session in active_sessions:
            session.update_activity(db)
        
        return {
            "success": True,
            "message": "Session refreshed successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Session refresh failed: {str(e)}") 