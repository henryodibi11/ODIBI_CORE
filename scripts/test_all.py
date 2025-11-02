"""Simple test runner compatible with Windows console."""

import sys
import os

# Set UTF-8 encoding for Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

print("=" * 70)
print("ODIBI CORE v1.0 - Test Suite")
print("=" * 70)
print()

# Check required dependencies
print("Checking dependencies...")
has_pandas = False
has_pytest = False
has_duckdb = False
has_pyspark = False

try:
    import pandas
    has_pandas = True
    print("[OK] pandas installed")
except ImportError:
    print("[MISSING] pandas NOT installed (required)")

try:
    import pytest
    has_pytest = True
    print("[OK] pytest installed")
except ImportError:
    print("[MISSING] pytest NOT installed (required)")

try:
    import duckdb
    has_duckdb = True
    print("[OK] duckdb installed")
except ImportError:
    print("[SKIP] duckdb NOT installed (some tests will be skipped)")

try:
    import pyspark
    has_pyspark = True
    print("[OK] pyspark installed")
except ImportError:
    print("[SKIP] pyspark NOT installed (Spark tests will be skipped)")

print()

if not has_pandas:
    print("[ERROR] pandas is required. Install with: pip install pandas")
    sys.exit(1)

if not has_pytest:
    print("[ERROR] pytest is required. Install with: pip install pytest")
    sys.exit(1)

# Run pytest
print("=" * 70)
print("Running tests...")
print("=" * 70)
print()

exit_code = pytest.main([
    "tests/",
    "-v",
    "--tb=short",
    "-ra",
])

print()
print("=" * 70)
if exit_code == 0:
    print("[SUCCESS] All tests passed!")
else:
    print("[FAIL] Some tests failed or were skipped")
print("=" * 70)

sys.exit(exit_code)
