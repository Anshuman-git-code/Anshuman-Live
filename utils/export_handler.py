import pandas as pd
import numpy as np
import json
import io
from datetime import datetime
from typing import Dict, Any, Optional
import streamlit as st

class ExportHandler:
    """Handle data export and report generation."""
    
    def __init__(self):
        self.export_formats = ['csv', 'xlsx', 'json']
    
    def export_data(self, df: pd.DataFrame, format: str) -> bytes:
        """Export DataFrame to specified format."""
        try:
            if format not in self.export_formats:
                raise ValueError(f"Unsupported export format: {format}")
            
            if format == 'csv':
                return self._export_to_csv(df)
            elif format == 'xlsx':
                return self._export_to_excel(df)
            elif format == 'json':
                return self._export_to_json(df)
            else:
                raise ValueError(f"Unsupported format: {format}")
                
        except Exception as e:
            raise Exception(f"Error exporting data: {str(e)}")
    
    def _export_to_csv(self, df: pd.DataFrame) -> bytes:
        """Export DataFrame to CSV."""
        try:
            output = io.StringIO()
            df.to_csv(output, index=False)
            return output.getvalue().encode('utf-8')
            
        except Exception as e:
            raise Exception(f"Error exporting to CSV: {str(e)}")
    
    def _export_to_excel(self, df: pd.DataFrame) -> bytes:
        """Export DataFrame to Excel."""
        try:
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Data', index=False)
                
                # Add a summary sheet
                summary_df = self._create_summary_sheet(df)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            return output.getvalue()
            
        except Exception as e:
            raise Exception(f"Error exporting to Excel: {str(e)}")
    
    def _export_to_json(self, df: pd.DataFrame) -> bytes:
        """Export DataFrame to JSON."""
        try:
            # Convert DataFrame to JSON
            json_data = df.to_dict(orient='records')
            
            # Create export package with metadata
            export_package = {
                'metadata': {
                    'export_date': datetime.now().isoformat(),
                    'rows': len(df),
                    'columns': len(df.columns),
                    'column_names': df.columns.tolist(),
                    'data_types': df.dtypes.astype(str).to_dict()
                },
                'data': json_data
            }
            
            return json.dumps(export_package, indent=2, default=str).encode('utf-8')
            
        except Exception as e:
            raise Exception(f"Error exporting to JSON: {str(e)}")
    
    def _create_summary_sheet(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create a summary sheet for Excel export."""
        try:
            summary_data = []
            
            # Basic info
            summary_data.append(['Metric', 'Value'])
            summary_data.append(['Total Rows', len(df)])
            summary_data.append(['Total Columns', len(df.columns)])
            summary_data.append(['Export Date', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
            summary_data.append(['', ''])  # Empty row
            
            # Column information
            summary_data.append(['Column Analysis', ''])
            summary_data.append(['Column Name', 'Data Type', 'Non-Null Count', 'Null Count', 'Null %'])
            
            for col in df.columns:
                non_null_count = df[col].count()
                null_count = df[col].isnull().sum()
                null_percentage = (null_count / len(df)) * 100
                
                summary_data.append([
                    col,
                    str(df[col].dtype),
                    non_null_count,
                    null_count,
                    f"{null_percentage:.1f}%"
                ])
            
            # Convert to DataFrame
            max_cols = max(len(row) for row in summary_data)
            for row in summary_data:
                while len(row) < max_cols:
                    row.append('')
            
            summary_df = pd.DataFrame(summary_data)
            
            return summary_df
            
        except Exception as e:
            # Return basic summary if detailed one fails
            return pd.DataFrame([
                ['Export Date', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
                ['Total Rows', len(df)],
                ['Total Columns', len(df.columns)]
            ])
    
    def generate_analysis_report(self, df: pd.DataFrame, analysis_results: Dict[str, Any]) -> str:
        """Generate a comprehensive analysis report in Markdown format."""
        try:
            report_lines = []
            
            # Header
            report_lines.append("# Data Analysis Report")
            report_lines.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report_lines.append("")
            
            # Data Overview
            report_lines.append("## Data Overview")
            report_lines.append(f"- **Total Rows:** {len(df):,}")
            report_lines.append(f"- **Total Columns:** {len(df.columns)}")
            report_lines.append(f"- **Columns:** {', '.join(df.columns.tolist())}")
            report_lines.append("")
            
            # Data Types
            report_lines.append("### Data Types")
            type_counts = df.dtypes.value_counts()
            for dtype, count in type_counts.items():
                report_lines.append(f"- **{dtype}:** {count} columns")
            report_lines.append("")
            
            # Missing Values
            missing_data = df.isnull().sum()
            missing_data = missing_data[missing_data > 0]
            if len(missing_data) > 0:
                report_lines.append("### Missing Values")
                for col, count in missing_data.items():
                    percentage = (count / len(df)) * 100
                    report_lines.append(f"- **{col}:** {count:,} ({percentage:.1f}%)")
                report_lines.append("")
            
            # AI Insights
            if analysis_results:
                report_lines.append("## AI-Generated Insights")
                
                if 'summary' in analysis_results:
                    report_lines.append("### Summary")
                    report_lines.append(analysis_results['summary'])
                    report_lines.append("")
                
                if 'key_findings' in analysis_results:
                    report_lines.append("### Key Findings")
                    for i, finding in enumerate(analysis_results['key_findings'], 1):
                        report_lines.append(f"{i}. {finding}")
                    report_lines.append("")
                
                if 'recommendations' in analysis_results:
                    report_lines.append("### Recommendations")
                    for i, rec in enumerate(analysis_results['recommendations'], 1):
                        report_lines.append(f"{i}. {rec}")
                    report_lines.append("")
                
                if 'metrics' in analysis_results:
                    report_lines.append("### Key Metrics")
                    for metric, value in analysis_results['metrics'].items():
                        report_lines.append(f"- **{metric}:** {value}")
                    report_lines.append("")
            
            # Statistical Summary
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            if numeric_cols:
                report_lines.append("## Statistical Summary")
                report_lines.append("### Numeric Columns")
                
                stats_df = df[numeric_cols].describe()
                report_lines.append("| Statistic | " + " | ".join(numeric_cols) + " |")
                report_lines.append("|" + "---|" * (len(numeric_cols) + 1))
                
                for stat in stats_df.index:
                    row = f"| {stat} |"
                    for col in numeric_cols:
                        value = stats_df.loc[stat, col]
                        if isinstance(value, float):
                            row += f" {value:.2f} |"
                        else:
                            row += f" {value} |"
                    report_lines.append(row)
                report_lines.append("")
            
            # Categorical Analysis
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
            if categorical_cols:
                report_lines.append("### Categorical Columns")
                for col in categorical_cols[:5]:  # Limit to first 5 categorical columns
                    unique_count = df[col].nunique()
                    top_values = df[col].value_counts().head(3)
                    
                    report_lines.append(f"**{col}:**")
                    report_lines.append(f"- Unique values: {unique_count}")
                    report_lines.append(f"- Top values:")
                    for value, count in top_values.items():
                        percentage = (count / len(df)) * 100
                        report_lines.append(f"  - {value}: {count:,} ({percentage:.1f}%)")
                    report_lines.append("")
            
            # Footer
            report_lines.append("---")
            report_lines.append("*This report was generated automatically by the AI-Powered Product Manager Data Analysis Tool.*")
            
            return "\n".join(report_lines)
            
        except Exception as e:
            raise Exception(f"Error generating analysis report: {str(e)}")
    
    def create_shareable_link(self, df: pd.DataFrame, analysis_results: Optional[Dict[str, Any]] = None) -> str:
        """Create a shareable link for the analysis (placeholder implementation)."""
        try:
            # In a real implementation, this would:
            # 1. Upload the data to a cloud storage
            # 2. Create a unique identifier
            # 3. Return a shareable URL
            
            # For now, return a placeholder
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            return f"https://your-app-domain.com/shared/{timestamp}"
            
        except Exception as e:
            raise Exception(f"Error creating shareable link: {str(e)}")
    
    def export_visualization(self, fig, format: str = 'html') -> bytes:
        """Export visualization to specified format."""
        try:
            if format == 'html':
                return fig.to_html().encode('utf-8')
            elif format == 'png':
                return fig.to_image(format='png')
            elif format == 'pdf':
                return fig.to_image(format='pdf')
            else:
                raise ValueError(f"Unsupported visualization export format: {format}")
                
        except Exception as e:
            raise Exception(f"Error exporting visualization: {str(e)}")
