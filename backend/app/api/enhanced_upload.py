from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict, Any, List, Optional
import os
import uuid
from datetime import datetime
import json
from app.core.auth import User, get_current_user
from app.services.enhanced_file_processor import EnhancedFileProcessor
from app.core.config import settings

router = APIRouter()

file_processor = EnhancedFileProcessor()

# In-memory storage
file_storage = {}
processing_logs = {}

class FileRecord:
    def __init__(self, file_id: str, user_id: str, filename: str, file_path: str = "", 
                 file_size: int = 0, file_type: str = "", **kwargs):
        self.id = file_id
        self.file_id = file_id
        self.user_id = user_id
        self.filename = filename
        self.original_filename = filename
        self.file_path = file_path
        self.file_size = file_size
        self.file_type = file_type
        self.schema = None
        self.total_rows = 0
        self.total_columns = 0
        self.is_processed = False
        self.is_normalized = False
        self.is_aggregated = False
        self.upload_timestamp = datetime.utcnow()
        self.processed_timestamp = None
        self.normalization_log = None
        self.aggregation_config = None
        self.preview_data = None
        self.tags = None
        self.category = None
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        
        # Update with any additional kwargs
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
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

class ProcessingLogRecord:
    def __init__(self, file_id: str, user_id: str, operation: str, status: str, details: str):
        self.id = str(uuid.uuid4())
        self.file_id = file_id
        self.user_id = user_id
        self.operation = operation
        self.status = status
        self.details = details
        self.created_at = datetime.utcnow()

@router.post("/file")
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user: User = Depends(get_current_user)
):
    try:
        if not file.filename:
            return JSONResponse(
                status_code=400,
                content={
                    "message": "No file provided",
                    "code": 400,
                    "error_id": f"ERR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                }
            )
        
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in file_processor.supported_formats:
            return JSONResponse(
                status_code=400,
                content={
                    "message": f"Unsupported file type: {file_extension}",
                    "code": 400,
                    "error_id": f"ERR_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    "supported_formats": file_processor.supported_formats
                }
            )
        
        file_size = 0
        content = b""
        while chunk := await file.read(8192):
            content += chunk
            file_size += len(chunk)
            if file_size > file_processor.max_file_size:
                return JSONResponse(
                    status_code=400,
                    content={
                        "message": f"File too large: {file_size} bytes (max: {file_processor.max_file_size})",
                        "code": 400,
                        "error_id": f"ERR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    }
                )
        
        file_id = str(uuid.uuid4())
        filename = f"{file_id}{file_extension}"
        file_path = os.path.join(settings.UPLOAD_DIR, filename)
        
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Store in memory
        file_record = FileRecord(
            file_id=file_id,
            user_id=user.uid,
            filename=file.filename,
            file_path=file_path,
            file_size=file_size,
            file_type=file_extension
        )
        
        file_storage[file_id] = file_record
        
        background_tasks.add_task(process_uploaded_file, file_id, file_path, file_extension, user.uid)
        
        return JSONResponse(
            status_code=202,
            content={
                "status": "success",
                "message": "File uploaded successfully and queued for processing",
                "code": 202,
                "data": {
                    "file_id": file_id,
                    "filename": file.filename,
                    "file_size": file_size,
                    "status": "processing"
                }
            }
        )
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Upload failed: {str(e)}",
                "code": 500,
                "error_id": f"ERR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            }
        )

@router.post("/api")
async def upload_from_api(
    background_tasks: BackgroundTasks,
    api_config: Dict[str, Any],
    user: User = Depends(get_current_user)
):
    try:
        if not api_config.get('url'):
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": "API URL is required",
                    "code": 400,
                    "error_id": f"ERR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                }
            )
        
        file_id = str(uuid.uuid4())
        
        file_record = FileRecord(
            file_id=file_id,
            user_id=user.uid,
            filename=f"api_data_{file_id}",
            file_type=".json"
        )
        
        file_storage[file_id] = file_record
        
        background_tasks.add_task(process_api_data, file_id, api_config, user.uid)
        
        return JSONResponse(
            status_code=202,
            content={
                "status": "success",
                "message": "API data processing queued",
                "code": 202,
                "data": {
                    "file_id": file_id,
                    "source": "API",
                    "url": api_config['url'],
                    "status": "processing"
                }
            }
        )
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"API upload failed: {str(e)}",
                "code": 500,
                "error_id": f"ERR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            }
        )

@router.post("/url")
async def upload_from_url(
    background_tasks: BackgroundTasks,
    url_config: Dict[str, Any],
    user: User = Depends(get_current_user)
):
    try:
        if not url_config.get('url'):
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": "URL is required",
                    "code": 400,
                    "error_id": f"ERR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                }
            )
        
        file_id = str(uuid.uuid4())
        
        file_record = FileRecord(
            file_id=file_id,
            user_id=user.uid,
            filename=f"url_data_{file_id}",
            file_type=".csv"
        )
        
        file_storage[file_id] = file_record
        
        background_tasks.add_task(process_url_data, file_id, url_config, user.uid)
        
        return JSONResponse(
            status_code=202,
            content={
                "status": "success",
                "message": "URL data processing queued",
                "code": 202,
                "data": {
                    "file_id": file_id,
                    "source": "URL",
                    "url": url_config['url'],
                    "status": "processing"
                }
            }
        )
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"URL upload failed: {str(e)}",
                "code": 500,
                "error_id": f"ERR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            }
        )

@router.post("/json")
async def upload_json_data(
    background_tasks: BackgroundTasks,
    json_data: Dict[str, Any],
    user: User = Depends(get_current_user)
):
    try:
        if not json_data:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": "JSON data is required",
                    "code": 400,
                    "error_id": f"ERR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                }
            )
        
        file_id = str(uuid.uuid4())
        
        file_record = FileRecord(
            file_id=file_id,
            user_id=user.uid,
            filename=f"json_data_{file_id}",
            file_type=".json",
            file_size=len(json.dumps(json_data))
        )
        
        file_storage[file_id] = file_record
        
        background_tasks.add_task(process_json_data, file_id, json_data, user.uid)
        
        return JSONResponse(
            status_code=202,
            content={
                "status": "success",
                "message": "JSON data processing queued",
                "code": 202,
                "data": {
                    "file_id": file_id,
                    "source": "JSON",
                    "data_size": len(json.dumps(json_data)),
                    "status": "processing"
                }
            }
        )
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"JSON upload failed: {str(e)}",
                "code": 500,
                "error_id": f"ERR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            }
        )

@router.get("/schema/{file_id}")
async def get_file_schema(
    file_id: str,
    user: User = Depends(get_current_user)
):
    try:
        if file_id not in file_storage:
            return JSONResponse(
                status_code=404,
                content={
                    "status": "error",
                    "message": "File not found",
                    "code": 404,
                    "error_id": f"ERR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                }
            )
        
        file_record = file_storage[file_id]
        
        # Check if user owns the file
        if file_record.user_id != user.uid:
            return JSONResponse(
                status_code=403,
                content={
                    "status": "error",
                    "message": "Access denied",
                    "code": 403,
                    "error_id": f"ERR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                }
            )
        
        if not file_record.schema:
            return JSONResponse(
                status_code=422,
                content={
                    "status": "error",
                    "message": "Schema not available yet. File may still be processing.",
                    "code": 422,
                    "error_id": f"ERR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                }
            )
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "Schema retrieved successfully",
                "code": 200,
                "data": {
                    "file_id": file_id,
                    "schema": file_record.schema,
                    "total_rows": file_record.total_rows,
                    "total_columns": file_record.total_columns
                }
            }
        )
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Failed to get schema: {str(e)}",
                "code": 500,
                "error_id": f"ERR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            }
        )

@router.get("/files")
async def list_user_files(
    user: User = Depends(get_current_user),
    limit: int = 50,
    offset: int = 0
):
    try:
        user_files = [
            file_record for file_record in file_storage.values() 
            if file_record.user_id == user.uid
        ]
        
        user_files.sort(key=lambda x: x.created_at, reverse=True)
        
        paginated_files = user_files[offset:offset + limit]
        
        file_list = []
        for file_record in paginated_files:
            file_list.append({
                "id": file_record.id,
                "filename": file_record.filename,
                "file_type": file_record.file_type,
                "file_size": file_record.file_size,
                "is_processed": file_record.is_processed,
                "total_rows": file_record.total_rows,
                "total_columns": file_record.total_columns,
                "created_at": file_record.created_at.isoformat(),
                "updated_at": file_record.updated_at.isoformat() if file_record.updated_at else None
            })
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "Files retrieved successfully",
                "code": 200,
                "data": {
                    "files": file_list,
                    "total": len(user_files),
                    "limit": limit,
                    "offset": offset
                }
            }
        )
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Failed to list files: {str(e)}",
                "code": 500,
                "error_id": f"ERR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            }
        )

async def process_uploaded_file(file_id: str, file_path: str, file_type: str, user_id: str):
    try:
        result = await file_processor.process_input({
            'type': 'file',
            'file_path': file_path,
            'file_type': file_type
        })
        
        if file_id in file_storage:
            file_record = file_storage[file_id]
            file_record.is_processed = True
            file_record.schema = result['schema']
            file_record.total_rows = result['total_rows']
            file_record.total_columns = result['total_columns']
            file_record.processed_timestamp = datetime.utcnow()
            file_record.updated_at = datetime.utcnow()
            file_record.normalization_log = json.dumps(result['normalization_log'])
        
        log_id = str(uuid.uuid4())
        processing_logs[log_id] = ProcessingLogRecord(
            file_id=file_id,
            user_id=user_id,
            operation="file_upload",
            status="success",
            details=json.dumps(result['normalization_log'])
        )
        
    except Exception as e:
        if file_id in file_storage:
            file_record = file_storage[file_id]
            file_record.is_processed = False
            file_record.processed_timestamp = datetime.utcnow()
            file_record.updated_at = datetime.utcnow()
        
        # Log error
        log_id = str(uuid.uuid4())
        processing_logs[log_id] = ProcessingLogRecord(
            file_id=file_id,
            user_id=user_id,
            operation="file_upload",
            status="error",
            details=str(e)
        )

async def process_api_data(file_id: str, api_config: Dict[str, Any], user_id: str):
    try:
        result = await file_processor.process_input({
            'type': 'api',
            **api_config
        })
        
        file_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}.json")
        with open(file_path, 'w') as f:
            json.dump(result['data'], f)
        
        if file_id in file_storage:
            file_record = file_storage[file_id]
            file_record.is_processed = True
            file_record.file_path = file_path
            file_record.schema = result['schema']
            file_record.total_rows = result['total_rows']
            file_record.total_columns = result['total_columns']
            file_record.processed_timestamp = datetime.utcnow()
            file_record.updated_at = datetime.utcnow()
        
        log_id = str(uuid.uuid4())
        processing_logs[log_id] = ProcessingLogRecord(
            file_id=file_id,
            user_id=user_id,
            operation="api_upload",
            status="success",
            details=json.dumps(result['normalization_log'])
        )
        
    except Exception as e:
        if file_id in file_storage:
            file_record = file_storage[file_id]
            file_record.is_processed = False
            file_record.processed_timestamp = datetime.utcnow()
            file_record.updated_at = datetime.utcnow()
        
        log_id = str(uuid.uuid4())
        processing_logs[log_id] = ProcessingLogRecord(
            file_id=file_id,
            user_id=user_id,
            operation="api_upload",
            status="error",
            details=str(e)
        )

async def process_url_data(file_id: str, url_config: Dict[str, Any], user_id: str):
    try:
        result = await file_processor.process_input({
            'type': 'url',
            **url_config
        })
        
        file_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}.csv")
        import pandas as pd
        df = pd.DataFrame(result['data'])
        df.to_csv(file_path, index=False)
        
        if file_id in file_storage:
            file_record = file_storage[file_id]
            file_record.is_processed = True
            file_record.file_path = file_path
            file_record.file_type = ".csv"
            file_record.schema = result['schema']
            file_record.total_rows = result['total_rows']
            file_record.total_columns = result['total_columns']
            file_record.processed_timestamp = datetime.utcnow()
            file_record.updated_at = datetime.utcnow()
        
        log_id = str(uuid.uuid4())
        processing_logs[log_id] = ProcessingLogRecord(
            file_id=file_id,
            user_id=user_id,
            operation="url_upload",
            status="success",
            details=json.dumps(result['normalization_log'])
        )
        
    except Exception as e:
        if file_id in file_storage:
            file_record = file_storage[file_id]
            file_record.is_processed = False
            file_record.processed_timestamp = datetime.utcnow()
            file_record.updated_at = datetime.utcnow()
        
        # Log error
        log_id = str(uuid.uuid4())
        processing_logs[log_id] = ProcessingLogRecord(
            file_id=file_id,
            user_id=user_id,
            operation="url_upload",
            status="error",
            details=str(e)
        )

async def process_json_data(file_id: str, json_data: Dict[str, Any], user_id: str):
    try:
        result = await file_processor.process_input({
            'type': 'json',
            'data': json_data
        })
        
        file_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}.json")
        with open(file_path, 'w') as f:
            json.dump(result['data'], f)
        
        if file_id in file_storage:
            file_record = file_storage[file_id]
            file_record.is_processed = True
            file_record.file_path = file_path
            file_record.schema = result['schema']
            file_record.total_rows = result['total_rows']
            file_record.total_columns = result['total_columns']
            file_record.processed_timestamp = datetime.utcnow()
            file_record.updated_at = datetime.utcnow()
        
        log_id = str(uuid.uuid4())
        processing_logs[log_id] = ProcessingLogRecord(
            file_id=file_id,
            user_id=user_id,
            operation="json_upload",
            status="success",
            details=json.dumps(result['normalization_log'])
        )
        
    except Exception as e:
        if file_id in file_storage:
            file_record = file_storage[file_id]
            file_record.is_processed = False
            file_record.processed_timestamp = datetime.utcnow()
            file_record.updated_at = datetime.utcnow()
        
        log_id = str(uuid.uuid4())
        processing_logs[log_id] = ProcessingLogRecord(
            file_id=file_id,
            user_id=user_id,
            operation="json_upload",
            status="error",
            details=str(e)
        )

@router.get("/status/{file_id}")
async def get_file_status(
    file_id: str,
    user: User = Depends(get_current_user)
):
    """Get processing status of a file"""
    if file_id not in file_storage:
        return JSONResponse(
            status_code=404,
            content={
                "status": "error",
                "message": "File not found",
                "code": 404
            }
        )
    
    file_record = file_storage[file_id]
    
    if file_record.user_id != user.uid:
        return JSONResponse(
            status_code=403,
            content={
                "status": "error",
                "message": "Access denied",
                "code": 403
            }
        )
    
    return JSONResponse(
        status_code=200,
        content={
            "status": "success",
            "data": {
                "file_id": file_id,
                "is_processed": file_record.is_processed,
                "created_at": file_record.created_at.isoformat(),
                "processed_timestamp": file_record.processed_timestamp.isoformat() if file_record.processed_timestamp else None
            }
        }
    )

@router.delete("/file/{file_id}")
async def delete_file(
    file_id: str,
    user: User = Depends(get_current_user)
):
    if file_id not in file_storage:
        return JSONResponse(
            status_code=404,
            content={
                "status": "error",
                "message": "File not found",
                "code": 404
            }
        )
    
    file_record = file_storage[file_id]
    
    if file_record.user_id != user.uid:
        return JSONResponse(
            status_code=403,
            content={
                "status": "error",
                "message": "Access denied",
                "code": 403
            }
        )
    
    del file_storage[file_id]
    
    if file_record.file_path and os.path.exists(file_record.file_path):
        try:
            os.remove(file_record.file_path)
        except Exception:
            pass
    
    return JSONResponse(
        status_code=200,
        content={
            "status": "success",
            "message": "File deleted successfully",
            "code": 200
        }
    )