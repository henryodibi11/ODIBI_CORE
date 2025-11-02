---
id: learnodibi_studio
title: "LearnODIBI Studio: Platform Mechanics"
level: "Intermediate"
tags: ["learnodibi", "streamlit", "teaching"]
checkpoints: 8
quiz_questions: 24
---

# LearnODIBI Studio - Developer Walkthrough

**Guide to Understanding and Extending the Interactive Learning Platform**

**Author**: AMP AI Engineering Agent  
**Date**: November 2, 2025  
**Audience**: Developers maintaining or extending LearnODIBI Studio  
**Duration**: ~2 hours (to understand the complete system)

---

## 📚 Overview

### What is LearnODIBI Studio?

LearnODIBI Studio is an **interactive learning platform** built on Streamlit that transforms ODIBI CORE documentation into hands-on, executable lessons. It's designed to help users learn the framework through guided walkthroughs, live code execution, and visual exploration.

### Why This Architecture?

The platform follows a **modular design** with clear separation of concerns:

1. **Core Modules** - Reusable logic (parsing, execution, scaffolding)
2. **UI Pages** - Streamlit pages for different learning experiences
3. **Components** - Shared UI components (already existed)
4. **Theme** - Consistent styling across all pages

This allows developers to:
- Add new pages easily
- Reuse execution/parsing logic
- Maintain consistent UX
- Test components independently

### 🎯 Checkpoint 1: Understanding the Platform Vision
**Quiz 1**: What is the primary purpose of LearnODIBI Studio?  
a) Code deployment  
b) Interactive learning through executable lessons  
c) Database management  
d) Version control

**Quiz 2**: Which architecture pattern does LearnODIBI follow?  
a) Monolithic  
b) Modular with separation of concerns  
c) Microservices  
d) Event-driven

**Quiz 3**: Name the three core components of the platform architecture.

---

## 🗺️ Architecture Map

```
learnodibi_ui/
│
├── Core Application
│   ├── app.py                    # Main entry point, home page
│   ├── theme.py                  # Theming (colors, styles, helper functions)
│   └── utils.py                  # Session state, helper utilities
│
├── Learning Modules (Phase 10)
│   ├── walkthrough_parser.py    # Parse markdown walkthroughs → structured lessons
│   ├── code_executor.py          # Safe code execution with output capture
│   └── project_scaffolder.py    # Create learning projects from templates
│
├── Components (Pre-existing)
│   ├── config_editor.py          # JSON config editing UI
│   ├── data_preview.py           # DataFrame viewer with tabs
│   └── metrics_display.py        # Execution metrics visualization
│
└── Pages (Interactive Lessons)
    ├── 0_guided_learning.py      # [NEW] Step-by-step walkthroughs
    ├── 1_core.py                 # Core concepts (nodes, engines)
    ├── 2_functions.py            # Functions explorer
    ├── 3_sdk.py                  # SDK code examples
    ├── 4_demo_project.py         # Demo pipeline
    ├── 5_docs.py                 # Documentation browser
    ├── 6_new_project.py          # [NEW] Project scaffolding wizard
    ├── 7_engines.py              # [NEW] Pandas vs Spark comparison
    ├── 8_transformations.py      # [NEW] DAG visualization
    ├── 9_function_notebook.py    # [NEW] Jupyter-style notebook
    └── 10_logs_viewer.py         # [NEW] Real-time log monitoring
```

**[NEW]** = Added in Phase 10

### 🎯 Checkpoint 2: Directory Structure Mastery
**Quiz 4**: Where are the core learning modules located?  
a) learnodibi_ui/  
b) learnodibi_ui/pages/  
c) learnodibi_ui/ root level  
d) learnodibi_ui/components/

**Quiz 5**: Which files were added in Phase 10? (Select all that apply)  
a) 0_guided_learning.py  
b) config_editor.py  
c) project_scaffolder.py  
d) 1_core.py

**Quiz 6**: What is the purpose of the `theme.py` file?

---

## 🔧 Core Modules Deep Dive

### 1. Walkthrough Parser (`walkthrough_parser.py`)

**Purpose**: Parse markdown walkthrough files into structured Python objects.

**Key Classes**:

#### `WalkthroughStep`
```python
@dataclass
class WalkthroughStep:
    step_number: int           # Sequential step number
    title: str                 # Step title (e.g., "Create Project Structure")
    explanation: str           # Markdown explanation text
    code: Optional[str]        # Code snippet (if present)
    language: Optional[str]    # Code language (python, bash, toml, etc.)
    is_runnable: bool          # Can this code be executed?
    related_files: List[str]   # Files mentioned in text
    tags: List[str]            # Key concepts extracted
```

#### `Walkthrough`
```python
@dataclass
class Walkthrough:
    title: str                 # Main title
    filename: str              # Source file name
    description: str           # Brief description
    author: str                # Author name
    date: str                  # Creation date
    audience: str              # Target audience
    duration: str              # Estimated time
    steps: List[WalkthroughStep]  # All steps
    overview: str              # Overview section
```

#### `WalkthroughParser`
```python
class WalkthroughParser:
    def __init__(self, walkthroughs_dir: Path):
        """Initialize with directory containing walkthrough markdown files"""
    
    def list_walkthroughs(self) -> List[Dict[str, str]]:
        """Get list of all available walkthroughs"""
    
    def parse_walkthrough(self, filepath: Path) -> Walkthrough:
        """Parse a markdown file into Walkthrough object"""
```

**How It Works**:

1. **Regex Matching**: Uses regex to find sections like `### Mission 1: ...`
2. **Code Block Extraction**: Finds all ` ```python` code blocks
3. **Metadata Extraction**: Parses front-matter (author, date, etc.)
4. **Tag Generation**: Extracts key terms from text (bold terms, code terms)
5. **Caching**: Stores parsed walkthroughs to avoid re-parsing

**Example Usage**:
```python
from odibi_core.learnodibi_ui.walkthrough_parser import get_walkthrough_parser

parser = get_walkthrough_parser()
walkthroughs = parser.list_walkthroughs()

# Parse specific walkthrough
wt = parser.parse_walkthrough(Path("docs/walkthroughs/DEVELOPER_WALKTHROUGH_PHASE_1.md"))

# Access steps
for step in wt.steps:
    print(f"Step {step.step_number}: {step.title}")
    if step.code:
        print(f"  Has code ({step.language}): {step.is_runnable}")
```

**Adding New Patterns**:

If walkthroughs use different section headers, update `_extract_steps()`:

```python
# Current pattern
mission_pattern = r'###\s+(Mission|Step)\s+(\d+):\s+(.+?)\n\n((?:(?!###).)+)'

# To support "Exercise" as well:
mission_pattern = r'###\s+(Mission|Step|Exercise)\s+(\d+):\s+(.+?)\n\n((?:(?!###).)+)'
```

### 🎯 Checkpoint 3: Walkthrough Parser Understanding
**Quiz 7**: What dataclass represents a single step in a walkthrough?  
a) Walkthrough  
b) WalkthroughStep  
c) StepParser  
d) ParsedStep

**Quiz 8**: Which attribute in `WalkthroughStep` determines if code can be executed?  
a) code  
b) is_executable  
c) is_runnable  
d) runnable

**Quiz 9**: What regex pattern is used to find walkthrough sections?

---

### 2. Code Executor (`code_executor.py`)

**Purpose**: Safely execute user code with output capture and variable persistence.

**Key Class**:

#### `CodeExecutor`
```python
class CodeExecutor:
    def __init__(self):
        """Initialize execution environment with ODIBI CORE imports"""
    
    def execute(self, code: str, context: Dict = None) -> Dict:
        """
        Execute code and return results
        
        Returns:
            {
                'success': bool,
                'output': str (stdout),
                'error': str (if failed),
                'result': Any (last expression value),
                'variables': Dict (new vars created),
                'stderr': str
            }
        """
    
    def reset_namespace(self):
        """Reset execution environment to initial state"""
    
    def add_to_namespace(self, **kwargs):
        """Add variables to execution namespace"""
```

**How It Works**:

1. **Isolated Namespace**: Creates a dict with `__builtins__` and common imports
2. **Pre-imports**: Automatically imports `pandas`, `odibi_core` modules
3. **Output Capture**: Redirects stdout/stderr using `io.StringIO`
4. **Expression Handling**: Tries `eval()` for last line, falls back to `exec()`
5. **Variable Tracking**: Compares namespace before/after to find new vars
6. **Error Isolation**: Catches exceptions, returns formatted traceback

**Example Usage**:
```python
from odibi_core.learnodibi_ui.code_executor import CodeExecutor

executor = CodeExecutor()

# Execute code
result = executor.execute("""
import pandas as pd
df = pd.DataFrame({'a': [1,2,3]})
df['b'] = df['a'] * 2
df.sum()
""")

if result['success']:
    print("Output:", result['output'])
    print("Result:", result['result'])
    print("Variables:", result['variables'])  # {'df': DataFrame}
else:
    print("Error:", result['error'])

# Variables persist
result2 = executor.execute("df['c'] = df['a'] + df['b']")  # 'df' still available

# Reset to clean state
executor.reset_namespace()
```

**Security Considerations**:

The executor is **NOT sandboxed** - it runs in the same Python process. For a production environment with untrusted users, consider:

- Using `RestrictedPython` library
- Running in a Docker container
- Implementing timeout mechanisms
- Blocking dangerous imports (`os.system`, `subprocess`, etc.)

Current implementation is safe for **self-learning** scenarios where users execute their own code.

**Helper Functions**:

```python
def get_function_source(function_name: str, module_name: str = None) -> Optional[str]:
    """Get source code of a function using inspect.getsource()"""

def get_function_call_stack(function_name: str) -> List[str]:
    """Get signature and documentation for a function"""
```

### 🎯 Checkpoint 4: Code Execution Mechanics
**Quiz 10**: What method executes code and returns results?  
a) run()  
b) execute()  
c) execute_code()  
d) run_code()

**Quiz 11**: Which Python modules are used to capture stdout/stderr?  
a) sys  
b) io.StringIO  
c) capture  
d) logging

**Quiz 12**: Is the CodeExecutor sandboxed for production use?  
a) Yes  
b) No  
c) Only in Docker  
d) Depends on configuration

**Quiz 13**: What happens to variables created during code execution?

---

### 3. Project Scaffolder (`project_scaffolder.py`)

**Purpose**: Create new learning projects with proper directory structure.

**Key Class**:

#### `ProjectScaffolder`
```python
class ProjectScaffolder:
    def __init__(self):
        """Load project templates"""
    
    def validate_path(self, path: str) -> tuple[bool, str]:
        """
        Validate project path
        Returns: (is_valid, message)
        """
    
    def create_project(
        self, 
        path: str, 
        template: str = "basic",
        project_name: Optional[str] = None
    ) -> Dict[str, List[str]]:
        """
        Create new project
        Returns: {'folders': [...], 'files': [...], 'logs': [...]}
        """
```

**Templates Available**:

1. **basic** - Simple Bronze → Silver → Gold pipeline
2. **transformation** - Focus on data transformations
3. **functions** - Explore ODIBI functions

**How It Works**:

1. **Path Validation**:
   - Must be absolute path
   - Parent directory must exist
   - Warns if directory exists and is non-empty

2. **Folder Creation**:
   ```
   project/
   ├── configs/
   ├── data/
   │   ├── bronze/
   │   ├── silver/
   │   └── gold/
   ├── notebooks/
   └── logs/
   ```

3. **File Generation**:
   - `run_project.py` - Main pipeline script
   - `configs/pipeline_config.json` - Configuration
   - `README.md` - Project documentation
   - Template-specific files

4. **Logging**:
   - Returns detailed logs of creation process
   - Can be displayed in UI for transparency

**Example Usage**:
```python
from odibi_core.learnodibi_ui.project_scaffolder import ProjectScaffolder

scaffolder = ProjectScaffolder()

# Validate first
is_valid, msg = scaffolder.validate_path("/d:/projects/my_learning")
if not is_valid:
    print(f"Invalid: {msg}")
    exit()

# Create project
result = scaffolder.create_project(
    path="/d:/projects/my_learning",
    template="basic",
    project_name="My First Pipeline"
)

# Show logs
for log in result['logs']:
    print(log)

# Created files
print(f"Folders: {len(result['folders'])}")
print(f"Files: {len(result['files'])}")
```

**Adding New Templates**:

1. Create a method `_get_mytemplate_template()`:
```python
def _get_mytemplate_template(self) -> Dict[str, str]:
    return {
        "myfile.py": '''
# My custom template
print("Hello from {{PROJECT_NAME}}")
''',
        "configs/myconfig.json": {
            "key": "value"
        }
    }
```

2. Register in `_load_templates()`:
```python
def _load_templates(self):
    return {
        "basic": {...},
        "mytemplate": {  # Add here
            "name": "My Template",
            "description": "Does something cool",
            "files": self._get_mytemplate_template()
        }
    }
```

### 🎯 Checkpoint 5: Project Scaffolding
**Quiz 14**: How many default templates are available?  
a) 2  
b) 3  
c) 4  
d) 5

**Quiz 15**: What validation rule applies to project paths?  
a) Must be relative  
b) Must be absolute  
c) Can be either  
d) No validation

**Quiz 16**: Which folder structure is created in the data directory?  
a) raw/processed/clean  
b) bronze/silver/gold  
c) input/output  
d) source/target

---

## 🖥️ UI Pages Deep Dive

### Page 0: Guided Learning (`0_guided_learning.py`)

**Purpose**: Interactive step-by-step walkthroughs with live code execution.

**Architecture**:

```
┌─────────────────────────────────────────────────────┐
│                   Main Area                          │
│  ┌────────────────────────────────────────────────┐ │
│  │ Walkthrough Header (title, author, date)       │ │
│  └────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────┐ │
│  │ Navigation (First | Prev | Progress | Next)    │ │
│  └────────────────────────────────────────────────┘ │
│  ┌──────────────────────────┬───────────────────┐  │
│  │  Step Content            │   Sidebar         │  │
│  │  - Explanation           │   - Status        │  │
│  │  - Code Display          │   - Tags          │  │
│  │  - Run Button            │   - Related Files │  │
│  │  - Output Display        │   - Learn More    │  │
│  │  - Modify & Experiment   │                   │  │
│  └──────────────────────────┴───────────────────┘  │
└─────────────────────────────────────────────────────┘
```

**Key Functions**:

```python
def render_step_navigation(total_steps: int):
    """Render First/Prev/Next/Last buttons with progress bar"""

def render_step_content(step: WalkthroughStep):
    """
    Render a single step with:
    - Explanation markdown
    - Code display
    - Run & See Output button
    - Modify & Experiment section
    - Learn More sidebar
    """
```

**Session State Variables**:
```python
st.session_state.current_walkthrough  # Selected walkthrough filename
st.session_state.current_step         # Current step index (0-based)
st.session_state.completed_steps      # Set of completed step numbers
st.session_state.code_executor        # CodeExecutor instance
```

**Interaction Flow**:

1. User selects walkthrough from sidebar
2. `parse_walkthrough()` loads it
3. Navigation buttons control `current_step`
4. `render_step_content()` displays current step
5. "Run This Code" executes via `code_executor`
6. Results displayed inline
7. "Learn More" shows function source
8. Progress tracked in `completed_steps`

**Extending**:

To add features like **annotations** or **hints**:

```python
def render_step_content(step):
    # ... existing code ...
    
    # Add hint system
    if step.step_number in [1, 5, 10]:  # Key steps
        with st.expander("💡 Hint", expanded=False):
            st.markdown(get_hint_for_step(step.step_number))
```

### 🎯 Checkpoint 6: UI Page Architecture
**Quiz 17**: What is the main purpose of the `0_guided_learning.py` page?  
a) Code editing  
b) Interactive step-by-step walkthroughs  
c) Log viewing  
d) Configuration management

**Quiz 18**: Which session state variable tracks completed steps?  
a) progress_state  
b) completed_steps  
c) finished_steps  
d) step_tracker

**Quiz 19**: How does the page track the current step being displayed?

---

### Page 6: New Project (`6_new_project.py`)

**Purpose**: Wizard for creating learning projects with validation.

**Architecture**:

```
┌──────────────────────┬──────────────────────┐
│  Configuration       │  Preview/Logs         │
│  ┌────────────────┐  │  ┌────────────────┐  │
│  │ Path Input     │  │  │ Structure      │  │
│  │ Validation     │  │  │ Preview        │  │
│  └────────────────┘  │  └────────────────┘  │
│  ┌────────────────┐  │  ┌────────────────┐  │
│  │ Project Name   │  │  │ Creation Logs  │  │
│  └────────────────┘  │  │ (real-time)    │  │
│  ┌────────────────┐  │  └────────────────┘  │
│  │ Template       │  │                       │
│  │ Selection      │  │                       │
│  └────────────────┘  │                       │
│  ┌────────────────┐  │                       │
│  │ Create Button  │  │                       │
│  └────────────────┘  │                       │
└──────────────────────┴──────────────────────┘
```

**Validation Logic**:

```python
# Path validation
is_valid, msg = scaffolder.validate_path(project_path)

# Rules:
# 1. Must be absolute (Path.is_absolute())
# 2. Parent must exist (Path.parent.exists())
# 3. Warn if exists and non-empty (Path.exists() + Path.iterdir())
```

**Real-time Logging**:

Uses `st.session_state.creation_logs` to store logs, then displays them:

```python
# Store logs
st.session_state.creation_logs.append("Creating folder: configs/")

# Display logs
for log in st.session_state.creation_logs:
    st.code(log)
```

---

## 🎨 Theming System

**File**: `theme.py`

**Color Palette**:

```python
COLORS = {
    "primary": "#F5B400",      # ODIBI Gold
    "secondary": "#00796B",    # Teal
    "background": "#1E1E1E",   # Dark background
    "surface": "#2D2D2D",      # Card/panel background
    "text": "#FFFFFF",         # Primary text
    "text_secondary": "#B0B0B0",  # Secondary text
    "success": "#4CAF50",      # Green
    "warning": "#FF9800",      # Orange
    "error": "#F44336",        # Red
    "info": "#2196F3"          # Blue
}
```

**Helper Functions**:

```python
def apply_theme():
    """Apply custom CSS to Streamlit app"""
    st.markdown(f"""
    <style>
    .stApp {{
        background-color: {COLORS['background']};
    }}
    /* ... more CSS ... */
    </style>
    """, unsafe_allow_html=True)

def success_box(message: str):
    """Display success message box"""
    st.markdown(f"""
    <div style='background: {COLORS['success']}22; border-left: 4px solid {COLORS['success']}; 
                padding: 1rem; border-radius: 4px;'>
        {message}
    </div>
    """, unsafe_allow_html=True)

# Also: error_box, info_box, warning_box
```

**Usage in Pages**:

```python
from odibi_core.learnodibi_ui.theme import apply_theme, COLORS, success_box

st.set_page_config(...)
apply_theme()

# Use colors
st.markdown(f"<h1 style='color: {COLORS['primary']};'>Title</h1>", unsafe_allow_html=True)

# Use helper boxes
success_box("✅ Operation completed!")
```

### 🎯 Checkpoint 7: Theme & Styling
**Quiz 20**: What is the primary brand color for ODIBI?  
a) Teal  
b) Gold  
c) Blue  
d) Green

**Quiz 21**: Which function applies the custom theme to the Streamlit app?  
a) set_theme()  
b) apply_theme()  
c) load_theme()  
d) init_theme()

**Quiz 22**: Name three helper functions for displaying styled message boxes.

---

## 🔌 Integration Points

### How Modules Connect

```
┌─────────────────────────────────────────────────┐
│              Streamlit Page                      │
│                                                  │
│  ┌────────────┐    ┌─────────────┐              │
│  │ UI Widgets │───▶│ Code Input  │              │
│  └────────────┘    └─────────────┘              │
│                          │                       │
│                          ▼                       │
│                   ┌──────────────┐               │
│                   │ CodeExecutor │               │
│                   └──────────────┘               │
│                          │                       │
│                          ▼                       │
│                    ┌──────────┐                  │
│                    │ Results  │                  │
│                    └──────────┘                  │
│                          │                       │
│                          ▼                       │
│                   ┌──────────────┐               │
│                   │ UI Display   │               │
│                   └──────────────┘               │
└─────────────────────────────────────────────────┘
```

**Example: Guided Learning Flow**

1. **Page Loads**: `0_guided_learning.py`
2. **Parse Walkthroughs**: Uses `WalkthroughParser`
3. **User Clicks "Run"**: Button triggers callback
4. **Execute Code**: `CodeExecutor.execute(step.code)`
5. **Display Results**: Format output, show in UI
6. **"Learn More"**: `get_function_source()` fetches code
7. **Update State**: Mark step as completed

---

## 🧪 Testing Strategies

### Unit Testing Modules

**Test `walkthrough_parser.py`**:
```python
def test_parse_walkthrough():
    parser = WalkthroughParser(Path("docs/walkthroughs"))
    wt = parser.parse_walkthrough(Path("docs/walkthroughs/DEVELOPER_WALKTHROUGH_PHASE_1.md"))
    
    assert len(wt.steps) > 0
    assert wt.title != ""
    assert all(step.step_number > 0 for step in wt.steps)
```

**Test `code_executor.py`**:
```python
def test_execute_simple_code():
    executor = CodeExecutor()
    result = executor.execute("x = 10\nx * 2")
    
    assert result['success'] == True
    assert result['result'] == 20
    assert 'x' in result['variables']

def test_execute_error():
    executor = CodeExecutor()
    result = executor.execute("1 / 0")
    
    assert result['success'] == False
    assert 'ZeroDivisionError' in result['error']
```

**Test `project_scaffolder.py`**:
```python
def test_validate_path():
    scaffolder = ProjectScaffolder()
    
    # Invalid: relative path
    is_valid, msg = scaffolder.validate_path("relative/path")
    assert not is_valid
    
    # Valid: absolute path
    is_valid, msg = scaffolder.validate_path("/d:/projects/test")
    assert is_valid

def test_create_project(tmp_path):
    scaffolder = ProjectScaffolder()
    project_path = tmp_path / "test_project"
    
    result = scaffolder.create_project(str(project_path), "basic")
    
    assert (project_path / "run_project.py").exists()
    assert (project_path / "configs").exists()
```

### Integration Testing Pages

**Test Page Loading**:
```python
def test_guided_learning_loads():
    """Test page imports and basic setup"""
    from odibi_core.learnodibi_ui.pages import guided_learning_0
    # No import errors = success
```

**Manual UI Testing**:

Use this checklist for manual validation:

- [ ] Can select walkthrough from dropdown
- [ ] Navigation buttons work (First, Prev, Next, Last)
- [ ] Progress bar updates correctly
- [ ] Code executes when "Run" clicked
- [ ] Output displays properly
- [ ] "Learn More" expands and shows source
- [ ] Completed steps are tracked
- [ ] Reset progress works

---

## 📝 Adding New Pages

### Step-by-Step Guide

**1. Create Page File**

```python
# odibi_core/learnodibi_ui/pages/11_my_new_page.py

import streamlit as st
from pathlib import Path
import sys

# Add odibi_core to path
ODIBI_ROOT = Path(__file__).parent.parent.parent.parent
if str(ODIBI_ROOT) not in sys.path:
    sys.path.insert(0, str(ODIBI_ROOT))

from odibi_core.learnodibi_ui.theme import apply_theme, COLORS, success_box
from odibi_core.learnodibi_ui.utils import initialize_session_state

# Page config (MUST be first Streamlit command)
st.set_page_config(
    page_title="My Page - ODB-CORE Studio",
    page_icon="🎯",
    layout="wide"
)

apply_theme()
initialize_session_state()

def main():
    st.title("🎯 My New Page")
    st.markdown(f"<p style='color: {COLORS['text_secondary']};'>Description</p>", 
                unsafe_allow_html=True)
    
    # Your page content here
    st.write("Hello from my new page!")

if __name__ == "__main__":
    main()
```

**2. Streamlit Auto-Discovery**

Streamlit automatically adds pages from `pages/` directory. Just name files with number prefix: `11_my_new_page.py`

**3. Use Theme**

Always import and apply theme:
```python
from odibi_core.learnodibi_ui.theme import apply_theme, COLORS
apply_theme()
```

**4. Session State**

Use `st.session_state` for persistence:
```python
if 'my_data' not in st.session_state:
    st.session_state.my_data = []
```

**5. Reuse Components**

```python
from odibi_core.learnodibi_ui.components import data_preview
data_preview(my_dataframe, title="My Data")
```

### 🎯 Checkpoint 8: Extension & Deployment
**Quiz 23**: What must be the first Streamlit command in a page file?  
a) apply_theme()  
b) st.title()  
c) st.set_page_config()  
d) initialize_session_state()

**Quiz 24**: How does Streamlit discover new pages?  
a) Manual registration  
b) Auto-discovery from pages/ directory  
c) Config file  
d) Import statements

---

## 🚀 Deployment

### Running Locally

```bash
cd /d:/projects/odibi_core
python -m streamlit run odibi_core\learnodibi_ui\app.py
```

### Running on Server

**Option 1: Streamlit Cloud**
1. Push to GitHub
2. Connect Streamlit Cloud
3. Deploy `odibi_core/learnodibi_ui/app.py`

**Option 2: Docker**
```dockerfile
FROM python:3.10
WORKDIR /app
COPY . .
RUN pip install -e .
EXPOSE 8501
CMD ["streamlit", "run", "odibi_core/learnodibi_ui/app.py"]
```

**Option 3: Custom Server**
```bash
# Install screen or tmux
apt-get install screen

# Start in background
screen -S learnodibi
streamlit run odibi_core/learnodibi_ui/app.py --server.port 8501
# Ctrl+A, D to detach
```

---

## 🐛 Common Issues & Solutions

### Issue: Import Errors

**Problem**: `ModuleNotFoundError: No module named 'odibi_core'`

**Solution**: Ensure ODIBI CORE is installed:
```bash
cd /d:/projects/odibi_core
pip install -e .
```

### Issue: Walkthrough Not Loading

**Problem**: Selected walkthrough shows no steps

**Solution**: Check:
1. Walkthrough file exists in `docs/walkthroughs/`
2. File follows naming convention `DEVELOPER_WALKTHROUGH_*.md`
3. File has proper `### Mission N:` or `### Step N:` headers

### Issue: Code Execution Fails

**Problem**: "Code executed but no output"

**Solution**: 
- Ensure code has `print()` statements or returns a value
- Check if last line is an expression (will be evaluated)
- Use `st.session_state.code_executor.reset_namespace()` to reset

### Issue: Theming Not Applied

**Problem**: UI shows default Streamlit theme

**Solution**:
```python
# Ensure apply_theme() is called AFTER st.set_page_config()
st.set_page_config(...)  # FIRST
apply_theme()            # SECOND
```

---

## 📈 Future Enhancements

### Potential Additions

1. **Quiz Mode**
   - Add quizzes after each walkthrough section
   - Track scores
   - Certificate generation

2. **Video Integration**
   - Embed YouTube videos
   - Sync with walkthrough steps

3. **AI Tutor**
   - GPT-powered Q&A
   - Context-aware help
   - Code suggestions

4. **Collaboration**
   - Share progress
   - Team leaderboards
   - Discussion forums

5. **Advanced Analytics**
   - Time spent per step
   - Common errors tracking
   - Completion rates

### Extension Points

**Adding Custom Transformations**:
```python
# In 8_transformations.py
CUSTOM_PIPELINES = {
    "my_pipeline": {
        "name": "My Custom Pipeline",
        "bronze": lambda: my_bronze_func(),
        "silver": lambda bronze: my_silver_func(bronze),
        "gold": lambda silver: my_gold_func(silver)
    }
}
```

**Adding Custom Functions**:
```python
# In 9_function_notebook.py
from my_custom_module import my_functions
# Add to function browser
```

---

## 🏆 Best Practices

### Code Style

1. **Type Hints**: Use for function parameters and returns
```python
def parse_walkthrough(self, filepath: Path) -> Walkthrough:
```

2. **Docstrings**: Google-style docstrings
```python
def execute(self, code: str) -> Dict[str, Any]:
    """
    Execute code safely.
    
    Args:
        code: Python code string
        
    Returns:
        Dict with success, output, error, result, variables
    """
```

3. **Error Handling**: Catch specific exceptions
```python
try:
    result = execute_code(code)
except CodeExecutionError as e:
    error_box(f"Execution failed: {e}")
```

### UI/UX

1. **Responsive Layout**: Use `st.columns()` for multi-column layouts
2. **Loading States**: Use `with st.spinner()` for long operations
3. **Error Messages**: User-friendly, actionable errors
4. **Progress Indicators**: Show progress for multi-step operations

### Performance

1. **Caching**: Use `@st.cache_data` for expensive computations
```python
@st.cache_data
def load_large_dataset():
    return pd.read_csv("large_file.csv")
```

2. **Lazy Loading**: Load data only when needed
3. **Session State**: Minimize state variables

---

## 📚 Resources

### Documentation

- **Streamlit Docs**: https://docs.streamlit.io
- **ODIBI CORE Docs**: See `docs/` folder
- **Python Markdown**: https://python-markdown.github.io

### Related Files

- [PHASE_10_LEARNODIBI_COMPLETE.md](file:///d:/projects/odibi_core/PHASE_10_LEARNODIBI_COMPLETE.md) - Implementation summary
- [LEARNODIBI_STUDIO_VALIDATION.md](file:///d:/projects/odibi_core/LEARNODIBI_STUDIO_VALIDATION.md) - Validation report
- [UI_REBUILD_COMPLETE.md](file:///d:/projects/odibi_core/UI_REBUILD_COMPLETE.md) - Previous UI work

---

## 🎯 Summary

LearnODIBI Studio is a **modular, extensible, educational platform** that transforms static documentation into interactive learning experiences.

**Key Takeaways**:

✅ **3 Core Modules**: Parser, Executor, Scaffolder  
✅ **6 New Pages**: Covering all aspects of learning ODIBI CORE  
✅ **Consistent Theme**: Dark with gold/teal accents  
✅ **Safe Execution**: Isolated code execution environment  
✅ **Extensible**: Easy to add pages, templates, features  

**For Developers**:
- Understand the module architecture
- Know how pages integrate with core modules
- Follow best practices for consistency
- Test thoroughly before deploying

**For Users**:
- Start with Guided Learning
- Create projects to practice
- Explore engines and transformations
- Use function notebook for experimentation
- Monitor with logs viewer

---

**Walkthrough Complete!**  
**Author**: AMP AI Assistant  
**Date**: November 2, 2025  
**Status**: Ready for Extension and Deployment
