"""
Functions Explorer Page - Browse and test available functions with improved UX
"""

import streamlit as st
import sys
from pathlib import Path
import inspect
import pandas as pd
import json
from typing import Any, Dict, List, Tuple, Optional
import importlib

# Add odibi_core to path
ODIBI_ROOT = Path(__file__).parent.parent.parent.parent
if str(ODIBI_ROOT) not in sys.path:
    sys.path.insert(0, str(ODIBI_ROOT))

from odibi_core.learnodibi_ui.theme import apply_theme, COLORS, info_box, success_box
from odibi_core.learnodibi_ui.utils import get_available_functions

apply_theme()

# ============================================================================
# Generic Function Tester
# ============================================================================

def try_import_function(func_name: str) -> Optional[Any]:
    """Try to import a function from odibi_core.functions submodules"""
    # Try each submodule
    submodules = ['data_ops', 'math_utils', 'string_utils', 'datetime_utils', 
                  'validation_utils', 'conversion_utils', 'helpers',
                  'thermo_utils', 'psychro_utils', 'reliability_utils', 'unit_conversion']
    
    for submodule_name in submodules:
        try:
            module = importlib.import_module(f'odibi_core.functions.{submodule_name}')
            if hasattr(module, func_name):
                return getattr(module, func_name)
        except Exception:
            continue
    
    return None


def infer_param_type(param: inspect.Parameter) -> str:
    """Infer parameter type from annotation or default value"""
    if param.annotation != inspect.Parameter.empty:
        ann = param.annotation
        if ann in (int, float):
            return 'number'
        elif ann == bool:
            return 'boolean'
        elif ann == str:
            return 'string'
        elif ann in (list, List):
            return 'list'
        elif ann in (dict, Dict):
            return 'dict'
    
    # Infer from default value
    if param.default != inspect.Parameter.empty:
        if isinstance(param.default, bool):
            return 'boolean'
        elif isinstance(param.default, (int, float)):
            return 'number'
        elif isinstance(param.default, str):
            return 'string'
        elif isinstance(param.default, list):
            return 'list'
        elif isinstance(param.default, dict):
            return 'dict'
    
    return 'string'  # Default


def create_input_widget(param_name: str, param: inspect.Parameter, idx: int) -> Any:
    """Create appropriate input widget for a parameter"""
    param_type = infer_param_type(param)
    default_value = param.default if param.default != inspect.Parameter.empty else None
    
    if param_type == 'boolean':
        return st.checkbox(
            param_name,
            value=default_value if default_value is not None else False,
            key=f"param_{idx}_{param_name}"
        )
    elif param_type == 'number':
        if isinstance(default_value, float):
            return st.number_input(
                param_name,
                value=float(default_value) if default_value is not None else 0.0,
                key=f"param_{idx}_{param_name}",
                format="%.4f"
            )
        else:
            return st.number_input(
                param_name,
                value=int(default_value) if default_value is not None else 0,
                key=f"param_{idx}_{param_name}"
            )
    elif param_type in ('list', 'dict'):
        help_text = "Enter as JSON (e.g., [1, 2, 3] or {\"key\": \"value\"})"
        default_str = json.dumps(default_value) if default_value is not None else ("[]" if param_type == 'list' else "{}")
        return st.text_input(
            param_name,
            value=default_str,
            key=f"param_{idx}_{param_name}",
            help=help_text
        )
    else:  # string
        return st.text_input(
            param_name,
            value=str(default_value) if default_value is not None else "",
            key=f"param_{idx}_{param_name}"
        )


def parse_input_value(value: Any, param_type: str) -> Any:
    """Parse input value to appropriate type"""
    if param_type in ('list', 'dict'):
        try:
            return json.loads(value)
        except:
            return value
    return value


def render_generic_tester(func_name: str, func: Any):
    """Render generic function tester using inspect"""
    try:
        sig = inspect.signature(func)
        doc = inspect.getdoc(func)
        
        # Show documentation
        if doc:
            with st.expander("📖 Documentation", expanded=False):
                st.markdown(f"```\n{doc}\n```")
        
        # Show function signature
        st.code(f"def {func_name}{sig}", language="python")
        
        st.markdown("### Parameters")
        
        # Collect parameter inputs
        params = {}
        param_types = {}
        
        for idx, (param_name, param) in enumerate(sig.parameters.items()):
            param_types[param_name] = infer_param_type(param)
            
            # Show parameter info
            required = param.default == inspect.Parameter.empty
            annotation = f": {param.annotation.__name__}" if param.annotation != inspect.Parameter.empty else ""
            default_text = f" = {param.default}" if not required else ""
            
            st.markdown(f"**{param_name}**{annotation}{default_text} {'*(required)*' if required else ''}")
            
            params[param_name] = create_input_widget(param_name, param, idx)
            st.markdown("")
        
        # Run button
        if st.button("▶️ Run Function", key=f"run_{func_name}", type="primary", use_container_width=True):
            try:
                # Parse inputs
                parsed_params = {
                    name: parse_input_value(value, param_types[name])
                    for name, value in params.items()
                }
                
                # Execute function
                result = func(**parsed_params)
                
                # Display result
                st.markdown("### 🎯 Result")
                
                if isinstance(result, pd.DataFrame):
                    st.dataframe(result, use_container_width=True)
                elif isinstance(result, (list, dict)):
                    st.json(result)
                elif isinstance(result, (int, float)):
                    st.metric("Result", result)
                else:
                    st.success(f"```\n{result}\n```")
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                with st.expander("🐛 Debug Info"):
                    st.code(f"{type(e).__name__}: {str(e)}")
    
    except Exception as e:
        st.error(f"Failed to analyze function: {str(e)}")


# ============================================================================
# Fallback Testers (for functions not in odibi_core.functions)
# ============================================================================

def fallback_tester(func_name: str, category: str):
    """Show a simulated tester for functions we can't import"""
    st.info(f"💡 Function `{func_name}` is not yet available in odibi_core.functions. Showing simulated example.")
    
    # Some common fallback examples
    if "divide" in func_name.lower():
        st.number_input("Numerator", value=10.0, key=f"fb_num_{func_name}")
        st.number_input("Denominator", value=2.0, key=f"fb_den_{func_name}")
        if st.button("▶️ Run", key=f"fb_run_{func_name}"):
            st.success("Result: 5.0")
    
    elif "string" in func_name.lower() or "clean" in func_name.lower():
        text = st.text_input("Input", value="example text", key=f"fb_text_{func_name}")
        if st.button("▶️ Run", key=f"fb_run_{func_name}"):
            st.success(f"Result: {text.strip().lower()}")
    
    elif "date" in func_name.lower() or "time" in func_name.lower():
        date_val = st.text_input("Date String", value="2024-01-15", key=f"fb_date_{func_name}")
        if st.button("▶️ Run", key=f"fb_run_{func_name}"):
            st.success(f"Parsed: {pd.to_datetime(date_val)}")
    
    else:
        st.markdown("""
        This function is not yet implemented in the testable functions library.
        
        **Coming Soon**: All 100+ functions will be automatically testable!
        """)


# ============================================================================
# Main Page Layout
# ============================================================================

st.title("🔍 Functions Explorer")
st.markdown("Browse and test data engineering functions with instant feedback")
st.markdown("---")

# Get available functions
functions_by_category = get_available_functions()
all_functions = [(cat, func) for cat, funcs in functions_by_category.items() for func in funcs]

# Initialize session state
if 'selected_function' not in st.session_state:
    st.session_state.selected_function = None

# Search functionality
search_term = st.text_input("🔍 Search functions", placeholder="e.g., divide, clean, parse...", key="search")

# Filter functions by search
if search_term:
    filtered_functions = [(cat, func) for cat, func in all_functions if search_term.lower() in func.lower()]
else:
    filtered_functions = all_functions

# Create two columns: 40% browser, 60% details
col_browser, col_details = st.columns([4, 6])

# ============================================================================
# LEFT SIDE: Function Browser
# ============================================================================

with col_browser:
    st.markdown("### 🗂️ Function Browser")
    
    # Category filter
    selected_category = st.selectbox(
        "Filter by Category",
        ["All Categories"] + list(functions_by_category.keys()),
        key="category_filter"
    )
    
    # Apply category filter
    if selected_category != "All Categories":
        display_functions = [(cat, func) for cat, func in filtered_functions if cat == selected_category]
    else:
        display_functions = filtered_functions
    
    st.markdown(f"**{len(display_functions)} functions**")
    
    # Function list with immediate selection
    current_category = None
    for cat, func in display_functions:
        # Category header
        if cat != current_category:
            st.markdown(f"**{cat}**")
            current_category = cat
        
        # Function button with visual feedback for selected
        is_selected = (st.session_state.selected_function == (cat, func))
        button_type = "primary" if is_selected else "secondary"
        
        if st.button(
            f"{'🔧' if not is_selected else '▶️'} {func}",
            key=f"btn_{cat}_{func}",
            use_container_width=True,
            type=button_type if is_selected else "secondary"
        ):
            st.session_state.selected_function = (cat, func)
            st.rerun()
    
    # Stats box
    st.markdown("---")
    st.markdown(f"""
    <div style='background-color: {COLORS['surface']}; padding: 1rem; border-radius: 8px;'>
        <h4 style='color: {COLORS['primary']}; margin-top: 0;'>📊 Library Stats</h4>
        <p style='margin: 0;'>
            📁 <strong>{len(functions_by_category)}</strong> categories<br/>
            🔧 <strong>{len(all_functions)}</strong> total functions<br/>
            👁️ <strong>{len(display_functions)}</strong> shown
        </p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# RIGHT SIDE: Function Details & Tester
# ============================================================================

with col_details:
    if st.session_state.selected_function:
        category, func_name = st.session_state.selected_function
        
        # Header
        st.markdown(f"""
        <div style='background-color: {COLORS['surface']}; padding: 1.5rem; border-radius: 8px; margin-bottom: 1rem;'>
            <h2 style='color: {COLORS['primary']}; margin: 0;'>📋 {func_name}</h2>
            <p style='color: {COLORS['text_secondary']}; margin: 0.5rem 0 0 0;'>
                Category: <strong>{category}</strong>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Try to import and test the real function
        func = try_import_function(func_name)
        
        if func:
            st.success("✅ Live function loaded from odibi_core.functions")
            render_generic_tester(func_name, func)
        else:
            fallback_tester(func_name, category)
    
    else:
        # Welcome message
        st.markdown(f"""
        <div style='background-color: {COLORS['surface']}; padding: 3rem; border-radius: 8px; text-align: center;'>
            <h2 style='color: {COLORS['primary']}; margin-top: 0;'>👈 Select a Function</h2>
            <p style='font-size: 1.2em; color: {COLORS['text_secondary']};'>
                Choose any function from the browser to see its details and test it interactively.
            </p>
            <p style='margin-top: 2rem;'>
                <strong>Features:</strong><br/>
                ✨ Instant feedback when you click<br/>
                🔍 Smart parameter detection<br/>
                🎯 Real function testing<br/>
                📖 Built-in documentation
            </p>
        </div>
        """, unsafe_allow_html=True)
