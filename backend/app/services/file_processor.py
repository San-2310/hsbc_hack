import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
import asyncio
from datetime import datetime
import re
import json

class FileProcessor:
    def __init__(self):
        self.supported_formats = ['.csv', '.xlsx', '.xls']
    
    async def detect_schema(self, file_path: str, file_type: str) -> Dict[str, Any]:
        """
        Detect schema and basic information from uploaded file
        """
        try:
            # Read file based on type
            if file_type == '.csv':
                df = pd.read_csv(file_path, nrows=1000)  # Read first 1000 rows for schema detection
            elif file_type in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path, nrows=1000)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
            
            # Get basic info
            total_rows = len(pd.read_csv(file_path) if file_type == '.csv' else pd.read_excel(file_path))
            total_columns = len(df.columns)
            
            # Detect column types
            column_types = {}
            column_info = {}
            
            for col in df.columns:
                col_type = self._detect_column_type(df[col])
                column_types[col] = col_type
                
                # Additional column info
                column_info[col] = {
                    "type": col_type,
                    "unique_values": df[col].nunique(),
                    "null_count": df[col].isnull().sum(),
                    "sample_values": df[col].dropna().head(5).tolist()
                }
            
            # Get preview data
            preview_df = df.head(10)
            preview_data = {
                "columns": preview_df.columns.tolist(),
                "data": preview_df.to_dict('records')
            }
            
            # Detect potential issues
            issues = self._detect_data_issues(df)
            
            return {
                "total_rows": total_rows,
                "total_columns": total_columns,
                "column_types": column_types,
                "column_info": column_info,
                "preview_data": preview_data,
                "issues": issues,
                "detected_date_columns": self._detect_date_columns(df),
                "detected_numeric_columns": self._detect_numeric_columns(df),
                "detected_currency_columns": self._detect_currency_columns(df)
            }
            
        except Exception as e:
            raise Exception(f"Schema detection failed: {str(e)}")
    
    async def get_preview(self, file_path: str, file_type: str, rows: int = 10) -> Dict[str, Any]:
        """
        Get preview data from file
        """
        try:
            if file_type == '.csv':
                df = pd.read_csv(file_path, nrows=rows)
            elif file_type in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path, nrows=rows)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
            
            return {
                "columns": df.columns.tolist(),
                "data": df.to_dict('records'),
                "total_rows": len(df)
            }
            
        except Exception as e:
            raise Exception(f"Preview generation failed: {str(e)}")
    
    def _detect_column_type(self, series: pd.Series) -> str:
        """
        Detect the data type of a column
        """
        # Remove nulls for type detection
        clean_series = series.dropna()
        
        if len(clean_series) == 0:
            return "unknown"
        
        # Check if it's datetime
        try:
            pd.to_datetime(clean_series.head(100))
            return "datetime"
        except:
            pass
        
        # Check if it's numeric
        try:
            pd.to_numeric(clean_series.head(100))
            return "numeric"
        except:
            pass
        
        # Check if it's boolean
        if clean_series.dtype == 'bool':
            return "boolean"
        
        # Check if it's categorical (low cardinality)
        if clean_series.nunique() <= 50:
            return "categorical"
        
        # Default to string
        return "string"
    
    def _detect_date_columns(self, df: pd.DataFrame) -> List[str]:
        """
        Detect columns that contain date/time data
        """
        date_columns = []
        
        for col in df.columns:
            try:
                # Try to parse as datetime
                pd.to_datetime(df[col].head(100))
                date_columns.append(col)
            except:
                continue
        
        return date_columns
    
    def _detect_numeric_columns(self, df: pd.DataFrame) -> List[str]:
        """
        Detect columns that contain numeric data
        """
        numeric_columns = []
        
        for col in df.columns:
            try:
                pd.to_numeric(df[col].head(100))
                numeric_columns.append(col)
            except:
                continue
        
        return numeric_columns
    
    def _detect_currency_columns(self, df: pd.DataFrame) -> List[str]:
        """
        Detect columns that might contain currency data
        """
        currency_columns = []
        currency_patterns = [
            r'\$[\d,]+\.?\d*',  # $1,234.56
            r'[\d,]+\.?\d*\s*[A-Z]{3}',  # 1234.56 USD
            r'[A-Z]{3}\s*[\d,]+\.?\d*',  # USD 1234.56
        ]
        
        for col in df.columns:
            # Check column name for currency indicators
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in ['amount', 'price', 'cost', 'revenue', 'income', 'expense']):
                currency_columns.append(col)
                continue
            
            # Check sample values for currency patterns
            sample_values = df[col].dropna().head(100).astype(str)
            for pattern in currency_patterns:
                if sample_values.str.contains(pattern, regex=True).any():
                    currency_columns.append(col)
                    break
        
        return currency_columns
    
    def _detect_data_issues(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Detect potential data quality issues
        """
        issues = {
            "null_columns": [],
            "duplicate_rows": 0,
            "inconsistent_types": [],
            "outliers": []
        }
        
        # Check for columns with high null percentage
        for col in df.columns:
            null_percentage = df[col].isnull().sum() / len(df) * 100
            if null_percentage > 50:
                issues["null_columns"].append({
                    "column": col,
                    "null_percentage": round(null_percentage, 2)
                })
        
        # Check for duplicate rows
        issues["duplicate_rows"] = df.duplicated().sum()
        
        # Check for inconsistent data types
        for col in df.columns:
            if df[col].dtype == 'object':
                # Check if object column might be numeric
                try:
                    pd.to_numeric(df[col].dropna().head(100))
                    issues["inconsistent_types"].append({
                        "column": col,
                        "issue": "Object column contains numeric data"
                    })
                except:
                    pass
        
        return issues
    
    async def normalize_data(self, file_path: str, file_type: str, normalization_rules: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize data according to specified rules
        """
        try:
            # Read file
            if file_type == '.csv':
                df = pd.read_csv(file_path)
            elif file_type in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
            
            original_shape = df.shape
            normalization_log = []
            
            # Apply normalization rules
            for rule in normalization_rules.get("rules", []):
                rule_type = rule.get("type")
                column = rule.get("column")
                
                if rule_type == "rename_column":
                    new_name = rule.get("new_name")
                    if column in df.columns:
                        df = df.rename(columns={column: new_name})
                        normalization_log.append(f"Renamed column '{column}' to '{new_name}'")
                
                elif rule_type == "convert_to_snake_case":
                    if column in df.columns:
                        new_name = self._to_snake_case(column)
                        df = df.rename(columns={column: new_name})
                        normalization_log.append(f"Converted column '{column}' to snake_case: '{new_name}'")
                
                elif rule_type == "strip_whitespace":
                    if column in df.columns and df[column].dtype == 'object':
                        df[column] = df[column].astype(str).str.strip()
                        normalization_log.append(f"Stripped whitespace from column '{column}'")
                
                elif rule_type == "convert_date":
                    if column in df.columns:
                        try:
                            df[column] = pd.to_datetime(df[column])
                            df[column] = df[column].dt.strftime('%Y-%m-%d')
                            normalization_log.append(f"Converted column '{column}' to date format YYYY-MM-DD")
                        except Exception as e:
                            normalization_log.append(f"Failed to convert column '{column}' to date: {str(e)}")
                
                elif rule_type == "convert_numeric":
                    if column in df.columns:
                        try:
                            df[column] = pd.to_numeric(df[column], errors='coerce')
                            normalization_log.append(f"Converted column '{column}' to numeric")
                        except Exception as e:
                            normalization_log.append(f"Failed to convert column '{column}' to numeric: {str(e)}")
                
                elif rule_type == "standardize_currency":
                    if column in df.columns:
                        df[column] = self._standardize_currency(df[column])
                        normalization_log.append(f"Standardized currency in column '{column}'")
            
            # Save normalized data
            normalized_path = file_path.replace(file_type, f"_normalized{file_type}")
            if file_type == '.csv':
                df.to_csv(normalized_path, index=False)
            else:
                df.to_excel(normalized_path, index=False)
            
            return {
                "original_shape": original_shape,
                "normalized_shape": df.shape,
                "normalization_log": normalization_log,
                "normalized_file_path": normalized_path,
                "columns": df.columns.tolist(),
                "preview_data": df.head(10).to_dict('records')
            }
            
        except Exception as e:
            raise Exception(f"Data normalization failed: {str(e)}")
    
    def _to_snake_case(self, text: str) -> str:
        """Convert text to snake_case"""
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    def _standardize_currency(self, series: pd.Series) -> pd.Series:
        """Standardize currency values"""
        def clean_currency(value):
            if pd.isna(value):
                return value
            value_str = str(value)
            # Remove currency symbols and commas
            cleaned = re.sub(r'[$,£€¥₹]', '', value_str)
            cleaned = re.sub(r',', '', cleaned)
            try:
                return float(cleaned)
            except:
                return value
        
        return series.apply(clean_currency) 