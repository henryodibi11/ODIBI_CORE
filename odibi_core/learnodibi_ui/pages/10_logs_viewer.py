"""
Logs Viewer - Real-time execution trace and debugging
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime
import json

# Add odibi_core to path
ODIBI_ROOT = Path(__file__).parent.parent.parent.parent
if str(ODIBI_ROOT) not in sys.path:
    sys.path.insert(0, str(ODIBI_ROOT))

from odibi_core.learnodibi_ui.theme import apply_theme, COLORS, success_box, error_box, info_box
from odibi_core.learnodibi_ui.utils import initialize_session_state

# Page config
st.set_page_config(
    page_title="Logs Viewer - ODIBI CORE Studio",
    page_icon="📋",
    layout="wide"
)

apply_theme()
initialize_session_state()

# Initialize session state
if 'execution_logs' not in st.session_state:
    st.session_state.execution_logs = []
if 'log_filter' not in st.session_state:
    st.session_state.log_filter = "ALL"


def add_log_entry(level: str, module: str, message: str, context: dict = None):
    """Add a log entry to the session"""
    entry = {
        'timestamp': datetime.now(),
        'level': level,
        'module': module,
        'message': message,
        'context': context or {}
    }
    st.session_state.execution_logs.append(entry)


def get_log_color(level: str) -> str:
    """Get color for log level"""
    colors = {
        'DEBUG': COLORS['text_secondary'],
        'INFO': COLORS['info'],
        'SUCCESS': COLORS['success'],
        'WARNING': COLORS['warning'],
        'ERROR': COLORS['error']
    }
    return colors.get(level, COLORS['text'])


def get_log_icon(level: str) -> str:
    """Get icon for log level"""
    icons = {
        'DEBUG': '🔍',
        'INFO': 'ℹ️',
        'SUCCESS': '✅',
        'WARNING': '⚠️',
        'ERROR': '❌'
    }
    return icons.get(level, '📝')


def main():
    st.title("📋 Logs & Execution Trace")
    st.markdown(f"<p style='color: {COLORS['text_secondary']}; font-size: 1.1em;'>Real-time execution monitoring and debugging</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Live Logs", "🔍 Log Analysis", "⚙️ Demo Execution", "📚 Guide"])
    
    with tab1:
        st.markdown("### 📊 Live Execution Logs")
        
        # Controls
        col_filter, col_clear, col_export = st.columns([2, 1, 1])
        
        with col_filter:
            log_level_filter = st.selectbox(
                "Filter by level:",
                options=["ALL", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR"],
                index=0,
                key="log_level_filter"
            )
        
        with col_clear:
            st.markdown("##")
            if st.button("🗑️ Clear Logs", use_container_width=True):
                st.session_state.execution_logs = []
                st.success("Logs cleared!")
                st.rerun()
        
        with col_export:
            st.markdown("##")
            if st.button("💾 Export", use_container_width=True):
                if st.session_state.execution_logs:
                    # Convert to DataFrame
                    logs_df = pd.DataFrame([
                        {
                            'timestamp': log['timestamp'].isoformat(),
                            'level': log['level'],
                            'module': log['module'],
                            'message': log['message'],
                            'context': json.dumps(log['context'])
                        }
                        for log in st.session_state.execution_logs
                    ])
                    
                    # Download
                    csv = logs_df.to_csv(index=False)
                    st.download_button(
                        "Download CSV",
                        csv,
                        f"odibi_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        "text/csv"
                    )
        
        st.markdown("##")
        
        # Display logs
        if st.session_state.execution_logs:
            # Filter logs
            filtered_logs = [
                log for log in st.session_state.execution_logs
                if log_level_filter == "ALL" or log['level'] == log_level_filter
            ]
            
            if filtered_logs:
                st.markdown(f"**Showing {len(filtered_logs)} of {len(st.session_state.execution_logs)} logs**")
                
                # Display in reverse chronological order
                for log in reversed(filtered_logs[-100:]):  # Show last 100
                    color = get_log_color(log['level'])
                    icon = get_log_icon(log['level'])
                    
                    with st.container():
                        st.markdown(f"""
                        <div style='background: {COLORS['surface']}; padding: 0.75rem; border-radius: 6px; 
                                    border-left: 3px solid {color}; margin-bottom: 0.5rem;'>
                            <div style='display: flex; justify-content: space-between; align-items: center;'>
                                <span style='color: {color}; font-weight: bold;'>
                                    {icon} {log['level']}
                                </span>
                                <span style='color: {COLORS['text_secondary']}; font-size: 0.85em;'>
                                    {log['timestamp'].strftime('%H:%M:%S.%f')[:-3]} | {log['module']}
                                </span>
                            </div>
                            <div style='margin-top: 0.5rem; color: {COLORS['text']};'>
                                {log['message']}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Show context if available
                        if log['context']:
                            with st.expander("View Context", expanded=False):
                                st.json(log['context'])
            else:
                info_box("No logs match the current filter.")
        else:
            info_box("No logs yet. Run the demo execution to generate logs!")
    
    with tab2:
        st.markdown("### 🔍 Log Analysis")
        
        if st.session_state.execution_logs:
            # Summary statistics
            st.markdown("#### 📊 Summary")
            
            logs_df = pd.DataFrame([
                {
                    'Level': log['level'],
                    'Module': log['module'],
                    'Timestamp': log['timestamp']
                }
                for log in st.session_state.execution_logs
            ])
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Logs", len(logs_df))
            
            with col2:
                error_count = len(logs_df[logs_df['Level'] == 'ERROR'])
                st.metric("Errors", error_count, delta=None if error_count == 0 else "⚠️")
            
            with col3:
                warning_count = len(logs_df[logs_df['Level'] == 'WARNING'])
                st.metric("Warnings", warning_count)
            
            with col4:
                success_count = len(logs_df[logs_df['Level'] == 'SUCCESS'])
                st.metric("Successes", success_count)
            
            st.markdown("##")
            
            # Charts
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                st.markdown("**Logs by Level**")
                level_counts = logs_df['Level'].value_counts()
                st.bar_chart(level_counts)
            
            with col_chart2:
                st.markdown("**Logs by Module**")
                module_counts = logs_df['Module'].value_counts()
                st.bar_chart(module_counts)
            
            st.markdown("##")
            
            # Timeline
            st.markdown("**Timeline**")
            logs_df['Count'] = 1
            timeline = logs_df.groupby(logs_df['Timestamp'].dt.floor('S'))['Count'].sum()
            st.line_chart(timeline)
            
        else:
            info_box("No logs to analyze. Run the demo execution first!")
    
    with tab3:
        st.markdown("### ⚙️ Demo Execution")
        st.markdown("Run a sample pipeline to generate execution logs")
        
        st.markdown("##")
        
        if st.button("🚀 Run Demo Pipeline", type="primary", use_container_width=True):
            with st.status("Running pipeline...", expanded=True) as status:
                # Simulate pipeline execution with logs
                import time
                
                st.write("Initializing...")
                add_log_entry("INFO", "Pipeline", "Pipeline execution started")
                time.sleep(0.5)
                
                st.write("Loading Bronze data...")
                add_log_entry("DEBUG", "BronzeLayer", "Reading source data", {"source": "sample.csv", "rows": 100})
                add_log_entry("SUCCESS", "BronzeLayer", "Bronze data loaded successfully", {"rows": 100, "columns": 5})
                time.sleep(0.5)
                
                st.write("Transforming to Silver...")
                add_log_entry("INFO", "SilverLayer", "Applying transformations")
                add_log_entry("DEBUG", "SilverLayer", "Running data quality checks")
                add_log_entry("WARNING", "SilverLayer", "Found 3 null values in column 'value'", {"nulls": 3, "column": "value"})
                add_log_entry("SUCCESS", "SilverLayer", "Silver data created", {"rows": 97, "columns": 6})
                time.sleep(0.5)
                
                st.write("Aggregating to Gold...")
                add_log_entry("INFO", "GoldLayer", "Computing aggregations")
                add_log_entry("DEBUG", "GoldLayer", "Grouping by category")
                add_log_entry("SUCCESS", "GoldLayer", "Gold layer complete", {"rows": 5, "aggregations": 3})
                time.sleep(0.5)
                
                st.write("Saving results...")
                add_log_entry("INFO", "Storage", "Writing to output")
                add_log_entry("SUCCESS", "Storage", "Data saved successfully", {"path": "/data/gold/output.csv"})
                
                add_log_entry("SUCCESS", "Pipeline", "Pipeline execution completed successfully", {
                    "duration": "2.5s",
                    "bronze_rows": 100,
                    "silver_rows": 97,
                    "gold_rows": 5
                })
                
                status.update(label="Pipeline complete!", state="complete")
            
            success_box("✅ Demo pipeline executed! Check the Live Logs tab to see the execution trace.")
            st.rerun()
    
    with tab4:
        st.markdown("### 📚 Logging Guide")
        
        st.markdown("#### 🎯 Log Levels")
        
        st.markdown(f"""
        <div style='background: {COLORS['surface']}; padding: 1.5rem; border-radius: 8px;'>
            <div style='margin-bottom: 1rem;'>
                <span style='color: {get_log_color("DEBUG")}; font-weight: bold;'>🔍 DEBUG</span> - 
                Detailed diagnostic information for troubleshooting
            </div>
            <div style='margin-bottom: 1rem;'>
                <span style='color: {get_log_color("INFO")}; font-weight: bold;'>ℹ️ INFO</span> - 
                General informational messages about pipeline execution
            </div>
            <div style='margin-bottom: 1rem;'>
                <span style='color: {get_log_color("SUCCESS")}; font-weight: bold;'>✅ SUCCESS</span> - 
                Successful completion of operations
            </div>
            <div style='margin-bottom: 1rem;'>
                <span style='color: {get_log_color("WARNING")}; font-weight: bold;'>⚠️ WARNING</span> - 
                Potential issues that don't stop execution
            </div>
            <div>
                <span style='color: {get_log_color("ERROR")}; font-weight: bold;'>❌ ERROR</span> - 
                Errors that caused operation failures
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("##")
        
        st.markdown("#### 💻 Using Logs in Your Code")
        
        st.code("""
from odibi_core.observability import DynamicLogger

# Initialize logger
logger = DynamicLogger(module="MyPipeline")

# Log at different levels
logger.debug("Detailed diagnostic info")
logger.info("Pipeline started")
logger.success("Data loaded successfully")
logger.warning("Missing values detected")
logger.error("Failed to connect to database")

# With context
logger.info("Processing data", context={
    "rows": 1000,
    "columns": 10,
    "source": "input.csv"
})
""", language="python")
        
        st.markdown("##")
        
        st.markdown("#### 🔍 Debugging Tips")
        
        st.markdown("""
        - **Use DEBUG level** during development to see detailed execution flow
        - **Add context** to logs with relevant metadata (row counts, file paths, etc.)
        - **Filter by module** to focus on specific parts of your pipeline
        - **Export logs** to CSV for external analysis
        - **Watch for patterns** in warnings/errors to identify recurring issues
        - **Use timestamps** to identify performance bottlenecks
        """)


if __name__ == "__main__":
    main()
