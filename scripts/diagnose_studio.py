"""
Diagnostic script to check for bugs in ODB-CORE Studio
"""
import sys
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Add odibi_core to path
ODIBI_ROOT = Path(__file__).parent
if str(ODIBI_ROOT) not in sys.path:
    sys.path.insert(0, str(ODIBI_ROOT))

print("=" * 70)
print("ODB-CORE Studio - Diagnostic Report")
print("=" * 70)
print()

issues = []
warnings = []

# 1. Check Python version
print("[1] Checking Python version...")
if sys.version_info < (3, 8):
    issues.append(f"Python {sys.version_info.major}.{sys.version_info.minor} is too old (requires 3.8+)")
else:
    print(f"  [OK] Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")

# 2. Check dependencies
print("\n[2] Checking dependencies...")
required_deps = {
    "streamlit": "1.30.0",
    "plotly": "5.0.0",
    "pandas": "1.5.0"
}

for package, min_version in required_deps.items():
    try:
        mod = __import__(package)
        version = getattr(mod, "__version__", "unknown")
        print(f"  [OK] {package} {version}")
    except ImportError:
        issues.append(f"Missing dependency: {package} (run: pip install {package})")

# 3. Check odibi_core modules
print("\n[3] Checking odibi_core modules...")
odibi_modules = [
    "odibi_core",
    "odibi_core.learnodibi_ui",
    "odibi_core.learnodibi_backend",
    "odibi_core.learnodibi_data",
    "odibi_core.learnodibi_project"
]

for module in odibi_modules:
    try:
        __import__(module)
        print(f"  [OK] {module}")
    except ImportError as e:
        issues.append(f"Cannot import {module}: {e}")

# 4. Check UI files
print("\n[4] Checking UI files...")
ui_files = [
    "odibi_core/learnodibi_ui/app.py",
    "odibi_core/learnodibi_ui/theme.py",
    "odibi_core/learnodibi_ui/utils.py",
    "odibi_core/learnodibi_ui/pages/1_core.py",
    "odibi_core/learnodibi_ui/pages/2_functions.py",
    "odibi_core/learnodibi_ui/pages/3_sdk.py",
    "odibi_core/learnodibi_ui/pages/4_demo_project.py",
    "odibi_core/learnodibi_ui/pages/5_docs.py"
]

for file_path in ui_files:
    full_path = Path(file_path)
    if full_path.exists():
        print(f"  [OK] {file_path}")
    else:
        issues.append(f"Missing file: {file_path}")

# 5. Check for syntax errors in UI files
print("\n[5] Checking for syntax errors...")
for file_path in ui_files:
    full_path = Path(file_path)
    if full_path.exists():
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                code = f.read()
                compile(code, str(full_path), 'exec')
            print(f"  [OK] {file_path}")
        except SyntaxError as e:
            issues.append(f"Syntax error in {file_path}: {e}")

# 6. Check app.py for set_page_config issues
print("\n[6] Checking app.py for Streamlit configuration...")
app_file = Path("odibi_core/learnodibi_ui/app.py")
if app_file.exists():
    with open(app_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    # Find where set_page_config is called
    set_page_config_line = None
    import_st_line = None
    
    for i, line in enumerate(lines, 1):
        if "import streamlit" in line and "st" in line:
            import_st_line = i
        if "st.set_page_config" in line:
            set_page_config_line = i
            break
    
    if set_page_config_line and import_st_line:
        # Check if set_page_config comes right after import streamlit
        if set_page_config_line - import_st_line <= 5:
            print(f"  [OK] st.set_page_config() at line {set_page_config_line} (after import at line {import_st_line})")
        else:
            warnings.append(f"st.set_page_config() at line {set_page_config_line} might be too late (import at line {import_st_line})")
    else:
        warnings.append("Could not find st.set_page_config() or streamlit import")

# 7. Test backend API
print("\n[7] Testing backend API...")
try:
    from odibi_core.learnodibi_backend import LearnODIBIBackend
    backend = LearnODIBIBackend()
    result = backend.get_available_functions()
    if result.get("success"):
        print(f"  [OK] Backend API functional")
    else:
        warnings.append("Backend API returned success=False")
except Exception as e:
    warnings.append(f"Backend API error: {e}")

# 8. Test demo pipeline
print("\n[8] Testing demo pipeline...")
try:
    from odibi_core.learnodibi_project import DemoPipeline
    pipeline = DemoPipeline()
    print(f"  [OK] Demo pipeline instantiated")
except Exception as e:
    warnings.append(f"Demo pipeline error: {e}")

# 9. Test data generation
print("\n[9] Testing data generation...")
try:
    from odibi_core.learnodibi_data import list_datasets, get_dataset
    datasets = list_datasets()
    if len(datasets) >= 3:
        print(f"  [OK] {len(datasets)} datasets available")
    else:
        warnings.append(f"Only {len(datasets)} datasets found (expected 3)")
except Exception as e:
    warnings.append(f"Data generation error: {e}")

# 10. Test theme configuration
print("\n[10] Testing theme configuration...")
try:
    from odibi_core.learnodibi_ui.theme import COLORS, apply_theme
    if COLORS.get("primary") == "#F5B400" and COLORS.get("secondary") == "#00796B":
        print(f"  [OK] Theme colors correct (Gold #F5B400, Teal #00796B)")
    else:
        warnings.append(f"Theme colors incorrect: {COLORS.get('primary')}, {COLORS.get('secondary')}")
except Exception as e:
    warnings.append(f"Theme configuration error: {e}")

# Summary
print("\n" + "=" * 70)
print("DIAGNOSTIC SUMMARY")
print("=" * 70)

if not issues and not warnings:
    print("\n[SUCCESS] No issues found! The studio should work perfectly.")
    print("\nTo launch:")
    print("  python -m streamlit run odibi_core\\learnodibi_ui\\app.py")
    exit_code = 0
else:
    if issues:
        print(f"\n[CRITICAL] {len(issues)} issue(s) found:")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
    
    if warnings:
        print(f"\n[WARNING] {len(warnings)} warning(s):")
        for i, warning in enumerate(warnings, 1):
            print(f"  {i}. {warning}")
    
    if not issues:
        print("\n[RESULT] Warnings only - studio should still work")
        exit_code = 0
    else:
        print("\n[RESULT] Critical issues found - fix before launching")
        exit_code = 1

print("=" * 70)
sys.exit(exit_code)
