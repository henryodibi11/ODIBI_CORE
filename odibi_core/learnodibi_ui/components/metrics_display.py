"""
Metrics Display Component
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Any, Optional
import pandas as pd
from datetime import datetime


def metrics_display(
    metrics: Dict[str, Any],
    title: str = "Execution Metrics",
    show_charts: bool = True,
    key: str = "metrics_display"
):
    """
    Display execution metrics with visualizations
    
    Args:
        metrics: Dictionary of metrics to display
        title: Display title
        show_charts: Whether to show metric charts
        key: Unique key for the component
    """
    st.subheader(title)
    
    if not metrics:
        st.info("No metrics available")
        return
    
    # Display key metrics in columns
    _display_metric_cards(metrics)
    
    # Detailed metrics view
    if show_charts:
        tabs = st.tabs(["📊 Overview", "📈 Timeline", "📋 Details"])
        
        with tabs[0]:
            _display_overview(metrics, key)
        
        with tabs[1]:
            _display_timeline(metrics, key)
        
        with tabs[2]:
            _display_details(metrics, key)


def _display_metric_cards(metrics: Dict[str, Any]):
    """Display metrics as cards"""
    # Extract common metrics
    execution_time = metrics.get("execution_time", 0)
    success = metrics.get("success", True)
    rows_processed = metrics.get("rows_processed", 0)
    errors = metrics.get("errors", 0)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "⏱️ Execution Time",
            f"{execution_time:.2f}s" if execution_time < 60 else f"{execution_time/60:.1f}m",
            delta=None
        )
    
    with col2:
        st.metric(
            "✅ Status",
            "Success" if success else "Failed",
            delta=None
        )
    
    with col3:
        st.metric(
            "📊 Rows Processed",
            f"{rows_processed:,}" if rows_processed else "N/A",
            delta=None
        )
    
    with col4:
        st.metric(
            "❌ Errors",
            errors,
            delta=None,
            delta_color="inverse"
        )


def _display_overview(metrics: Dict[str, Any], key: str):
    """Display overview charts"""
    st.markdown("##### Metrics Overview")
    
    # Create gauge chart for success rate
    if "success_rate" in metrics:
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=metrics["success_rate"],
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Success Rate (%)"},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "#4CAF50"},
                'steps': [
                    {'range': [0, 50], 'color': "#FFCDD2"},
                    {'range': [50, 80], 'color': "#FFF9C4"},
                    {'range': [80, 100], 'color': "#C8E6C9"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    # Performance breakdown
    if "performance" in metrics:
        perf_data = metrics["performance"]
        
        fig = go.Figure(data=[
            go.Bar(
                x=list(perf_data.keys()),
                y=list(perf_data.values()),
                marker_color='#F5B400'
            )
        ])
        
        fig.update_layout(
            title="Performance Breakdown",
            xaxis_title="Component",
            yaxis_title="Time (seconds)",
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)


def _display_timeline(metrics: Dict[str, Any], key: str):
    """Display execution timeline"""
    st.markdown("##### Execution Timeline")
    
    # Check if we have execution history in session state
    if "execution_history" in st.session_state and st.session_state.execution_history:
        history = st.session_state.execution_history
        
        df = pd.DataFrame(history)
        
        # Create timeline chart
        fig = px.line(
            df,
            x="timestamp",
            y=[d.get("execution_time", 0) for d in df["details"]],
            title="Execution Time Over Runs",
            markers=True
        )
        
        fig.update_layout(
            xaxis_title="Timestamp",
            yaxis_title="Execution Time (s)",
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True, key=f"timeline_{key}")
        
        # Recent executions table
        st.markdown("**Recent Executions:**")
        recent_df = pd.DataFrame([
            {
                "Timestamp": h["timestamp"].strftime("%Y-%m-%d %H:%M:%S"),
                "Action": h["action"],
                "Duration": f"{h['details'].get('execution_time', 0):.2f}s"
            }
            for h in history[-10:]  # Last 10
        ])
        st.dataframe(recent_df, use_container_width=True, hide_index=True)
    else:
        st.info("No execution history available yet. Run some operations to see timeline.")


def _display_details(metrics: Dict[str, Any], key: str):
    """Display detailed metrics"""
    st.markdown("##### Detailed Metrics")
    
    # Convert metrics to DataFrame for better display
    details = []
    
    for metric_key, value in metrics.items():
        if isinstance(value, (int, float, str, bool)):
            details.append({
                "Metric": metric_key.replace("_", " ").title(),
                "Value": value
            })
    
    if details:
        df = pd.DataFrame(details)
        st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Show raw metrics as JSON
    with st.expander("🔧 Raw Metrics (JSON)"):
        st.json(metrics)


def execution_progress(
    current: int,
    total: int,
    stage: str = "Processing",
    key: str = "progress"
):
    """
    Display execution progress bar
    
    Args:
        current: Current progress value
        total: Total value
        stage: Current stage name
        key: Unique key
    """
    progress = current / total if total > 0 else 0
    
    st.markdown(f"**{stage}**")
    st.progress(progress)
    st.caption(f"{current} / {total} ({progress*100:.1f}%)")


def metric_comparison(
    metrics_list: List[Dict[str, Any]],
    labels: List[str],
    metric_key: str = "execution_time",
    title: str = "Metric Comparison"
):
    """
    Compare metrics across multiple runs
    
    Args:
        metrics_list: List of metric dictionaries
        labels: Labels for each metric set
        metric_key: Which metric to compare
        title: Chart title
    """
    st.subheader(title)
    
    values = [m.get(metric_key, 0) for m in metrics_list]
    
    fig = go.Figure(data=[
        go.Bar(
            x=labels,
            y=values,
            marker_color=['#F5B400', '#00796B', '#2196F3'][:len(labels)]
        )
    ])
    
    fig.update_layout(
        xaxis_title="Run",
        yaxis_title=metric_key.replace("_", " ").title(),
        height=300
    )
    
    st.plotly_chart(fig, use_container_width=True)


def real_time_metrics(
    metric_name: str,
    current_value: float,
    previous_value: Optional[float] = None,
    unit: str = "",
    threshold: Optional[float] = None
):
    """
    Display real-time metric with delta
    
    Args:
        metric_name: Name of the metric
        current_value: Current metric value
        previous_value: Previous value for delta calculation
        unit: Unit of measurement
        threshold: Optional threshold for color coding
    """
    delta = None
    delta_color = "normal"
    
    if previous_value is not None:
        delta = current_value - previous_value
        if threshold and abs(delta) > threshold:
            delta_color = "inverse"
    
    display_value = f"{current_value:.2f} {unit}".strip()
    
    st.metric(
        label=metric_name,
        value=display_value,
        delta=f"{delta:+.2f} {unit}".strip() if delta is not None else None,
        delta_color=delta_color
    )
