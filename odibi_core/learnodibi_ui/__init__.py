"""
ODIBI CORE Studio - Interactive Learning Platform
An interactive Streamlit-based learning environment for ODIBI CORE framework

Phase 10 Enhanced:
- Guided step-by-step walkthroughs with live code execution
- Project scaffolding wizard
- Engine comparison (Pandas vs Spark)
- Transformation DAG visualization
- Function notebook interface
- Real-time logs viewer

Created by Henry Odibi
"""

__version__ = "1.1.0"
__author__ = "Henry Odibi"

# Core modules (can be imported for programmatic use)
from odibi_core.learnodibi_ui.walkthrough_parser import WalkthroughParser, get_walkthrough_parser
from odibi_core.learnodibi_ui.code_executor import CodeExecutor, execute_code_snippet
from odibi_core.learnodibi_ui.project_scaffolder import ProjectScaffolder

# Don't import app here - it causes set_page_config issues with Streamlit multipage
# Users should run: streamlit run odibi_core/learnodibi_ui/app.py

__all__ = [
    'WalkthroughParser',
    'get_walkthrough_parser',
    'CodeExecutor',
    'execute_code_snippet',
    'ProjectScaffolder',
]
