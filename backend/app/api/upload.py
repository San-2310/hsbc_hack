from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
import pandas as pd
import aiofiles
import os
import uuid
from datetime import datetime
import json

from app.core.database import get_db
from app.core.auth import verify_firebase_token, User
from app.models.file_upload import FileUpload
from app.models.processing_log import ProcessingLog
from app.core.config import settings
from app.services.file_processor import FileProcessor

router = APIRouter()
security = HTTPBearer()

@router.post("/")
async def upload_file(
    file: UploadFile = File(...),
    tags: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    try:
        user = await verify_firebase_token(token.credentials)
        
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400, 
                detail=f"File type not allowed. Allowed types: {', '.join(settings.ALLOWED_EXTENSIONS)}"
            )
        
        file_size = 0
        content = await file.read()
        file_size = len(content)
        
        if file_size > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE / (1024*1024)}MB"
            )
        
        file_id = str(uuid.uuid4())
        filename = f"{file_id}{file_ext}"
        file_path = os.path.join(settings.UPLOAD_DIR, filename)
        
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
        
        log = ProcessingLog.create_log(
            db=db,
            file_id=file_id,
            user_id=user.uid,
            operation_type="upload",
            operation_details=f"File uploaded: {file.filename}",
            input_data={
                "original_filename": file.filename,
                "file_size": file_size,
                "file_type": file_ext
            }
        )
        
        processor = FileProcessor()
        schema_info = await processor.detect_schema(file_path, file_ext)
        
        file_upload = FileUpload(
            file_id=file_id,
            user_id=user.uid,
            filename=filename,
            original_filename=file.filename,
            file_path=file_path,
            file_size=file_size,
            file_type=file_ext,
            schema=schema_info,
            total_rows=schema_info.get("total_rows"),
            total_columns=schema_info.get("total_columns"),
            tags=json.loads(tags) if tags else [],
            category=category,
            preview_data=schema_info.get("preview_data")
        )
        
        db.add(file_upload)
        db.commit()
        db.refresh(file_upload)
        
        log.complete_success(
            db=db,
            output_data={
                "file_id": file_id,
                "schema": schema_info,
                "preview_data": schema_info.get("preview_data")
            },
            rows_processed=schema_info.get("total_rows", 0)
        )
        
        return {
            "success": True,
            "file_id": file_id,
            "filename": file.filename,
            "file_size": file_size,
            "schema": schema_info,
            "message": "File uploaded and processed successfully"
        }
        
    except Exception as e:
        if 'log' in locals():
            log.complete_failure(db, str(e))
        
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/{file_id}/schema")
async def get_file_schema(
    file_id: str,
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    try:
        user = await verify_firebase_token(token.credentials)
        
        file_upload = db.query(FileUpload).filter(
            FileUpload.file_id == file_id,
            FileUpload.user_id == user.uid
        ).first()
        
        if not file_upload:
            raise HTTPException(status_code=404, detail="File not found")
        
        return {
            "file_id": file_id,
            "schema": file_upload.schema,
            "total_rows": file_upload.total_rows,
            "total_columns": file_upload.total_columns,
            "preview_data": file_upload.preview_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get schema: {str(e)}")

@router.get("/{file_id}/preview")
async def get_file_preview(
    file_id: str,
    rows: int = 10,
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    try:
        user = await verify_firebase_token(token.credentials)
        
        file_upload = db.query(FileUpload).filter(
            FileUpload.file_id == file_id,
            FileUpload.user_id == user.uid
        ).first()
        
        if not file_upload:
            raise HTTPException(status_code=404, detail="File not found")
        
        processor = FileProcessor()
        preview_data = await processor.get_preview(
            file_upload.file_path, 
            file_upload.file_type, 
            rows
        )
        
        return {
            "file_id": file_id,
            "preview_data": preview_data,
            "total_rows": file_upload.total_rows
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get preview: {str(e)}")

@router.get("/")
async def get_user_files(
    token: str = Depends(security),
    db: Session = Depends(get_db),
    limit: int = 50,
    offset: int = 0
):
    try:
        user = await verify_firebase_token(token.credentials)
        
        files = db.query(FileUpload).filter(
            FileUpload.user_id == user.uid
        ).order_by(FileUpload.created_at.desc()).offset(offset).limit(limit).all()
        
        total_count = db.query(FileUpload).filter(
            FileUpload.user_id == user.uid
        ).count()
        
        return {
            "files": [file.to_dict() for file in files],
            "total_count": total_count,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get files: {str(e)}")

@router.delete("/{file_id}")
async def delete_file(
    file_id: str,
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    try:
        user = await verify_firebase_token(token.credentials)
        
        file_upload = db.query(FileUpload).filter(
            FileUpload.file_id == file_id,
            FileUpload.user_id == user.uid
        ).first()
        
        if not file_upload:
            raise HTTPException(status_code=404, detail="File not found")
        
        if os.path.exists(file_upload.file_path):
            os.remove(file_upload.file_path)
        
        db.delete(file_upload)
        db.commit()
        
        return {
            "success": True,
            "message": "File deleted successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}") 