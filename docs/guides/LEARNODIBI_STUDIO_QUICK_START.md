# LearnODIBI Studio - Quick Start Guide 🚀

**Version**: 1.1.0 (Phase 10 Enhanced)  
**Date**: November 2, 2025

---

## 🎯 What's New in Phase 10?

LearnODIBI Studio now includes **6 powerful new pages** for interactive learning:

### ✨ New Features

1. **📚 Guided Learning** (Page 0)
   - Step-by-step walkthroughs from all documentation
   - "Run & See Output" buttons for every code snippet
   - "Learn More" toggles showing function internals
   - Progress tracking and bookmarking

2. **🆕 New Project Wizard** (Page 6)
   - Interactive project scaffolding
   - Path validation: "Where do you want to create your learning project?"
   - 3 templates: Basic, Transformation Focus, Functions Playground
   - Real-time creation logging

3. **⚙️ Engines Explorer** (Page 7)
   - Live Pandas vs Spark comparison
   - Performance benchmarks
   - Side-by-side code examples
   - Best practices guide

4. **🔄 Transformations** (Page 8)
   - DAG visualization with Mermaid diagrams
   - Bronze → Silver → Gold pipeline explorer
   - Before/after data previews
   - SQL vs Functions comparison

5. **📓 Function Notebook** (Page 9)
   - Jupyter-style cell-based interface
   - Browse and test 100+ functions
   - Chain multiple function calls
   - Export as Python script

6. **📋 Logs Viewer** (Page 10)
   - Real-time execution monitoring
   - Color-coded log levels
   - Analysis dashboard with charts
   - Export logs to CSV

---

## 🚀 Getting Started

### 1. Launch the Studio

```bash
# Navigate to project root
cd /d:/projects/odibi_core

# Run the studio
python -m streamlit run odibi_core\learnodibi_ui\app.py

# Or use the launcher
.\run_studio.bat
```

The studio will open at: **http://localhost:8501**

### 2. Start Learning!

**Recommended Path**:

```
📚 Guided Learning → 🆕 New Project → ⚙️ Engines → 🔄 Transformations → 📓 Functions → 📋 Logs
```

#### Step 1: Guided Learning
- Open **"Guided Learning"** page
- Select **"Phase 1"** walkthrough
- Follow steps one by one
- Click **"Run This Code"** to execute examples
- Use **"Learn More"** to see internals

#### Step 2: Create Your Project
- Go to **"New Project"** page
- Enter path: `/d:/projects/my_odibi_learning`
- Select **"Basic Pipeline"** template
- Click **"Create Project"**
- Watch real-time creation logs

#### Step 3: Explore Engines
- Navigate to **"Engines"** page
- Run live comparisons: Pandas vs Spark
- See performance differences
- Learn when to use which engine

#### Step 4: Build Pipelines
- Open **"Transformations"** page
- View DAG diagrams
- Execute Bronze → Silver → Gold
- See data transformation in action

#### Step 5: Experiment with Functions
- Go to **"Function Notebook"**
- Browse functions by category
- Insert templates and run
- Chain multiple functions
- Export your experiments

#### Step 6: Monitor Execution
- Check **"Logs Viewer"**
- Run demo pipeline
- Analyze execution patterns
- Export logs for debugging

---

## 📂 File Structure

```
odibi_core/learnodibi_ui/
├── Core Application
│   ├── app.py                    # Main entry point
│   ├── theme.py                  # Dark theme with gold/teal
│   └── utils.py                  # Utilities
│
├── New Learning Modules
│   ├── walkthrough_parser.py    # ✨ Parse markdown lessons
│   ├── code_executor.py          # ✨ Safe code execution
│   └── project_scaffolder.py    # ✨ Project creation
│
├── Components
│   ├── config_editor.py
│   ├── data_preview.py
│   └── metrics_display.py
│
└── Pages
    ├── 0_guided_learning.py      # ✨ NEW: Interactive walkthroughs
    ├── 1_core.py                 # Core concepts
    ├── 2_functions.py            # Functions explorer
    ├── 3_sdk.py                  # SDK examples
    ├── 4_demo_project.py         # Demo pipeline
    ├── 5_docs.py                 # Documentation
    ├── 6_new_project.py          # ✨ NEW: Project wizard
    ├── 7_engines.py              # ✨ NEW: Engine comparison
    ├── 8_transformations.py      # ✨ NEW: DAG visualization
    ├── 9_function_notebook.py    # ✨ NEW: Notebook interface
    └── 10_logs_viewer.py         # ✨ NEW: Log monitoring
```

**✨ = New in Phase 10**

---

## 🎨 Theme

LearnODIBI Studio features a professional dark theme:

- **Primary**: #F5B400 (ODIBI Gold)
- **Secondary**: #00796B (Teal)
- **Background**: #1E1E1E (Dark)
- **Text**: #FFFFFF (White)

---

## 💡 Tips & Tricks

### Guided Learning
- ✅ Use **"Modify & Experiment"** to test variations
- ✅ Click **"Learn More"** to see function source code
- ✅ Reset progress anytime with **"Reset Progress"** button
- ✅ Navigate non-linearly with First/Previous/Next/Last buttons

### New Project
- ✅ Always use **absolute paths** (e.g., `/d:/projects/my_project`)
- ✅ Choose **"Basic Pipeline"** template to start
- ✅ Follow the **Quick Start** commands after creation
- ✅ Modify generated files to customize your project

### Engines
- ✅ Start with **"Small"** dataset for quick comparisons
- ✅ Try different operations: Filter, Aggregate, Transform, Join
- ✅ Read **"Best Practices"** tab for decision guidance
- ✅ Note: Spark may be simulated if not installed

### Transformations
- ✅ View **DAG** first to understand flow
- ✅ Execute layers **step-by-step** to see progression
- ✅ Compare **before/after** data in previews
- ✅ Study **SQL vs Functions** patterns

### Function Notebook
- ✅ Use **"Add Cell"** to create multi-step workflows
- ✅ **Run All Cells** to execute complete pipeline
- ✅ **Insert Template** for quick function setup
- ✅ **Export** your notebook as Python script when done

### Logs Viewer
- ✅ Run **"Demo Execution"** to generate sample logs
- ✅ Filter by **log level** to focus on errors/warnings
- ✅ Use **"Log Analysis"** for visual insights
- ✅ **Export to CSV** for external analysis tools

---

## 🔧 Programmatic Usage

You can also use the core modules programmatically:

```python
from odibi_core.learnodibi_ui import (
    WalkthroughParser,
    CodeExecutor,
    ProjectScaffolder
)

# Parse walkthroughs
parser = WalkthroughParser(Path("docs/walkthroughs"))
walkthroughs = parser.list_walkthroughs()

# Execute code
executor = CodeExecutor()
result = executor.execute("print('Hello ODIBI')")

# Create projects
scaffolder = ProjectScaffolder()
scaffolder.create_project("/d:/projects/my_project", "basic")
```

---

## 📚 Documentation

For detailed information, see:

- **[PHASE_10_LEARNODIBI_COMPLETE.md](file:///d:/projects/odibi_core/PHASE_10_LEARNODIBI_COMPLETE.md)** - Complete implementation summary
- **[LEARNODIBI_STUDIO_VALIDATION.md](file:///d:/projects/odibi_core/LEARNODIBI_STUDIO_VALIDATION.md)** - Validation report
- **[DEVELOPER_WALKTHROUGH_LEARNODIBI.md](file:///d:/projects/odibi_core/docs/walkthroughs/DEVELOPER_WALKTHROUGH_LEARNODIBI.md)** - Developer guide

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
streamlit run odibi_core/learnodibi_ui/app.py --server.port 8502
```

### Import Errors
```bash
# Reinstall ODIBI CORE
cd /d:/projects/odibi_core
pip install -e .
```

### Theme Not Applying
```bash
# Clear Streamlit cache
streamlit cache clear
```

### Walkthrough Not Loading
- Check file exists in `docs/walkthroughs/`
- Verify filename matches pattern: `DEVELOPER_WALKTHROUGH_*.md`
- Check for proper `### Mission N:` headers

---

## ✅ Quick Validation

Run this to verify installation:

```python
# Test imports
from odibi_core.learnodibi_ui import (
    WalkthroughParser,
    CodeExecutor,
    ProjectScaffolder
)

print("✅ All modules imported successfully!")

# Test parser
parser = WalkthroughParser(Path("docs/walkthroughs"))
wts = parser.list_walkthroughs()
print(f"✅ Found {len(wts)} walkthroughs")

# Test executor
executor = CodeExecutor()
result = executor.execute("2 + 2")
assert result['result'] == 4
print("✅ Code executor working")

# Test scaffolder
scaffolder = ProjectScaffolder()
is_valid, msg = scaffolder.validate_path("/d:/projects")
print(f"✅ Scaffolder working: {msg}")
```

---

## 🎯 Learning Path

### For Beginners
1. Start with **Guided Learning** → Phase 1
2. Create a **New Project** using basic template
3. Run the generated `run_project.py`
4. Modify and experiment

### For Intermediate Users
1. Explore **Engines** → Compare Pandas vs Spark
2. Study **Transformations** → DAG patterns
3. Use **Function Notebook** → Build custom pipelines
4. Monitor with **Logs Viewer**

### For Advanced Users
1. Study all **walkthroughs** through Guided Learning
2. Build complex **transformation pipelines**
3. Optimize with **engine comparison** insights
4. Debug using **logs analysis**

---

## 🏆 Success Metrics

After completing LearnODIBI Studio, you should be able to:

✅ Understand ODIBI CORE architecture  
✅ Create Bronze → Silver → Gold pipelines  
✅ Choose between Pandas and Spark engines  
✅ Build transformations using SQL and functions  
✅ Test and chain ODIBI functions  
✅ Debug pipelines with logs  
✅ Scaffold new projects from scratch  

---

## 🚀 Next Steps

1. **Complete all walkthroughs** in Guided Learning
2. **Build your first project** using New Project wizard
3. **Experiment** in Function Notebook
4. **Share** your learnings with the community
5. **Contribute** back to ODIBI CORE

---

**Happy Learning!** 🎓

Built with ❤️ by AMP for Henry Odibi

---

**Launch Command**:
```bash
python -m streamlit run odibi_core\learnodibi_ui\app.py
```
