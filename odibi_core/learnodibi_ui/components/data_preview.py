"""
DataFrame Preview Component
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional, List


def data_preview(
    df: pd.DataFrame,
    title: str = "Data Preview",
    show_stats: bool = True,
    show_chart: bool = True,
    max_rows: int = 100,
    key: str = "data_preview"
):
    """
    Interactive DataFrame preview with statistics and visualizations
    
    Args:
        df: DataFrame to preview
        title: Preview title
        show_stats: Whether to show statistics
        show_chart: Whether to show charts
        max_rows: Maximum rows to display
        key: Unique key for the component
    """
    st.subheader(title)
    
    if df is None or df.empty:
        st.warning("⚠️ No data available")
        return
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Rows", f"{len(df):,}")
    with col2:
        st.metric("Columns", len(df.columns))
    with col3:
        memory_mb = df.memory_usage(deep=True).sum() / 1024**2
        st.metric("Memory", f"{memory_mb:.2f} MB")
    with col4:
        null_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100)
        st.metric("Nulls", f"{null_pct:.1f}%")
    
    # Tabs for different views
    tabs = st.tabs(["📊 Data", "📈 Statistics", "📉 Visualizations", "🔍 Schema"])
    
    with tabs[0]:
        _show_data_table(df, max_rows, key)
    
    with tabs[1]:
        if show_stats:
            _show_statistics(df, key)
    
    with tabs[2]:
        if show_chart:
            _show_visualizations(df, key)
    
    with tabs[3]:
        _show_schema(df, key)


def _show_data_table(df: pd.DataFrame, max_rows: int, key: str):
    """Display data table with filters"""
    st.markdown("##### Data Table")
    
    # Row limit selector
    n_rows = st.slider(
        "Rows to display",
        min_value=10,
        max_value=min(len(df), max_rows),
        value=min(50, len(df)),
        step=10,
        key=f"{key}_rows"
    )
    
    # Column selector
    selected_cols = st.multiselect(
        "Select columns",
        df.columns.tolist(),
        default=df.columns.tolist()[:5] if len(df.columns) > 5 else df.columns.tolist(),
        key=f"{key}_cols"
    )
    
    if selected_cols:
        st.dataframe(
            df[selected_cols].head(n_rows),
            use_container_width=True,
            height=400
        )
        
        # Download button
        csv = df[selected_cols].head(n_rows).to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name="data_preview.csv",
            mime="text/csv",
            key=f"{key}_download"
        )
    else:
        st.info("Select at least one column to display")


def _show_statistics(df: pd.DataFrame, key: str):
    """Display statistical summary"""
    st.markdown("##### Statistical Summary")
    
    # Numeric columns stats
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    if numeric_cols:
        st.markdown("**Numeric Columns:**")
        stats_df = df[numeric_cols].describe()
        st.dataframe(stats_df, use_container_width=True)
    
    # Categorical columns stats
    cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    if cat_cols:
        st.markdown("**Categorical Columns:**")
        for col in cat_cols[:5]:  # Limit to first 5
            with st.expander(f"📋 {col}"):
                value_counts = df[col].value_counts()
                st.write(f"Unique values: {df[col].nunique()}")
                st.write("Top 10 values:")
                st.dataframe(value_counts.head(10))
    
    # Missing data analysis
    st.markdown("**Missing Data:**")
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(2)
    missing_df = pd.DataFrame({
        'Column': missing.index,
        'Missing Count': missing.values,
        'Missing %': missing_pct.values
    })
    missing_df = missing_df[missing_df['Missing Count'] > 0]
    
    if not missing_df.empty:
        st.dataframe(missing_df, use_container_width=True, hide_index=True)
    else:
        st.success("✅ No missing data detected")


def _show_visualizations(df: pd.DataFrame, key: str):
    """Display data visualizations"""
    st.markdown("##### Data Visualizations")
    
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    if not numeric_cols:
        st.info("No numeric columns available for visualization")
        return
    
    # Chart type selector
    chart_type = st.selectbox(
        "Chart Type",
        ["Line Chart", "Bar Chart", "Histogram", "Box Plot", "Correlation Matrix"],
        key=f"{key}_chart_type"
    )
    
    if chart_type == "Line Chart":
        _show_line_chart(df, numeric_cols, key)
    elif chart_type == "Bar Chart":
        _show_bar_chart(df, numeric_cols, key)
    elif chart_type == "Histogram":
        _show_histogram(df, numeric_cols, key)
    elif chart_type == "Box Plot":
        _show_box_plot(df, numeric_cols, key)
    elif chart_type == "Correlation Matrix":
        _show_correlation_matrix(df, numeric_cols, key)


def _show_line_chart(df: pd.DataFrame, numeric_cols: List[str], key: str):
    """Display line chart"""
    selected_col = st.selectbox("Select column", numeric_cols, key=f"{key}_line_col")
    
    fig = px.line(df.reset_index(), y=selected_col, title=f"{selected_col} over rows")
    st.plotly_chart(fig, use_container_width=True)


def _show_bar_chart(df: pd.DataFrame, numeric_cols: List[str], key: str):
    """Display bar chart"""
    selected_col = st.selectbox("Select column", numeric_cols, key=f"{key}_bar_col")
    
    # Aggregate for top values
    top_n = min(20, len(df))
    data = df[selected_col].head(top_n)
    
    fig = px.bar(x=data.index, y=data.values, title=f"Top {top_n} values of {selected_col}")
    st.plotly_chart(fig, use_container_width=True)


def _show_histogram(df: pd.DataFrame, numeric_cols: List[str], key: str):
    """Display histogram"""
    selected_col = st.selectbox("Select column", numeric_cols, key=f"{key}_hist_col")
    
    fig = px.histogram(df, x=selected_col, title=f"Distribution of {selected_col}")
    st.plotly_chart(fig, use_container_width=True)


def _show_box_plot(df: pd.DataFrame, numeric_cols: List[str], key: str):
    """Display box plot"""
    selected_cols = st.multiselect(
        "Select columns",
        numeric_cols,
        default=numeric_cols[:3],
        key=f"{key}_box_cols"
    )
    
    if selected_cols:
        fig = go.Figure()
        for col in selected_cols:
            fig.add_trace(go.Box(y=df[col], name=col))
        
        fig.update_layout(title="Box Plot Comparison")
        st.plotly_chart(fig, use_container_width=True)


def _show_correlation_matrix(df: pd.DataFrame, numeric_cols: List[str], key: str):
    """Display correlation matrix"""
    if len(numeric_cols) < 2:
        st.info("Need at least 2 numeric columns for correlation")
        return
    
    corr = df[numeric_cols].corr()
    
    fig = px.imshow(
        corr,
        text_auto=True,
        aspect="auto",
        color_continuous_scale="RdBu_r",
        title="Correlation Matrix"
    )
    st.plotly_chart(fig, use_container_width=True)


def _show_schema(df: pd.DataFrame, key: str):
    """Display DataFrame schema"""
    st.markdown("##### Schema Information")
    
    schema_data = {
        "Column": df.columns,
        "Type": df.dtypes.astype(str),
        "Non-Null Count": df.count(),
        "Null Count": df.isnull().sum(),
        "Unique Values": [df[col].nunique() for col in df.columns]
    }
    
    schema_df = pd.DataFrame(schema_data)
    st.dataframe(schema_df, use_container_width=True, hide_index=True)
