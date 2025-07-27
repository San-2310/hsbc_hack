from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
import json
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.auth import verify_firebase_token, User
from app.models.file_upload import FileUpload
from app.models.processing_log import ProcessingLog
from app.services.analytics_service import AnalyticsService

router = APIRouter()
security = HTTPBearer()

@router.get("/overview")
async def get_dashboard_overview(
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    try:
        user = await verify_firebase_token(token.credentials)
        
        files = db.query(FileUpload).filter(
            FileUpload.user_id == user.uid
        ).all()
        
        total_files = len(files)
        total_size = sum(f.file_size for f in files)
        processed_files = len([f for f in files if f.is_processed])
        normalized_files = len([f for f in files if f.is_normalized])
        aggregated_files = len([f for f in files if f.is_aggregated])
        
        recent_logs = db.query(ProcessingLog).filter(
            ProcessingLog.user_id == user.uid
        ).order_by(ProcessingLog.created_at.desc()).limit(10).all()
        
        file_types = {}
        for file in files:
            file_type = file.file_type
            file_types[file_type] = file_types.get(file_type, 0) + 1
        
        processing_status = {
            "uploaded": len([f for f in files if not f.is_processed]),
            "processed": processed_files,
            "normalized": normalized_files,
            "aggregated": aggregated_files
        }
        
        return {
            "user": {
                "uid": user.uid,
                "email": user.email,
                "display_name": user.display_name,
                "role": user.role
            },
            "metrics": {
                "total_files": total_files,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "processed_files": processed_files,
                "normalized_files": normalized_files,
                "aggregated_files": aggregated_files
            },
            "file_types": file_types,
            "processing_status": processing_status,
            "recent_activity": [log.to_dict() for log in recent_logs]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard overview: {str(e)}")

@router.get("/files/summary")
async def get_files_summary(
    token: str = Depends(security),
    db: Session = Depends(get_db),
    limit: int = 10
):
    try:
        user = await verify_firebase_token(token.credentials)
        
        files = db.query(FileUpload).filter(
            FileUpload.user_id == user.uid
        ).order_by(FileUpload.created_at.desc()).limit(limit).all()
        
        files_summary = []
        for file in files:
            logs = db.query(ProcessingLog).filter(
                ProcessingLog.file_id == file.file_id,
                ProcessingLog.user_id == user.uid
            ).order_by(ProcessingLog.created_at.desc()).limit(5).all()
            
            files_summary.append({
                **file.to_dict(),
                "recent_logs": [log.to_dict() for log in logs]
            })
        
        return {
            "files": files_summary,
            "total_count": len(files_summary)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get files summary: {str(e)}")

@router.get("/analytics")
async def get_analytics(
    token: str = Depends(security),
    db: Session = Depends(get_db),
    days: int = 30
):
    try:
        user = await verify_firebase_token(token.credentials)
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        files_in_range = db.query(FileUpload).filter(
            FileUpload.user_id == user.uid,
            FileUpload.created_at >= start_date,
            FileUpload.created_at <= end_date
        ).all()
        
        logs_in_range = db.query(ProcessingLog).filter(
            ProcessingLog.user_id == user.uid,
            ProcessingLog.created_at >= start_date,
            ProcessingLog.created_at <= end_date
        ).all()
        
        # Generate analytics
        # analytics_service = AnalyticsService()
        # analytics = await analytics_service.generate_analytics(
        #     files_in_range,
        #     logs_in_range,
        #     start_date,
        #     end_date
        # )
        
        return {
            "time_series": [],
            "file_analytics": {},
            "processing_analytics": {},
            "performance_metrics": {},
            "trends": {}
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")

@router.get("/insights")
async def get_insights(
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    try:
        user = await verify_firebase_token(token.credentials)
        
        files = db.query(FileUpload).filter(
            FileUpload.user_id == user.uid
        ).all()
        
        insights = []
        
        if files:
            file_sizes = [f.file_size for f in files]
            avg_size = sum(file_sizes) / len(file_sizes)
            largest_file = max(files, key=lambda x: x.file_size)
            
            insights.append({
                "type": "file_size",
                "title": "File Size Analysis",
                "description": f"Average file size: {round(avg_size / (1024*1024), 2)}MB",
                "recommendation": "Consider splitting large files for better processing performance",
                "severity": "info"
            })
            
            processed_count = len([f for f in files if f.is_processed])
            if processed_count < len(files):
                insights.append({
                    "type": "processing",
                    "title": "Unprocessed Files",
                    "description": f"{len(files) - processed_count} files haven't been processed yet",
                    "recommendation": "Process your files to unlock analytics capabilities",
                    "severity": "warning"
                })
            
            schemas = [f.schema for f in files if f.schema]
            if schemas:
                common_issues = []
                for schema in schemas:
                    issues = schema.get("issues", {})
                    if issues.get("null_columns"):
                        common_issues.append("Missing data in columns")
                    if issues.get("duplicate_rows", 0) > 0:
                        common_issues.append("Duplicate rows detected")
                
                if common_issues:
                    insights.append({
                        "type": "data_quality",
                        "title": "Data Quality Issues",
                        "description": f"Found: {', '.join(set(common_issues))}",
                        "recommendation": "Use normalization to clean your data",
                        "severity": "warning"
                    })
        
        return {
            "insights": insights,
            "total_insights": len(insights)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get insights: {str(e)}")

@router.get("/performance")
async def get_performance_metrics(
    token: str = Depends(security),
    db: Session = Depends(get_db),
    days: int = 7
):
    try:
        user = await verify_firebase_token(token.credentials)
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        logs = db.query(ProcessingLog).filter(
            ProcessingLog.user_id == user.uid,
            ProcessingLog.created_at >= start_date,
            ProcessingLog.created_at <= end_date,
            ProcessingLog.processing_time_ms.isnot(None)
        ).all()
        
        if logs:
            avg_processing_time = sum(log.processing_time_ms or 0 for log in logs) / len(logs)
            total_rows_processed = sum(log.rows_processed or 0 for log in logs)
            success_rate = len([log for log in logs if log.operation_status == "success"]) / len(logs) * 100
        else:
            avg_processing_time = 0
            total_rows_processed = 0
            success_rate = 100
        
        operation_types = {}
        for log in logs:
            op_type = log.operation_type
            operation_types[op_type] = operation_types.get(op_type, 0) + 1
        
        return {
            "performance_metrics": {
                "avg_processing_time_ms": round(avg_processing_time, 2),
                "total_rows_processed": total_rows_processed,
                "success_rate_percent": round(success_rate, 2),
                "total_operations": len(logs)
            },
            "operation_distribution": operation_types,
            "time_period_days": days
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get performance metrics: {str(e)}")

@router.get("/recommendations")
async def get_recommendations(
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    try:
        user = await verify_firebase_token(token.credentials)
        
        files = db.query(FileUpload).filter(
            FileUpload.user_id == user.uid
        ).all()
        
        logs = db.query(ProcessingLog).filter(
            ProcessingLog.user_id == user.uid
        ).order_by(ProcessingLog.created_at.desc()).limit(50).all()
        
        recommendations = []
        
        if len(files) < 5:
            recommendations.append({
                "type": "upload",
                "title": "Upload More Data",
                "description": "Upload more files to get better insights",
                "priority": "medium"
            })
        
        unprocessed_files = [f for f in files if not f.is_processed]
        if unprocessed_files:
            recommendations.append({
                "type": "processing",
                "title": "Process Your Files",
                "description": f"Process {len(unprocessed_files)} files to unlock analytics",
                "priority": "high"
            })
        
        unnormalized_files = [f for f in files if f.is_processed and not f.is_normalized]
        if unnormalized_files:
            recommendations.append({
                "type": "normalization",
                "title": "Normalize Your Data",
                "description": f"Normalize {len(unnormalized_files)} files for better analysis",
                "priority": "medium"
            })
        
        unaggregated_files = [f for f in files if f.is_normalized and not f.is_aggregated]
        if unaggregated_files:
            recommendations.append({
                "type": "aggregation",
                "title": "Create Aggregations",
                "description": f"Create aggregations for {len(unaggregated_files)} files",
                "priority": "low"
            })
        
        if logs:
            recent_operations = [log.operation_type for log in logs[:10]]
            if "upload" in recent_operations and "normalize" not in recent_operations:
                recommendations.append({
                    "type": "workflow",
                    "title": "Complete Your Workflow",
                    "description": "Consider normalizing your recently uploaded files",
                    "priority": "medium"
                })
        
        return {
            "recommendations": recommendations,
            "total_recommendations": len(recommendations)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}") 