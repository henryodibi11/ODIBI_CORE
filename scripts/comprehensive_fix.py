"""
Comprehensive Fix for LearnODIBI Studio
Audits and fixes all errors systematically
"""

import re
from pathlib import Path
from typing import Dict, List, Set
import importlib.util


def audit_real_functions() -> Dict[str, List[str]]:
    """Audit all real functions from odibi_core.functions modules"""
    
    function_modules = {
        "data_ops": [],
        "math_utils": [],
        "validation_utils": [],
        "string_utils": [],
        "datetime_utils": [],
        "conversion_utils": [],
        "psychro_utils": [],
        "thermo_utils": [],
        "reliability_utils": [],
        "unit_conversion": []
    }
    
    base_path = Path(__file__).parent / "odibi_core" / "functions"
    
    for module_name in function_modules.keys():
        module_path = base_path / f"{module_name}.py"
        if not module_path.exists():
            continue
            
        # Import module dynamically
        try:
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Get all public functions
            functions = [
                name for name in dir(module)
                if not name.startswith('_') and callable(getattr(module, name))
                and not name[0].isupper()  # Exclude type names
            ]
            function_modules[module_name] = functions
        except Exception as e:
            print(f"Error importing {module_name}: {e}")
    
    return function_modules


def find_fake_function_references(directory: Path) -> Dict[str, List[tuple]]:
    """Find all references to fake functions in code"""
    
    fake_functions = {
        "handle_nulls", "coalesce", "apply_transformation",
        "filter_data", "clean_string", "normalize_text",
        "extract_pattern", "split_and_trim", 
        "concatenate_with_separator", "calculate_percentage",
        "moving_average", "exponential_smoothing",
        "parse_datetime", "calculate_duration", "is_business_day"
    }
    
    findings = {}
    
    for file_path in directory.rglob("*.py"):
        if "__pycache__" in str(file_path):
            continue
            
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Find function references
            for fake_func in fake_functions:
                pattern = rf'\b{fake_func}\b'
                matches = list(re.finditer(pattern, content))
                
                if matches:
                    if str(file_path) not in findings:
                        findings[str(file_path)] = []
                    
                    for match in matches:
                        # Get line number
                        line_num = content[:match.start()].count('\n') + 1
                        findings[str(file_path)].append((fake_func, line_num))
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
    
    return findings


def check_walkthrough_parsing():
    """Test walkthrough parsing with current regex"""
    
    parser_path = Path(__file__).parent / "odibi_core" / "learnodibi_ui" / "walkthrough_parser.py"
    walkthroughs_dir = Path(__file__).parent / "docs" / "walkthroughs"
    
    # Read parser to get current pattern
    parser_content = parser_path.read_text(encoding='utf-8')
    pattern_match = re.search(r'mission_pattern = r[\'"](.+?)[\'"]', parser_content)
    
    if pattern_match:
        current_pattern = pattern_match.group(1)
        print(f"Current pattern: {current_pattern}")
    
    # Check each walkthrough
    results = {}
    
    for walkthrough in walkthroughs_dir.glob("DEVELOPER_WALKTHROUGH_*.md"):
        content = walkthrough.read_text(encoding='utf-8')
        
        # Count Mission headers
        mission_count = len(re.findall(r'###\s+Mission\s+\d+:', content))
        step_count = len(re.findall(r'###\s+Step\s+\d+:', content))
        exercise_count = len(re.findall(r'###\s+Exercise\s+\d+:', content))
        
        results[walkthrough.name] = {
            "missions": mission_count,
            "steps": step_count,
            "exercises": exercise_count,
            "total": mission_count + step_count + exercise_count
        }
    
    return results


def generate_audit_report():
    """Generate comprehensive audit report"""
    
    print("=" * 80)
    print("LEARNODIBI STUDIO - COMPREHENSIVE AUDIT")
    print("=" * 80)
    print()
    
    # 1. Audit real functions
    print("1. REAL FUNCTIONS AUDIT")
    print("-" * 80)
    real_functions = audit_real_functions()
    
    total_functions = 0
    for module, funcs in sorted(real_functions.items()):
        if funcs:
            print(f"\n{module} ({len(funcs)} functions):")
            for func in sorted(funcs):
                print(f"  - {func}")
            total_functions += len(funcs)
    
    print(f"\nTotal real functions: {total_functions}")
    print()
    
    # 2. Find fake function references
    print("2. FAKE FUNCTION REFERENCES")
    print("-" * 80)
    ui_dir = Path(__file__).parent / "odibi_core" / "learnodibi_ui"
    fake_refs = find_fake_function_references(ui_dir)
    
    if fake_refs:
        for file_path, refs in sorted(fake_refs.items()):
            print(f"\n{file_path}:")
            for func, line_num in refs:
                print(f"  Line {line_num}: {func}")
    else:
        print("No fake function references found!")
    print()
    
    # 3. Check walkthrough parsing
    print("3. WALKTHROUGH PARSING TEST")
    print("-" * 80)
    walkthrough_results = check_walkthrough_parsing()
    
    for name, counts in sorted(walkthrough_results.items()):
        print(f"\n{name}:")
        print(f"  Missions: {counts['missions']}")
        print(f"  Steps: {counts['steps']}")
        print(f"  Exercises: {counts['exercises']}")
        print(f"  Total: {counts['total']}")
    
    print()
    print("=" * 80)
    
    return real_functions, fake_refs, walkthrough_results


if __name__ == "__main__":
    generate_audit_report()
