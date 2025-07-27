from typing import Dict, Any, List
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

class AnalyticsService:
    def __init__(self):
        pass
    
    async def generate_analytics(self, files: List, logs: List, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        Generate comprehensive analytics from files and logs
        """
        try:
            analytics = {
                "time_series": await self._generate_time_series(files, logs, start_date, end_date),
                "file_analytics": await self._generate_file_analytics(files),
                "processing_analytics": await self._generate_processing_analytics(logs),
                "performance_metrics": await self._generate_performance_metrics(logs),
                "trends": await self._generate_trends(files, logs, start_date, end_date)
            }
            
            return analytics
            
        except Exception as e:
            raise Exception(f"Analytics generation failed: {str(e)}")
    
    async def _generate_time_series(self, files: List, logs: List, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        Generate time series data for uploads and processing
        """
        # Create date range
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Count uploads by date
        upload_counts = {}
        for file in files:
            upload_date = file.created_at.date()
            upload_counts[upload_date] = upload_counts.get(upload_date, 0) + 1
        
        # Count processing operations by date
        processing_counts = {}
        for log in logs:
            log_date = log.created_at.date()
            processing_counts[log_date] = processing_counts.get(log_date, 0) + 1
        
        # Create time series data
        time_series_data = []
        for date in date_range:
            date_obj = date.date()
            time_series_data.append({
                "date": date_obj.isoformat(),
                "uploads": upload_counts.get(date_obj, 0),
                "processing_operations": processing_counts.get(date_obj, 0)
            })
        
        return {
            "data": time_series_data,
            "total_uploads": len(files),
            "total_operations": len(logs)
        }
    
    async def _generate_file_analytics(self, files: List) -> Dict[str, Any]:
        """
        Generate analytics about file characteristics
        """
        if not files:
            return {"message": "No files available for analysis"}
        
        # File size analysis
        file_sizes = [f.file_size for f in files]
        size_stats = {
            "total_size_mb": sum(file_sizes) / (1024 * 1024),
            "average_size_mb": np.mean(file_sizes) / (1024 * 1024),
            "median_size_mb": np.median(file_sizes) / (1024 * 1024),
            "largest_file_mb": max(file_sizes) / (1024 * 1024),
            "smallest_file_mb": min(file_sizes) / (1024 * 1024)
        }
        
        # File type distribution
        file_types = {}
        for file in files:
            file_type = file.file_type
            file_types[file_type] = file_types.get(file_type, 0) + 1
        
        # Processing status distribution
        processing_status = {
            "uploaded": len([f for f in files if not f.is_processed]),
            "processed": len([f for f in files if f.is_processed]),
            "normalized": len([f for f in files if f.is_normalized]),
            "aggregated": len([f for f in files if f.is_aggregated])
        }
        
        # Schema analysis
        schemas = [f.schema for f in files if f.schema]
        schema_stats = {}
        if schemas:
            total_columns = sum(len(schema.get("column_types", {})) for schema in schemas)
            total_rows = sum(schema.get("total_rows", 0) for schema in schemas)
            schema_stats = {
                "average_columns": total_columns / len(schemas),
                "average_rows": total_rows / len(schemas),
                "total_columns": total_columns,
                "total_rows": total_rows
            }
        
        return {
            "file_count": len(files),
            "size_statistics": size_stats,
            "file_type_distribution": file_types,
            "processing_status": processing_status,
            "schema_statistics": schema_stats
        }
    
    async def _generate_processing_analytics(self, logs: List) -> Dict[str, Any]:
        """
        Generate analytics about processing operations
        """
        if not logs:
            return {"message": "No processing logs available"}
        
        # Operation type distribution
        operation_types = {}
        for log in logs:
            op_type = log.operation_type
            operation_types[op_type] = operation_types.get(op_type, 0) + 1
        
        # Success rate analysis
        success_count = len([log for log in logs if log.operation_status == "success"])
        failure_count = len([log for log in logs if log.operation_status == "failed"])
        total_count = len(logs)
        
        success_rate = (success_count / total_count * 100) if total_count > 0 else 0
        
        # Processing time analysis
        processing_times = [log.processing_time_ms for log in logs if log.processing_time_ms]
        time_stats = {}
        if processing_times:
            time_stats = {
                "average_time_ms": np.mean(processing_times),
                "median_time_ms": np.median(processing_times),
                "min_time_ms": min(processing_times),
                "max_time_ms": max(processing_times)
            }
        
        # Rows processed analysis
        rows_processed = [log.rows_processed for log in logs if log.rows_processed]
        rows_stats = {}
        if rows_processed:
            rows_stats = {
                "total_rows_processed": sum(rows_processed),
                "average_rows_per_operation": np.mean(rows_processed),
                "max_rows_in_single_operation": max(rows_processed)
            }
        
        return {
            "operation_distribution": operation_types,
            "success_rate_percent": success_rate,
            "total_operations": total_count,
            "successful_operations": success_count,
            "failed_operations": failure_count,
            "processing_time_statistics": time_stats,
            "rows_processed_statistics": rows_stats
        }
    
    async def _generate_performance_metrics(self, logs: List) -> Dict[str, Any]:
        """
        Generate performance metrics
        """
        if not logs:
            return {"message": "No logs available for performance analysis"}
        
        # Calculate performance metrics
        successful_logs = [log for log in logs if log.operation_status == "success"]
        
        if successful_logs:
            avg_processing_time = np.mean([log.processing_time_ms for log in successful_logs if log.processing_time_ms])
            total_rows_processed = sum([log.rows_processed for log in successful_logs if log.rows_processed])
            
            # Throughput calculation
            total_time_seconds = sum([log.processing_time_ms for log in successful_logs if log.processing_time_ms]) / 1000
            throughput = total_rows_processed / total_time_seconds if total_time_seconds > 0 else 0
            
            return {
                "average_processing_time_ms": round(avg_processing_time, 2),
                "total_rows_processed": total_rows_processed,
                "throughput_rows_per_second": round(throughput, 2),
                "total_processing_time_seconds": round(total_time_seconds, 2)
            }
        else:
            return {
                "average_processing_time_ms": 0,
                "total_rows_processed": 0,
                "throughput_rows_per_second": 0,
                "total_processing_time_seconds": 0
            }
    
    async def _generate_trends(self, files: List, logs: List, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        Generate trend analysis
        """
        trends = {
            "upload_trends": {},
            "processing_trends": {},
            "performance_trends": {}
        }
        
        # Upload trends
        if files:
            # Weekly upload trend
            weekly_uploads = {}
            for file in files:
                week_start = file.created_at - timedelta(days=file.created_at.weekday())
                week_key = week_start.strftime("%Y-%m-%d")
                weekly_uploads[week_key] = weekly_uploads.get(week_key, 0) + 1
            
            trends["upload_trends"]["weekly"] = weekly_uploads
        
        # Processing trends
        if logs:
            # Weekly processing trend
            weekly_processing = {}
            for log in logs:
                week_start = log.created_at - timedelta(days=log.created_at.weekday())
                week_key = week_start.strftime("%Y-%m-%d")
                weekly_processing[week_key] = weekly_processing.get(week_key, 0) + 1
            
            trends["processing_trends"]["weekly"] = weekly_processing
            
            # Success rate trend
            success_rate_trend = {}
            for log in logs:
                date_key = log.created_at.strftime("%Y-%m-%d")
                if date_key not in success_rate_trend:
                    success_rate_trend[date_key] = {"success": 0, "total": 0}
                
                success_rate_trend[date_key]["total"] += 1
                if log.operation_status == "success":
                    success_rate_trend[date_key]["success"] += 1
            
            # Calculate success rate for each date
            for date_key in success_rate_trend:
                total = success_rate_trend[date_key]["total"]
                success = success_rate_trend[date_key]["success"]
                success_rate_trend[date_key]["rate"] = (success / total * 100) if total > 0 else 0
            
            trends["processing_trends"]["success_rate"] = success_rate_trend
        
        return trends
    
    async def generate_insights(self, files: List, logs: List) -> List[Dict[str, Any]]:
        """
        Generate AI-powered insights
        """
        insights = []
        
        if not files:
            insights.append({
                "type": "onboarding",
                "title": "Welcome to HSBC Dashboard",
                "description": "Upload your first file to get started with data analysis",
                "priority": "high",
                "action": "upload_file"
            })
            return insights
        
        # File size insights
        file_sizes = [f.file_size for f in files]
        avg_size = np.mean(file_sizes) if file_sizes else 0
        
        if avg_size > 50 * 1024 * 1024:  # 50MB
            insights.append({
                "type": "performance",
                "title": "Large File Detected",
                "description": f"Average file size is {round(avg_size / (1024*1024), 1)}MB",
                "recommendation": "Consider splitting large files for faster processing",
                "priority": "medium"
            })
        
        # Processing insights
        processed_files = len([f for f in files if f.is_processed])
        if processed_files < len(files):
            insights.append({
                "type": "workflow",
                "title": "Unprocessed Files",
                "description": f"{len(files) - processed_files} files need processing",
                "recommendation": "Process your files to unlock analytics",
                "priority": "high"
            })
        
        # Usage pattern insights
        if logs:
            recent_operations = [log.operation_type for log in logs[-10:]]
            if "upload" in recent_operations and "normalize" not in recent_operations:
                insights.append({
                    "type": "workflow",
                    "title": "Complete Your Workflow",
                    "description": "Consider normalizing your recently uploaded files",
                    "priority": "medium"
                })
        
        return insights 