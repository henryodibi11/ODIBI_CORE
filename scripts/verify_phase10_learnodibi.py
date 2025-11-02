"""
Verification Script for LearnODIBI Studio Phase 10
Run this to validate the enhanced platform is working correctly
"""

import sys
import os
from pathlib import Path

# Fix Windows encoding
if os.name == 'nt':
    sys.stdout.reconfigure(encoding='utf-8')

# Add to path
ODIBI_ROOT = Path(__file__).parent
sys.path.insert(0, str(ODIBI_ROOT))

def test_imports():
    """Test that all new modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        from odibi_core.learnodibi_ui import (
            WalkthroughParser,
            get_walkthrough_parser,
            CodeExecutor,
            execute_code_snippet,
            ProjectScaffolder
        )
        print("  ✅ Core modules imported successfully")
        return True
    except ImportError as e:
        print(f"  ❌ Import failed: {e}")
        return False


def test_walkthrough_parser():
    """Test walkthrough parser functionality"""
    print("\n🔍 Testing Walkthrough Parser...")
    
    try:
        from odibi_core.learnodibi_ui.walkthrough_parser import get_walkthrough_parser
        
        parser = get_walkthrough_parser(ODIBI_ROOT)
        walkthroughs = parser.list_walkthroughs()
        
        if len(walkthroughs) == 0:
            print("  ⚠️  No walkthroughs found")
            return False
        
        print(f"  ✅ Found {len(walkthroughs)} walkthroughs")
        
        # Try parsing first walkthrough
        first_wt = walkthroughs[0]
        wt_path = ODIBI_ROOT / "docs" / "walkthroughs" / first_wt['filename']
        walkthrough = parser.parse_walkthrough(wt_path)
        
        print(f"  ✅ Parsed: {walkthrough.title}")
        print(f"  ✅ Steps: {len(walkthrough.steps)}")
        
        return True
    except Exception as e:
        print(f"  ❌ Parser test failed: {e}")
        return False


def test_code_executor():
    """Test code executor functionality"""
    print("\n🔍 Testing Code Executor...")
    
    try:
        from odibi_core.learnodibi_ui.code_executor import CodeExecutor
        
        executor = CodeExecutor()
        
        # Test simple execution
        result = executor.execute("x = 10\nx * 2")
        
        if not result['success']:
            print(f"  ❌ Execution failed: {result['error']}")
            return False
        
        if result['result'] != 20:
            print(f"  ❌ Wrong result: {result['result']} (expected 20)")
            return False
        
        print("  ✅ Simple execution works")
        
        # Test error handling
        result = executor.execute("1 / 0")
        
        if result['success']:
            print("  ❌ Should have failed on 1/0")
            return False
        
        if 'ZeroDivisionError' not in result['error']:
            print("  ❌ Wrong error type")
            return False
        
        print("  ✅ Error handling works")
        
        # Test pandas execution
        result = executor.execute("""
import pandas as pd
df = pd.DataFrame({'a': [1,2,3]})
df['b'] = df['a'] * 2
df.shape
""")
        
        if not result['success']:
            print(f"  ❌ Pandas execution failed: {result['error']}")
            return False
        
        print("  ✅ Pandas execution works")
        
        return True
    except Exception as e:
        print(f"  ❌ Executor test failed: {e}")
        return False


def test_project_scaffolder():
    """Test project scaffolder functionality"""
    print("\n🔍 Testing Project Scaffolder...")
    
    try:
        from odibi_core.learnodibi_ui.project_scaffolder import ProjectScaffolder
        
        scaffolder = ProjectScaffolder()
        
        # Test path validation - invalid path
        is_valid, msg = scaffolder.validate_path("relative/path")
        if is_valid:
            print("  ❌ Should reject relative path")
            return False
        print("  ✅ Rejects relative paths")
        
        # Test path validation - valid path
        is_valid, msg = scaffolder.validate_path(str(ODIBI_ROOT / "test_validation"))
        if not is_valid and "Parent directory does not exist" not in msg:
            print(f"  ⚠️  Validation: {msg}")
        else:
            print("  ✅ Path validation works")
        
        # Test template loading
        templates = scaffolder.templates
        if len(templates) < 3:
            print(f"  ❌ Expected 3+ templates, got {len(templates)}")
            return False
        print(f"  ✅ Loaded {len(templates)} templates")
        
        return True
    except Exception as e:
        print(f"  ❌ Scaffolder test failed: {e}")
        return False


def test_pages_exist():
    """Test that all new pages exist"""
    print("\n🔍 Testing Page Files...")
    
    pages_dir = ODIBI_ROOT / "odibi_core" / "learnodibi_ui" / "pages"
    
    required_pages = [
        "0_guided_learning.py",
        "6_new_project.py",
        "7_engines.py",
        "8_transformations.py",
        "9_function_notebook.py",
        "10_logs_viewer.py"
    ]
    
    all_exist = True
    for page in required_pages:
        page_path = pages_dir / page
        if page_path.exists():
            print(f"  ✅ {page}")
        else:
            print(f"  ❌ {page} NOT FOUND")
            all_exist = False
    
    return all_exist


def test_documentation_exists():
    """Test that documentation files exist"""
    print("\n🔍 Testing Documentation...")
    
    required_docs = [
        "PHASE_10_LEARNODIBI_COMPLETE.md",
        "LEARNODIBI_STUDIO_VALIDATION.md",
        "LEARNODIBI_STUDIO_QUICK_START.md",
        "docs/walkthroughs/DEVELOPER_WALKTHROUGH_LEARNODIBI.md"
    ]
    
    all_exist = True
    for doc in required_docs:
        doc_path = ODIBI_ROOT / doc
        if doc_path.exists():
            print(f"  ✅ {doc}")
        else:
            print(f"  ❌ {doc} NOT FOUND")
            all_exist = False
    
    return all_exist


def main():
    """Run all verification tests"""
    print("=" * 60)
    print("LearnODIBI Studio Phase 10 Verification")
    print("=" * 60)
    
    results = {
        "Imports": test_imports(),
        "Walkthrough Parser": test_walkthrough_parser(),
        "Code Executor": test_code_executor(),
        "Project Scaffolder": test_project_scaffolder(),
        "Page Files": test_pages_exist(),
        "Documentation": test_documentation_exists()
    }
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:.<40} {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("✅ LearnODIBI Studio Phase 10 is ready to use")
        print("\nTo launch the studio, run:")
        print("  python -m streamlit run odibi_core\\learnodibi_ui\\app.py")
    else:
        print("⚠️  SOME TESTS FAILED")
        print("Please review the errors above and fix the issues")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
