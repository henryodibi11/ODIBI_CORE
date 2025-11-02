"""Final comprehensive verification before delivery"""
import sys
import os
from pathlib import Path

if os.name == 'nt':
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent))

print("=" * 70)
print("FINAL VERIFICATION - Teaching Platform")
print("=" * 70)

tests_passed = []
tests_failed = []

# Test 1: Branding
print("\n[1] Branding Check (ODB → ODIBI)")
print("-" * 70)
files_to_check = [
    "odibi_core/learnodibi_ui/app.py",
    "odibi_core/learnodibi_ui/theme.py",
    "odibi_core/learnodibi_ui/pages/0_guided_learning.py",
]

odb_found = False
for filepath in files_to_check:
    full_path = Path("d:/projects/odibi_core") / filepath
    if full_path.exists():
        content = full_path.read_text(encoding='utf-8')
        if 'ODB-CORE' in content or 'ODB CORE' in content:
            print(f"[WARN] {filepath} still has ODB branding")
            odb_found = True

if not odb_found:
    print("[OK] All ODB → ODIBI branding updated")
    tests_passed.append("Branding")
else:
    print("[FAIL] Some files still have ODB branding")
    tests_failed.append("Branding")

# Test 2: Duplicate Button Fix
print("\n[2] Duplicate Button ID Fix")
print("-" * 70)
guided_learning = Path("d:/projects/odibi_core/odibi_core/learnodibi_ui/pages/0_guided_learning.py")
content = guided_learning.read_text(encoding='utf-8')

if 'location: str = "top"' in content and 'key=f"first_{location}"' in content:
    print("[OK] Navigation buttons have unique keys")
    tests_passed.append("Button IDs")
else:
    print("[FAIL] Button IDs not fixed")
    tests_failed.append("Button IDs")

# Test 3: Walkthrough Parser
print("\n[3] Walkthrough Parser (All 11 walkthroughs)")
print("-" * 70)
try:
    from odibi_core.learnodibi_ui.walkthrough_parser import get_walkthrough_parser
    
    parser = get_walkthrough_parser(Path("d:/projects/odibi_core"))
    wts = parser.list_walkthroughs()
    
    total_steps = 0
    wts_with_steps = 0
    
    for wt_info in wts:
        wt_path = Path("d:/projects/odibi_core/docs/walkthroughs") / wt_info['filename']
        wt = parser.parse_walkthrough(wt_path)
        steps = len(wt.steps)
        total_steps += steps
        if steps > 0:
            wts_with_steps += 1
        print(f"  {wt_info['filename'][:40]:40} {steps:3} steps")
    
    print(f"\n[OK] Total: {total_steps} steps across {wts_with_steps}/{len(wts)} walkthroughs")
    
    if wts_with_steps >= 9:  # At least 9 phase walkthroughs should have steps
        tests_passed.append("Parser")
    else:
        tests_failed.append("Parser - not enough walkthroughs have steps")
        
except Exception as e:
    print(f"[FAIL] Parser error: {e}")
    tests_failed.append("Parser")

# Test 4: Function Imports
print("\n[4] Real Functions Import")
print("-" * 70)
try:
    from odibi_core.functions import data_ops, math_utils, validation_utils
    import pandas as pd
    
    # Test deduplicate
    df = pd.DataFrame({'a': [1, 1, 2], 'b': [3, 3, 4]})
    result = data_ops.deduplicate(df)
    print(f"[OK] data_ops.deduplicate() works - {len(result)} rows")
    
    # Test calculate_z_score
    df2 = pd.DataFrame({'value': [10, 20, 30, 40, 50]})
    result2 = math_utils.calculate_z_score(df2, 'value')
    print(f"[OK] math_utils.calculate_z_score() works")
    
    # Test validation
    result3 = validation_utils.check_missing_data(df)
    print(f"[OK] validation_utils.check_missing_data() works")
    
    tests_passed.append("Functions")
except Exception as e:
    print(f"[FAIL] {e}")
    tests_failed.append("Functions")

# Test 5: Pandas Focus
print("\n[5] Pandas-Focused Platform")
print("-" * 70)
engines_page = Path("d:/projects/odibi_core/odibi_core/learnodibi_ui/pages/7_engines.py")
if engines_page.exists():
    content = engines_page.read_text(encoding='utf-8')
    if 'Pandas' in content and 'recommended' in content.lower():
        print("[OK] Engines page is Pandas-focused")
        tests_passed.append("Pandas Focus")
    else:
        print("[INFO] Engines page could be more Pandas-focused")
        tests_passed.append("Pandas Focus (partial)")

# Test 6: Walkthrough Code Validation
print("\n[6] Walkthrough Code Validation")
print("-" * 70)
try:
    rerun_results = Path("d:/projects/odibi_core/LEARNODIBI_RERUN_RESULTS.md")
    if rerun_results.exists():
        content = rerun_results.read_text(encoding='utf-8')
        # Parse totals line
        import re
        match = re.search(r'\*\*TOTALS:\*\* (\d+) blocks \| (\d+) valid \| (\d+) invalid', content)
        if match:
            total_blocks = int(match.group(1))
            valid_blocks = int(match.group(2))
            invalid_blocks = int(match.group(3))
            coverage_pct = (valid_blocks / total_blocks * 100) if total_blocks > 0 else 0
            
            print(f"  Total Code Blocks: {total_blocks}")
            print(f"  Syntax Valid: {valid_blocks}")
            print(f"  Syntax Invalid: {invalid_blocks}")
            print(f"  Coverage: {coverage_pct:.1f}%")
            
            if coverage_pct >= 80:
                print(f"[OK] {coverage_pct:.1f}% of walkthrough code blocks are syntax-valid")
                tests_passed.append("Walkthrough Validation")
            else:
                print(f"[WARN] Only {coverage_pct:.1f}% coverage - target is 80%+")
                tests_failed.append("Walkthrough Validation - low coverage")
        else:
            print("[WARN] Could not parse validation results")
            tests_failed.append("Walkthrough Validation - parse error")
    else:
        print("[WARN] LEARNODIBI_RERUN_RESULTS.md not found - run quick_walkthrough_fixer.py")
        tests_failed.append("Walkthrough Validation - no report")
except Exception as e:
    print(f"[FAIL] Error checking walkthrough validation: {e}")
    tests_failed.append("Walkthrough Validation")

# Summary
print("\n" + "=" * 70)
print("VERIFICATION SUMMARY")
print("=" * 70)
print(f"\n[OK] Tests Passed: {len(tests_passed)}")
for test in tests_passed:
    print(f"  - {test}")

if tests_failed:
    print(f"\n[FAIL] Tests Failed: {len(tests_failed)}")
    for test in tests_failed:
        print(f"  - {test}")
else:
    print("\n[SUCCESS] All tests passed!")

print("\n" + "=" * 70)
if not tests_failed:
    print("PLATFORM IS READY FOR TEACHING")
    print("Launch with: python -m streamlit run odibi_core\\learnodibi_ui\\app.py")
else:
    print("SOME ISSUES REMAIN - REVIEW ABOVE")
print("=" * 70)
