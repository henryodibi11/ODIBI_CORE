"""
ODIBI CORE Studio - Main Application
Interactive Learning Platform for ODIBI CORE Framework
Created by Henry Odibi
"""

import streamlit as st

# Page configuration MUST be first Streamlit command
st.set_page_config(
    page_title="ODIBI CORE Studio",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

import sys
from pathlib import Path

# Add odibi_core to path
ODIBI_ROOT = Path(__file__).parent.parent.parent
if str(ODIBI_ROOT) not in sys.path:
    sys.path.insert(0, str(ODIBI_ROOT))

from odibi_core.learnodibi_ui.theme import apply_theme, COLORS
from odibi_core.learnodibi_ui.utils import initialize_session_state, splash_screen

# Apply custom theme
apply_theme()

# Initialize session state
initialize_session_state()

# Splash screen on first load
splash_screen()


def render_sidebar():
    """Render consistent sidebar across all pages"""
    with st.sidebar:
        st.markdown(f"""
        <div style='text-align: center; padding: 1rem;'>
            <h1 style='color: {COLORS['primary']}; margin: 0;'>🔧 ODIBI CORE</h1>
            <h3 style='color: {COLORS['secondary']}; margin: 0;'>Studio</h3>
            <p style='color: {COLORS['text_secondary']}; font-size: 0.9em;'>
                Interactive Learning Platform<br/>
                <strong>by Henry Odibi</strong>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Version info
        try:
            from odibi_core.__version__ import __version__
            st.info(f"📦 Version: {__version__}")
        except:
            st.info("📦 Version: 1.0.0")
        
        st.markdown("---")
        
        # Engine selector (persistent across sessions)
        if 'selected_engine' not in st.session_state:
            st.session_state.selected_engine = 'pandas'
        
        st.markdown("### ⚙️ Engine Settings")
        engine = st.selectbox(
            "Execution Engine:",
            options=['pandas', 'spark'],
            index=0 if st.session_state.selected_engine == 'pandas' else 1,
            key="engine_selector_main",
            help="Choose the default engine for code execution"
        )
        
        if engine != st.session_state.selected_engine:
            st.session_state.selected_engine = engine
            st.toast(f"Engine switched to {engine.upper()} 🔄", icon="⚙️")
        
        st.markdown("---")
        
        # Quick Start Guide
        with st.expander("🚀 Quick Start", expanded=False):
            st.markdown("""
            **Welcome to ODIBI CORE Studio!**
            
            1. **Guided Learning** - Step-by-step walkthroughs
            2. **Core Concepts** - Learn the fundamentals
            3. **Functions Explorer** - Discover 83+ real functions
            4. **Demo Project** - Run interactive pipelines
            5. **New Project** - Create your own pipeline
            
            Navigate using the pages menu above.
            """)
        
        # Navigation Guide
        with st.expander("📚 Navigation Guide", expanded=False):
            st.markdown("""
            **Main Sections:**
            
            - 🏠 **Home** - Overview and getting started
            - 📚 **Guided Learning** - Interactive walkthroughs
            - 🔧 **Core Concepts** - Node types and architecture
            - 🔍 **Functions Explorer** - Browse all functions
            - 📖 **SDK Examples** - Real code patterns
            - 🎯 **Demo Project** - Complete pipeline
            - ⚙️ **Engines** - Pandas vs Spark
            - 🔄 **Transformations** - Data transformations
            - 📊 **Logs Viewer** - Execution logs
            - 🗺️ **DAG Visualizer** - Pipeline visualization
            """)
        
        st.markdown("---")
        
        # Theme toggle (placeholder for future dark mode)
        theme_mode = st.radio(
            "🎨 Theme",
            options=["Light", "Dark"],
            index=0,
            key="theme_toggle_main",
            help="Toggle between light and dark themes"
        )
        
        if theme_mode == "Dark":
            st.info("🌙 Dark mode coming soon!")
        
        st.markdown("---")
        
        # Support info
        st.markdown(f"""
        <div style='text-align: center; padding: 1rem; background-color: {COLORS['surface']}; border-radius: 8px;'>
            <p style='color: {COLORS['text_secondary']}; font-size: 0.85em; margin: 0;'>
                💡 <strong>Need Help?</strong><br/>
                Check the <em>Docs</em> page or view examples in <em>SDK Examples</em>
            </p>
        </div>
        """, unsafe_allow_html=True)


def main():
    """Main application entry point"""
    
    # Render sidebar
    render_sidebar()
    
    # Main content
    st.title("🏠 Welcome to ODIBI CORE Studio")
    
    st.markdown(f"""
    <div style='background-color: {COLORS['surface']}; padding: 2rem; border-radius: 12px; margin: 1rem 0;'>
        <h2 style='color: {COLORS['primary']}; margin-top: 0;'>Your Interactive Learning Platform</h2>
        <p style='font-size: 1.1em; line-height: 1.6;'>
            ODIBI CORE Studio is a comprehensive interactive environment designed to help you master the 
            <strong>ODIBI CORE</strong> data engineering framework. Whether you're just starting out or 
            looking to deepen your understanding, this platform provides hands-on learning experiences.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature cards
    st.markdown("### ✨ Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div style='background-color: {COLORS['surface']}; padding: 1.5rem; border-radius: 8px; height: 100%;'>
            <h3 style='color: {COLORS['primary']};'>🎓 Learn by Doing</h3>
            <p>Interactive examples and live code execution help you understand concepts through practice.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style='background-color: {COLORS['surface']}; padding: 1.5rem; border-radius: 8px; height: 100%;'>
            <h3 style='color: {COLORS['primary']};'>🔍 Explore Functions</h3>
            <p>Browse and test over 100+ data engineering functions with real-time parameter inputs.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style='background-color: {COLORS['surface']}; padding: 1.5rem; border-radius: 8px; height: 100%;'>
            <h3 style='color: {COLORS['primary']};'>⚡ Build Pipelines</h3>
            <p>Create end-to-end data pipelines using the medallion architecture (Bronze → Silver → Gold).</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br/>", unsafe_allow_html=True)
    
    # Getting Started
    st.markdown("### 🚀 Getting Started")
    
    tab1, tab2, tab3 = st.tabs(["📖 Overview", "🎯 Quick Tour", "💡 Tips"])
    
    with tab1:
        st.markdown("""
        #### What is ODIBI CORE?
        
        ODIBI CORE is a modern data engineering framework built on five canonical node types:
        
        - **ConnectNode** 🔌 - Establish connections to data sources
        - **IngestNode** 📥 - Read data into DataFrames
        - **TransformNode** ⚙️ - Apply transformations and business logic
        - **StoreNode** 💾 - Persist data to storage layers
        - **PublishNode** 📤 - Expose data to consumers
        
        Each node is designed for composability, reusability, and observability.
        """)
        
        st.info("👉 Visit the **Core Concepts** page to learn more about each node type.")
    
    with tab2:
        st.markdown("""
        #### Take a Quick Tour
        
        1. **Start with Core Concepts** - Understand the fundamental building blocks
        2. **Explore Functions** - Discover the rich library of utilities
        3. **Try SDK Examples** - See real code patterns in action
        4. **Run the Demo Project** - Experience a complete data pipeline
        5. **Read the Docs** - Dive deeper into specific topics
        
        Each page includes interactive elements - don't hesitate to click buttons and experiment!
        """)
        
        if st.button("🚀 Start with Core Concepts", use_container_width=True, key="start_core_concepts_btn"):
            st.toast("Navigate to **1_core** in the sidebar 👈", icon="🎯")
    
    with tab3:
        st.markdown("""
        #### Pro Tips 💡
        
        - **Use the sidebar** to navigate between pages
        - **Click "Try It" buttons** to run code examples
        - **Experiment with parameters** in the Functions Explorer
        - **Download results** from the Demo Project
        - **Check the tooltips** (ℹ️) for additional context
        - **View execution metrics** to understand performance
        - **Switch engines** in sidebar (Pandas ⇄ Spark)
        
        #### Keyboard Shortcuts ⌨️
        
        - `Ctrl + K` - Focus search
        - `R` - Rerun the app
        - `C` - Clear cache
        """)
    
    # Announcements section
    st.markdown("---")
    st.markdown("### 📢 Latest Updates")
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.container():
            st.markdown(f"""
            <div style='background-color: {COLORS['info']}; padding: 1rem; border-radius: 8px;'>
                <h4 style='margin-top: 0;'>🆕 Engine-Aware Execution</h4>
                <p>Code snippets now support both Pandas and Spark engines with automatic namespace isolation!</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        with st.container():
            st.markdown(f"""
            <div style='background-color: {COLORS['success']}; padding: 1rem; border-radius: 8px;'>
                <h4 style='margin-top: 0;'>✅ Pre-flight Validation</h4>
                <p>All code is now syntax-checked before execution to prevent crashes!</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown(f"""
        <div style='text-align: center; color: {COLORS['text_secondary']}; padding: 1rem;'>
            <p style='margin: 0;'>
                Made with ❤️ by <strong>Henry Odibi</strong><br/>
                <small>Powered by ODIBI CORE Framework</small>
            </p>
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
