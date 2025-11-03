"""
Comprehensive Walkthrough Execution Validation
Tests every python[pandas] code block in all 11 walkthroughs
"""
import json
from pathlib import Path
from odibi_core.learnodibi_ui.walkthrough_parser import WalkthroughParser
from odibi_core.learnodibi_ui.code_executor import CodeExecutor

# Setup
ODIBI_ROOT = Path(__file__).parent
walkthroughs_dir = ODIBI_ROOT / "docs" / "walkthroughs"
parser = WalkthroughParser(walkthroughs_dir)

# Target walkthroughs (11 total)
WALKTHROUGH_FILES = [
    "DEVELOPER_WALKTHROUGH_PHASE_1.md",
    "DEVELOPER_WALKTHROUGH_PHASE_2.md",
    "DEVELOPER_WALKTHROUGH_PHASE_3.md",
    "DEVELOPER_WALKTHROUGH_PHASE_4.md",
    "DEVELOPER_WALKTHROUGH_PHASE_5.md",
    "DEVELOPER_WALKTHROUGH_PHASE_6.md",
    "DEVELOPER_WALKTHROUGH_PHASE_7.md",
    "DEVELOPER_WALKTHROUGH_PHASE_8.md",
    "DEVELOPER_WALKTHROUGH_PHASE_9.md",
    "DEVELOPER_WALKTHROUGH_FUNCTIONS.md",
    "DEVELOPER_WALKTHROUGH_LEARNODIBI_FINAL_QA.md"
]

def validate_walkthrough(filename):
    """Validate all code blocks in a walkthrough"""
    print(f"\n{'='*80}")
    print(f"VALIDATING: {filename}")
    print(f"{'='*80}")
    
    filepath = walkthroughs_dir / filename
    if not filepath.exists():
        return {
            'filename': filename,
            'status': 'NOT_FOUND',
            'steps': [],
            'summary': {'total': 0, 'runnable': 0, 'passed': 0, 'failed': 0}
        }
    
    walkthrough = parser.parse_walkthrough(filepath)
    executor = CodeExecutor(engine='pandas')
    
    results = {
        'filename': filename,
        'title': walkthrough.title,
        'status': 'OK',
        'steps': [],
        'summary': {'total': 0, 'runnable': 0, 'passed': 0, 'failed': 0, 'demo': 0}
    }
    
    for step in walkthrough.steps:
        step_result = {
            'step_number': step.step_number,
            'title': step.title,
            'is_runnable': step.is_runnable,
            'is_demo': step.is_demo,
            'engine': step.engine,
            'has_code': step.code is not None
        }
        
        results['summary']['total'] += 1
        
        if step.is_demo:
            results['summary']['demo'] += 1
            step_result['status'] = 'DEMO'
            step_result['message'] = 'Teaching example - not executed'
        elif step.is_runnable and step.code:
            results['summary']['runnable'] += 1
            
            # Pre-flight check
            preflight = executor.preflight_check(step.code)
            if not preflight.passed:
                results['summary']['failed'] += 1
                step_result['status'] = 'SYNTAX_ERROR'
                step_result['error'] = preflight.error_msg
                print(f"  [FAIL] Step {step.step_number}: {step.title}")
                print(f"         Syntax Error: {preflight.error_msg}")
            else:
                # Execute
                exec_result = executor.execute(step.code)
                if exec_result['success']:
                    results['summary']['passed'] += 1
                    step_result['status'] = 'PASSED'
                    print(f"  [PASS] Step {step.step_number}: {step.title}")
                else:
                    results['summary']['failed'] += 1
                    step_result['status'] = 'RUNTIME_ERROR'
                    step_result['error'] = exec_result['error'][:200]
                    print(f"  [FAIL] Step {step.step_number}: {step.title}")
                    print(f"         Runtime Error: {exec_result['error'][:100]}...")
        else:
            step_result['status'] = 'NOT_RUNNABLE'
        
        results['steps'].append(step_result)
    
    # Summary
    print(f"\nSummary for {filename}:")
    print(f"  Total steps: {results['summary']['total']}")
    print(f"  Runnable: {results['summary']['runnable']}")
    print(f"  Demo/Teaching: {results['summary']['demo']}")
    print(f"  Passed: {results['summary']['passed']}")
    print(f"  Failed: {results['summary']['failed']}")
    
    return results

def main():
    print("ODIBI CORE - Walkthrough Execution Validation")
    print("=" * 80)
    print(f"Walkthroughs directory: {walkthroughs_dir}")
    print(f"Target files: {len(WALKTHROUGH_FILES)}")
    
    all_results = []
    
    for filename in WALKTHROUGH_FILES:
        result = validate_walkthrough(filename)
        all_results.append(result)
    
    # Overall summary
    print(f"\n{'='*80}")
    print("OVERALL SUMMARY")
    print(f"{'='*80}")
    
    total_walkthroughs = len(all_results)
    total_steps = sum(r['summary']['total'] for r in all_results)
    total_runnable = sum(r['summary']['runnable'] for r in all_results)
    total_demo = sum(r['summary']['demo'] for r in all_results)
    total_passed = sum(r['summary']['passed'] for r in all_results)
    total_failed = sum(r['summary']['failed'] for r in all_results)
    
    print(f"Walkthroughs: {total_walkthroughs}")
    print(f"Total steps: {total_steps}")
    print(f"Runnable code blocks: {total_runnable}")
    print(f"Demo/Teaching blocks: {total_demo}")
    print(f"Passed: {total_passed}")
    print(f"Failed: {total_failed}")
    
    if total_runnable > 0:
        pass_rate = (total_passed / total_runnable) * 100
        print(f"\nExecution Success Rate: {pass_rate:.1f}%")
    
    # Detailed failures
    print(f"\n{'='*80}")
    print("DETAILED FAILURES")
    print(f"{'='*80}")
    
    for result in all_results:
        failed_steps = [s for s in result['steps'] if s.get('status') in ['SYNTAX_ERROR', 'RUNTIME_ERROR']]
        if failed_steps:
            print(f"\n{result['filename']}:")
            for step in failed_steps:
                print(f"  Step {step['step_number']}: {step['title']}")
                print(f"    Status: {step['status']}")
                if 'error' in step:
                    print(f"    Error: {step['error'][:150]}")
    
    # Save JSON report
    report_path = ODIBI_ROOT / "walkthrough_validation_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n{'='*80}")
    print(f"Full report saved to: {report_path}")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()
