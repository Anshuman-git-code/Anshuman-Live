import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.figure_factory as ff
from typing import Dict, List, Any, Optional
import streamlit as st

class VisualizationManager:
    """Create and manage interactive visualizations."""
    
    def __init__(self):
        self.color_palette = px.colors.qualitative.Set3
        self.theme = {
            'background_color': 'white',
            'grid_color': '#f0f0f0',
            'text_color': '#333333'
        }
    
    def create_auto_visualizations(self, df: pd.DataFrame) -> Dict[str, go.Figure]:
        """Automatically create the most relevant visualizations for the data."""
        try:
            visualizations = {}
            
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
            datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
            
            # 1. Distribution of numeric columns
            if numeric_cols:
                fig = self._create_numeric_distributions(df, numeric_cols[:4])
                if fig:
                    visualizations["Numeric Distributions"] = fig
            
            # 2. Correlation heatmap
            if len(numeric_cols) >= 2:
                fig = self.create_correlation_heatmap(df[numeric_cols])
                if fig:
                    visualizations["Correlation Heatmap"] = fig
            
            # 3. Categorical analysis
            if categorical_cols:
                fig = self._create_categorical_analysis(df, categorical_cols[:3])
                if fig:
                    visualizations["Categorical Analysis"] = fig
            
            # 4. Time series analysis
            if datetime_cols and numeric_cols:
                fig = self._create_time_series_analysis(df, datetime_cols[0], numeric_cols[:2])
                if fig:
                    visualizations["Time Series Analysis"] = fig
            
            # 5. Top N analysis
            if categorical_cols and numeric_cols:
                fig = self._create_top_n_analysis(df, categorical_cols[0], numeric_cols[0])
                if fig:
                    visualizations["Top Categories Analysis"] = fig
            
            return visualizations
            
        except Exception as e:
            st.error(f"Error creating automatic visualizations: {str(e)}")
            return {}
    
    def create_line_chart(self, df: pd.DataFrame, x_col: str, y_col: str, color_col: Optional[str] = None) -> go.Figure:
        """Create an interactive line chart."""
        try:
            fig = px.line(
                df, 
                x=x_col, 
                y=y_col, 
                color=color_col,
                title=f"{y_col} over {x_col}",
                color_discrete_sequence=self.color_palette
            )
            
            fig.update_layout(
                xaxis_title=x_col,
                yaxis_title=y_col,
                hovermode='x unified',
                template='plotly_white'
            )
            
            return fig
            
        except Exception as e:
            raise Exception(f"Error creating line chart: {str(e)}")
    
    def create_bar_chart(self, df: pd.DataFrame, x_col: str, y_col: str) -> go.Figure:
        """Create an interactive bar chart."""
        try:
            # Aggregate data if needed
            if df[x_col].dtype in ['object', 'category']:
                agg_df = df.groupby(x_col)[y_col].sum().reset_index()
            else:
                agg_df = df
            
            fig = px.bar(
                agg_df,
                x=x_col,
                y=y_col,
                title=f"{y_col} by {x_col}",
                color_discrete_sequence=self.color_palette
            )
            
            fig.update_layout(
                xaxis_title=x_col,
                yaxis_title=y_col,
                template='plotly_white'
            )
            
            return fig
            
        except Exception as e:
            raise Exception(f"Error creating bar chart: {str(e)}")
    
    def create_scatter_plot(self, df: pd.DataFrame, x_col: str, y_col: str, 
                           size_col: Optional[str] = None, color_col: Optional[str] = None) -> go.Figure:
        """Create an interactive scatter plot."""
        try:
            fig = px.scatter(
                df,
                x=x_col,
                y=y_col,
                size=size_col,
                color=color_col,
                title=f"{y_col} vs {x_col}",
                color_discrete_sequence=self.color_palette
            )
            
            fig.update_layout(
                xaxis_title=x_col,
                yaxis_title=y_col,
                template='plotly_white'
            )
            
            return fig
            
        except Exception as e:
            raise Exception(f"Error creating scatter plot: {str(e)}")
    
    def create_histogram(self, df: pd.DataFrame, col: str, bins: int = 30) -> go.Figure:
        """Create an interactive histogram."""
        try:
            fig = px.histogram(
                df,
                x=col,
                nbins=bins,
                title=f"Distribution of {col}",
                color_discrete_sequence=self.color_palette
            )
            
            fig.update_layout(
                xaxis_title=col,
                yaxis_title='Frequency',
                template='plotly_white'
            )
            
            return fig
            
        except Exception as e:
            raise Exception(f"Error creating histogram: {str(e)}")
    
    def create_correlation_heatmap(self, df: pd.DataFrame) -> go.Figure:
        """Create a correlation heatmap."""
        try:
            # Calculate correlation matrix
            corr_matrix = df.corr()
            
            # Create heatmap
            fig = px.imshow(
                corr_matrix,
                title="Correlation Heatmap",
                color_continuous_scale='RdBu',
                aspect='auto'
            )
            
            fig.update_layout(
                title="Correlation Matrix",
                template='plotly_white'
            )
            
            return fig
            
        except Exception as e:
            raise Exception(f"Error creating correlation heatmap: {str(e)}")
    
    def _create_numeric_distributions(self, df: pd.DataFrame, cols: List[str]) -> Optional[go.Figure]:
        """Create distribution plots for numeric columns."""
        try:
            if not cols:
                return None
            
            # Create subplots
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=cols[:4],
                specs=[[{"secondary_y": False}, {"secondary_y": False}],
                       [{"secondary_y": False}, {"secondary_y": False}]]
            )
            
            positions = [(1, 1), (1, 2), (2, 1), (2, 2)]
            
            for i, col in enumerate(cols[:4]):
                row, col_pos = positions[i]
                
                # Create histogram
                fig.add_trace(
                    go.Histogram(
                        x=df[col],
                        name=col,
                        nbinsx=30,
                        opacity=0.7
                    ),
                    row=row, col=col_pos
                )
            
            fig.update_layout(
                title="Distribution of Numeric Columns",
                template='plotly_white',
                showlegend=False
            )
            
            return fig
            
        except Exception as e:
            return None
    
    def _create_categorical_analysis(self, df: pd.DataFrame, cols: List[str]) -> Optional[go.Figure]:
        """Create analysis for categorical columns."""
        try:
            if not cols:
                return None
            
            # Create subplots
            fig = make_subplots(
                rows=len(cols), cols=1,
                subplot_titles=[f"Distribution of {col}" for col in cols],
                vertical_spacing=0.1
            )
            
            for i, col in enumerate(cols):
                # Get value counts
                value_counts = df[col].value_counts().head(10)
                
                fig.add_trace(
                    go.Bar(
                        x=value_counts.index,
                        y=value_counts.values,
                        name=col,
                        marker_color=self.color_palette[i % len(self.color_palette)]
                    ),
                    row=i+1, col=1
                )
            
            fig.update_layout(
                title="Categorical Variables Analysis",
                template='plotly_white',
                showlegend=False,
                height=300 * len(cols)
            )
            
            return fig
            
        except Exception as e:
            return None
    
    def _create_time_series_analysis(self, df: pd.DataFrame, date_col: str, value_cols: List[str]) -> Optional[go.Figure]:
        """Create time series analysis."""
        try:
            if not value_cols:
                return None
            
            # Sort by date
            df_sorted = df.sort_values(date_col)
            
            fig = go.Figure()
            
            for i, col in enumerate(value_cols):
                fig.add_trace(
                    go.Scatter(
                        x=df_sorted[date_col],
                        y=df_sorted[col],
                        mode='lines+markers',
                        name=col,
                        line=dict(color=self.color_palette[i % len(self.color_palette)])
                    )
                )
            
            fig.update_layout(
                title=f"Time Series Analysis: {', '.join(value_cols)}",
                xaxis_title=date_col,
                yaxis_title="Value",
                template='plotly_white',
                hovermode='x unified'
            )
            
            return fig
            
        except Exception as e:
            return None
    
    def _create_top_n_analysis(self, df: pd.DataFrame, category_col: str, value_col: str, n: int = 10) -> Optional[go.Figure]:
        """Create top N analysis."""
        try:
            # Aggregate data
            agg_df = df.groupby(category_col)[value_col].sum().reset_index()
            agg_df = agg_df.sort_values(value_col, ascending=False).head(n)
            
            fig = px.bar(
                agg_df,
                x=category_col,
                y=value_col,
                title=f"Top {n} {category_col} by {value_col}",
                color_discrete_sequence=self.color_palette
            )
            
            fig.update_layout(
                xaxis_title=category_col,
                yaxis_title=value_col,
                template='plotly_white'
            )
            
            return fig
            
        except Exception as e:
            return None
    
    def create_dashboard(self, df: pd.DataFrame) -> Dict[str, go.Figure]:
        """Create a comprehensive dashboard."""
        try:
            dashboard = {}
            
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
            
            # Key metrics overview
            if numeric_cols:
                dashboard['metrics'] = self._create_metrics_overview(df, numeric_cols)
            
            # Trend analysis
            if len(numeric_cols) >= 2:
                dashboard['trends'] = self._create_trend_analysis(df, numeric_cols[:3])
            
            # Category breakdown
            if categorical_cols and numeric_cols:
                dashboard['breakdown'] = self._create_category_breakdown(df, categorical_cols[0], numeric_cols[0])
            
            return dashboard
            
        except Exception as e:
            st.error(f"Error creating dashboard: {str(e)}")
            return {}
    
    def _create_metrics_overview(self, df: pd.DataFrame, cols: List[str]) -> go.Figure:
        """Create metrics overview chart."""
        try:
            # Calculate summary statistics
            metrics = []
            values = []
            
            for col in cols[:5]:  # Limit to first 5 columns
                total = df[col].sum()
                avg = df[col].mean()
                metrics.extend([f"{col} Total", f"{col} Average"])
                values.extend([total, avg])
            
            fig = go.Figure(data=[
                go.Bar(x=metrics, y=values, marker_color=self.color_palette[0])
            ])
            
            fig.update_layout(
                title="Key Metrics Overview",
                xaxis_title="Metrics",
                yaxis_title="Value",
                template='plotly_white'
            )
            
            return fig
            
        except Exception as e:
            return None
    
    def _create_trend_analysis(self, df: pd.DataFrame, cols: List[str]) -> go.Figure:
        """Create trend analysis chart."""
        try:
            fig = go.Figure()
            
            for i, col in enumerate(cols):
                # Create a simple trend line using index as x-axis
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df[col],
                        mode='lines',
                        name=col,
                        line=dict(color=self.color_palette[i % len(self.color_palette)])
                    )
                )
            
            fig.update_layout(
                title="Trend Analysis",
                xaxis_title="Index",
                yaxis_title="Value",
                template='plotly_white',
                hovermode='x unified'
            )
            
            return fig
            
        except Exception as e:
            return None
    
    def _create_category_breakdown(self, df: pd.DataFrame, category_col: str, value_col: str) -> go.Figure:
        """Create category breakdown chart."""
        try:
            # Aggregate data
            agg_df = df.groupby(category_col)[value_col].sum().reset_index()
            
            fig = px.pie(
                agg_df,
                values=value_col,
                names=category_col,
                title=f"{value_col} Breakdown by {category_col}",
                color_discrete_sequence=self.color_palette
            )
            
            fig.update_layout(template='plotly_white')
            
            return fig
            
        except Exception as e:
            return None
