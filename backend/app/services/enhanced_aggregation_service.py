import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
import json
import re

class EnhancedAggregationService:
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
            "var": np.var,
            "first": lambda x: x.iloc[0] if len(x) > 0 else None,
            "last": lambda x: x.iloc[-1] if len(x) > 0 else None,
            "unique_count": lambda x: x.nunique()
        }
        
        # HSBC-specific aggregation patterns
        self.hsbc_patterns = {
            'transaction_summary': {
                'group_by': ['account', 'transaction_type', 'date'],
                'aggregations': {
                    'amount': ['sum', 'count', 'mean'],
                    'transaction_type': ['count']
                }
            },
            'customer_summary': {
                'group_by': ['customer_id', 'month'],
                'aggregations': {
                    'amount': ['sum', 'count'],
                    'transaction_type': ['unique_count']
                }
            },
            'regional_summary': {
                'group_by': ['region', 'quarter'],
                'aggregations': {
                    'amount': ['sum', 'mean'],
                    'transaction_count': ['sum']
                }
            }
        }
    
    async def aggregate_data(self, data: Union[pd.DataFrame, List[Dict]], config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhanced aggregation with error handling and data cleaning
        """
        try:
            # Convert data to DataFrame if needed
            if isinstance(data, list):
                df = pd.DataFrame(data)
            else:
                df = data.copy()
            
            # Clean and prepare data
            df = await self._clean_data(df, config.get('cleaning_rules', {}))
            
            # Validate aggregation config
            validation_result = self._validate_aggregation_config(config)
            if not validation_result['valid']:
                return {
                    'error': True,
                    'message': 'Invalid aggregation configuration',
                    'details': validation_result['errors']
                }
            
            # Perform aggregation
            aggregation_type = config.get('type', 'group_by')
            
            if aggregation_type == 'group_by':
                result = await self._group_by_aggregation(df, config)
            elif aggregation_type == 'time_series':
                result = await self._time_series_aggregation(df, config)
            elif aggregation_type == 'pivot':
                result = await self._pivot_aggregation(df, config)
            elif aggregation_type == 'summary_stats':
                result = await self._summary_stats_aggregation(df, config)
            elif aggregation_type == 'hsbc_pattern':
                result = await self._hsbc_pattern_aggregation(df, config)
            else:
                return {
                    'error': True,
                    'message': f'Unsupported aggregation type: {aggregation_type}'
                }
            
            # Add metadata
            result['metadata'] = {
                'aggregation_type': aggregation_type,
                'total_input_rows': len(df),
                'total_output_rows': len(result.get('result', [])),
                'processing_timestamp': datetime.now().isoformat(),
                'config_used': config
            }
            
            return result
            
        except Exception as e:
            return {
                'error': True,
                'message': f'Aggregation failed: {str(e)}',
                'error_id': f"AGG_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            }
    
    async def _clean_data(self, df: pd.DataFrame, cleaning_rules: Dict[str, Any]) -> pd.DataFrame:
        """Clean data based on rules"""
        cleaned_df = df.copy()
        
        # Handle missing values
        missing_strategy = cleaning_rules.get('missing_values', 'drop')
        if missing_strategy == 'drop':
            cleaned_df = cleaned_df.dropna()
        elif missing_strategy == 'fill_mean':
            numeric_columns = cleaned_df.select_dtypes(include=[np.number]).columns
            cleaned_df[numeric_columns] = cleaned_df[numeric_columns].fillna(cleaned_df[numeric_columns].mean())
        elif missing_strategy == 'fill_mode':
            for col in cleaned_df.columns:
                if cleaned_df[col].dtype == 'object':
                    mode_value = cleaned_df[col].mode()
                    if len(mode_value) > 0:
                        cleaned_df[col] = cleaned_df[col].fillna(mode_value[0])
        
        # Handle outliers
        outlier_strategy = cleaning_rules.get('outliers', 'keep')
        if outlier_strategy == 'remove':
            numeric_columns = cleaned_df.select_dtypes(include=[np.number]).columns
            for col in numeric_columns:
                Q1 = cleaned_df[col].quantile(0.25)
                Q3 = cleaned_df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                cleaned_df = cleaned_df[(cleaned_df[col] >= lower_bound) & (cleaned_df[col] <= upper_bound)]
        
        # Standardize date formats
        date_columns = cleaning_rules.get('date_columns', [])
        for col in date_columns:
            if col in cleaned_df.columns:
                try:
                    cleaned_df[col] = pd.to_datetime(cleaned_df[col], errors='coerce')
                except:
                    pass
        
        return cleaned_df
    
    def _validate_aggregation_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate aggregation configuration"""
        errors = []
        warnings = []
        
        aggregation_type = config.get('type')
        
        if aggregation_type == 'group_by':
            if not config.get('group_by'):
                errors.append("group_by is required for group_by aggregation")
            if not config.get('value_columns'):
                warnings.append("value_columns is recommended for group_by aggregation")
        
        elif aggregation_type == 'time_series':
            if not config.get('date_column'):
                errors.append("date_column is required for time_series aggregation")
            if not config.get('value_column'):
                errors.append("value_column is required for time_series aggregation")
        
        elif aggregation_type == 'pivot':
            if not config.get('index'):
                errors.append("index is required for pivot aggregation")
            if not config.get('values'):
                errors.append("values is required for pivot aggregation")
        
        # Check aggregation functions
        aggregations = config.get('aggregations', {})
        for col, agg_funcs in aggregations.items():
            if isinstance(agg_funcs, list):
                for agg_func in agg_funcs:
                    if agg_func not in self.supported_aggregations:
                        errors.append(f"Unsupported aggregation function '{agg_func}' for column '{col}'")
            else:
                if agg_funcs not in self.supported_aggregations:
                    errors.append(f"Unsupported aggregation function '{agg_funcs}' for column '{col}'")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    async def _group_by_aggregation(self, df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced group by aggregation with multiple functions"""
        group_by_columns = config.get('group_by', [])
        value_columns = config.get('value_columns', [])
        aggregations = config.get('aggregations', {})
        
        # Validate columns exist
        missing_columns = [col for col in group_by_columns + value_columns if col not in df.columns]
        if missing_columns:
            return {
                'error': True,
                'message': f"Columns not found: {missing_columns}"
            }
        
        # Perform group by
        grouped = df.groupby(group_by_columns)
        
        # Apply aggregations
        agg_dict = {}
        for col in value_columns:
            if col in aggregations:
                agg_funcs = aggregations[col]
                if isinstance(agg_funcs, list):
                    for func in agg_funcs:
                        if func in self.supported_aggregations:
                            agg_dict[f"{col}_{func}"] = self.supported_aggregations[func]
                else:
                    if agg_funcs in self.supported_aggregations:
                        agg_dict[col] = self.supported_aggregations[agg_funcs]
            else:
                # Default aggregation
                agg_dict[col] = 'sum'
        
        result_df = grouped.agg(agg_dict).reset_index()
        
        return {
            'type': 'group_by',
            'result': result_df.to_dict('records'),
            'columns': result_df.columns.tolist(),
            'total_rows': len(result_df),
            'group_by_columns': group_by_columns,
            'value_columns': value_columns,
            'aggregations': aggregations
        }
    
    async def _time_series_aggregation(self, df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced time series aggregation with multiple frequencies"""
        date_column = config.get('date_column')
        value_column = config.get('value_column')
        frequency = config.get('frequency', 'D')
        aggregation = config.get('aggregation', 'sum')
        additional_columns = config.get('additional_columns', [])
        
        if not date_column or not value_column:
            return {
                'error': True,
                'message': 'Date column and value column are required'
            }
        
        if date_column not in df.columns or value_column not in df.columns:
            return {
                'error': True,
                'message': f'Columns not found: {date_column}, {value_column}'
            }
        
        # Convert date column to datetime
        df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
        df = df.dropna(subset=[date_column])
        
        # Set date as index and resample
        df_time = df.set_index(date_column)
        
        # Resample by frequency
        resampled = df_time[value_column].resample(frequency)
        
        # Apply aggregation
        if aggregation in self.supported_aggregations:
            result_series = resampled.apply(self.supported_aggregations[aggregation])
        else:
            result_series = resampled.sum()
        
        # Convert to DataFrame
        result_df = result_series.reset_index()
        result_df.columns = [date_column, f"{value_column}_{aggregation}"]
        
        # Add additional aggregations if specified
        if additional_columns:
            for col in additional_columns:
                if col in df.columns:
                    col_resampled = df_time[col].resample(frequency)
                    col_result = col_resampled.apply(self.supported_aggregations.get(aggregation, np.sum))
                    result_df[f"{col}_{aggregation}"] = col_result.values
        
        return {
            'type': 'time_series',
            'result': result_df.to_dict('records'),
            'columns': result_df.columns.tolist(),
            'total_rows': len(result_df),
            'date_column': date_column,
            'value_column': value_column,
            'frequency': frequency,
            'aggregation': aggregation
        }
    
    async def _pivot_aggregation(self, df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced pivot table aggregation"""
        index_columns = config.get('index', [])
        columns = config.get('columns', [])
        values = config.get('values', [])
        aggfunc = config.get('aggfunc', 'sum')
        fill_value = config.get('fill_value', 0)
        
        if not index_columns or not values:
            return {
                'error': True,
                'message': 'Index and values are required for pivot'
            }
        
        # Validate columns exist
        all_columns = index_columns + (columns or []) + values
        missing_columns = [col for col in all_columns if col not in df.columns]
        if missing_columns:
            return {
                'error': True,
                'message': f'Columns not found: {missing_columns}'
            }
        
        # Perform pivot
        pivot_df = df.pivot_table(
            index=index_columns,
            columns=columns,
            values=values,
            aggfunc=aggfunc,
            fill_value=fill_value
        )
        
        # Reset index to make it a regular DataFrame
        result_df = pivot_df.reset_index()
        
        return {
            'type': 'pivot',
            'result': result_df.to_dict('records'),
            'columns': result_df.columns.tolist(),
            'total_rows': len(result_df),
            'index_columns': index_columns,
            'pivot_columns': columns,
            'value_columns': values,
            'aggregation': aggfunc
        }
    
    async def _summary_stats_aggregation(self, df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced summary statistics with financial metrics"""
        columns = config.get('columns', [])
        include_financial_metrics = config.get('include_financial_metrics', True)
        
        if not columns:
            # Use all numeric columns
            columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        # Validate columns exist
        missing_columns = [col for col in columns if col not in df.columns]
        if missing_columns:
            return {
                'error': True,
                'message': f'Columns not found: {missing_columns}'
            }
        
        # Calculate summary statistics
        summary_stats = {}
        for col in columns:
            if col in df.columns:
                series = df[col].dropna()
                if len(series) > 0:
                    stats = {
                        'count': len(series),
                        'mean': float(series.mean()),
                        'median': float(series.median()),
                        'std': float(series.std()),
                        'min': float(series.min()),
                        'max': float(series.max()),
                        'q25': float(series.quantile(0.25)),
                        'q75': float(series.quantile(0.75)),
                        'null_count': int(df[col].isnull().sum()),
                        'null_percentage': float((df[col].isnull().sum() / len(df)) * 100)
                    }
                    
                    # Add financial metrics if requested
                    if include_financial_metrics and series.dtype in ['float64', 'int64']:
                        stats.update({
                            'total': float(series.sum()),
                            'positive_sum': float(series[series > 0].sum()),
                            'negative_sum': float(series[series < 0].sum()),
                            'positive_count': int((series > 0).sum()),
                            'negative_count': int((series < 0).sum()),
                            'zero_count': int((series == 0).sum())
                        })
                    
                    summary_stats[col] = stats
        
        return {
            'type': 'summary_stats',
            'result': summary_stats,
            'columns': list(summary_stats.keys()),
            'total_columns': len(summary_stats)
        }
    
    async def _hsbc_pattern_aggregation(self, df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """HSBC-specific pattern aggregation"""
        pattern_name = config.get('pattern', 'transaction_summary')
        
        if pattern_name not in self.hsbc_patterns:
            return {
                'error': True,
                'message': f'Unknown HSBC pattern: {pattern_name}'
            }
        
        pattern = self.hsbc_patterns[pattern_name]
        
        # Use pattern configuration
        config.update({
            'type': 'group_by',
            'group_by': pattern['group_by'],
            'aggregations': pattern['aggregations']
        })
        
        return await self._group_by_aggregation(df, config)
    
    def get_available_aggregations(self) -> List[str]:
        """Get list of available aggregation functions"""
        return list(self.supported_aggregations.keys())
    
    def get_hsbc_patterns(self) -> Dict[str, Any]:
        """Get available HSBC aggregation patterns"""
        return self.hsbc_patterns
    
    def create_custom_aggregation(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create custom aggregation configuration"""
        return {
            'type': config.get('type', 'group_by'),
            'group_by': config.get('group_by', []),
            'value_columns': config.get('value_columns', []),
            'aggregations': config.get('aggregations', {}),
            'cleaning_rules': config.get('cleaning_rules', {}),
            'filters': config.get('filters', {}),
            'sort_by': config.get('sort_by', []),
            'limit': config.get('limit', None)
        } 