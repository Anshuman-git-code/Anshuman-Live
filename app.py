import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import io
import base64
from datetime import datetime, timedelta
import os

# Import utility modules
from utils.data_processor import DataProcessor
from utils.ai_analyzer import AIAnalyzer
from utils.visualization import VisualizationManager
from utils.export_handler import ExportHandler

# Page configuration
st.set_page_config(
    page_title="PM Data Analysis Tool",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = None
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Initialize utility classes
@st.cache_resource
def get_analyzers():
    data_processor = DataProcessor()
    ai_analyzer = AIAnalyzer()
    viz_manager = VisualizationManager()
    export_handler = ExportHandler()
    return data_processor, ai_analyzer, viz_manager, export_handler

data_processor, ai_analyzer, viz_manager, export_handler = get_analyzers()

def main():
    st.title("🚀 AI-Powered Product Manager Data Analysis Tool")
    st.markdown("Transform your data into actionable insights with AI-powered analysis and interactive visualizations.")
    
    # Sidebar for data upload and basic controls
    with st.sidebar:
        st.header("📁 Data Upload")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Upload your data file",
            type=['csv', 'xlsx', 'xls', 'json'],
            help="Supported formats: CSV, Excel, JSON"
        )
        
        if uploaded_file is not None:
            try:
                with st.spinner("Processing your data..."):
                    df = data_processor.process_file(uploaded_file)
                    st.session_state.data = df
                    st.success(f"✅ Data loaded successfully! {len(df)} rows, {len(df.columns)} columns")
                    
                    # Show basic data info
                    st.subheader("📋 Data Overview")
                    st.write(f"**Shape:** {df.shape[0]} rows × {df.shape[1]} columns")
                    st.write(f"**Columns:** {', '.join(df.columns[:3])}{'...' if len(df.columns) > 3 else ''}")
                    
            except Exception as e:
                st.error(f"❌ Error processing file: {str(e)}")
                st.session_state.data = None
        
        # Data filtering options
        if st.session_state.data is not None:
            st.header("🔍 Data Filters")
            df = st.session_state.data
            
            # Column selection
            selected_columns = st.multiselect(
                "Select columns to analyze",
                df.columns.tolist(),
                default=df.columns.tolist()[:5] if len(df.columns) > 5 else df.columns.tolist()
            )
            
            if selected_columns:
                filtered_df = df[selected_columns]
                
                # Numeric filters
                numeric_cols = filtered_df.select_dtypes(include=[np.number]).columns.tolist()
                if numeric_cols:
                    st.subheader("📊 Numeric Filters")
                    for col in numeric_cols[:3]:  # Limit to first 3 numeric columns
                        if not filtered_df[col].isna().all():
                            min_val = float(filtered_df[col].min())
                            max_val = float(filtered_df[col].max())
                            if min_val != max_val:
                                range_val = st.slider(
                                    f"{col} range",
                                    min_val, max_val, (min_val, max_val),
                                    key=f"slider_{col}"
                                )
                                filtered_df = filtered_df[
                                    (filtered_df[col] >= range_val[0]) & 
                                    (filtered_df[col] <= range_val[1])
                                ]
                
                st.session_state.filtered_data = filtered_df
            else:
                st.session_state.filtered_data = df

    # Main content area
    if st.session_state.data is not None:
        df = st.session_state.get('filtered_data', st.session_state.data)
        
        # Create tabs for different functionalities
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Data Overview", 
            "🤖 AI Insights", 
            "📈 Visualizations", 
            "💬 Natural Language Query",
            "📤 Export & Share"
        ])
        
        with tab1:
            show_data_overview(df)
        
        with tab2:
            show_ai_insights(df)
        
        with tab3:
            show_visualizations(df)
        
        with tab4:
            show_natural_language_query(df)
        
        with tab5:
            show_export_options(df)
    
    else:
        # Landing page when no data is uploaded
        st.info("👈 Please upload a data file to get started")
        
        # Show sample use cases
        st.subheader("🎯 Perfect for Product Managers")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **📊 User Analytics**
            - User engagement metrics
            - Conversion funnel analysis
            - Retention cohort analysis
            """)
        
        with col2:
            st.markdown("""
            **💼 Product Metrics**
            - Feature adoption rates
            - A/B test results
            - Performance KPIs
            """)
        
        with col3:
            st.markdown("""
            **🔍 Market Research**
            - Survey data analysis
            - Customer feedback insights
            - Competitive analysis
            """)

def show_data_overview(df):
    st.header("📊 Data Overview")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Data Preview")
        st.dataframe(df.head(100), use_container_width=True)
    
    with col2:
        st.subheader("Data Statistics")
        st.write(f"**Total Rows:** {len(df):,}")
        st.write(f"**Total Columns:** {len(df.columns)}")
        
        # Data types
        st.subheader("Column Types")
        type_counts = df.dtypes.value_counts()
        for dtype, count in type_counts.items():
            st.write(f"**{dtype}:** {count} columns")
        
        # Missing values
        st.subheader("Missing Values")
        missing_data = df.isnull().sum()
        missing_data = missing_data[missing_data > 0]
        if len(missing_data) > 0:
            for col, count in missing_data.items():
                percentage = (count / len(df)) * 100
                st.write(f"**{col}:** {count} ({percentage:.1f}%)")
        else:
            st.write("✅ No missing values found")
    
    # Statistical summary
    st.subheader("Statistical Summary")
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if numeric_cols:
        st.dataframe(df[numeric_cols].describe(), use_container_width=True)
    else:
        st.info("No numeric columns found for statistical summary")

def show_ai_insights(df):
    st.header("🤖 AI-Powered Insights")
    
    if st.button("🔍 Generate AI Insights", type="primary"):
        with st.spinner("Analyzing your data with AI..."):
            try:
                insights = ai_analyzer.generate_insights(df)
                st.session_state.analysis_results = insights
            except Exception as e:
                st.error(f"❌ Error generating insights: {str(e)}")
                return
    
    if st.session_state.analysis_results:
        insights = st.session_state.analysis_results
        
        # Display insights in organized sections
        if 'summary' in insights:
            st.subheader("📋 Data Summary")
            st.write(insights['summary'])
        
        if 'key_findings' in insights:
            st.subheader("🔍 Key Findings")
            for i, finding in enumerate(insights['key_findings'], 1):
                st.write(f"**{i}.** {finding}")
        
        if 'recommendations' in insights:
            st.subheader("💡 Recommendations")
            for i, rec in enumerate(insights['recommendations'], 1):
                st.write(f"**{i}.** {rec}")
        
        if 'metrics' in insights:
            st.subheader("📊 Key Metrics")
            metric_cols = st.columns(len(insights['metrics']))
            for i, (metric, value) in enumerate(insights['metrics'].items()):
                with metric_cols[i]:
                    st.metric(metric, value)

def show_visualizations(df):
    st.header("📈 Interactive Visualizations")
    
    # Visualization type selection
    viz_type = st.selectbox(
        "Select visualization type",
        ["Automatic", "Line Chart", "Bar Chart", "Scatter Plot", "Histogram", "Box Plot", "Correlation Heatmap", "Distribution Plot"]
    )
    
    if viz_type == "Automatic":
        # Let AI suggest the best visualizations
        if st.button("🎨 Generate Automatic Visualizations"):
            with st.spinner("Creating visualizations..."):
                try:
                    figs = viz_manager.create_auto_visualizations(df)
                    for title, fig in figs.items():
                        st.subheader(title)
                        st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.error(f"❌ Error creating visualizations: {str(e)}")
    
    else:
        # Manual visualization creation
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        if viz_type == "Line Chart":
            if len(numeric_cols) >= 2:
                x_col = st.selectbox("X-axis", numeric_cols + categorical_cols)
                y_col = st.selectbox("Y-axis", numeric_cols)
                color_col = st.selectbox("Color by (optional)", [None] + categorical_cols)
                
                if st.button("Create Line Chart"):
                    fig = viz_manager.create_line_chart(df, x_col, y_col, color_col)
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Need at least 2 numeric columns for line chart")
        
        elif viz_type == "Bar Chart":
            if categorical_cols and numeric_cols:
                x_col = st.selectbox("X-axis (categorical)", categorical_cols)
                y_col = st.selectbox("Y-axis (numeric)", numeric_cols)
                
                if st.button("Create Bar Chart"):
                    fig = viz_manager.create_bar_chart(df, x_col, y_col)
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Need at least 1 categorical and 1 numeric column for bar chart")
        
        elif viz_type == "Scatter Plot":
            if len(numeric_cols) >= 2:
                x_col = st.selectbox("X-axis", numeric_cols)
                y_col = st.selectbox("Y-axis", [col for col in numeric_cols if col != x_col])
                size_col = st.selectbox("Size by (optional)", [None] + numeric_cols)
                color_col = st.selectbox("Color by (optional)", [None] + categorical_cols)
                
                if st.button("Create Scatter Plot"):
                    fig = viz_manager.create_scatter_plot(df, x_col, y_col, size_col, color_col)
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Need at least 2 numeric columns for scatter plot")
        
        elif viz_type == "Histogram":
            if numeric_cols:
                col = st.selectbox("Column", numeric_cols)
                bins = st.slider("Number of bins", 10, 100, 30)
                
                if st.button("Create Histogram"):
                    fig = viz_manager.create_histogram(df, col, bins)
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Need at least 1 numeric column for histogram")
        
        elif viz_type == "Correlation Heatmap":
            if len(numeric_cols) >= 2:
                if st.button("Create Correlation Heatmap"):
                    fig = viz_manager.create_correlation_heatmap(df[numeric_cols])
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Need at least 2 numeric columns for correlation heatmap")

def show_natural_language_query(df):
    st.header("💬 Natural Language Query")
    st.markdown("Ask questions about your data in plain English!")
    
    # Chat interface
    query = st.text_input("Ask a question about your data:", placeholder="e.g., What are the top 5 products by revenue?")
    
    if st.button("🔍 Ask AI") and query:
        with st.spinner("Processing your question..."):
            try:
                response = ai_analyzer.process_natural_language_query(df, query)
                
                # Add to chat history
                st.session_state.chat_history.append({
                    'query': query,
                    'response': response,
                    'timestamp': datetime.now()
                })
                
                # Display response
                st.subheader("🤖 AI Response")
                st.write(response['answer'])
                
                # Show visualization if generated
                if 'visualization' in response and response['visualization']:
                    st.subheader("📊 Generated Visualization")
                    st.plotly_chart(response['visualization'], use_container_width=True)
                
                # Show data if relevant
                if 'data' in response and response['data'] is not None:
                    st.subheader("📋 Relevant Data")
                    st.dataframe(response['data'], use_container_width=True)
                
            except Exception as e:
                st.error(f"❌ Error processing query: {str(e)}")
    
    # Show chat history
    if st.session_state.chat_history:
        st.subheader("💬 Chat History")
        for i, chat in enumerate(reversed(st.session_state.chat_history[-5:])):  # Show last 5
            with st.expander(f"Q: {chat['query'][:50]}... ({chat['timestamp'].strftime('%H:%M')})"):
                st.write(f"**Question:** {chat['query']}")
                st.write(f"**Answer:** {chat['response']['answer']}")

def show_export_options(df):
    st.header("📤 Export & Share")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Export Data")
        
        # Export formats
        export_format = st.selectbox("Select format", ["CSV", "Excel", "JSON"])
        
        if st.button("📥 Download Data"):
            try:
                file_data = export_handler.export_data(df, export_format.lower())
                
                if export_format == "CSV":
                    st.download_button(
                        label="Download CSV",
                        data=file_data,
                        file_name=f"data_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                elif export_format == "Excel":
                    st.download_button(
                        label="Download Excel",
                        data=file_data,
                        file_name=f"data_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                elif export_format == "JSON":
                    st.download_button(
                        label="Download JSON",
                        data=file_data,
                        file_name=f"data_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
            except Exception as e:
                st.error(f"❌ Error exporting data: {str(e)}")
    
    with col2:
        st.subheader("📈 Export Insights")
        
        if st.session_state.analysis_results:
            if st.button("📄 Download Analysis Report"):
                try:
                    report = export_handler.generate_analysis_report(
                        df, 
                        st.session_state.analysis_results
                    )
                    
                    st.download_button(
                        label="Download Report",
                        data=report,
                        file_name=f"analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                        mime="text/markdown"
                    )
                except Exception as e:
                    st.error(f"❌ Error generating report: {str(e)}")
        else:
            st.info("Generate AI insights first to export analysis report")
    
    # Sharing options
    st.subheader("🔗 Share Analysis")
    st.info("💡 Tip: Share the URL of this app with your team to collaborate on data analysis!")
    
    # Generate shareable link (placeholder for actual implementation)
    if st.button("🔗 Generate Shareable Link"):
        st.success("🎉 Shareable link generated! Copy the current URL to share this analysis.")
        st.code(st.query_params.to_dict())

if __name__ == "__main__":
    main()
