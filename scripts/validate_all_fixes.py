"""
Validation Script - Test all fixes are working
"""

import sys
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

def test_walkthrough_parser():
    """Test walkthrough parser with new regex"""
    from odibi_core.learnodibi_ui.walkthrough_parser import get_walkthrough_parser
    
    print("Testing Walkthrough Parser...")
    parser = get_walkthrough_parser()
    
    walkthroughs = parser.list_walkthroughs()
    print(f"  Found {len(walkthroughs)} walkthrough files")
    
    total_steps = 0
    for wt in walkthroughs:
        filepath = parser.walkthroughs_dir / wt['filename']
        parsed = parser.parse_walkthrough(filepath)
        total_steps += len(parsed.steps)
        print(f"  [OK] {wt['filename']}: {len(parsed.steps)} steps")
    
    print(f"  Total steps parsed: {total_steps}")
    return total_steps > 100  # Should have 100+ missions


def test_real_functions():
    """Test that real functions can be imported"""
    print("\nTesting Real Functions Import...")
    
    try:
        from odibi_core.functions import (
            data_ops,
            math_utils,
            validation_utils,
            string_utils,
            datetime_utils,
            conversion_utils
        )
        
        # Test key functions exist
        assert hasattr(data_ops, 'deduplicate'), "deduplicate not found"
        assert hasattr(data_ops, 'filter_rows'), "filter_rows not found"
        assert hasattr(conversion_utils, 'fill_null'), "fill_null not found"
        assert hasattr(math_utils, 'calculate_z_score'), "calculate_z_score not found"
        assert hasattr(string_utils, 'trim_whitespace'), "trim_whitespace not found"
        
        print("  [OK] All core functions imported successfully")
        return True
    except Exception as e:
        print(f"  [FAIL] Import failed: {e}")
        return False


def test_code_examples():
    """Test that code examples execute without errors"""
    print("\nTesting Code Examples...")
    
    try:
        import pandas as pd
        from odibi_core.functions import conversion_utils, data_ops
        
        # Test Example 1: Fill nulls and deduplicate
        df = pd.DataFrame({
            'temperature': [20.5, 22.1, None, 19.8, 21.3],
            'humidity': [45, 52, 48, None, 50]
        })
        
        # Fill nulls in each column
        df_clean = conversion_utils.fill_null(df, 'temperature', fill_value=20.0)
        df_clean = conversion_utils.fill_null(df_clean, 'humidity', fill_value=50)
        df_final = data_ops.deduplicate(df_clean)
        
        assert len(df_final) > 0, "Deduplicate failed"
        print("  [OK] Example 1: Fill nulls + deduplicate works")
        
        # Test Example 2: Math operations
        from odibi_core.functions import math_utils
        
        df2 = pd.DataFrame({'value': [10, 20, 30, 40, 50]})
        df2_with_z = math_utils.calculate_z_score(df2, 'value')
        df2_with_pct = math_utils.calculate_percent_change(df2, 'value')
        
        assert 'value_zscore' in df2_with_z.columns, "Z-score calculation failed"
        print("  [OK] Example 2: Math operations work")
        
        # Test Example 3: String operations
        from odibi_core.functions import string_utils
        
        df3 = pd.DataFrame({'name': ['  Alice  ', '  BOB  ', '  Charlie  ']})
        df3_clean = string_utils.trim_whitespace(df3, 'name')
        df3_lower = string_utils.to_lowercase(df3_clean, 'name')
        
        assert 'name' in df3_lower.columns, "String operations failed"
        print("  [OK] Example 3: String operations work")
        
        return True
        
    except Exception as e:
        print(f"  [FAIL] Code example failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_utils_functions():
    """Test utils.py has real functions"""
    print("\nTesting Utils Function List...")
    
    from odibi_core.learnodibi_ui.utils import get_available_functions
    
    funcs = get_available_functions()
    
    # Check for fake functions (should NOT be present)
    all_funcs = []
    for category, func_list in funcs.items():
        all_funcs.extend(func_list)
    
    fake_functions = {'handle_nulls', 'coalesce', 'apply_transformation', 
                     'clean_string', 'normalize_text', 'filter_data'}
    
    found_fake = set(all_funcs) & fake_functions
    
    if found_fake:
        print(f"  [FAIL] Found fake functions: {found_fake}")
        return False
    else:
        print(f"  [OK] No fake functions found")
        print(f"  [OK] Total real functions listed: {len(all_funcs)}")
        return True


def main():
    """Run all validation tests"""
    print("=" * 80)
    print("LEARNODIBI STUDIO - VALIDATION SUITE")
    print("=" * 80)
    
    results = []
    
    # Run tests
    results.append(("Walkthrough Parser", test_walkthrough_parser()))
    results.append(("Real Functions Import", test_real_functions()))
    results.append(("Code Examples", test_code_examples()))
    results.append(("Utils Functions", test_utils_functions()))
    
    # Summary
    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)
    
    for test_name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status}: {test_name}")
    
    all_passed = all(r[1] for r in results)
    
    print("\n" + "=" * 80)
    if all_passed:
        print("SUCCESS: ALL TESTS PASSED - LEARNODIBI STUDIO IS READY!")
    else:
        print("WARNING: SOME TESTS FAILED - REVIEW ERRORS ABOVE")
    print("=" * 80)
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
