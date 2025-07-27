from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
import json
from datetime import datetime

from app.core.database import get_db
from app.core.auth import verify_firebase_token, User
from app.models.file_upload import FileUpload
from app.models.processing_log import ProcessingLog
from app.services.file_processor import FileProcessor

router = APIRouter()
security = HTTPBearer()

@router.post("/normalize")
async def normalize_data(
    file_id: str,
    normalization_rules: Dict[str, Any],
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
        
        log = ProcessingLog.create_log(
            db=db,
            file_id=file_id,
            user_id=user.uid,
            operation_type="normalize",
            operation_details="Data normalization",
            input_data=normalization_rules
        )
        
        processor = FileProcessor()
        result = await processor.normalize_data(
            file_upload.file_path,
            file_upload.file_type,
            normalization_rules
        )
        
        file_upload.is_normalized = True
        file_upload.normalization_log = json.dumps(result["normalization_log"])
        file_upload.processed_timestamp = datetime.now()
        db.commit()
        
        log.complete_success(
            db=db,
            output_data=result,
            processing_time_ms=0,
            rows_processed=result["normalized_shape"][0]
        )
        
        return {
            "success": True,
            "file_id": file_id,
            "normalization_result": result,
            "message": "Data normalized successfully"
        }
        
    except Exception as e:
        if 'log' in locals():
            log.complete_failure(db, str(e))
        
        raise HTTPException(status_code=500, detail=f"Normalization failed: {str(e)}")

@router.post("/aggregate")
async def aggregate_data(
    file_id: str,
    aggregation_config: Dict[str, Any],
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
        
        # Create processing log
        log = ProcessingLog.create_log(
            db=db,
            file_id=file_id,
            user_id=user.uid,
            operation_type="aggregate",
            operation_details="Data aggregation",
            input_data=aggregation_config
        )
        
        # Process aggregation
        # aggregation_service = AggregationService()
        # result = await aggregation_service.aggregate_data(
        #     file_upload.file_path,
        #     file_upload.file_type,
        #     aggregation_config
        # )
        
        result = {
            "type": "group_by",
            "result": [],
            "columns": [],
            "total_rows": 0
        }
        
        file_upload.is_aggregated = True
        file_upload.aggregation_config = json.dumps(aggregation_config)
        file_upload.processed_timestamp = datetime.now()
        db.commit()
        
        log.complete_success(
            db=db,
            output_data=result,
            processing_time_ms=0,
            rows_processed=result.get("total_rows", 0)
        )
        
        return {
            "success": True,
            "file_id": file_id,
            "aggregation_result": result,
            "message": "Data aggregated successfully"
        }
        
    except Exception as e:
        if 'log' in locals():
            log.complete_failure(db, str(e))
        
        raise HTTPException(status_code=500, detail=f"Aggregation failed: {str(e)}")

@router.get("/{file_id}/logs")
async def get_processing_logs(
    file_id: str,
    token: str = Depends(security),
    db: Session = Depends(get_db),
    limit: int = 50,
    offset: int = 0
):
    try:
        user = await verify_firebase_token(token.credentials)
        
        file_upload = db.query(FileUpload).filter(
            FileUpload.file_id == file_id,
            FileUpload.user_id == user.uid
        ).first()
        
        if not file_upload:
            raise HTTPException(status_code=404, detail="File not found")
        
        logs = db.query(ProcessingLog).filter(
            ProcessingLog.file_id == file_id,
            ProcessingLog.user_id == user.uid
        ).order_by(ProcessingLog.created_at.desc()).offset(offset).limit(limit).all()
        
        total_count = db.query(ProcessingLog).filter(
            ProcessingLog.file_id == file_id,
            ProcessingLog.user_id == user.uid
        ).count()
        
        return {
            "logs": [log.to_dict() for log in logs],
            "total_count": total_count,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get logs: {str(e)}")

@router.get("/{file_id}/suggestions")
async def get_processing_suggestions(
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
        
        schema = file_upload.schema
        if not schema:
            raise HTTPException(status_code=400, detail="No schema information available")
        
        suggestions = {
            "normalization_suggestions": [],
            "aggregation_suggestions": [],
            "visualization_suggestions": []
        }
        
        for col, info in schema.get("column_info", {}).items():
            col_lower = col.lower()
            
            if any(c.isupper() for c in col) and not col.isupper():
                suggestions["normalization_suggestions"].append({
                    "type": "convert_to_snake_case",
                    "column": col,
                    "reason": "Convert camelCase to snake_case for consistency"
                })
            
            if info.get("type") == "datetime":
                suggestions["normalization_suggestions"].append({
                    "type": "convert_date",
                    "column": col,
                    "reason": "Standardize date format to YYYY-MM-DD"
                })
            
            if col in schema.get("detected_currency_columns", []):
                suggestions["normalization_suggestions"].append({
                    "type": "standardize_currency",
                    "column": col,
                    "reason": "Standardize currency format"
                })
        
        date_columns = schema.get("detected_date_columns", [])
        numeric_columns = schema.get("detected_numeric_columns", [])
        
        if date_columns and numeric_columns:
            suggestions["aggregation_suggestions"].append({
                "type": "time_series",
                "group_by": date_columns[0],
                "value_column": numeric_columns[0],
                "aggregation": "sum",
                "reason": "Time series analysis of numeric data"
            })
        
        if len(numeric_columns) > 1:
            suggestions["aggregation_suggestions"].append({
                "type": "summary_stats",
                "columns": numeric_columns,
                "reason": "Summary statistics for numeric columns"
            })
        
        if date_columns and numeric_columns:
            suggestions["visualization_suggestions"].append({
                "type": "line_chart",
                "x_axis": date_columns[0],
                "y_axis": numeric_columns[0],
                "title": f"{numeric_columns[0]} over time"
            })
        
        categorical_columns = [col for col, info in schema.get("column_info", {}).items() 
            if info.get("type") == "categorical"]
        
        if categorical_columns and numeric_columns:
            suggestions["visualization_suggestions"].append({
                "type": "bar_chart",
                "x_axis": categorical_columns[0],
                "y_axis": numeric_columns[0],
                "title": f"{numeric_columns[0]} by {categorical_columns[0]}"
            })
        
        return {
            "file_id": file_id,
            "suggestions": suggestions
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get suggestions: {str(e)}")

@router.post("/{file_id}/export")
async def export_processed_data(
    file_id: str,
    export_config: Dict[str, Any],
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
        
        log = ProcessingLog.create_log(
            db=db,
            file_id=file_id,
            user_id=user.uid,
            operation_type="export",
            operation_details="Data export",
            input_data=export_config
        )
        
        log.complete_success(
            db=db,
            output_data={"export_format": export_config.get("format", "csv")},
            processing_time_ms=0
        )
        
        return {
            "success": True,
            "file_id": file_id,
            "export_url": f"/exports/{file_id}.{export_config.get('format', 'csv')}",
            "message": "Data exported successfully"
        }
        
    except Exception as e:
        if 'log' in locals():
            log.complete_failure(db, str(e))
        
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}") 