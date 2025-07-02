import os
import json
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import plotly.express as px
import plotly.graph_objects as go
from openai import OpenAI

class AIAnalyzer:
    """AI-powered data analysis using OpenAI."""
    
    def __init__(self):
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o"
    
    def generate_insights(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate comprehensive AI insights from the data."""
        try:
            # Prepare data summary for AI analysis
            data_summary = self._prepare_data_summary(df)
            
            # Generate insights using AI
            prompt = self._create_insights_prompt(data_summary)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert data analyst specializing in product management metrics. "
                        "Analyze the provided data and generate actionable insights for product managers. "
                        "Focus on key trends, patterns, and recommendations that can drive product decisions. "
                        "Respond with JSON in the specified format."
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            insights = json.loads(response.choices[0].message.content)
            
            # Add calculated metrics
            insights['metrics'] = self._calculate_key_metrics(df)
            
            return insights
            
        except Exception as e:
            raise Exception(f"Error generating AI insights: {str(e)}")
    
    def process_natural_language_query(self, df: pd.DataFrame, query: str) -> Dict[str, Any]:
        """Process natural language queries about the data."""
        try:
            # Prepare data context
            data_context = self._prepare_data_context(df)
            
            # Create query processing prompt
            prompt = self._create_query_prompt(data_context, query)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a data analysis assistant. Process the user's natural language query "
                        "about their data and provide a comprehensive answer. If the query asks for specific data, "
                        "describe what data should be filtered or calculated. If visualization would be helpful, "
                        "suggest the appropriate chart type. Respond with JSON in the specified format."
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            query_result = json.loads(response.choices[0].message.content)
            
            # Execute any data operations suggested by AI
            if 'data_operation' in query_result:
                query_result['data'] = self._execute_data_operation(df, query_result['data_operation'])
            
            # Create visualization if suggested
            if 'visualization_type' in query_result:
                query_result['visualization'] = self._create_query_visualization(
                    df, query_result['visualization_type'], query_result.get('visualization_params', {})
                )
            
            return query_result
            
        except Exception as e:
            raise Exception(f"Error processing natural language query: {str(e)}")
    
    def _prepare_data_summary(self, df: pd.DataFrame) -> str:
        """Prepare a comprehensive data summary for AI analysis."""
        try:
            summary_parts = []
            
            # Basic info
            summary_parts.append(f"Dataset shape: {df.shape[0]} rows, {df.shape[1]} columns")
            
            # Column information
            summary_parts.append(f"Columns: {', '.join(df.columns.tolist())}")
            
            # Data types
            dtypes_info = df.dtypes.value_counts().to_dict()
            summary_parts.append(f"Data types: {dtypes_info}")
            
            # Missing values
            missing_info = df.isnull().sum()
            missing_info = missing_info[missing_info > 0]
            if len(missing_info) > 0:
                summary_parts.append(f"Missing values: {missing_info.to_dict()}")
            
            # Numeric columns statistics
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            if numeric_cols:
                stats = df[numeric_cols].describe()
                summary_parts.append(f"Numeric columns statistics:\n{stats.to_string()}")
            
            # Categorical columns info
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
            if categorical_cols:
                cat_info = []
                for col in categorical_cols[:5]:  # Limit to first 5 categorical columns
                    unique_count = df[col].nunique()
                    top_values = df[col].value_counts().head(3).to_dict()
                    cat_info.append(f"{col}: {unique_count} unique values, top values: {top_values}")
                summary_parts.append(f"Categorical columns info:\n" + "\n".join(cat_info))
            
            # Sample data
            summary_parts.append(f"Sample data:\n{df.head(3).to_string()}")
            
            return "\n\n".join(summary_parts)
            
        except Exception as e:
            return f"Error preparing data summary: {str(e)}"
    
    def _prepare_data_context(self, df: pd.DataFrame) -> str:
        """Prepare data context for natural language queries."""
        try:
            context_parts = []
            
            # Basic structure
            context_parts.append(f"Data shape: {df.shape[0]} rows, {df.shape[1]} columns")
            context_parts.append(f"Columns: {', '.join(df.columns.tolist())}")
            
            # Column types
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
            datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
            
            if numeric_cols:
                context_parts.append(f"Numeric columns: {', '.join(numeric_cols)}")
            if categorical_cols:
                context_parts.append(f"Categorical columns: {', '.join(categorical_cols)}")
            if datetime_cols:
                context_parts.append(f"Date columns: {', '.join(datetime_cols)}")
            
            # Sample data
            context_parts.append(f"Sample data:\n{df.head(2).to_string()}")
            
            return "\n".join(context_parts)
            
        except Exception as e:
            return f"Error preparing data context: {str(e)}"
    
    def _create_insights_prompt(self, data_summary: str) -> str:
        """Create prompt for generating insights."""
        return f"""
        Analyze the following dataset and provide comprehensive insights for product managers.
        
        Data Summary:
        {data_summary}
        
        Please provide insights in the following JSON format:
        {{
            "summary": "Brief overview of the dataset and what it represents",
            "key_findings": [
                "List of 3-5 key findings from the data",
                "Focus on patterns, trends, and anomalies",
                "Make findings actionable for product managers"
            ],
            "recommendations": [
                "List of 3-5 actionable recommendations",
                "Based on the findings, what should product managers do?",
                "Focus on product strategy and decision-making"
            ],
            "data_quality_notes": [
                "Any data quality issues or considerations",
                "Missing values, outliers, or data consistency issues"
            ]
        }}
        
        Focus on product management metrics like user engagement, conversion rates, feature adoption, 
        retention, and growth indicators where applicable.
        """
    
    def _create_query_prompt(self, data_context: str, query: str) -> str:
        """Create prompt for processing natural language queries."""
        return f"""
        Data Context:
        {data_context}
        
        User Query: {query}
        
        Please analyze the user's query and provide a response in the following JSON format:
        {{
            "answer": "Direct answer to the user's question",
            "data_operation": {{
                "type": "filter|aggregate|sort|calculate",
                "parameters": {{
                    "columns": ["column_names"],
                    "conditions": "filtering conditions if applicable",
                    "aggregation": "aggregation method if applicable",
                    "calculation": "calculation to perform if applicable"
                }}
            }},
            "visualization_type": "chart_type_if_helpful",
            "visualization_params": {{
                "x_column": "column_name",
                "y_column": "column_name",
                "color_column": "column_name_if_applicable"
            }},
            "additional_insights": "Any additional context or insights"
        }}
        
        If the query doesn't require data operations or visualization, omit those fields.
        Focus on providing accurate, helpful answers based on the available data.
        """
    
    def _calculate_key_metrics(self, df: pd.DataFrame) -> Dict[str, str]:
        """Calculate key metrics from the data."""
        try:
            metrics = {}
            
            # Basic metrics
            metrics["Total Records"] = f"{len(df):,}"
            metrics["Total Columns"] = str(len(df.columns))
            
            # Numeric metrics
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            if numeric_cols:
                # Find potential revenue/value columns
                value_cols = [col for col in numeric_cols if any(word in col.lower() 
                             for word in ['revenue', 'price', 'value', 'amount', 'total', 'cost'])]
                if value_cols:
                    total_value = df[value_cols[0]].sum()
                    metrics[f"Total {value_cols[0]}"] = f"${total_value:,.2f}" if total_value > 1000 else f"{total_value:.2f}"
                
                # Find potential count columns
                count_cols = [col for col in numeric_cols if any(word in col.lower() 
                             for word in ['count', 'quantity', 'users', 'customers', 'orders'])]
                if count_cols:
                    avg_count = df[count_cols[0]].mean()
                    metrics[f"Avg {count_cols[0]}"] = f"{avg_count:.1f}"
            
            # Date-based metrics
            datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
            if datetime_cols:
                date_col = datetime_cols[0]
                date_range = df[date_col].max() - df[date_col].min()
                metrics["Date Range"] = f"{date_range.days} days"
            
            return metrics
            
        except Exception as e:
            return {"Error": f"Could not calculate metrics: {str(e)}"}
    
    def _execute_data_operation(self, df: pd.DataFrame, operation: Dict[str, Any]) -> Optional[pd.DataFrame]:
        """Execute data operations based on AI suggestions."""
        try:
            op_type = operation.get('type')
            params = operation.get('parameters', {})
            
            if op_type == 'filter':
                # Simple filtering implementation
                result_df = df.copy()
                columns = params.get('columns', [])
                conditions = params.get('conditions', '')
                
                # This is a simplified implementation
                # In a production system, you'd want more robust query parsing
                return result_df.head(10)  # Return top 10 for display
            
            elif op_type == 'aggregate':
                columns = params.get('columns', [])
                agg_method = params.get('aggregation', 'sum')
                
                if columns and all(col in df.columns for col in columns):
                    if agg_method == 'sum':
                        return df[columns].sum().to_frame('Total').T
                    elif agg_method == 'mean':
                        return df[columns].mean().to_frame('Average').T
                    elif agg_method == 'count':
                        return df[columns].count().to_frame('Count').T
            
            elif op_type == 'sort':
                columns = params.get('columns', [])
                if columns and columns[0] in df.columns:
                    return df.sort_values(columns[0], ascending=False).head(10)
            
            return None
            
        except Exception as e:
            return None
    
    def _create_query_visualization(self, df: pd.DataFrame, viz_type: str, params: Dict[str, Any]) -> Optional[go.Figure]:
        """Create visualization based on AI suggestions."""
        try:
            x_col = params.get('x_column')
            y_col = params.get('y_column')
            color_col = params.get('color_column')
            
            if not x_col or not y_col or x_col not in df.columns or y_col not in df.columns:
                return None
            
            if viz_type == 'bar':
                fig = px.bar(df.head(20), x=x_col, y=y_col, color=color_col)
            elif viz_type == 'line':
                fig = px.line(df.head(50), x=x_col, y=y_col, color=color_col)
            elif viz_type == 'scatter':
                fig = px.scatter(df.head(100), x=x_col, y=y_col, color=color_col)
            elif viz_type == 'histogram':
                fig = px.histogram(df, x=x_col)
            else:
                return None
            
            fig.update_layout(
                title=f"{viz_type.title()} Chart: {y_col} by {x_col}",
                xaxis_title=x_col,
                yaxis_title=y_col
            )
            
            return fig
            
        except Exception as e:
            return None
