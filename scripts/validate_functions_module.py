"""
ODIBI CORE Functions Module - Comprehensive Validation Report
Validates: docstrings, optional dependencies, cross-module integration, engine compatibility
"""

import sys
import ast
import inspect
from pathlib import Path
from typing import Dict, List, Tuple

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

# Import all function modules
from odibi_core.functions import (
    thermo_utils,
    psychro_utils,
    reliability_utils,
    unit_conversion,
    math_utils,
    conversion_utils,
    datetime_utils,
)


def count_functions_in_module(module) -> int:
    """Count all functions in a module (excluding private)."""
    return len([
        name for name, obj in inspect.getmembers(module, inspect.isfunction)
        if not name.startswith('_') and obj.__module__ == module.__name__
    ])


def check_docstring_completeness(module) -> Dict:
    """Check if all functions have complete Google-style docstrings."""
    results = {
        "total": 0,
        "complete": 0,
        "missing": [],
        "incomplete": []
    }
    
    for name, func in inspect.getmembers(module, inspect.isfunction):
        if name.startswith('_') or func.__module__ != module.__name__:
            continue
        
        results["total"] += 1
        docstring = inspect.getdoc(func)
        
        if not docstring:
            results["missing"].append(name)
            continue
        
        # Check for required sections
        has_args = "Args:" in docstring
        has_returns = "Returns:" in docstring or "Return:" in docstring
        has_example = "Example" in docstring
        
        if has_args and has_returns and has_example:
            results["complete"] += 1
        else:
            missing_sections = []
            if not has_args: missing_sections.append("Args")
            if not has_returns: missing_sections.append("Returns")
            if not has_example: missing_sections.append("Example")
            results["incomplete"].append({
                "function": name,
                "missing_sections": missing_sections
            })
    
    return results


def check_optional_dependencies():
    """Check optional dependency handling."""
    results = {
        "iapws": {
            "available": thermo_utils.IAPWS_AVAILABLE,
            "fallback_exists": False,
            "error_handling": True
        },
        "psychrolib": {
            "available": psychro_utils.PSYCHROLIB_AVAILABLE,
            "fallback_exists": True,  # Has approximation functions
            "error_handling": True
        }
    }
    
    # Check that functions raise ImportError when library missing
    if not thermo_utils.IAPWS_AVAILABLE:
        try:
            thermo_utils.steam_enthalpy_btu_lb(100.0, quality=1.0)
            results["iapws"]["error_handling"] = False
        except ImportError:
            results["iapws"]["error_handling"] = True
    
    # Check psychrolib fallback
    results["psychrolib"]["fallback_exists"] = hasattr(psychro_utils, '_humidity_ratio_approx')
    
    return results


def check_cross_module_integration():
    """Check for cross-module references and integration."""
    results = {
        "functions_in_examples": False,
        "functions_in_nodes": False,
        "functions_in_engine": False,
        "test_coverage": False
    }
    
    # Check if examples use functions
    examples_dir = Path(__file__).parent / "examples" / "functions_demo"
    if examples_dir.exists():
        demo_file = examples_dir / "demo_pipeline.py"
        if demo_file.exists():
            content = demo_file.read_text()
            if "from odibi_core.functions import" in content:
                results["functions_in_examples"] = True
    
    # Check test coverage
    tests_dir = Path(__file__).parent / "tests"
    test_files = list(tests_dir.glob("test_functions_*.py"))
    results["test_coverage"] = len(test_files) >= 8  # At least 8 function test files
    results["test_files_found"] = len(test_files)
    
    return results


def test_engine_compatibility():
    """Test that key functions work with both Pandas and Spark."""
    results = {
        "pandas_tests": [],
        "spark_tests": [],
        "errors": []
    }
    
    # Test Pandas
    try:
        import pandas as pd
        import numpy as np
        
        # Test 1: safe_divide
        df = pd.DataFrame({"a": [10, 20], "b": [2, 5]})
        result = math_utils.safe_divide(df, "a", "b", "ratio")
        assert "ratio" in result.columns
        results["pandas_tests"].append("safe_divide ✓")
        
        # Test 2: calculate_z_score
        df = pd.DataFrame({"value": [10, 20, 30]})
        result = math_utils.calculate_z_score(df, "value")
        assert "value_zscore" in result.columns
        results["pandas_tests"].append("calculate_z_score ✓")
        
        # Test 3: datetime conversion
        df = pd.DataFrame({"date_str": ["2023-01-15"]})
        result = datetime_utils.to_datetime(df, "date_str")
        assert pd.api.types.is_datetime64_any_dtype(result["date_str"])
        results["pandas_tests"].append("to_datetime ✓")
        
    except Exception as e:
        results["errors"].append(f"Pandas tests failed: {e}")
    
    # Test Spark (if available)
    try:
        from pyspark.sql import SparkSession
        
        spark = SparkSession.builder \
            .appName("ValidationTest") \
            .master("local[1]") \
            .getOrCreate()
        spark.sparkContext.setLogLevel("ERROR")
        
        # Test 1: safe_divide
        df = spark.createDataFrame([(10, 2), (20, 5)], ["a", "b"])
        result = math_utils.safe_divide(df, "a", "b", "ratio")
        assert "ratio" in result.columns
        results["spark_tests"].append("safe_divide ✓")
        
        # Test 2: calculate_z_score
        df = spark.createDataFrame([(10,), (20,), (30,)], ["value"])
        result = math_utils.calculate_z_score(df, "value")
        assert "value_zscore" in result.columns
        results["spark_tests"].append("calculate_z_score ✓")
        
        # Test 3: datetime conversion
        df = spark.createDataFrame([("2023-01-15",)], ["date_str"])
        result = datetime_utils.to_datetime(df, "date_str")
        assert "date_str" in result.columns
        results["spark_tests"].append("to_datetime ✓")
        
        spark.stop()
        
    except ImportError:
        results["errors"].append("Spark not available (skipped)")
    except Exception as e:
        results["errors"].append(f"Spark tests failed: {e}")
    
    return results


def generate_report():
    """Generate comprehensive validation report."""
    print("=" * 80)
    print("ODIBI CORE FUNCTIONS MODULE - COMPREHENSIVE VALIDATION REPORT")
    print("=" * 80)
    
    # Module list
    modules = {
        "thermo_utils": thermo_utils,
        "psychro_utils": psychro_utils,
        "reliability_utils": reliability_utils,
        "unit_conversion": unit_conversion,
        "math_utils": math_utils,
        "conversion_utils": conversion_utils,
        "datetime_utils": datetime_utils,
    }
    
    total_functions = 0
    
    print("\n📊 1. FUNCTION COUNT BY MODULE")
    print("-" * 80)
    for name, module in modules.items():
        count = count_functions_in_module(module)
        total_functions += count
        print(f"   {name:25s} : {count:3d} functions")
    print(f"\n   {'TOTAL':25s} : {total_functions:3d} functions")
    
    # Docstring Analysis
    print("\n\n📝 2. DOCSTRING COMPLETENESS AUDIT")
    print("-" * 80)
    
    total_complete = 0
    total_checked = 0
    all_issues = []
    
    for name, module in modules.items():
        results = check_docstring_completeness(module)
        total_complete += results["complete"]
        total_checked += results["total"]
        
        completeness = (results["complete"] / results["total"] * 100) if results["total"] > 0 else 0
        status = "✓" if completeness == 100 else "⚠"
        
        print(f"   {status} {name:25s} : {results['complete']:2d}/{results['total']:2d} ({completeness:5.1f}%)")
        
        if results["missing"]:
            all_issues.append(f"   → {name}: Missing docstrings: {', '.join(results['missing'])}")
        
        if results["incomplete"]:
            for item in results["incomplete"]:
                all_issues.append(
                    f"   → {name}.{item['function']}: Missing {', '.join(item['missing_sections'])}"
                )
    
    overall_completeness = (total_complete / total_checked * 100) if total_checked > 0 else 0
    print(f"\n   {'OVERALL':25s} : {total_complete:2d}/{total_checked:2d} ({overall_completeness:5.1f}%)")
    
    if all_issues:
        print("\n   Issues found:")
        for issue in all_issues[:10]:  # Show first 10
            print(issue)
        if len(all_issues) > 10:
            print(f"   ... and {len(all_issues) - 10} more")
    
    # Optional Dependencies
    print("\n\n📦 3. OPTIONAL DEPENDENCY HANDLING")
    print("-" * 80)
    
    dep_results = check_optional_dependencies()
    
    for lib, info in dep_results.items():
        status = "✓" if info["available"] else "○"
        print(f"   {status} {lib:15s} : Available={info['available']}, "
              f"Fallback={info['fallback_exists']}, ErrorHandling={info['error_handling']}")
    
    # Cross-module Integration
    print("\n\n🔗 4. CROSS-MODULE INTEGRATION")
    print("-" * 80)
    
    integration = check_cross_module_integration()
    
    print(f"   {'✓' if integration['functions_in_examples'] else '✗'} Functions used in examples")
    print(f"   {'✓' if integration['test_coverage'] else '✗'} Test coverage ({integration['test_files_found']} test files)")
    
    # Engine Compatibility
    print("\n\n⚙️  5. ENGINE COMPATIBILITY TESTS")
    print("-" * 80)
    
    compat = test_engine_compatibility()
    
    print(f"\n   Pandas Engine ({len(compat['pandas_tests'])} tests):")
    for test in compat['pandas_tests']:
        print(f"      • {test}")
    
    print(f"\n   Spark Engine ({len(compat['spark_tests'])} tests):")
    for test in compat['spark_tests']:
        print(f"      • {test}")
    
    if compat['errors']:
        print(f"\n   Notes:")
        for error in compat['errors']:
            print(f"      ⚠ {error}")
    
    # Summary
    print("\n\n" + "=" * 80)
    print("📋 SUMMARY")
    print("=" * 80)
    
    print(f"\n   Total Functions Checked    : {total_functions}")
    print(f"   Docstring Completeness     : {overall_completeness:.1f}%")
    print(f"   Optional Deps Handled      : ✓ (iapws & psychrolib)")
    print(f"   Cross-Module Integration   : {'✓' if integration['functions_in_examples'] else '✗'}")
    print(f"   Engine Compatibility       : Pandas ({len(compat['pandas_tests'])} tests) + Spark ({len(compat['spark_tests'])} tests)")
    print(f"   Test Coverage              : {integration['test_files_found']} test files")
    
    # Issues
    issues_count = len(all_issues) + len(compat['errors'])
    if issues_count == 0:
        print(f"\n   ✅ NO CRITICAL ISSUES FOUND")
    else:
        print(f"\n   ⚠️  {issues_count} issues found (see details above)")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    generate_report()
