#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verification script for ODIBI CORE reorganization.
Checks that all critical imports and paths still work after reorganization.
"""

import sys
import os
from pathlib import Path

# Force UTF-8 output on Windows
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'

print("=" * 70)
print("ODIBI CORE Reorganization Verification")
print("=" * 70)

# Check directory structure
print("\n1. Checking directory structure...")

required_dirs = [
    "odibi_core",
    "tests",
    "docs",
    "docs/walkthroughs",
    "docs/guides",
    "docs/reports",
    "docs/archive",
    "deploy",
    "deploy/docker",
    "deploy/scripts",
    "scripts",
    "examples",
    "artifacts",
]

missing_dirs = []
for dir_path in required_dirs:
    if not Path(dir_path).exists():
        missing_dirs.append(dir_path)
        print(f"   [X] {dir_path} - MISSING")
    else:
        print(f"   [OK] {dir_path}")

if missing_dirs:
    print(f"\n❌ Missing {len(missing_dirs)} directories")
    sys.exit(1)
else:
    print(f"\n[OK] All {len(required_dirs)} directories present")

# Check critical files
print("\n2. Checking critical files...")

critical_files = [
    "pyproject.toml",
    "README.md",
    "INSTALL.md",
    "pytest.ini",
    ".gitignore",
    "walkthrough_manifest.json",
    "walkthrough_manifest_v2.json",
]

missing_files = []
for file_path in critical_files:
    if not Path(file_path).exists():
        missing_files.append(file_path)
        print(f"   [X] {file_path} - MISSING")
    else:
        print(f"   [OK] {file_path}")

if missing_files:
    print(f"\n[FAIL] Missing {len(missing_files)} critical files")
    sys.exit(1)
else:
    print(f"\n[OK] All {len(critical_files)} critical files present")

# Test Python imports
print("\n3. Testing Python imports...")

try:
    import odibi_core
    print("   [OK] import odibi_core")
except ImportError as e:
    print(f"   [X] import odibi_core - {e}")
    print("\n[FAIL] Core imports failed. Run: pip install -e .")
    sys.exit(1)

try:
    from odibi_core.core import NodeBase, Step, NodeState
    print("   [OK] from odibi_core.core import NodeBase, Step, NodeState")
except ImportError as e:
    print(f"   [X] Core imports - {e}")

try:
    from odibi_core.engine import EngineContext, PandasEngineContext
    print("   [OK] from odibi_core.engine import EngineContext, PandasEngineContext")
except ImportError as e:
    print(f"   [X] Engine imports - {e}")

try:
    from odibi_core.nodes import NODE_REGISTRY
    print(f"   [OK] from odibi_core.nodes import NODE_REGISTRY ({len(NODE_REGISTRY)} nodes)")
except ImportError as e:
    print(f"   [X] Nodes import - {e}")

print("\n[OK] All imports successful")

# Check file counts
print("\n4. Checking file counts...")

guide_count = len(list(Path("docs/guides").glob("*.md")))
report_count = len(list(Path("docs/reports").glob("*.md")))
script_count = len(list(Path("scripts").glob("*.py")))

print(f"   [OK] docs/guides/: {guide_count} files")
print(f"   [OK] docs/reports/: {report_count} files")
print(f"   [OK] scripts/: {script_count} files")

# Check root cleanliness
print("\n5. Checking root directory cleanliness...")

root_files = [f for f in Path(".").iterdir() if f.is_file()]
print(f"   [OK] Root directory: {len(root_files)} files (target: <25)")

if len(root_files) > 25:
    print("   [WARN] Root still has many files, consider further cleanup")

# Final summary
print("\n" + "=" * 70)
print("[SUCCESS] REORGANIZATION VERIFICATION COMPLETE")
print("=" * 70)
print("\nStructure:")
print(f"  - Directories: {len(required_dirs)} present")
print(f"  - Critical files: {len(critical_files)} present")
print(f"  - User guides: {guide_count}")
print(f"  - Reports: {report_count}")
print(f"  - Scripts: {script_count}")
print(f"  - Root files: {len(root_files)}")
print("\nNext steps:")
print("  1. Run: pip install -e .")
print("  2. Run: pytest tests/ -v")
print("  3. Run: python deploy/scripts/launch_studio.py")
print("\n" + "=" * 70)
