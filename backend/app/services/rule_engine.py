import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import json
import re

class RuleEngine:
    def __init__(self):
        self.normalization_rules = {}
        self.aggregation_rules = {}
        self.flag_rules = {}
        self.validation_rules = {}
        
    def add_normalization_rule(self, rule_name: str, rule_config: Dict[str, Any]):
        """Add a normalization rule"""
        self.normalization_rules[rule_name] = {
            'type': 'normalization',
            'config': rule_config,
            'created_at': datetime.now().isoformat()
        }
        
    def add_aggregation_rule(self, rule_name: str, rule_config: Dict[str, Any]):
        """Add an aggregation rule"""
        self.aggregation_rules[rule_name] = {
            'type': 'aggregation',
            'config': rule_config,
            'created_at': datetime.now().isoformat()
        }
        
    def add_flag_rule(self, rule_name: str, rule_config: Dict[str, Any]):
        """Add a flag rule for anomaly detection"""
        self.flag_rules[rule_name] = {
            'type': 'flag',
            'config': rule_config,
            'created_at': datetime.now().isoformat()
        }
        
    def add_validation_rule(self, rule_name: str, rule_config: Dict[str, Any]):
        """Add a validation rule"""
        self.validation_rules[rule_name] = {
            'type': 'validation',
            'config': rule_config,
            'created_at': datetime.now().isoformat()
        }
        
    def apply_normalization_rules(self, df: pd.DataFrame, rule_names: List[str] = None) -> tuple[pd.DataFrame, List[str]]:
        """Apply normalization rules to dataframe"""
        if rule_names is None:
            rule_names = list(self.normalization_rules.keys())
            
        normalized_df = df.copy()
        applied_rules = []
        
        for rule_name in rule_names:
            if rule_name in self.normalization_rules:
                rule = self.normalization_rules[rule_name]
                config = rule['config']
                
                if config.get('type') == 'column_mapping':
                    normalized_df = self._apply_column_mapping(normalized_df, config)
                elif config.get('type') == 'data_type_conversion':
                    normalized_df = self._apply_data_type_conversion(normalized_df, config)
                elif config.get('type') == 'value_mapping':
                    normalized_df = self._apply_value_mapping(normalized_df, config)
                elif config.get('type') == 'date_format':
                    normalized_df = self._apply_date_format(normalized_df, config)
                elif config.get('type') == 'currency_cleanup':
                    normalized_df = self._apply_currency_cleanup(normalized_df, config)
                    
                applied_rules.append(rule_name)
                
        return normalized_df, applied_rules
        
    def apply_aggregation_rules(self, df: pd.DataFrame, rule_names: List[str] = None) -> Dict[str, Any]:
        """Apply aggregation rules to dataframe"""
        if rule_names is None:
            rule_names = list(self.aggregation_rules.keys())
            
        results = {}
        
        for rule_name in rule_names:
            if rule_name in self.aggregation_rules:
                rule = self.aggregation_rules[rule_name]
                config = rule['config']
                
                if config.get('type') == 'group_by':
                    results[rule_name] = self._apply_group_by_aggregation(df, config)
                elif config.get('type') == 'time_series':
                    results[rule_name] = self._apply_time_series_aggregation(df, config)
                elif config.get('type') == 'summary_stats':
                    results[rule_name] = self._apply_summary_stats(df, config)
                    
        return results
        
    def apply_flag_rules(self, df: pd.DataFrame, rule_names: List[str] = None) -> Dict[str, Any]:
        """Apply flag rules for anomaly detection"""
        if rule_names is None:
            rule_names = list(self.flag_rules.keys())
            
        flagged_data = {}
        
        for rule_name in rule_names:
            if rule_name in self.flag_rules:
                rule = self.flag_rules[rule_name]
                config = rule['config']
                
                if config.get('type') == 'threshold':
                    flagged_data[rule_name] = self._apply_threshold_flag(df, config)
                elif config.get('type') == 'outlier':
                    flagged_data[rule_name] = self._apply_outlier_flag(df, config)
                elif config.get('type') == 'pattern':
                    flagged_data[rule_name] = self._apply_pattern_flag(df, config)
                    
        return flagged_data
        
    def _apply_column_mapping(self, df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """Apply column mapping rules"""
        column_mapping = config.get('mapping', {})
        return df.rename(columns=column_mapping)
        
    def _apply_data_type_conversion(self, df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """Apply data type conversion rules"""
        conversions = config.get('conversions', {})
        
        for column, target_type in conversions.items():
            if column in df.columns:
                try:
                    if target_type == 'numeric':
                        df[column] = pd.to_numeric(df[column], errors='coerce')
                    elif target_type == 'datetime':
                        df[column] = pd.to_datetime(df[column], errors='coerce')
                    elif target_type == 'string':
                        df[column] = df[column].astype(str)
                    elif target_type == 'boolean':
                        df[column] = df[column].astype(bool)
                except Exception as e:
                    print(f"Error converting {column} to {target_type}: {e}")
                    
        return df
        
    def _apply_value_mapping(self, df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """Apply value mapping rules"""
        mappings = config.get('mappings', {})
        
        for column, value_mapping in mappings.items():
            if column in df.columns:
                df[column] = df[column].map(value_mapping).fillna(df[column])
                
        return df
        
    def _apply_date_format(self, df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """Apply date format rules"""
        date_columns = config.get('columns', [])
        output_format = config.get('output_format', '%Y-%m-%d')
        
        for column in date_columns:
            if column in df.columns:
                try:
                    df[column] = pd.to_datetime(df[column], errors='coerce')
                    df[column] = df[column].dt.strftime(output_format)
                except Exception as e:
                    print(f"Error formatting date column {column}: {e}")
                    
        return df
        
    def _apply_currency_cleanup(self, df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """Apply currency cleanup rules"""
        currency_columns = config.get('columns', [])
        currency_symbols = config.get('symbols', ['$', '£', '€', '₹', '¥'])
        
        for column in currency_columns:
            if column in df.columns:
                df[column] = df[column].astype(str).str.replace('|'.join(currency_symbols), '', regex=True)
                df[column] = df[column].str.replace(',', '', regex=True)
                df[column] = pd.to_numeric(df[column], errors='coerce')
                
        return df
        
    def _apply_group_by_aggregation(self, df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply group by aggregation rules"""
        group_by_columns = config.get('group_by', [])
        aggregations = config.get('aggregations', {})
        
        if not group_by_columns:
            return {'error': 'No group by columns specified'}
            
        grouped = df.groupby(group_by_columns)
        result = {}
        
        for column, agg_funcs in aggregations.items():
            if column in df.columns:
                if isinstance(agg_funcs, list):
                    for func in agg_funcs:
                        if func == 'sum':
                            result[f"{column}_sum"] = grouped[column].sum().to_dict()
                        elif func == 'mean':
                            result[f"{column}_mean"] = grouped[column].mean().to_dict()
                        elif func == 'count':
                            result[f"{column}_count"] = grouped[column].count().to_dict()
                        elif func == 'max':
                            result[f"{column}_max"] = grouped[column].max().to_dict()
                        elif func == 'min':
                            result[f"{column}_min"] = grouped[column].min().to_dict()
                else:
                    if agg_funcs == 'sum':
                        result[f"{column}_sum"] = grouped[column].sum().to_dict()
                    elif agg_funcs == 'mean':
                        result[f"{column}_mean"] = grouped[column].mean().to_dict()
                        
        return result
        
    def _apply_time_series_aggregation(self, df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply time series aggregation rules"""
        date_column = config.get('date_column')
        value_column = config.get('value_column')
        frequency = config.get('frequency', 'D')
        aggregation = config.get('aggregation', 'sum')
        
        if not date_column or not value_column:
            return {'error': 'Date column and value column required'}
            
        if date_column not in df.columns or value_column not in df.columns:
            return {'error': 'Specified columns not found'}
            
        try:
            df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
            df_time = df.set_index(date_column)
            
            if aggregation == 'sum':
                result = df_time[value_column].resample(frequency).sum()
            elif aggregation == 'mean':
                result = df_time[value_column].resample(frequency).mean()
            elif aggregation == 'count':
                result = df_time[value_column].resample(frequency).count()
                
            return {
                'time_series': result.to_dict(),
                'frequency': frequency,
                'aggregation': aggregation
            }
        except Exception as e:
            return {'error': f'Time series aggregation failed: {str(e)}'}
            
    def _apply_summary_stats(self, df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply summary statistics rules"""
        columns = config.get('columns', [])
        
        if not columns:
            columns = df.select_dtypes(include=[np.number]).columns.tolist()
            
        stats = {}
        
        for column in columns:
            if column in df.columns:
                series = df[column].dropna()
                if len(series) > 0:
                    stats[column] = {
                        'count': len(series),
                        'mean': float(series.mean()),
                        'median': float(series.median()),
                        'std': float(series.std()),
                        'min': float(series.min()),
                        'max': float(series.max()),
                        'q25': float(series.quantile(0.25)),
                        'q75': float(series.quantile(0.75))
                    }
                    
        return stats
        
    def _apply_threshold_flag(self, df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply threshold-based flagging"""
        column = config.get('column')
        threshold = config.get('threshold')
        operator = config.get('operator', '>')
        flag_name = config.get('flag_name', 'threshold_flag')
        
        if not column or threshold is None:
            return {'error': 'Column and threshold required'}
            
        if column not in df.columns:
            return {'error': 'Column not found'}
            
        if operator == '>':
            flagged = df[df[column] > threshold]
        elif operator == '<':
            flagged = df[df[column] < threshold]
        elif operator == '>=':
            flagged = df[df[column] >= threshold]
        elif operator == '<=':
            flagged = df[df[column] <= threshold]
        elif operator == '==':
            flagged = df[df[column] == threshold]
        else:
            return {'error': 'Invalid operator'}
            
        return {
            'flagged_count': len(flagged),
            'total_count': len(df),
            'flagged_percentage': (len(flagged) / len(df)) * 100,
            'flagged_data': flagged.to_dict('records')
        }
        
    def _apply_outlier_flag(self, df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply outlier detection flagging"""
        column = config.get('column')
        method = config.get('method', 'iqr')
        
        if not column or column not in df.columns:
            return {'error': 'Column not found'}
            
        series = df[column].dropna()
        
        if method == 'iqr':
            Q1 = series.quantile(0.25)
            Q3 = series.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)]
        elif method == 'zscore':
            z_scores = np.abs((series - series.mean()) / series.std())
            outliers = df[z_scores > 3]
        else:
            return {'error': 'Invalid outlier detection method'}
            
        return {
            'outlier_count': len(outliers),
            'total_count': len(df),
            'outlier_percentage': (len(outliers) / len(df)) * 100,
            'outlier_data': outliers.to_dict('records')
        }
        
    def _apply_pattern_flag(self, df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply pattern-based flagging"""
        column = config.get('column')
        pattern = config.get('pattern')
        pattern_type = config.get('pattern_type', 'regex')
        
        if not column or not pattern:
            return {'error': 'Column and pattern required'}
            
        if column not in df.columns:
            return {'error': 'Column not found'}
            
        if pattern_type == 'regex':
            flagged = df[df[column].astype(str).str.contains(pattern, regex=True, na=False)]
        elif pattern_type == 'exact':
            flagged = df[df[column] == pattern]
        elif pattern_type == 'contains':
            flagged = df[df[column].astype(str).str.contains(pattern, na=False)]
        else:
            return {'error': 'Invalid pattern type'}
            
        return {
            'pattern_count': len(flagged),
            'total_count': len(df),
            'pattern_percentage': (len(flagged) / len(df)) * 100,
            'pattern_data': flagged.to_dict('records')
        }
        
    def get_all_rules(self) -> Dict[str, Any]:
        """Get all rules"""
        return {
            'normalization': self.normalization_rules,
            'aggregation': self.aggregation_rules,
            'flag': self.flag_rules,
            'validation': self.validation_rules
        }
        
    def delete_rule(self, rule_type: str, rule_name: str) -> bool:
        """Delete a rule"""
        if rule_type == 'normalization' and rule_name in self.normalization_rules:
            del self.normalization_rules[rule_name]
            return True
        elif rule_type == 'aggregation' and rule_name in self.aggregation_rules:
            del self.aggregation_rules[rule_name]
            return True
        elif rule_type == 'flag' and rule_name in self.flag_rules:
            del self.flag_rules[rule_name]
            return True
        elif rule_type == 'validation' and rule_name in self.validation_rules:
            del self.validation_rules[rule_name]
            return True
        return False
        
    def export_rules(self) -> str:
        """Export rules to JSON"""
        return json.dumps(self.get_all_rules(), indent=2)
        
    def import_rules(self, rules_json: str):
        """Import rules from JSON"""
        rules = json.loads(rules_json)
        self.normalization_rules.update(rules.get('normalization', {}))
        self.aggregation_rules.update(rules.get('aggregation', {}))
        self.flag_rules.update(rules.get('flag', {}))
        self.validation_rules.update(rules.get('validation', {})) 