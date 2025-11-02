"""
New Project - Interactive project scaffolding wizard
"""

import streamlit as st
import sys
from pathlib import Path

# Add odibi_core to path
ODIBI_ROOT = Path(__file__).parent.parent.parent.parent
if str(ODIBI_ROOT) not in sys.path:
    sys.path.insert(0, str(ODIBI_ROOT))

from odibi_core.learnodibi_ui.theme import apply_theme, COLORS, success_box, error_box, info_box, warning_box
from odibi_core.learnodibi_ui.project_scaffolder import ProjectScaffolder
from odibi_core.learnodibi_ui.utils import initialize_session_state

# Page config
st.set_page_config(
    page_title="New Project - ODIBI CORE Studio",
    page_icon="🆕",
    layout="wide"
)

apply_theme()
initialize_session_state()

# Initialize session state
if 'scaffolder' not in st.session_state:
    st.session_state.scaffolder = ProjectScaffolder()
if 'creation_logs' not in st.session_state:
    st.session_state.creation_logs = []


def main():
    st.title("🆕 Create New Learning Project")
    st.markdown(f"<p style='color: {COLORS['text_secondary']}; font-size: 1.1em;'>Scaffold a new ODIBI CORE project with proper structure</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Two-column layout
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.markdown("### 📋 Project Configuration")
        
        # Project path
        st.markdown("#### 📁 Where do you want to create your learning project?")
        
        info_box("💡 Provide an **absolute path** (e.g., /d:/projects/my_learning_project)")
        
        project_path = st.text_input(
            "Project Location:",
            value="",
            placeholder="e.g., /d:/projects/my_odibi_project",
            help="Full path where the project will be created"
        )
        
        # Validate path
        if project_path:
            is_valid, validation_msg = st.session_state.scaffolder.validate_path(project_path)
            
            if is_valid:
                success_box(f"✅ {validation_msg}")
            else:
                error_box(f"❌ {validation_msg}")
        
        st.markdown("##")
        
        # Project name
        project_name = st.text_input(
            "Project Name:",
            value="" if not project_path else Path(project_path).name,
            help="Human-readable name for your project"
        )
        
        st.markdown("##")
        
        # Template selection
        st.markdown("#### 🎨 Choose a Template")
        
        templates = st.session_state.scaffolder.templates
        
        template_options = {
            f"**{data['name']}** - {data['description']}": key
            for key, data in templates.items()
        }
        
        selected_template_display = st.radio(
            "Template:",
            options=list(template_options.keys()),
            index=0
        )
        
        selected_template = template_options[selected_template_display]
        
        # Template preview
        template_data = templates[selected_template]
        with st.expander("📄 Template Details", expanded=False):
            st.markdown(f"**Name**: {template_data['name']}")
            st.markdown(f"**Description**: {template_data['description']}")
            st.markdown("**Includes**:")
            for filename in template_data['files'].keys():
                st.markdown(f"- `{filename}`")
        
        st.markdown("##")
        
        # Create button
        can_create = project_path and project_name
        
        if st.button(
            "🚀 Create Project",
            type="primary",
            disabled=not can_create,
            use_container_width=True
        ):
            try:
                # Validate again
                is_valid, validation_msg = st.session_state.scaffolder.validate_path(project_path)
                
                if not is_valid:
                    error_box(f"Cannot create project: {validation_msg}")
                else:
                    with st.spinner("Creating project..."):
                        result = st.session_state.scaffolder.create_project(
                            path=project_path,
                            template=selected_template,
                            project_name=project_name
                        )
                        
                        st.session_state.creation_logs = result['logs']
                        
                        success_box("🎉 Project created successfully!")
                        
                        # Show quick start
                        st.markdown("### 🚀 Quick Start")
                        st.code(f"""# Navigate to your project
cd {project_path}

# Run the pipeline
python run_project.py

# Or open in your IDE
code .
""", language="bash")
            
            except Exception as e:
                error_box(f"Failed to create project: {str(e)}")
    
    with col_right:
        st.markdown("### 📊 Project Structure Preview")
        
        # Show what will be created
        st.markdown(f"""
        <div style='background: {COLORS['surface']}; padding: 1.5rem; border-radius: 8px; font-family: monospace;'>
        📁 {project_name or "your_project"}/
        ├── 📁 configs/
        │   └── 📄 pipeline_config.json
        ├── 📁 data/
        │   ├── 📁 bronze/
        │   ├── 📁 silver/
        │   └── 📁 gold/
        ├── 📁 notebooks/
        ├── 📁 logs/
        ├── 📄 run_project.py
        └── 📄 README.md
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("##")
        
        # Creation logs
        if st.session_state.creation_logs:
            st.markdown("### 📝 Creation Log")
            
            log_container = st.container()
            with log_container:
                for log in st.session_state.creation_logs:
                    if log.startswith("✅"):
                        st.success(log)
                    elif log.startswith("❌"):
                        st.error(log)
                    elif log.startswith("🎉"):
                        st.balloons()
                        st.success(log)
                    elif log:
                        st.info(log)
        
        else:
            st.markdown("### 💡 Tips")
            
            info_box("""
            **Best Practices**:
            - Choose a descriptive project name
            - Use the basic template to start learning
            - Explore the generated files to understand the structure
            - Run `python run_project.py` to see it in action
            """)
            
            st.markdown("##")
            
            st.markdown("### 📚 What You'll Learn")
            st.markdown("""
            - 🏗️ **Project Structure** - Medallion architecture (Bronze → Silver → Gold)
            - ⚙️ **Configuration** - JSON-based pipeline configuration
            - 📊 **Data Processing** - Using ODIBI CORE nodes
            - 🔄 **Transformations** - Building data pipelines
            - 📈 **Best Practices** - Industry-standard patterns
            """)
    
    st.markdown("---")
    
    # Help section
    with st.expander("❓ Need Help?", expanded=False):
        st.markdown("""
        ### Common Questions
        
        **Q: What's an absolute path?**  
        A: A full path starting from the root, like `/d:/projects/my_project` (Windows) or `/home/user/projects/my_project` (Linux/Mac).
        
        **Q: Where should I create my project?**  
        A: Anywhere you have write permissions. Common locations:
        - Windows: `D:/projects/`, `C:/Users/YourName/Documents/`
        - Linux/Mac: `/home/username/projects/`, `~/projects/`
        
        **Q: Can I modify the generated files?**  
        A: Absolutely! The scaffolded project is a starting point. Customize it to your needs.
        
        **Q: What if the directory already exists?**  
        A: The wizard will check and warn you. You can choose a different location.
        
        **Q: Which template should I choose?**  
        A: 
        - **Basic Pipeline**: Start here if you're new to ODIBI CORE
        - **Transformation Focus**: If you want to explore data transformations
        - **Functions Playground**: To experiment with ODIBI functions
        """)


if __name__ == "__main__":
    main()
