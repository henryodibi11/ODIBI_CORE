"""
Helper utilities for ODIBI CORE Studio
"""

import streamlit as st
import pandas as pd
import json
import time
from typing import Any, Dict, List, Optional, Callable
from pathlib import Path
import sys

# Add odibi_core to path
ODIBI_ROOT = Path(__file__).parent.parent.parent
if str(ODIBI_ROOT) not in sys.path:
    sys.path.insert(0, str(ODIBI_ROOT))


def format_execution_time(seconds: float) -> str:
    """Format execution time in human-readable format"""
    if seconds < 1:
        return f"{seconds * 1000:.2f}ms"
    elif seconds < 60:
        return f"{seconds:.2f}s"
    else:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.2f}s"


def create_sample_data(n_rows: int = 100) -> pd.DataFrame:
    """Create sample data for demonstrations"""
    import numpy as np
    
    np.random.seed(42)
    return pd.DataFrame({
        "timestamp": pd.date_range("2024-01-01", periods=n_rows, freq="h"),
        "sensor_id": np.random.choice(["S001", "S002", "S003"], n_rows),
        "temperature": np.random.normal(25, 5, n_rows),
        "humidity": np.random.normal(60, 10, n_rows),
        "pressure": np.random.normal(1013, 5, n_rows),
        "energy_kwh": np.random.uniform(10, 100, n_rows),
    })


def execute_with_metrics(func: Callable, *args, **kwargs) -> Dict[str, Any]:
    """Execute a function and capture metrics"""
    start_time = time.time()
    
    try:
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        
        return {
            "success": True,
            "result": result,
            "execution_time": execution_time,
            "error": None
        }
    except Exception as e:
        execution_time = time.time() - start_time
        return {
            "success": False,
            "result": None,
            "execution_time": execution_time,
            "error": str(e)
        }


def display_code_with_run(code: str, description: str = "", language: str = "python"):
    """Display code with a run button"""
    st.markdown(f"**{description}**" if description else "")
    st.code(code, language=language)
    
    if st.button(f"▶️ Run", key=f"run_{hash(code)}"):
        with st.spinner("Executing..."):
            try:
                # Execute code in a safe namespace
                namespace = {}
                exec(code, namespace)
                st.success("✅ Execution completed successfully!")
                
                # Display any outputs
                if "result" in namespace:
                    st.write("**Result:**")
                    st.write(namespace["result"])
                    
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")


def json_editor(data: Dict, key: str = "json_editor") -> Dict:
    """Create an interactive JSON editor"""
    json_str = json.dumps(data, indent=2)
    edited_json = st.text_area("Edit JSON", json_str, height=300, key=key)
    
    try:
        return json.loads(edited_json)
    except json.JSONDecodeError as e:
        st.error(f"Invalid JSON: {str(e)}")
        return data


def show_function_signature(func: Callable):
    """Display function signature and docstring"""
    import inspect
    
    # Get signature
    sig = inspect.signature(func)
    st.code(f"{func.__name__}{sig}", language="python")
    
    # Get docstring
    if func.__doc__:
        st.markdown("**Description:**")
        st.info(inspect.cleandoc(func.__doc__))


def create_downloadable_df(df: pd.DataFrame, filename: str = "data.csv"):
    """Create a download button for DataFrame"""
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name=filename,
        mime="text/csv"
    )


def splash_screen():
    """Display splash screen on first load"""
    if "splash_shown" not in st.session_state:
        with st.spinner(""):
            time.sleep(1.5)
        st.session_state.splash_shown = True


def get_node_types() -> List[Dict[str, str]]:
    """Get information about the 5 canonical node types"""
    return [
        {
            "name": "ConnectNode",
            "icon": "🔌",
            "description": "Establishes connections to data sources and targets",
            "example": "Connect to Azure Blob Storage, SQL databases, APIs"
        },
        {
            "name": "IngestNode",
            "icon": "📥",
            "description": "Reads data from connected sources into DataFrames",
            "example": "Read CSV, Parquet, JSON files or query databases"
        },
        {
            "name": "TransformNode",
            "icon": "⚙️",
            "description": "Applies transformations and business logic to data",
            "example": "Clean data, apply functions, aggregate, join datasets"
        },
        {
            "name": "StoreNode",
            "icon": "💾",
            "description": "Persists transformed data to storage layers",
            "example": "Write to Delta Lake, Parquet, or databases"
        },
        {
            "name": "PublishNode",
            "icon": "📤",
            "description": "Exposes data to downstream consumers",
            "example": "Create APIs, dashboards, or export to external systems"
        }
    ]


def get_all_functions() -> Dict[str, List[str]]:
    """Get categorized list of available REAL functions from odibi_core.functions"""
    return {
        "Data Operations": [
            "deduplicate", "filter_rows", "safe_join", 
            "group_and_aggregate", "select_columns", "sort_data",
            "pivot_table", "unpivot", "rename_columns"
        ],
        "String Utilities": [
            "trim_whitespace", "to_lowercase", "to_uppercase",
            "regex_extract", "regex_replace", "split_string",
            "concat_strings", "standardize_column_names", "pad_string"
        ],
        "Math Utilities": [
            "safe_sqrt", "safe_log", "safe_divide",
            "calculate_moving_average", "calculate_z_score", "normalize_min_max",
            "calculate_percentile", "outlier_detection_iqr", "calculate_percent_change"
        ],
        "DateTime Utilities": [
            "to_datetime", "date_diff", "add_time_delta",
            "extract_date_parts", "is_weekend", "format_datetime",
            "truncate_datetime", "get_current_timestamp", "calculate_age"
        ],
        "Conversion Utilities": [
            "fill_null", "cast_column", "to_numeric",
            "to_boolean", "normalize_nulls", "one_hot_encode",
            "extract_numbers", "map_values", "parse_json"
        ],
        "Validation Utilities": [
            "check_missing_data", "find_duplicates", "validate_not_null",
            "validate_range", "validate_unique", "generate_data_quality_report",
            "get_schema", "get_value_counts", "check_schema_match"
        ],
        "Unit Conversion": [
            "convert_temperature", "convert_pressure", "convert_energy",
            "convert_power", "convert_flow", "convert_density"
        ],
        "Thermodynamics": [
            "saturation_temperature", "saturation_pressure", "steam_enthalpy_btu_lb",
            "feedwater_enthalpy_btu_lb", "fahrenheit_to_kelvin", "kelvin_to_fahrenheit",
            "btu_lb_to_kj_kg", "kj_kg_to_btu_lb", "psia_to_mpa", "mpa_to_psia"
        ],
        "Psychrometrics": [
            "relative_humidity", "dew_point", "wet_bulb_temperature",
            "humidity_ratio", "enthalpy_moist_air"
        ],
        "Reliability": [
            "mean_time_between_failures", "failure_rate", "reliability_at_time",
            "availability_index", "mttr", "weibull_reliability",
            "expected_failures", "mission_reliability"
        ]
    }


# Alias for backward compatibility
get_available_functions = get_all_functions


def initialize_session_state():
    """Initialize session state variables"""
    if "execution_history" not in st.session_state:
        st.session_state.execution_history = []
    
    if "current_layer" not in st.session_state:
        st.session_state.current_layer = "bronze"
    
    if "demo_data" not in st.session_state:
        st.session_state.demo_data = {
            "bronze": None,
            "silver": None,
            "gold": None
        }


def add_to_history(action: str, details: Dict):
    """Add action to execution history"""
    if "execution_history" not in st.session_state:
        st.session_state.execution_history = []
    
    st.session_state.execution_history.append({
        "timestamp": pd.Timestamp.now(),
        "action": action,
        "details": details
    })
