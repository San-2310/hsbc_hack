import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

class AggregationService:
    def __init__(self):
        self.supported_aggregations = {
            "sum": np.sum,
            "mean": np.mean,
            "average": np.mean,
            "median": np.median,
            "min": np.min,
            "max": np.max,
            "count": len,
            "std": np.std,
            "var": np.var
        }
    
    async def aggregate_data(self, file_path: str, file_type: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aggregate data according to configuration
        """
        try:
            # Read file
            if file_type == '.csv':
                df = pd.read_csv(file_path)
            elif file_type in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
            
            aggregation_type = config.get("type", "group_by")
            
            if aggregation_type == "group_by":
                result = await self._group_by_aggregation(df, config)
            elif aggregation_type == "time_series":
                result = await self._time_series_aggregation(df, config)
            elif aggregation_type == "pivot":
                result = await self._pivot_aggregation(df, config)
            elif aggregation_type == "summary_stats":
                result = await self._summary_stats_aggregation(df, config)
            else:
                raise ValueError(f"Unsupported aggregation type: {aggregation_type}")
            
            return result
            
        except Exception as e:
            raise Exception(f"Aggregation failed: {str(e)}")
    
    async def _group_by_aggregation(self, df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform group by aggregation
        """
        group_by_columns = config.get("group_by", [])
        value_columns = config.get("value_columns", [])
        aggregation_functions = config.get("aggregations", {})
        
        if not group_by_columns:
            raise ValueError("Group by columns are required")
        
        # Validate columns exist
        missing_columns = [col for col in group_by_columns + value_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Columns not found: {missing_columns}")
        
        # Perform group by
        grouped = df.groupby(group_by_columns)
        
        # Apply aggregations
        agg_dict = {}
        for col in value_columns:
            if col in aggregation_functions:
                agg_dict[col] = aggregation_functions[col]
            else:
                agg_dict[col] = 'sum'  # Default aggregation
        
        result_df = grouped.agg(agg_dict).reset_index()
        
        return {
            "type": "group_by",
            "result": result_df.to_dict('records'),
            "columns": result_df.columns.tolist(),
            "total_rows": len(result_df),
            "group_by_columns": group_by_columns,
            "value_columns": value_columns,
            "aggregations": aggregation_functions
        }
    
    async def _time_series_aggregation(self, df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform time series aggregation
        """
        date_column = config.get("date_column")
        value_column = config.get("value_column")
        frequency = config.get("frequency", "D")  # D=day, W=week, M=month, Q=quarter, Y=year
        aggregation = config.get("aggregation", "sum")
        
        if not date_column or not value_column:
            raise ValueError("Date column and value column are required")
        
        if date_column not in df.columns or value_column not in df.columns:
            raise ValueError(f"Columns not found: {date_column}, {value_column}")
        
        # Convert date column to datetime
        df[date_column] = pd.to_datetime(df[date_column])
        
        # Set date as index and resample
        df_time = df.set_index(date_column)
        
        # Resample by frequency
        resampled = df_time[value_column].resample(frequency)
        
        # Apply aggregation
        if aggregation in self.supported_aggregations:
            result_series = resampled.apply(self.supported_aggregations[aggregation])
        else:
            result_series = resampled.sum()  # Default to sum
        
        # Convert to DataFrame
        result_df = result_series.reset_index()
        result_df.columns = [date_column, f"{value_column}_{aggregation}"]
        
        return {
            "type": "time_series",
            "result": result_df.to_dict('records'),
            "columns": result_df.columns.tolist(),
            "total_rows": len(result_df),
            "date_column": date_column,
            "value_column": value_column,
            "frequency": frequency,
            "aggregation": aggregation
        }
    
    async def _pivot_aggregation(self, df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform pivot table aggregation
        """
        index_columns = config.get("index", [])
        columns = config.get("columns", [])
        values = config.get("values", [])
        aggfunc = config.get("aggfunc", "sum")
        
        if not index_columns or not values:
            raise ValueError("Index and values are required for pivot")
        
        # Validate columns exist
        all_columns = index_columns + (columns or []) + values
        missing_columns = [col for col in all_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Columns not found: {missing_columns}")
        
        # Perform pivot
        pivot_df = df.pivot_table(
            index=index_columns,
            columns=columns,
            values=values,
            aggfunc=aggfunc,
            fill_value=0
        )
        
        # Reset index to make it a regular DataFrame
        result_df = pivot_df.reset_index()
        
        return {
            "type": "pivot",
            "result": result_df.to_dict('records'),
            "columns": result_df.columns.tolist(),
            "total_rows": len(result_df),
            "index_columns": index_columns,
            "pivot_columns": columns,
            "value_columns": values,
            "aggregation": aggfunc
        }
    
    async def _summary_stats_aggregation(self, df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate summary statistics for numeric columns
        """
        columns = config.get("columns", [])
        
        if not columns:
            # Use all numeric columns
            columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        # Validate columns exist
        missing_columns = [col for col in columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Columns not found: {missing_columns}")
        
        # Calculate summary statistics
        summary_stats = {}
        for col in columns:
            if col in df.columns:
                series = df[col].dropna()
                if len(series) > 0:
                    summary_stats[col] = {
                        "count": len(series),
                        "mean": float(series.mean()),
                        "median": float(series.median()),
                        "std": float(series.std()),
                        "min": float(series.min()),
                        "max": float(series.max()),
                        "q25": float(series.quantile(0.25)),
                        "q75": float(series.quantile(0.75)),
                        "null_count": int(df[col].isnull().sum())
                    }
        
        return {
            "type": "summary_stats",
            "result": summary_stats,
            "columns": list(summary_stats.keys()),
            "total_columns": len(summary_stats)
        }
    
    def get_available_aggregations(self) -> List[str]:
        """
        Get list of available aggregation functions
        """
        return list(self.supported_aggregations.keys())
    
    def validate_aggregation_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate aggregation configuration
        """
        errors = []
        warnings = []
        
        # Check required fields based on type
        aggregation_type = config.get("type")
        
        if aggregation_type == "group_by":
            if not config.get("group_by"):
                errors.append("group_by is required for group_by aggregation")
            if not config.get("value_columns"):
                warnings.append("value_columns is recommended for group_by aggregation")
        
        elif aggregation_type == "time_series":
            if not config.get("date_column"):
                errors.append("date_column is required for time_series aggregation")
            if not config.get("value_column"):
                errors.append("value_column is required for time_series aggregation")
        
        elif aggregation_type == "pivot":
            if not config.get("index"):
                errors.append("index is required for pivot aggregation")
            if not config.get("values"):
                errors.append("values is required for pivot aggregation")
        
        # Check aggregation functions
        aggregations = config.get("aggregations", {})
        for col, agg_func in aggregations.items():
            if agg_func not in self.supported_aggregations:
                errors.append(f"Unsupported aggregation function '{agg_func}' for column '{col}'")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        } 