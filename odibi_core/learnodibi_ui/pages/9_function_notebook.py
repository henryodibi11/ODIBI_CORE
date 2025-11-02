"""
Functions Interactive Notebook - Cell-based function exploration and experimentation
"""

import streamlit as st
import sys
from pathlib import Path
import inspect
import pandas as pd
import json
from typing import Any, Dict, List, Optional
import importlib
from datetime import datetime
import re

# Add odibi_core to path
ODIBI_ROOT = Path(__file__).parent.parent.parent.parent
if str(ODIBI_ROOT) not in sys.path:
    sys.path.insert(0, str(ODIBI_ROOT))

from odibi_core.learnodibi_ui.theme import apply_theme, COLORS, info_box, success_box, warning_box
from odibi_core.learnodibi_ui.utils import get_available_functions, format_execution_time
from odibi_core.learnodibi_ui.code_executor import CodeExecutor, get_function_source

apply_theme()

# ============================================================================
# Session State Initialization
# ============================================================================

def initialize_notebook_state():
    """Initialize notebook session state"""
    if 'notebook_cells' not in st.session_state:
        st.session_state.notebook_cells = []
    
    if 'cell_counter' not in st.session_state:
        st.session_state.cell_counter = 0
    
    if 'execution_history' not in st.session_state:
        st.session_state.execution_history = []
    
    if 'code_executor' not in st.session_state:
        st.session_state.code_executor = CodeExecutor()
    
    if 'selected_function' not in st.session_state:
        st.session_state.selected_function = None
    
    if 'notebook_variables' not in st.session_state:
        st.session_state.notebook_variables = {}

initialize_notebook_state()

# ============================================================================
# Cell Management
# ============================================================================

class NotebookCell:
    """Represents a single notebook cell"""
    
    def __init__(self, cell_id: int, cell_type: str = "code", content: str = ""):
        self.id = cell_id
        self.type = cell_type  # "code", "function", "markdown"
        self.content = content
        self.output = None
        self.error = None
        self.execution_time = None
        self.executed_at = None
        self.variables_created = {}

def add_cell(cell_type: str = "code", content: str = ""):
    """Add a new cell to the notebook"""
    st.session_state.cell_counter += 1
    cell = NotebookCell(st.session_state.cell_counter, cell_type, content)
    st.session_state.notebook_cells.append(cell)
    return cell

def delete_cell(cell_id: int):
    """Delete a cell from the notebook"""
    st.session_state.notebook_cells = [
        cell for cell in st.session_state.notebook_cells if cell.id != cell_id
    ]

def move_cell_up(cell_id: int):
    """Move cell up in the list"""
    cells = st.session_state.notebook_cells
    for i, cell in enumerate(cells):
        if cell.id == cell_id and i > 0:
            cells[i], cells[i-1] = cells[i-1], cells[i]
            break

def move_cell_down(cell_id: int):
    """Move cell down in the list"""
    cells = st.session_state.notebook_cells
    for i, cell in enumerate(cells):
        if cell.id == cell_id and i < len(cells) - 1:
            cells[i], cells[i+1] = cells[i+1], cells[i]
            break

def execute_cell(cell: NotebookCell):
    """Execute a cell and capture output"""
    import time
    
    start_time = time.time()
    cell.executed_at = datetime.now()
    
    try:
        result = st.session_state.code_executor.execute(cell.content)
        
        cell.execution_time = time.time() - start_time
        cell.output = result
        cell.error = None
        cell.variables_created = result.get('variables', {})
        
        # Update notebook variables
        st.session_state.notebook_variables.update(cell.variables_created)
        
        # Add to history
        st.session_state.execution_history.append({
            'cell_id': cell.id,
            'timestamp': cell.executed_at,
            'duration': cell.execution_time,
            'success': result['success']
        })
        
        return True
    except Exception as e:
        cell.execution_time = time.time() - start_time
        cell.error = str(e)
        cell.output = None
        return False

# ============================================================================
# Function Browser
# ============================================================================

def try_import_function(func_name: str) -> Optional[Any]:
    """Try to import a function from odibi_core.functions"""
    try:
        module = importlib.import_module('odibi_core.functions')
        if hasattr(module, func_name):
            return getattr(module, func_name)
    except:
        pass
    return None

def get_function_signature(func_name: str) -> str:
    """Get function signature"""
    func = try_import_function(func_name)
    if func:
        sig = inspect.signature(func)
        return f"{func_name}{sig}"
    return f"{func_name}()"

def get_function_doc(func_name: str) -> str:
    """Get function documentation"""
    func = try_import_function(func_name)
    if func:
        doc = inspect.getdoc(func)
        return doc if doc else "No documentation available"
    return "Function not found"

def generate_function_template(func_name: str) -> str:
    """Generate a template code snippet for a function"""
    func = try_import_function(func_name)
    if not func:
        return f"# {func_name} not found\n"
    
    sig = inspect.signature(func)
    params = []
    
    for param_name, param in sig.parameters.items():
        if param.default == inspect.Parameter.empty:
            # Required parameter
            params.append(f"{param_name}=???")
        else:
            # Optional parameter with default
            if isinstance(param.default, str):
                params.append(f'{param_name}="{param.default}"')
            else:
                params.append(f"{param_name}={param.default}")
    
    params_str = ", ".join(params)
    
    return f"""# Test {func_name}
from odibi_core.functions import {func_name}

result = {func_name}({params_str})
print(result)"""

# ============================================================================
# UI Components
# ============================================================================

def render_cell(cell: NotebookCell, idx: int):
    """Render a single cell"""
    
    # Cell container
    with st.container():
        st.markdown(f"""
        <div style='background-color: {COLORS['surface']}; padding: 0.5rem; border-radius: 8px; margin-bottom: 1rem; border-left: 4px solid {COLORS['primary']};'>
        """, unsafe_allow_html=True)
        
        # Cell header
        col_header1, col_header2, col_header3, col_header4, col_header5, col_header6 = st.columns([1, 1, 1, 1, 1, 6])
        
        with col_header1:
            if st.button("▶️", key=f"run_{cell.id}", help="Run cell"):
                with st.spinner("Executing..."):
                    execute_cell(cell)
                    st.rerun()
        
        with col_header2:
            if st.button("🔼", key=f"up_{cell.id}", help="Move up"):
                move_cell_up(cell.id)
                st.rerun()
        
        with col_header3:
            if st.button("🔽", key=f"down_{cell.id}", help="Move down"):
                move_cell_down(cell.id)
                st.rerun()
        
        with col_header4:
            if st.button("📋", key=f"copy_{cell.id}", help="Copy cell"):
                add_cell(cell.type, cell.content)
                st.rerun()
        
        with col_header5:
            if st.button("🗑️", key=f"del_{cell.id}", help="Delete cell"):
                delete_cell(cell.id)
                st.rerun()
        
        with col_header6:
            st.markdown(f"<p style='color: {COLORS['text_secondary']}; margin: 0;'>Cell [{idx}]</p>", unsafe_allow_html=True)
        
        # Cell content editor
        cell.content = st.text_area(
            "Code",
            value=cell.content,
            height=150,
            key=f"content_{cell.id}",
            label_visibility="collapsed"
        )
        
        # Cell output
        if cell.output:
            if cell.output['success']:
                st.markdown(f"<div style='background-color: #1a3d1a; padding: 0.5rem; border-radius: 4px; margin-top: 0.5rem;'>", unsafe_allow_html=True)
                
                # Show stdout
                if cell.output.get('output'):
                    st.code(cell.output['output'], language="text")
                
                # Show result
                if cell.output.get('result') is not None:
                    result = cell.output['result']
                    if isinstance(result, pd.DataFrame):
                        st.dataframe(result, use_container_width=True)
                    elif isinstance(result, (list, dict)):
                        st.json(result)
                    else:
                        st.code(f"→ {result}", language="text")
                
                # Show variables created
                if cell.variables_created:
                    vars_str = ", ".join(f"{k}: {type(v).__name__}" for k, v in cell.variables_created.items())
                    st.caption(f"Variables: {vars_str}")
                
                # Execution time
                if cell.execution_time:
                    st.caption(f"⏱️ {format_execution_time(cell.execution_time)}")
                
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                # Show error
                st.markdown(f"<div style='background-color: #3d1a1a; padding: 0.5rem; border-radius: 4px; margin-top: 0.5rem;'>", unsafe_allow_html=True)
                st.error(cell.output.get('error', 'Unknown error'))
                st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

def render_function_browser():
    """Render the function browser sidebar"""
    functions_by_category = get_available_functions()
    
    st.markdown(f"""
    <div style='background-color: {COLORS['surface']}; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;'>
        <h3 style='color: {COLORS['primary']}; margin-top: 0;'>📚 Function Library</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Search
    search = st.text_input("🔍 Search functions", key="func_search")
    
    # Category selector
    categories = ["All"] + list(functions_by_category.keys())
    selected_category = st.selectbox("Category", categories, key="func_category")
    
    # Function list
    for category, functions in functions_by_category.items():
        if selected_category != "All" and selected_category != category:
            continue
        
        st.markdown(f"**{category}**")
        
        for func_name in functions:
            if search and search.lower() not in func_name.lower():
                continue
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                if st.button(f"🔧 {func_name}", key=f"func_btn_{func_name}", use_container_width=True):
                    st.session_state.selected_function = func_name
            
            with col2:
                if st.button("➕", key=f"add_{func_name}", help="Add to notebook"):
                    template = generate_function_template(func_name)
                    add_cell("code", template)
                    st.rerun()
    
    # Show selected function details
    if st.session_state.selected_function:
        st.markdown("---")
        st.markdown(f"### 📖 {st.session_state.selected_function}")
        
        # Signature
        sig = get_function_signature(st.session_state.selected_function)
        st.code(sig, language="python")
        
        # Documentation
        doc = get_function_doc(st.session_state.selected_function)
        with st.expander("Documentation", expanded=False):
            st.markdown(doc)
        
        # Source code
        source = get_function_source(st.session_state.selected_function)
        if source:
            with st.expander("Source Code", expanded=False):
                st.code(source, language="python")

def export_notebook() -> str:
    """Export notebook as Python script"""
    script_parts = [
        "# ODIBI CORE Function Notebook Export",
        f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "import pandas as pd",
        "from odibi_core.functions import *",
        "",
        "# ============================================================================",
        "# Notebook Cells",
        "# ============================================================================",
        ""
    ]
    
    for idx, cell in enumerate(st.session_state.notebook_cells, 1):
        script_parts.append(f"# Cell [{idx}]")
        script_parts.append(cell.content)
        script_parts.append("")
    
    return "\n".join(script_parts)

# ============================================================================
# Main Layout
# ============================================================================

st.title("📓 Functions Interactive Notebook")
st.markdown("Explore, test, and chain functions in a notebook-style environment")
st.markdown("---")

# Create sidebar and main area
col_sidebar, col_main = st.columns([3, 7])

# ============================================================================
# Sidebar: Function Browser
# ============================================================================

with col_sidebar:
    render_function_browser()

# ============================================================================
# Main Area: Notebook Cells
# ============================================================================

with col_main:
    # Toolbar
    col_t1, col_t2, col_t3, col_t4, col_t5 = st.columns([2, 2, 2, 2, 2])
    
    with col_t1:
        if st.button("➕ Code Cell", use_container_width=True):
            add_cell("code", "# Write your code here\n")
            st.rerun()
    
    with col_t2:
        if st.button("▶️ Run All", use_container_width=True):
            for cell in st.session_state.notebook_cells:
                execute_cell(cell)
            st.rerun()
    
    with col_t3:
        if st.button("🔄 Reset Kernel", use_container_width=True):
            st.session_state.code_executor.reset_namespace()
            st.session_state.notebook_variables = {}
            success_box("Kernel reset successfully")
            st.rerun()
    
    with col_t4:
        if st.button("🗑️ Clear All", use_container_width=True):
            st.session_state.notebook_cells = []
            st.session_state.notebook_variables = {}
            st.rerun()
    
    with col_t5:
        if st.button("💾 Export", use_container_width=True):
            script = export_notebook()
            st.download_button(
                label="📥 Download Script",
                data=script,
                file_name=f"odibi_notebook_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py",
                mime="text/x-python",
                use_container_width=True
            )
    
    st.markdown("---")
    
    # Show variables in scope
    if st.session_state.notebook_variables:
        with st.expander("🔢 Variables in Scope", expanded=False):
            vars_df = pd.DataFrame([
                {
                    'Variable': name,
                    'Type': type(value).__name__,
                    'Value': str(value)[:50] + '...' if len(str(value)) > 50 else str(value)
                }
                for name, value in st.session_state.notebook_variables.items()
            ])
            st.dataframe(vars_df, use_container_width=True)
    
    # Render cells
    if st.session_state.notebook_cells:
        for idx, cell in enumerate(st.session_state.notebook_cells, 1):
            render_cell(cell, idx)
    else:
        # Welcome message
        st.markdown(f"""
        <div style='background-color: {COLORS['surface']}; padding: 3rem; border-radius: 8px; text-align: center;'>
            <h2 style='color: {COLORS['primary']}; margin-top: 0;'>📝 Start Your Notebook</h2>
            <p style='font-size: 1.2em; color: {COLORS['text_secondary']};'>
                Click <strong>➕ Code Cell</strong> to add your first cell, or select a function from the library to get started.
            </p>
            <p style='margin-top: 2rem;'>
                <strong>Features:</strong><br/>
                📦 Browse 100+ data engineering functions<br/>
                ⚡ Execute code cells interactively<br/>
                🔗 Chain functions together<br/>
                📊 Visualize results inline<br/>
                💾 Export as Python script
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Execution history
    if st.session_state.execution_history:
        st.markdown("---")
        with st.expander("📜 Execution History", expanded=False):
            history_df = pd.DataFrame([
                {
                    'Cell': h['cell_id'],
                    'Time': h['timestamp'].strftime('%H:%M:%S'),
                    'Duration': format_execution_time(h['duration']),
                    'Status': '✅ Success' if h['success'] else '❌ Error'
                }
                for h in st.session_state.execution_history[-10:]  # Last 10 executions
            ])
            st.dataframe(history_df, use_container_width=True)

# ============================================================================
# Quick Start Guide
# ============================================================================

with st.sidebar:
    st.markdown("---")
    with st.expander("💡 Quick Start Guide"):
        st.markdown("""
        ### How to Use
        
        1. **Browse Functions**: Explore the function library on the left
        2. **Add Cells**: Click ➕ to add code cells
        3. **Write Code**: Use any ODIBI CORE functions
        4. **Execute**: Run individual cells or all at once
        5. **Chain Functions**: Use variables across cells
        6. **Export**: Save your work as a Python script
        
        ### Keyboard Shortcuts
        
        - `Ctrl+Enter`: Run current cell
        - `Shift+Enter`: Run and move to next
        
        ### Tips
        
        - Variables persist across cells
        - Use tab for autocomplete
        - Check execution history for debugging
        - Reset kernel to clear all state
        """)
