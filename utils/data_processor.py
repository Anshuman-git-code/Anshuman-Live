import pandas as pd
import numpy as np
import json
import io
from typing import Union, Dict, Any
import streamlit as st

class DataProcessor:
    """Handle data loading, processing, and basic transformations."""
    
    def __init__(self):
        self.supported_formats = ['csv', 'xlsx', 'xls', 'json']
    
    def process_file(self, uploaded_file) -> pd.DataFrame:
        """Process uploaded file and return DataFrame."""
        try:
            file_extension = uploaded_file.name.split('.')[-1].lower()
            
            if file_extension not in self.supported_formats:
                raise ValueError(f"Unsupported file format: {file_extension}")
            
            if file_extension == 'csv':
                return self._process_csv(uploaded_file)
            elif file_extension in ['xlsx', 'xls']:
                return self._process_excel(uploaded_file)
            elif file_extension == 'json':
                return self._process_json(uploaded_file)
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
                
        except Exception as e:
            raise Exception(f"Error processing file: {str(e)}")
    
    def _process_csv(self, uploaded_file) -> pd.DataFrame:
        """Process CSV file."""
        try:
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            
            for encoding in encodings:
                try:
                    uploaded_file.seek(0)
                    df = pd.read_csv(uploaded_file, encoding=encoding)
                    return self._clean_dataframe(df)
                except UnicodeDecodeError:
                    continue
            
            # If all encodings fail, try with error handling
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, encoding='utf-8', errors='ignore')
            return self._clean_dataframe(df)
            
        except Exception as e:
            raise Exception(f"Error reading CSV file: {str(e)}")
    
    def _process_excel(self, uploaded_file) -> pd.DataFrame:
        """Process Excel file."""
        try:
            # Read Excel file
            df = pd.read_excel(uploaded_file, engine='openpyxl')
            return self._clean_dataframe(df)
            
        except Exception as e:
            raise Exception(f"Error reading Excel file: {str(e)}")
    
    def _process_json(self, uploaded_file) -> pd.DataFrame:
        """Process JSON file."""
        try:
            # Read JSON file
            content = uploaded_file.read()
            if isinstance(content, bytes):
                content = content.decode('utf-8')
            
            data = json.loads(content)
            
            # Handle different JSON structures
            if isinstance(data, list):
                df = pd.json_normalize(data)
            elif isinstance(data, dict):
                if len(data) == 1 and isinstance(list(data.values())[0], list):
                    # Handle {"data": [...]} structure
                    key = list(data.keys())[0]
                    df = pd.json_normalize(data[key])
                else:
                    # Handle single record or nested structure
                    df = pd.json_normalize([data])
            else:
                raise ValueError("JSON structure not supported")
            
            return self._clean_dataframe(df)
            
        except Exception as e:
            raise Exception(f"Error reading JSON file: {str(e)}")
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize DataFrame."""
        try:
            # Remove completely empty rows and columns
            df = df.dropna(how='all').dropna(axis=1, how='all')
            
            # Clean column names
            df.columns = df.columns.astype(str)
            df.columns = [col.strip() for col in df.columns]
            
            # Convert data types
            df = self._optimize_dtypes(df)
            
            # Handle dates
            df = self._parse_dates(df)
            
            return df
            
        except Exception as e:
            raise Exception(f"Error cleaning DataFrame: {str(e)}")
    
    def _optimize_dtypes(self, df: pd.DataFrame) -> pd.DataFrame:
        """Optimize DataFrame data types."""
        try:
            for col in df.columns:
                # Skip if column is already numeric
                if df[col].dtype in ['int64', 'float64']:
                    continue
                
                # Try to convert to numeric
                try:
                    # Remove common non-numeric characters
                    cleaned_col = df[col].astype(str).str.replace(r'[$,]', '', regex=True)
                    numeric_col = pd.to_numeric(cleaned_col, errors='coerce')
                    
                    # If more than 50% of values are numeric, convert the column
                    if numeric_col.notna().sum() / len(df) > 0.5:
                        df[col] = numeric_col
                except:
                    pass
            
            return df
            
        except Exception as e:
            # If optimization fails, return original DataFrame
            return df
    
    def _parse_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Parse potential date columns."""
        try:
            for col in df.columns:
                if df[col].dtype == 'object':
                    # Check if column name suggests it's a date
                    if any(word in col.lower() for word in ['date', 'time', 'created', 'updated', 'timestamp']):
                        try:
                            df[col] = pd.to_datetime(df[col], errors='coerce')
                        except:
                            pass
            
            return df
            
        except Exception as e:
            return df
    
    def get_data_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get comprehensive data summary."""
        try:
            summary = {
                'shape': df.shape,
                'columns': df.columns.tolist(),
                'dtypes': df.dtypes.to_dict(),
                'missing_values': df.isnull().sum().to_dict(),
                'memory_usage': df.memory_usage(deep=True).sum(),
                'numeric_columns': df.select_dtypes(include=[np.number]).columns.tolist(),
                'categorical_columns': df.select_dtypes(include=['object', 'category']).columns.tolist(),
                'datetime_columns': df.select_dtypes(include=['datetime64']).columns.tolist(),
            }
            
            # Add statistical summary for numeric columns
            if summary['numeric_columns']:
                summary['numeric_stats'] = df[summary['numeric_columns']].describe().to_dict()
            
            return summary
            
        except Exception as e:
            raise Exception(f"Error generating data summary: {str(e)}")
    
    def filter_data(self, df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
        """Apply filters to DataFrame."""
        try:
            filtered_df = df.copy()
            
            for column, filter_config in filters.items():
                if column not in df.columns:
                    continue
                
                filter_type = filter_config.get('type')
                
                if filter_type == 'range' and df[column].dtype in ['int64', 'float64']:
                    min_val = filter_config.get('min')
                    max_val = filter_config.get('max')
                    if min_val is not None and max_val is not None:
                        filtered_df = filtered_df[
                            (filtered_df[column] >= min_val) & 
                            (filtered_df[column] <= max_val)
                        ]
                
                elif filter_type == 'categorical':
                    values = filter_config.get('values', [])
                    if values:
                        filtered_df = filtered_df[filtered_df[column].isin(values)]
                
                elif filter_type == 'date_range':
                    start_date = filter_config.get('start_date')
                    end_date = filter_config.get('end_date')
                    if start_date and end_date:
                        filtered_df = filtered_df[
                            (filtered_df[column] >= start_date) & 
                            (filtered_df[column] <= end_date)
                        ]
            
            return filtered_df
            
        except Exception as e:
            raise Exception(f"Error filtering data: {str(e)}")
