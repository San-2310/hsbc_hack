import pandas as pd
import numpy as np
import requests
import json
import re
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
import asyncio
import aiohttp
from io import StringIO, BytesIO

class EnhancedFileProcessor:
    def __init__(self):
        self.supported_formats = ['.csv', '.xlsx', '.xls', '.json']
        self.max_file_size = 100 * 1024 * 1024  # 100MB
        
        # HSBC-specific normalization rules
        self.hsbc_normalization_rules = {
            'date_columns': {
                'patterns': ['date', 'txn_date', 'value_date', 'transaction_date', 'created_date'],
                'output_format': 'YYYY-MM-DD'
            },
            'amount_columns': {
                'patterns': ['amount', 'txn_amt', 'transaction_value', 'value', 'sum'],
                'currency_symbols': ['₹', '$', '£', '€', '¥'],
                'output_format': 'float'
            },
            'type_columns': {
                'patterns': ['type', 'cr_dr_flag', 'transaction_type', 'direction'],
                'mappings': {
                    'C': 'Credit', 'CR': 'Credit', 'Credit': 'Credit',
                    'D': 'Debit', 'DR': 'Debit', 'Debit': 'Debit'
                }
            },
            'account_columns': {
                'patterns': ['account', 'user_id', 'account_no', 'customer_id', 'account_number']
            }
        }
    
    async def process_input(self, input_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input from various sources (file, API, URL, JSON)
        """
        input_type = input_config.get('type', 'file')
        
        if input_type == 'file':
            return await self._process_file_input(input_config)
        elif input_type == 'api':
            return await self._process_api_input(input_config)
        elif input_type == 'url':
            return await self._process_url_input(input_config)
        elif input_type == 'json':
            return await self._process_json_input(input_config)
        else:
            raise ValueError(f"Unsupported input type: {input_type}")
    
    async def _process_file_input(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Process file upload"""
        file_path = config['file_path']
        file_type = config['file_type']
        
        # Validate file
        self._validate_file(file_path, file_type)
        
        # Read file
        df = self._read_file(file_path, file_type)
        
        # Detect schema
        schema_info = self._detect_schema(df)
        
        # Apply HSBC normalization rules
        normalized_df, normalization_log = self._apply_hsbc_normalization(df)
        
        return {
            'data': normalized_df.to_dict('records'),
            'schema': schema_info,
            'normalization_log': normalization_log,
            'total_rows': len(normalized_df),
            'total_columns': len(normalized_df.columns)
        }
    
    async def _process_api_input(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Process API endpoint input"""
        url = config['url']
        method = config.get('method', 'GET')
        headers = config.get('headers', {})
        params = config.get('params', {})
        data = config.get('data', {})
        
        async with aiohttp.ClientSession() as session:
            if method.upper() == 'GET':
                async with session.get(url, headers=headers, params=params) as response:
                    response_data = await response.json()
            else:
                async with session.post(url, headers=headers, json=data) as response:
                    response_data = await response.json()
            
            if response.status != 200:
                raise ValueError(f"API request failed with status {response.status}")
            
            # Convert to DataFrame
            df = pd.DataFrame(response_data)
            
            # Process the data
            schema_info = self._detect_schema(df)
            normalized_df, normalization_log = self._apply_hsbc_normalization(df)
            
            return {
                'data': normalized_df.to_dict('records'),
                'schema': schema_info,
                'normalization_log': normalization_log,
                'total_rows': len(normalized_df),
                'total_columns': len(normalized_df.columns),
                'source': f"API: {url}"
            }
    
    async def _process_url_input(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Process URL input (download file from URL)"""
        url = config['url']
        headers = config.get('headers', {})
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    raise ValueError(f"URL request failed with status {response.status}")
                
                content = await response.read()
                
                # Determine file type from URL or content
                file_type = self._detect_file_type_from_url(url, content)
                
                # Save to temporary file
                temp_path = f"/tmp/temp_file_{datetime.now().timestamp()}{file_type}"
                with open(temp_path, 'wb') as f:
                    f.write(content)
                
                try:
                    return await self._process_file_input({
                        'file_path': temp_path,
                        'file_type': file_type
                    })
                finally:
                    # Clean up temp file
                    import os
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
    
    async def _process_json_input(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Process JSON input"""
        json_data = config['data']
        
        # Convert to DataFrame
        if isinstance(json_data, list):
            df = pd.DataFrame(json_data)
        else:
            df = pd.DataFrame([json_data])
        
        # Process the data
        schema_info = self._detect_schema(df)
        normalized_df, normalization_log = self._apply_hsbc_normalization(df)
        
        return {
            'data': normalized_df.to_dict('records'),
            'schema': schema_info,
            'normalization_log': normalization_log,
            'total_rows': len(normalized_df),
            'total_columns': len(normalized_df.columns),
            'source': 'JSON Input'
        }
    
    def _validate_file(self, file_path: str, file_type: str) -> None:
        """Validate file type and size"""
        if file_type not in self.supported_formats:
            raise ValueError(f"Unsupported file type: {file_type}")
        
        import os
        file_size = os.path.getsize(file_path)
        if file_size > self.max_file_size:
            raise ValueError(f"File too large: {file_size} bytes (max: {self.max_file_size})")
    
    def _read_file(self, file_path: str, file_type: str) -> pd.DataFrame:
        """Read file based on type"""
        try:
            if file_type == '.csv':
                return pd.read_csv(file_path)
            elif file_type in ['.xlsx', '.xls']:
                return pd.read_excel(file_path)
            elif file_type == '.json':
                return pd.read_json(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
        except Exception as e:
            raise ValueError(f"Error reading file: {str(e)}")
    
    def _detect_file_type_from_url(self, url: str, content: bytes) -> str:
        """Detect file type from URL or content"""
        # Check URL extension
        if url.endswith('.csv'):
            return '.csv'
        elif url.endswith(('.xlsx', '.xls')):
            return '.xlsx'
        elif url.endswith('.json'):
            return '.json'
        
        # Try to detect from content
        try:
            # Try JSON first
            json.loads(content.decode('utf-8'))
            return '.json'
        except:
            pass
        
        try:
            # Try CSV
            pd.read_csv(StringIO(content.decode('utf-8')))
            return '.csv'
        except:
            pass
        
        # Default to CSV
        return '.csv'
    
    def _detect_schema(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Enhanced schema detection with HSBC-specific patterns"""
        schema_info = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'column_types': {},
            'column_info': {},
            'hsbc_patterns': {},
            'data_quality': {}
        }
        
        for col in df.columns:
            col_lower = col.lower()
            
            # Detect column type
            col_type = self._detect_column_type(df[col])
            schema_info['column_types'][col] = col_type
            
            # Check for HSBC patterns
            hsbc_pattern = self._detect_hsbc_pattern(col_lower)
            if hsbc_pattern:
                schema_info['hsbc_patterns'][col] = hsbc_pattern
            
            # Column info
            schema_info['column_info'][col] = {
                'type': col_type,
                'unique_values': df[col].nunique(),
                'null_count': df[col].isnull().sum(),
                'null_percentage': (df[col].isnull().sum() / len(df)) * 100,
                'sample_values': df[col].dropna().head(5).tolist()
            }
        
        # Data quality assessment
        schema_info['data_quality'] = self._assess_data_quality(df)
        
        return schema_info
    
    def _detect_column_type(self, series: pd.Series) -> str:
        """Enhanced column type detection"""
        clean_series = series.dropna()
        
        if len(clean_series) == 0:
            return "unknown"
        
        # Check for datetime
        try:
            pd.to_datetime(clean_series.head(100))
            return "datetime"
        except:
            pass
        
        # Check for numeric
        try:
            pd.to_numeric(clean_series.head(100))
            return "numeric"
        except:
            pass
        
        # Check for boolean
        if clean_series.dtype == 'bool':
            return "boolean"
        
        # Check for categorical (low cardinality)
        if clean_series.nunique() <= 50:
            return "categorical"
        
        return "string"
    
    def _detect_hsbc_pattern(self, column_name: str) -> Optional[str]:
        """Detect HSBC-specific column patterns"""
        for pattern_type, pattern_info in self.hsbc_normalization_rules.items():
            for pattern in pattern_info['patterns']:
                if pattern in column_name:
                    return pattern_type
        return None
    
    def _assess_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Assess data quality"""
        quality_issues = {
            'null_columns': [],
            'duplicate_rows': df.duplicated().sum(),
            'inconsistent_types': [],
            'outliers': []
        }
        
        for col in df.columns:
            null_percentage = (df[col].isnull().sum() / len(df)) * 100
            if null_percentage > 50:
                quality_issues['null_columns'].append({
                    'column': col,
                    'null_percentage': round(null_percentage, 2)
                })
        
        return quality_issues
    
    def _apply_hsbc_normalization(self, df: pd.DataFrame) -> tuple[pd.DataFrame, List[str]]:
        """Apply HSBC-specific normalization rules"""
        normalized_df = df.copy()
        normalization_log = []
        
        # Apply date normalization
        date_columns = [col for col in df.columns 
                       if self._detect_hsbc_pattern(col.lower()) == 'date_columns']
        
        for col in date_columns:
            try:
                normalized_df[col] = pd.to_datetime(df[col])
                normalized_df[col] = normalized_df[col].dt.strftime('%Y-%m-%d')
                normalization_log.append(f"Normalized date column: {col} -> YYYY-MM-DD format")
            except Exception as e:
                normalization_log.append(f"Failed to normalize date column {col}: {str(e)}")
        
        # Apply amount normalization
        amount_columns = [col for col in df.columns 
                         if self._detect_hsbc_pattern(col.lower()) == 'amount_columns']
        
        for col in amount_columns:
            try:
                normalized_df[col] = self._normalize_amount_column(df[col])
                normalization_log.append(f"Normalized amount column: {col} -> float format")
            except Exception as e:
                normalization_log.append(f"Failed to normalize amount column {col}: {str(e)}")
        
        # Apply type normalization
        type_columns = [col for col in df.columns 
                       if self._detect_hsbc_pattern(col.lower()) == 'type_columns']
        
        for col in type_columns:
            try:
                normalized_df[col] = self._normalize_type_column(df[col])
                normalization_log.append(f"Normalized type column: {col} -> standardized values")
            except Exception as e:
                normalization_log.append(f"Failed to normalize type column {col}: {str(e)}")
        
        # Standardize column names
        column_mapping = {}
        for col in normalized_df.columns:
            new_name = self._standardize_column_name(col)
            if new_name != col:
                column_mapping[col] = new_name
        
        if column_mapping:
            normalized_df = normalized_df.rename(columns=column_mapping)
            normalization_log.append(f"Standardized column names: {column_mapping}")
        
        return normalized_df, normalization_log
    
    def _normalize_amount_column(self, series: pd.Series) -> pd.Series:
        """Normalize amount columns by removing currency symbols and commas"""
        def clean_amount(value):
            if pd.isna(value):
                return value
            
            value_str = str(value)
            
            # Remove currency symbols
            for symbol in self.hsbc_normalization_rules['amount_columns']['currency_symbols']:
                value_str = value_str.replace(symbol, '')
            
            # Remove commas
            value_str = value_str.replace(',', '')
            
            # Remove extra whitespace
            value_str = value_str.strip()
            
            try:
                return float(value_str)
            except:
                return value
        
        return series.apply(clean_amount)
    
    def _normalize_type_column(self, series: pd.Series) -> pd.Series:
        """Normalize type columns using predefined mappings"""
        mappings = self.hsbc_normalization_rules['type_columns']['mappings']
        
        def map_type(value):
            if pd.isna(value):
                return value
            
            value_str = str(value).strip()
            return mappings.get(value_str, value_str)
        
        return series.apply(map_type)
    
    def _standardize_column_name(self, column_name: str) -> str:
        """Standardize column names to snake_case"""
        # Convert to snake_case
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', column_name)
        s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
        return s2.lower().replace(' ', '_').replace('-', '_')
    
    def create_normalization_rules(self, user_rules: Dict[str, Any]) -> Dict[str, Any]:
        """Create custom normalization rules from user input"""
        rules = {
            'column_mappings': user_rules.get('column_mappings', {}),
            'type_conversions': user_rules.get('type_conversions', {}),
            'value_mappings': user_rules.get('value_mappings', {}),
            'date_formats': user_rules.get('date_formats', {}),
            'currency_columns': user_rules.get('currency_columns', [])
        }
        
        return rules
    
    def apply_custom_normalization(self, df: pd.DataFrame, rules: Dict[str, Any]) -> tuple[pd.DataFrame, List[str]]:
        """Apply custom normalization rules"""
        normalized_df = df.copy()
        normalization_log = []
        
        # Apply column mappings
        if rules.get('column_mappings'):
            normalized_df = normalized_df.rename(columns=rules['column_mappings'])
            normalization_log.append(f"Applied column mappings: {rules['column_mappings']}")
        
        # Apply type conversions
        for col, target_type in rules.get('type_conversions', {}).items():
            if col in normalized_df.columns:
                try:
                    if target_type == 'numeric':
                        normalized_df[col] = pd.to_numeric(normalized_df[col], errors='coerce')
                    elif target_type == 'datetime':
                        normalized_df[col] = pd.to_datetime(normalized_df[col], errors='coerce')
                    elif target_type == 'string':
                        normalized_df[col] = normalized_df[col].astype(str)
                    
                    normalization_log.append(f"Converted {col} to {target_type}")
                except Exception as e:
                    normalization_log.append(f"Failed to convert {col} to {target_type}: {str(e)}")
        
        # Apply value mappings
        for col, mappings in rules.get('value_mappings', {}).items():
            if col in normalized_df.columns:
                try:
                    normalized_df[col] = normalized_df[col].map(mappings).fillna(normalized_df[col])
                    normalization_log.append(f"Applied value mappings to {col}")
                except Exception as e:
                    normalization_log.append(f"Failed to apply value mappings to {col}: {str(e)}")
        
        return normalized_df, normalization_log 