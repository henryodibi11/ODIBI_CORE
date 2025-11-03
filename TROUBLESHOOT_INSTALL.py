"""
Troubleshooting script for LearnODIBI installation issues
Run this when you see "No walkthroughs found!"
"""
import sys
from pathlib import Path

print("="*80)
print("ODIBI CORE INSTALLATION TROUBLESHOOTER")
print("="*80)

# Step 1: Check if package is installed
print("\n[Step 1] Checking if odibi_core is installed...")
try:
    import odibi_core
    print(f"✓ odibi_core found")
    print(f"  Version: {odibi_core.__version__}")
    print(f"  Location: {Path(odibi_core.__file__).parent}")
except ImportError as e:
    print(f"✗ odibi_core NOT installed: {e}")
    print("\nFIX: Run 'pip install odibi-core' or 'pip install -e .' from project root")
    sys.exit(1)

# Step 2: Check walkthrough location
print("\n[Step 2] Checking walkthrough files...")
pkg_path = Path(odibi_core.__file__).parent
walkthrough_path = pkg_path / "docs" / "walkthroughs"

print(f"  Expected location: {walkthrough_path}")
print(f"  Exists: {walkthrough_path.exists()}")

if walkthrough_path.exists():
    md_files = list(walkthrough_path.glob("DEVELOPER_WALKTHROUGH_*.md"))
    print(f"  Walkthrough files found: {len(md_files)}")
    
    if len(md_files) == 0:
        print(f"\n✗ PROBLEM: Directory exists but no walkthroughs inside!")
        print(f"\nFIX: The package was installed without walkthrough files.")
        print(f"     If installed from GitHub:")
        print(f"       pip uninstall -y odibi-core")
        print(f"       pip install --no-cache-dir git+https://github.com/henryodibi11/ODIBI_CORE.git")
        print(f"     If installed locally:")
        print(f"       pip uninstall -y odibi-core")
        print(f"       pip install -e .")
    else:
        print(f"✓ Walkthroughs present:")
        for f in md_files[:3]:
            print(f"    - {f.name}")
else:
    print(f"\n✗ PROBLEM: Walkthrough directory does not exist!")
    print(f"\nFIX: Reinstall the package to include data files:")
    print(f"     pip uninstall -y odibi-core")
    print(f"     pip cache purge")
    print(f"     pip install --no-cache-dir git+https://github.com/henryodibi11/ODIBI_CORE.git")

# Step 3: Test parser
print("\n[Step 3] Testing walkthrough parser...")
try:
    from odibi_core.learnodibi_ui.walkthrough_parser import get_walkthrough_parser
    parser = get_walkthrough_parser()
    walkthroughs = parser.list_walkthroughs()
    
    print(f"  Parser initialized: ✓")
    print(f"  Search location: {parser.walkthroughs_dir}")
    print(f"  Walkthroughs found: {len(walkthroughs)}")
    
    if len(walkthroughs) == 0:
        print(f"\n✗ PROBLEM: Parser found no walkthroughs!")
        print(f"\n  Debugging info:")
        print(f"    Directory exists: {parser.walkthroughs_dir.exists()}")
        if parser.walkthroughs_dir.exists():
            all_files = list(parser.walkthroughs_dir.glob("*.md"))
            print(f"    All .md files: {len(all_files)}")
            if all_files:
                print(f"    Files found:")
                for f in all_files[:5]:
                    print(f"      - {f.name}")
    else:
        print(f"✓ Parser working correctly")
        
except Exception as e:
    print(f"✗ Parser error: {e}")
    import traceback
    traceback.print_exc()

# Step 4: Test code executor
print("\n[Step 4] Testing code executor...")
try:
    from odibi_core.learnodibi_ui.code_executor import CodeExecutor
    executor = CodeExecutor()
    result = executor.execute("x = 42")
    
    if result['success']:
        print(f"✓ Code executor working")
    else:
        print(f"✗ Code executor failed: {result.get('error')}")
except Exception as e:
    print(f"✗ Executor error: {e}")

# Step 5: Check streamlit
print("\n[Step 5] Checking streamlit (for UI)...")
try:
    import streamlit
    print(f"✓ Streamlit installed: {streamlit.__version__}")
except ImportError:
    print(f"✗ Streamlit not installed")
    print(f"\nFIX: pip install streamlit>=1.32.0")

# Summary
print("\n" + "="*80)
print("SUMMARY")
print("="*80)

if walkthrough_path.exists() and len(list(walkthrough_path.glob("DEVELOPER_WALKTHROUGH_*.md"))) > 0:
    print("✓ Installation looks good!")
    print("\nYou can launch LearnODIBI with:")
    print("  python -c 'from odibi_core.learnodibi import launch_ui; launch_ui()'")
    print("  or simply: learnodibi")
else:
    print("✗ Installation has issues - see fixes above")
    print("\nQuick fix (most common):")
    print("  pip uninstall -y odibi-core")
    print("  pip cache purge")
    print("  pip install --no-cache-dir git+https://github.com/henryodibi11/ODIBI_CORE.git")

print("="*80)
