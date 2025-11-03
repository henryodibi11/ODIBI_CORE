"""
Guided Learning - Interactive step-by-step walkthroughs with engine awareness
"""

import streamlit as st
import sys
from pathlib import Path

# Add odibi_core to path
ODIBI_ROOT = Path(__file__).parent.parent.parent.parent
if str(ODIBI_ROOT) not in sys.path:
    sys.path.insert(0, str(ODIBI_ROOT))

from odibi_core.learnodibi_ui.theme import apply_theme, COLORS, success_box, error_box, info_box
from odibi_core.learnodibi_ui.walkthrough_parser import get_walkthrough_parser
from odibi_core.learnodibi_ui.code_executor import CodeExecutor, get_function_source, get_function_call_stack
from odibi_core.learnodibi_ui.utils import initialize_session_state
from odibi_core.learnodibi_ui.walkthrough_validator import WalkthroughValidator
from odibi_core.learnodibi_ui.manifest_loader import ManifestLoader
import pandas as pd

# Page config
st.set_page_config(
    page_title="Guided Learning - ODIBI CORE Studio",
    page_icon="📚",
    layout="wide"
)

apply_theme()
initialize_session_state()

# Initialize session state for learning
if 'current_walkthrough' not in st.session_state:
    st.session_state.current_walkthrough = None
if 'current_step' not in st.session_state:
    st.session_state.current_step = 0
if 'completed_steps' not in st.session_state:
    st.session_state.completed_steps = set()
if 'code_executor' not in st.session_state:
    st.session_state.code_executor = CodeExecutor(engine='pandas')
if 'selected_engine' not in st.session_state:
    st.session_state.selected_engine = 'pandas'
if 'walkthrough_validator' not in st.session_state:
    st.session_state.walkthrough_validator = WalkthroughValidator(ODIBI_ROOT)
if 'manifest_loader' not in st.session_state:
    st.session_state.manifest_loader = ManifestLoader(ODIBI_ROOT)
if 'validation_mode' not in st.session_state:
    st.session_state.validation_mode = 'learn'  # 'learn' or 'teach'


def render_step_navigation(total_steps: int, location: str = "top"):
    """Render step navigation controls with unique keys"""
    col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
    
    with col1:
        if st.button("⏮️ First", disabled=st.session_state.current_step == 0, key=f"first_{location}"):
            st.session_state.current_step = 0
            st.rerun()
    
    with col2:
        if st.button("⬅️ Previous", disabled=st.session_state.current_step == 0, key=f"prev_{location}"):
            st.session_state.current_step -= 1
            st.rerun()
    
    with col3:
        # Progress bar
        progress = (st.session_state.current_step + 1) / total_steps
        st.progress(progress, text=f"Step {st.session_state.current_step + 1} of {total_steps}")
    
    with col4:
        if st.button("Next ➡️", disabled=st.session_state.current_step >= total_steps - 1, key=f"next_{location}"):
            st.session_state.current_step += 1
            st.rerun()
    
    with col5:
        if st.button("Last ⏭️", disabled=st.session_state.current_step >= total_steps - 1, key=f"last_{location}"):
            st.session_state.current_step = total_steps - 1
            st.rerun()


def render_preflight_badge(preflight_result: dict, is_demo: bool = False):
    """Render pre-flight check badge with demo awareness"""
    if is_demo:
        st.markdown(f"""
        <div style='background-color: {COLORS['warning']}; padding: 0.5rem 1rem; border-radius: 4px; display: inline-block;'>
            <span style='color: white; font-weight: bold;'>🧠 Teaching Example - Not Executed</span>
        </div>
        """, unsafe_allow_html=True)
        st.info("This is a demonstration block. It will be displayed but not executed.")
    elif preflight_result['passed']:
        st.markdown(f"""
        <div style='background-color: {COLORS['success']}; padding: 0.5rem 1rem; border-radius: 4px; display: inline-block;'>
            <span style='color: white; font-weight: bold;'>✅ Pre-flight Check: PASSED</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        error_msg = preflight_result.get('error_msg', 'Unknown error')
        line_no = preflight_result.get('line_no')
        line_info = f" (Line {line_no})" if line_no else ""
        
        st.markdown(f"""
        <div style='background-color: {COLORS['error']}; padding: 0.5rem 1rem; border-radius: 4px; display: inline-block;'>
            <span style='color: white; font-weight: bold;'>❌ Pre-flight Check: FAILED</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.error(f"**Syntax Error{line_info}:** {error_msg}")


def render_step_content(step, parser):
    """Render a walkthrough step with interactive features"""
    # Step header
    st.markdown(f"""
    <div style='background: {COLORS['surface']}; padding: 1.5rem; border-radius: 8px; border-left: 4px solid {COLORS['primary']};'>
        <h3 style='color: {COLORS['primary']}; margin: 0;'>
            Step {step.step_number}: {step.title}
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("##")
    
    # Main content area
    col_main, col_side = st.columns([2, 1])
    
    with col_main:
        # Explanation
        st.markdown("### 📖 Explanation")
        st.markdown(step.explanation)
        
        # Get code for selected engine
        current_engine = st.session_state.selected_engine
        code_to_show = parser.get_step_code_for_engine(step, current_engine)
        
        # Code section
        if code_to_show or step.code:
            st.markdown("### 💻 Code")
            
            # Engine indicator if dual-engine step
            if step.code_pandas and step.code_spark:
                st.info(f"🔧 Showing code for: **{current_engine.upper()}** engine (switch in sidebar)")
            
            # Show code
            display_code = code_to_show or step.code
            st.code(display_code, language=step.language or "python")
            
            # Show info for non-Python code
            if step.language and step.language not in ['python', 'py']:
                info_box(f"ℹ️ This is {step.language} code. Copy and run it in your terminal.")
            
            # Interactive execution (ONLY for Python)
            if step.is_runnable and step.language in ['python', 'py']:
                st.markdown("### ▶️ Run & See Output")
                
                # Pre-flight check (skip for demo blocks in learn mode)
                validation_mode = st.session_state.get('validation_mode', 'learn')
                skip_validation = step.is_demo and validation_mode == 'learn'
                
                preflight = st.session_state.code_executor.preflight_check(display_code)
                render_preflight_badge(preflight.to_dict(), is_demo=skip_validation)
                
                st.markdown("##")
                
                col_run, col_reset = st.columns([3, 1])
                
                with col_run:
                    run_disabled = not preflight.passed
                    if st.button(
                        "🚀 Run This Code", 
                        key=f"run_step_{step.step_number}", 
                        type="primary",
                        disabled=run_disabled,
                        help="Execute the code above" if not run_disabled else "Fix syntax errors first"
                    ):
                        with st.spinner("Executing..."):
                            # Ensure executor uses correct engine
                            st.session_state.code_executor.set_engine(current_engine)
                            
                            result = st.session_state.code_executor.execute(display_code)
                            
                            if result['success']:
                                st.toast("Execution complete ✅", icon="🎯")
                                success_box("✅ Code executed successfully!")
                                
                                if result['output']:
                                    st.markdown("**Output:**")
                                    st.text(result['output'])
                                
                                if result['result'] is not None:
                                    st.markdown("**Result:**")
                                    if isinstance(result['result'], pd.DataFrame):
                                        st.dataframe(result['result'], use_container_width=True)
                                    else:
                                        st.write(result['result'])
                                
                                if result['variables']:
                                    st.markdown("**Variables Created:**")
                                    for var_name, var_value in result['variables'].items():
                                        st.markdown(f"- `{var_name}`: {type(var_value).__name__}")
                                
                                # Mark step as completed
                                st.session_state.completed_steps.add(step.step_number)
                            else:
                                st.toast("Error detected ❌", icon="⚠️")
                                
                                # Collapsible error display
                                with st.expander("❌ Error Details", expanded=True):
                                    st.code(result['error'], language="text")
                
                with col_reset:
                    if st.button("🔄 Reset", key=f"reset_step_{step.step_number}"):
                        st.session_state.code_executor.reset_namespace()
                        st.toast("Environment reset ✅", icon="🔄")
                        st.success("Environment reset!")
                
                # Custom code input
                with st.expander("✏️ Modify & Experiment", expanded=False):
                    custom_code = st.text_area(
                        "Edit the code:",
                        value=display_code,
                        height=200,
                        key=f"custom_code_{step.step_number}"
                    )
                    
                    # Pre-flight for custom code
                    custom_preflight = st.session_state.code_executor.preflight_check(custom_code)
                    render_preflight_badge(custom_preflight.to_dict())
                    
                    st.markdown("##")
                    
                    if st.button(
                        "Run Modified Code", 
                        key=f"run_custom_{step.step_number}",
                        disabled=not custom_preflight.passed
                    ):
                        with st.spinner("Executing custom code..."):
                            st.session_state.code_executor.set_engine(current_engine)
                            result = st.session_state.code_executor.execute(custom_code)
                            
                            if result['success']:
                                st.toast("Custom code executed ✅", icon="🎯")
                                success_box("✅ Custom code executed!")
                                if result['output']:
                                    st.text(result['output'])
                                if result['result'] is not None:
                                    if isinstance(result['result'], pd.DataFrame):
                                        st.dataframe(result['result'], use_container_width=True)
                                    else:
                                        st.write(result['result'])
                            else:
                                st.toast("Error in custom code ❌", icon="⚠️")
                                with st.expander("Error Details", expanded=True):
                                    st.code(result['error'], language="text")
        
        elif not code_to_show and (step.code_pandas or step.code_spark):
            # No code available for current engine
            available_engines = []
            if step.code_pandas:
                available_engines.append("pandas")
            if step.code_spark:
                available_engines.append("spark")
            
            st.warning(f"No code available for **{current_engine}** engine. This step has code for: {', '.join(available_engines)}")
    
    with col_side:
        # Sidebar info
        st.markdown("### 📌 Quick Info")
        
        # Step status
        if step.step_number in st.session_state.completed_steps:
            st.markdown(f"<div style='background: {COLORS['success']}; padding: 0.5rem; border-radius: 4px; text-align: center;'>✅ Completed</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='background: {COLORS['surface']}; padding: 0.5rem; border-radius: 4px; text-align: center;'>⏳ Not Started</div>", unsafe_allow_html=True)
        
        st.markdown("##")
        
        # Engine info
        if step.engine:
            engine_label = step.engine.upper()
            st.markdown(f"**🔧 Engine:** {engine_label}")
        elif step.code_pandas and step.code_spark:
            st.markdown("**🔧 Engine:** Dual (Pandas + Spark)")
        
        st.markdown("##")
        
        # Tags
        if step.tags:
            st.markdown("**📍 Key Concepts:**")
            for tag in step.tags[:5]:
                st.markdown(f"- {tag}")
        
        # Related files
        if step.related_files:
            st.markdown("**📁 Related Files:**")
            for file in step.related_files[:5]:
                st.markdown(f"- `{file}`")
        
        st.markdown("##")
        
        # Learn More section
        with st.expander("🔍 Learn More", expanded=False):
            st.markdown("**Implementation Details**")
            
            # Try to show function source for ODIBI functions mentioned in code
            code_for_analysis = code_to_show or step.code
            if code_for_analysis:
                import re
                function_pattern = r'([a-zA-Z_][a-zA-Z0-9_]*)\('
                functions_found = re.findall(function_pattern, code_for_analysis)
                
                odibi_functions = []
                for func_name in set(functions_found):
                    if get_function_source(func_name):
                        odibi_functions.append(func_name)
                
                if odibi_functions:
                    selected_func = st.selectbox(
                        "View function source:",
                        options=["Select..."] + sorted(odibi_functions),
                        key=f"func_select_{step.step_number}"
                    )
                    
                    if selected_func != "Select...":
                        source = get_function_source(selected_func)
                        if source:
                            st.code(source, language="python")
                            
                            # Call stack info
                            st.markdown("**Call Stack:**")
                            call_info = get_function_call_stack(selected_func)
                            for info in call_info:
                                st.text(info)
            
            st.markdown("**Tips:**")
            st.markdown("- Use the debugger to step through code")
            st.markdown("- Check variable values with `print()`")
            st.markdown("- Experiment with different inputs")


def main():
    st.title("📚 Guided Learning")
    st.markdown(f"<p style='color: {COLORS['text_secondary']}; font-size: 1.1em;'>Step-by-step interactive walkthroughs to master ODIBI CORE</p>", unsafe_allow_html=True)
    
    # Info banner about persistent context
    info_box("ℹ️ **Session Context**: Variables, imports, and mock data persist across all steps in this walkthrough.")
    
    st.markdown("---")
    
    # Get parser
    parser = get_walkthrough_parser(ODIBI_ROOT)
    
    # Sidebar - Walkthrough selector
    with st.sidebar:
        st.markdown("### 📚 Select Walkthrough")
        
        walkthroughs = parser.list_walkthroughs()
        
        if not walkthroughs:
            error_box("No walkthroughs found!")
            return
        
        # Get manifest data for enhanced display
        manifest_loader = st.session_state.manifest_loader
        manifest_walkthroughs = {wt['filename']: wt for wt in manifest_loader.get_all_walkthroughs()}
        
        # Create selection options with manifest info
        walkthrough_options = {}
        for wt in walkthroughs:
            filename = wt['filename']
            manifest_data = manifest_walkthroughs.get(filename, {})
            
            # Add validation indicator
            if manifest_data:
                code_coverage = (manifest_data.get('code_blocks_valid', 0) / manifest_data.get('code_blocks_total', 1) * 100) if manifest_data.get('code_blocks_total', 0) > 0 else 100
                if code_coverage >= 90:
                    indicator = "✅"
                elif code_coverage >= 70:
                    indicator = "⚠️"
                else:
                    indicator = "❌"
                
                label = f"{indicator} {wt['title']} ({wt['duration']})"
            else:
                label = f"{wt['title']} ({wt['duration']})"
            
            walkthrough_options[label] = filename
        
        selected_title = st.selectbox(
            "Choose a lesson:",
            options=list(walkthrough_options.keys()),
            key="walkthrough_selector"
        )
        
        selected_filename = walkthrough_options[selected_title]
        
        # Load walkthrough
        if st.session_state.current_walkthrough != selected_filename:
            st.session_state.current_walkthrough = selected_filename
            st.session_state.current_step = 0
            st.session_state.completed_steps = set()
        
        st.markdown("---")
        
        # Show manifest info for selected walkthrough
        manifest_data = manifest_walkthroughs.get(selected_filename)
        if manifest_data:
            st.markdown("### 📊 Walkthrough Info")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Steps", manifest_data.get('total_steps', 0))
                st.metric("Code Blocks", manifest_data.get('code_blocks_total', 0))
            with col2:
                runnable = manifest_data.get('runnable_steps', 0)
                total = manifest_data.get('total_steps', 1)
                st.metric("Runnable", f"{runnable}/{total}")
                
                valid = manifest_data.get('code_blocks_valid', 0)
                total_blocks = manifest_data.get('code_blocks_total', 1)
                coverage = (valid / total_blocks * 100) if total_blocks > 0 else 100
                st.metric("Code Valid", f"{coverage:.0f}%")
            
            st.markdown("---")
        
        # Engine selector (sync with main app)
        current_engine = st.selectbox(
            "🔧 Execution Engine:",
            options=['pandas', 'spark'],
            index=0 if st.session_state.selected_engine == 'pandas' else 1,
            key="engine_selector_guided"
        )
        
        if current_engine != st.session_state.selected_engine:
            st.session_state.selected_engine = current_engine
            st.session_state.code_executor.set_engine(current_engine)
            st.toast(f"Engine switched to {current_engine.upper()} 🔄", icon="⚙️")
        
        st.markdown("---")
        
        # Validation mode toggle
        st.markdown("### 🎯 Validation Mode")
        validation_mode = st.radio(
            "Select mode:",
            options=['learn', 'teach'],
            format_func=lambda x: "🎓 Learn Mode (Skip demos)" if x == 'learn' else "🧠 Teach Mode (Validate all)",
            key="validation_mode_toggle",
            index=0 if st.session_state.validation_mode == 'learn' else 1
        )
        
        if validation_mode != st.session_state.validation_mode:
            st.session_state.validation_mode = validation_mode
            st.toast(f"Mode: {validation_mode.title()} 🔄", icon="🎯")
        
        if validation_mode == 'learn':
            st.caption("✓ Only validates runnable code\n✓ Skips [demo] examples")
        else:
            st.caption("✓ Validates all code blocks\n✓ Includes [demo] examples")
        
        st.markdown("---")
        
        # Progress summary
        walkthrough = parser.parse_walkthrough(ODIBI_ROOT / "docs" / "walkthroughs" / selected_filename)
        total_steps = len(walkthrough.steps)
        completed_count = len(st.session_state.completed_steps)
        
        st.markdown("### 📊 Progress")
        st.metric("Steps Completed", f"{completed_count}/{total_steps}")
        
        if total_steps > 0:
            progress_pct = (completed_count / total_steps) * 100
            st.progress(progress_pct / 100)
            st.markdown(f"<p style='text-align: center; color: {COLORS['text_secondary']};'>{progress_pct:.0f}% Complete</p>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Reset progress
        if st.button("🔄 Reset Progress", key="reset_progress_btn"):
            st.session_state.completed_steps = set()
            st.session_state.current_step = 0
            st.session_state.code_executor.reset_namespace()
            st.toast("Progress reset ✅", icon="🔄")
            st.success("Progress reset!")
            st.rerun()
    
    # Main content
    if st.session_state.current_walkthrough:
        walkthrough = parser.parse_walkthrough(
            ODIBI_ROOT / "docs" / "walkthroughs" / st.session_state.current_walkthrough
        )
        
        # Walkthrough header
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, {COLORS['primary']}22, {COLORS['secondary']}22); 
                    padding: 2rem; border-radius: 12px; margin-bottom: 2rem;'>
            <h2 style='color: {COLORS['primary']}; margin: 0;'>{walkthrough.title}</h2>
            <p style='color: {COLORS['text_secondary']}; margin-top: 0.5rem;'>
                👤 {walkthrough.author} | 📅 {walkthrough.date} | ⏱️ {walkthrough.duration}
            </p>
            <p style='margin-top: 1rem;'>{walkthrough.description}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Overview
        if walkthrough.overview:
            with st.expander("📋 Overview", expanded=False):
                st.markdown(walkthrough.overview)
        
        st.markdown("##")
        
        # Step navigation
        if walkthrough.steps:
            render_step_navigation(len(walkthrough.steps), location="top")
            
            st.markdown("##")
            
            # Current step
            current_step = walkthrough.steps[st.session_state.current_step]
            render_step_content(current_step, parser)
            
            st.markdown("##")
            
            # Bottom navigation
            render_step_navigation(len(walkthrough.steps), location="bottom")
        else:
            info_box("This walkthrough has no steps defined yet.")
    else:
        info_box("Please select a walkthrough from the sidebar to begin learning.")


if __name__ == "__main__":
    main()
