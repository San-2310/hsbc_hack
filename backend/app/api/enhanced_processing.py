from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from typing import Dict, Any, List, Optional
import os
import json
import pandas as pd
from datetime import datetime
import tempfile

from app.core.auth import User, get_current_user
from app.core.database import get_db
from app.models.file_upload import FileUpload
from app.models.processing_log import ProcessingLog
from app.services.enhanced_file_processor import EnhancedFileProcessor
from app.services.enhanced_aggregation_service import EnhancedAggregationService
from app.core.config import settings

router = APIRouter()

file_processor = EnhancedFileProcessor()
aggregation_service = EnhancedAggregationService()

@router.post("/normalize")
async def normalize_data(
    background_tasks: BackgroundTasks,
    request: Dict[str, Any],
    user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    try:
        file_id = request.get('file_id')
        normalization_rules = request.get('normalization_rules', {})
        
        if not file_id:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": "File ID is required",
                    "code": 400,
                    "error_id": f"ERR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                }
            )
        
        file_upload = db.query(FileUpload).filter(
            FileUpload.id == file_id,
            FileUpload.user_id == user.uid
        ).first()
        
        if not file_upload:
            return JSONResponse(
                status_code=404,
                content={
                    "status": "error",
                    "message": "File not found",
                    "code": 404,
                    "error_id": f"ERR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                }
            )
        
        background_tasks.add_task(
            process_normalization,
            file_id,
            file_upload.file_path,
            file_upload.file_type,
            normalization_rules,
            user.uid,
            db
        )
        
        return JSONResponse(
            status_code=202,
            content={
                "status": "success",
                "message": "Normalization processing started",
                "code": 202,
                "data": {
                    "file_id": file_id,
                    "status": "processing"
                }
            }
        )
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Normalization failed: {str(e)}",
                "code": 500,
                "error_id": f"ERR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            }
        )

@router.post("/aggregate")
async def aggregate_data(
    background_tasks: BackgroundTasks,
    request: Dict[str, Any],
    user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    try:
        file_id = request.get('file_id')
        config = request.get('config', {})
        
        if not file_id:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": "File ID is required",
                    "code": 400,
                    "error_id": f"ERR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                }
            )
        
        file_upload = db.query(FileUpload).filter(
            FileUpload.id == file_id,
            FileUpload.user_id == user.uid
        ).first()
        
        if not file_upload:
            return JSONResponse(
                status_code=404,
                content={
                    "status": "error",
                    "message": "File not found",
                    "code": 404,
                    "error_id": f"ERR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                }
            )
        
        background_tasks.add_task(
            process_aggregation,
            file_id,
            file_upload.file_path,
            file_upload.file_type,
            config,
            user.uid,
            db
        )
        
        return JSONResponse(
            status_code=202,
            content={
                "status": "success",
                "message": "Aggregation processing started",
                "code": 202,
                "data": {
                    "file_id": file_id,
                    "status": "processing"
                }
            }
        )
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Aggregation failed: {str(e)}",
                "code": 500,
                "error_id": f"ERR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            }
        )

@router.post("/export")
async def export_data(
    request: Dict[str, Any],
    user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    try:
        file_id = request.get('file_id')
        aggregation_result = request.get('aggregation_result', {})
        export_format = request.get('format', 'csv')
        
        if not file_id or not aggregation_result:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": "File ID and aggregation result are required",
                    "code": 400,
                    "error_id": f"ERR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                }
            )
        
        export_filename = f"export_{file_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{export_format}"
        export_path = os.path.join(settings.UPLOAD_DIR, export_filename)
        
        df = pd.DataFrame(aggregation_result.get('result', []))
        
        if export_format == 'csv':
            df.to_csv(export_path, index=False)
        elif export_format == 'xlsx':
            df.to_excel(export_path, index=False)
        elif export_format == 'json':
            df.to_json(export_path, orient='records', indent=2)
        else:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": f"Unsupported export format: {export_format}",
                    "code": 400,
                    "error_id": f"ERR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                }
            )
        
        log = ProcessingLog(
            file_id=file_id,
            user_id=user.uid,
            operation="export",
            status="success",
            details=json.dumps({
                "format": export_format,
                "rows": len(df),
                "columns": len(df.columns)
            }),
            created_at=datetime.utcnow()
        )
        db.add(log)
        db.commit()
        
        return FileResponse(
            path=export_path,
            filename=export_filename,
            media_type='application/octet-stream'
        )
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Export failed: {str(e)}",
                "code": 500,
                "error_id": f"ERR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            }
        )

@router.get("/suggestions/{file_id}")
async def get_processing_suggestions(
    file_id: str,
    user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    try:
        file_upload = db.query(FileUpload).filter(
            FileUpload.id == file_id,
            FileUpload.user_id == user.uid
        ).first()
        
        if not file_upload:
            return JSONResponse(
                status_code=404,
                content={
                    "status": "error",
                    "message": "File not found",
                    "code": 404,
                    "error_id": f"ERR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                }
            )
        
        if not file_upload.schema_info:
            return JSONResponse(
                status_code=422,
                content={
                    "status": "error",
                    "message": "Schema not available",
                    "code": 422,
                    "error_id": f"ERR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                }
            )
        
        schema = json.loads(file_upload.schema_info)
        suggestions = generate_suggestions(schema)
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "Suggestions generated successfully",
                "code": 200,
                "data": suggestions
            }
        )
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Failed to generate suggestions: {str(e)}",
                "code": 500,
                "error_id": f"ERR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            }
        )

@router.get("/logs/{file_id}")
async def get_processing_logs(
    file_id: str,
    user: User = Depends(get_current_user),
    db = Depends(get_db),
    limit: int = 50,
    offset: int = 0
):
    try:
        file_upload = db.query(FileUpload).filter(
            FileUpload.id == file_id,
            FileUpload.user_id == user.uid
        ).first()
        
        if not file_upload:
            return JSONResponse(
                status_code=404,
                content={
                    "status": "error",
                    "message": "File not found",
                    "code": 404,
                    "error_id": f"ERR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                }
            )
        
        logs = db.query(ProcessingLog).filter(
            ProcessingLog.file_id == file_id
        ).order_by(ProcessingLog.created_at.desc()).offset(offset).limit(limit).all()
        
        log_list = []
        for log in logs:
            log_list.append({
                "id": log.id,
                "operation": log.operation,
                "status": log.status,
                "details": log.details,
                "created_at": log.created_at.isoformat()
            })
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "Logs retrieved successfully",
                "code": 200,
                "data": {
                    "logs": log_list,
                    "total": len(log_list),
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
                "message": f"Failed to get logs: {str(e)}",
                "code": 500,
                "error_id": f"ERR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            }
        )

async def process_normalization(
    file_id: str,
    file_path: str,
    file_type: str,
    normalization_rules: Dict[str, Any],
    user_id: str,
    db
):
    try:
        if file_type == '.csv':
            df = pd.read_csv(file_path)
        elif file_type in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path)
        elif file_type == '.json':
            df = pd.read_json(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
        
        normalized_df, normalization_log = file_processor.apply_custom_normalization(df, normalization_rules)
        
        normalized_path = file_path.replace(file_type, f"_normalized{file_type}")
        if file_type == '.csv':
            normalized_df.to_csv(normalized_path, index=False)
        elif file_type in ['.xlsx', '.xls']:
            normalized_df.to_excel(normalized_path, index=False)
        elif file_type == '.json':
            normalized_df.to_json(normalized_path, orient='records', indent=2)
        
        file_upload = db.query(FileUpload).filter(FileUpload.id == file_id).first()
        if file_upload:
            file_upload.file_path = normalized_path
            file_upload.updated_at = datetime.utcnow()
            db.commit()
        
        log = ProcessingLog(
            file_id=file_id,
            user_id=user_id,
            operation="normalization",
            status="success",
            details=json.dumps(normalization_log),
            created_at=datetime.utcnow()
        )
        db.add(log)
        db.commit()
        
    except Exception as e:
        log = ProcessingLog(
            file_id=file_id,
            user_id=user_id,
            operation="normalization",
            status="error",
            details=str(e),
            created_at=datetime.utcnow()
        )
        db.add(log)
        db.commit()

async def process_aggregation(
    file_id: str,
    file_path: str,
    file_type: str,
    config: Dict[str, Any],
    user_id: str,
    db
):
    try:
        if file_type == '.csv':
            df = pd.read_csv(file_path)
        elif file_type in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path)
        elif file_type == '.json':
            df = pd.read_json(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
        
        result = await aggregation_service.aggregate_data(df, config)
        
        result_path = os.path.join(settings.UPLOAD_DIR, f"aggregation_{file_id}.json")
        with open(result_path, 'w') as f:
            json.dump(result, f, indent=2)
        
        log = ProcessingLog(
            file_id=file_id,
            user_id=user_id,
            operation="aggregation",
            status="success",
            details=json.dumps({
                "config": config,
                "result_rows": len(result.get('result', [])),
                "result_columns": len(result.get('columns', []))
            }),
            created_at=datetime.utcnow()
        )
        db.add(log)
        db.commit()
        
    except Exception as e:
        log = ProcessingLog(
            file_id=file_id,
            user_id=user_id,
            operation="aggregation",
            status="error",
            details=str(e),
            created_at=datetime.utcnow()
        )
        db.add(log)
        db.commit()

def generate_suggestions(schema: Dict[str, Any]) -> Dict[str, Any]:
    suggestions = {
        "normalization": [],
        "aggregation": [],
        "visualization": []
    }
    
    column_info = schema.get('column_info', {})
    hsbc_patterns = schema.get('hsbc_patterns', {})
    
    for col, info in column_info.items():
        if info.get('type') == 'datetime':
            suggestions["normalization"].append({
                "type": "date_format",
                "column": col,
                "description": f"Standardize date format for {col}",
                "priority": "high"
            })
        
        if info.get('type') == 'numeric':
            suggestions["normalization"].append({
                "type": "currency_cleanup",
                "column": col,
                "description": f"Remove currency symbols from {col}",
                "priority": "medium"
            })
    
    numeric_columns = [col for col, info in column_info.items() if info.get('type') == 'numeric']
    date_columns = [col for col, info in column_info.items() if info.get('type') == 'datetime']
    categorical_columns = [col for col, info in column_info.items() if info.get('type') == 'categorical']
    
    if numeric_columns and categorical_columns:
        suggestions["aggregation"].append({
            "type": "group_by",
            "description": f"Group by {categorical_columns[0]} and sum {numeric_columns[0]}",
            "config": {
                "type": "group_by",
                "group_by": [categorical_columns[0]],
                "value_columns": [numeric_columns[0]],
                "aggregations": {numeric_columns[0]: ["sum", "mean"]}
            }
        })
    
    if date_columns and numeric_columns:
        suggestions["aggregation"].append({
            "type": "time_series",
            "description": f"Time series analysis of {numeric_columns[0]} by {date_columns[0]}",
            "config": {
                "type": "time_series",
                "date_column": date_columns[0],
                "value_column": numeric_columns[0],
                "frequency": "M"
            }
        })
    
    if hsbc_patterns:
        suggestions["aggregation"].append({
            "type": "hsbc_pattern",
            "description": "Use HSBC transaction summary pattern",
            "config": {
                "type": "hsbc_pattern",
                "pattern": "transaction_summary"
            }
        })
    
    return suggestions 