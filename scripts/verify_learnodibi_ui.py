"""
Verification script for ODB-CORE Studio installation
Run this to ensure all components are properly installed
"""

import sys
from pathlib import Path
from typing import List, Tuple

def check_file_exists(filepath: Path) -> Tuple[bool, str]:
    """Check if a file exists"""
    if filepath.exists():
        return True, f"[OK] {filepath.name}"
    else:
        return False, f"[MISSING] {filepath}"

def verify_structure():
    """Verify the complete learnodibi_ui structure"""
    
    print("=" * 60)
    print("ODB-CORE Studio - Installation Verification")
    print("=" * 60)
    print()
    
    base_path = Path(__file__).parent / "odibi_core" / "learnodibi_ui"
    
    # Define required structure
    required_files = [
        base_path / "__init__.py",
        base_path / "app.py",
        base_path / "theme.py",
        base_path / "utils.py",
        base_path / "README.md",
        base_path / "INSTALL.md",
    ]
    
    required_component_files = [
        base_path / "components" / "__init__.py",
        base_path / "components" / "config_editor.py",
        base_path / "components" / "data_preview.py",
        base_path / "components" / "metrics_display.py",
    ]
    
    required_page_files = [
        base_path / "pages" / "__init__.py",
        base_path / "pages" / "1_core.py",
        base_path / "pages" / "2_functions.py",
        base_path / "pages" / "3_sdk.py",
        base_path / "pages" / "4_demo_project.py",
        base_path / "pages" / "5_docs.py",
    ]
    
    all_checks_passed = True
    
    # Check main files
    print("[Main Files]")
    for filepath in required_files:
        passed, message = check_file_exists(filepath)
        print(f"  {message}")
        all_checks_passed &= passed
    
    print()
    
    # Check component files
    print("[Component Files]")
    for filepath in required_component_files:
        passed, message = check_file_exists(filepath)
        print(f"  {message}")
        all_checks_passed &= passed
    
    print()
    
    # Check page files
    print("[Page Files]")
    for filepath in required_page_files:
        passed, message = check_file_exists(filepath)
        print(f"  {message}")
        all_checks_passed &= passed
    
    print()
    
    # Check dependencies
    print("[Dependencies]")
    dependencies = ["streamlit", "plotly", "pandas", "numpy"]
    
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"  [OK] {dep}")
        except ImportError:
            print(f"  [MISSING] {dep}")
            all_checks_passed = False
    
    print()
    
    # Check ODIBI CORE
    print("[ODIBI CORE]")
    try:
        import odibi_core
        print(f"  [OK] odibi_core installed")
        try:
            from odibi_core.__version__ import __version__
            print(f"  [OK] Version: {__version__}")
        except ImportError:
            print(f"  [WARN] Version info not available")
    except ImportError:
        print(f"  [MISSING] odibi_core not installed")
        all_checks_passed = False
    
    print()
    print("=" * 60)
    
    if all_checks_passed:
        print("SUCCESS: ALL CHECKS PASSED!")
        print()
        print("You're ready to run ODB-CORE Studio!")
        print()
        print("Run with:")
        print("  streamlit run odibi_core/learnodibi_ui/app.py")
        print()
        print("Or use quick launchers:")
        print("  Windows: run_studio.bat")
        print("  Linux/Mac: ./run_studio.sh")
    else:
        print("ERROR: SOME CHECKS FAILED!")
        print()
        print("Please install missing components:")
        print("  pip install streamlit plotly pandas numpy")
        print("  pip install -e .")
    
    print("=" * 60)
    
    return all_checks_passed


if __name__ == "__main__":
    success = verify_structure()
    sys.exit(0 if success else 1)
