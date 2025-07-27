from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import json
import uuid
from datetime import datetime

from app.services.rule_engine import RuleEngine

router = APIRouter()

rule_engine = RuleEngine()

# In-memory storage for processing logs
processing_logs = {}

# Import file_storage from the upload module
from app.api.enhanced_upload import file_storage

class RuleCreateRequest(BaseModel):
    rule_name: str
    rule_config: Dict[str, Any]

class ApplyRulesRequest(BaseModel):
    file_id: str
    rule_types: Optional[List[str]] = None
    rule_names: Optional[Dict[str, List[str]]] = None

class ImportRulesRequest(BaseModel):
    rules_json: str

class ProcessingLogRecord:
    def __init__(self, file_id: str, operation: str, status: str, details: str):
        self.id = str(uuid.uuid4())
        self.file_id = file_id
        self.operation = operation
        self.status = status
        self.details = details
        self.created_at = datetime.utcnow()

def create_processing_log(file_id: str, operation: str, status: str, details: dict):
    log_id = str(uuid.uuid4())
    processing_logs[log_id] = ProcessingLogRecord(
        file_id=file_id,
        operation=operation,
        status=status,
        details=json.dumps(details)
    )
    return log_id

@router.post("/normalization")
async def create_normalization_rule(request: RuleCreateRequest):
    try:
        rule_engine.add_normalization_rule(request.rule_name, request.rule_config)
        
        create_processing_log(
            file_id="rule_engine",
            operation="create_normalization_rule",
            status="success",
            details={"rule_name": request.rule_name, "config": request.rule_config}
        )
        
        return JSONResponse(
            status_code=201,
            content={
                "status": "success",
                "message": f"Normalization rule '{request.rule_name}' created successfully",
                "code": 201,
                "data": {
                    "rule_name": request.rule_name,
                    "rule_type": "normalization",
                    "config": request.rule_config
                }
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Failed to create normalization rule: {str(e)}",
                "code": 500,
                "error_id": f"ERR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            }
        )

@router.post("/aggregation")
async def create_aggregation_rule(request: RuleCreateRequest):
    try:
        rule_engine.add_aggregation_rule(request.rule_name, request.rule_config)
        
        create_processing_log(
            file_id="rule_engine",
            operation="create_aggregation_rule",
            status="success",
            details={"rule_name": request.rule_name, "config": request.rule_config}
        )
        
        return JSONResponse(
            status_code=201,
            content={
                "status": "success",
                "message": f"Aggregation rule '{request.rule_name}' created successfully",
                "code": 201,
                "data": {
                    "rule_name": request.rule_name,
                    "rule_type": "aggregation",
                    "config": request.rule_config
                }
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Failed to create aggregation rule: {str(e)}",
                "code": 500,
                "error_id": f"ERR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            }
        )

@router.post("/flag")
async def create_flag_rule(request: RuleCreateRequest):
    try:
        rule_engine.add_flag_rule(request.rule_name, request.rule_config)
        
        create_processing_log(
            file_id="rule_engine",
            operation="create_flag_rule",
            status="success",
            details={"rule_name": request.rule_name, "config": request.rule_config}
        )
        
        return JSONResponse(
            status_code=201,
            content={
                "status": "success",
                "message": f"Flag rule '{request.rule_name}' created successfully",
                "code": 201,
                "data": {
                    "rule_name": request.rule_name,
                    "rule_type": "flag",
                    "config": request.rule_config
                }
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Failed to create flag rule: {str(e)}",
                "code": 500,
                "error_id": f"ERR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            }
        )

@router.get("/rules")
async def get_all_rules():
    try:
        rules = rule_engine.get_all_rules()
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "Rules retrieved successfully",
                "code": 200,
                "data": rules
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Failed to get rules: {str(e)}",
                "code": 500,
                "error_id": f"ERR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            }
        )

@router.delete("/rules/{rule_type}/{rule_name}")
async def delete_rule(
    rule_type: str,
    rule_name: str
):
    try:
        success = rule_engine.delete_rule(rule_type, rule_name)
        
        if success:
            create_processing_log(
                file_id="rule_engine",
                operation="delete_rule",
                status="success",
                details={"rule_type": rule_type, "rule_name": rule_name}
            )
            
            return JSONResponse(
                status_code=200,
                content={
                    "status": "success",
                    "message": f"Rule '{rule_name}' deleted successfully",
                    "code": 200
                }
            )
        else:
            return JSONResponse(
                status_code=404,
                content={
                    "status": "error",
                    "message": f"Rule '{rule_name}' not found",
                    "code": 404,
                    "error_id": f"ERR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                }
            )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Failed to delete rule: {str(e)}",
                "code": 500,
                "error_id": f"ERR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            }
        )

@router.post("/apply")
async def apply_rules(request: ApplyRulesRequest):
    try:
        import pandas as pd
        
        if request.file_id not in file_storage:
            return JSONResponse(
                status_code=404,
                content={
                    "status": "error",
                    "message": "File not found",
                    "code": 404,
                    "error_id": f"ERR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                }
            )
        
        file_record = file_storage[request.file_id]
        
        if not file_record.file_path:
            return JSONResponse(
                status_code=422,
                content={
                    "status": "error",
                    "message": "File not processed yet",
                    "code": 422,
                    "error_id": f"ERR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                }
            )
        
        df = pd.read_csv(file_record.file_path)
        results = {}
        
        rule_types = request.rule_types or ['normalization', 'aggregation', 'flag']
        
        if 'normalization' in rule_types:
            normalized_df, applied_rules = rule_engine.apply_normalization_rules(
                df, 
                request.rule_names.get('normalization') if request.rule_names else None
            )
            results['normalization'] = {
                'applied_rules': applied_rules,
                'total_rows': len(normalized_df),
                'total_columns': len(normalized_df.columns)
            }
            df = normalized_df
        
        if 'aggregation' in rule_types:
            aggregation_results = rule_engine.apply_aggregation_rules(
                df,
                request.rule_names.get('aggregation') if request.rule_names else None
            )
            results['aggregation'] = aggregation_results
        
        if 'flag' in rule_types:
            flag_results = rule_engine.apply_flag_rules(
                df,
                request.rule_names.get('flag') if request.rule_names else None
            )
            results['flag'] = flag_results
        
        create_processing_log(
            file_id=request.file_id,
            operation="apply_rules",
            status="success",
            details={"rule_types": rule_types, "results": results}
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "Rules applied successfully",
                "code": 200,
                "data": results
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Failed to apply rules: {str(e)}",
                "code": 500,
                "error_id": f"ERR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            }
        )

@router.get("/export")
async def export_rules():
    try:
        rules_json = rule_engine.export_rules()
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "Rules exported successfully",
                "code": 200,
                "data": {
                    "rules": json.loads(rules_json)
                }
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Failed to export rules: {str(e)}",
                "code": 500,
                "error_id": f"ERR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            }
        )

@router.post("/import")
async def import_rules(request: ImportRulesRequest):
    try:
        rule_engine.import_rules(request.rules_json)
        
        create_processing_log(
            file_id="rule_engine",
            operation="import_rules",
            status="success",
            details={"imported_rules": json.loads(request.rules_json)}
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "Rules imported successfully",
                "code": 200
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Failed to import rules: {str(e)}",
                "code": 500,
                "error_id": f"ERR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            }
        )

@router.get("/templates")
async def get_rule_templates():
    templates = {
        "normalization": {
            "hsbc_currency_cleanup": {
                "type": "currency_cleanup",
                "columns": ["amount", "transaction_amount", "value"],
                "symbols": ["$", "£", "€", "₹", "¥"]
            },
            "hsbc_date_format": {
                "type": "date_format",
                "columns": ["date", "transaction_date", "created_date"],
                "output_format": "%Y-%m-%d"
            },
            "hsbc_transaction_type": {
                "type": "value_mapping",
                "mappings": {
                    "transaction_type": {
                        "C": "Credit",
                        "CR": "Credit", 
                        "D": "Debit",
                        "DR": "Debit"
                    }
                }
            }
        },
        "aggregation": {
            "hsbc_transaction_summary": {
                "type": "group_by",
                "group_by": ["transaction_type", "account"],
                "aggregations": {
                    "amount": ["sum", "count", "mean"]
                }
            },
            "hsbc_time_series": {
                "type": "time_series",
                "date_column": "date",
                "value_column": "amount",
                "frequency": "M",
                "aggregation": "sum"
            }
        },
        "flag": {
            "hsbc_high_amount": {
                "type": "threshold",
                "column": "amount",
                "threshold": 5000,
                "operator": ">",
                "flag_name": "high_amount_flag"
            },
            "hsbc_outlier_detection": {
                "type": "outlier",
                "column": "amount",
                "method": "iqr"
            }
        }
    }
    
    return JSONResponse(
        status_code=200,
        content={
            "status": "success",
            "message": "Rule templates retrieved successfully",
            "code": 200,
            "data": templates
        }
    )

@router.get("/logs")
async def get_processing_logs(
    limit: int = 50,
    offset: int = 0
):
    try:
        all_logs = list(processing_logs.values())
        
        all_logs.sort(key=lambda x: x.created_at, reverse=True)
        
        paginated_logs = all_logs[offset:offset + limit]
        
        log_list = []
        for log in paginated_logs:
            log_list.append({
                "id": log.id,
                "file_id": log.file_id,
                "operation": log.operation,
                "status": log.status,
                "details": json.loads(log.details) if log.details else None,
                "created_at": log.created_at.isoformat()
            })
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "Processing logs retrieved successfully",
                "code": 200,
                "data": {
                    "logs": log_list,
                    "total": len(all_logs),
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
                "message": f"Failed to get processing logs: {str(e)}",
                "code": 500,
                "error_id": f"ERR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            }
        )

@router.delete("/logs")
async def clear_processing_logs():
    try:
        logs_count = len(processing_logs)
        processing_logs.clear()
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": f"Cleared {logs_count} processing logs",
                "code": 200
            }
        )
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Failed to clear processing logs: {str(e)}",
                "code": 500,
                "error_id": f"ERR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            }
        )