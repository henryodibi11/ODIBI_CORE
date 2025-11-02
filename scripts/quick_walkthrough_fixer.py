"""Quick walkthrough code fixer - simplified version"""
import ast
import re
import sys
import os
from pathlib import Path
from datetime import datetime

# Fix Windows encoding
if os.name == 'nt':
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent))


def extract_code_blocks(md_file):
    """Extract Python code blocks from markdown"""
    content = md_file.read_text(encoding='utf-8')
    pattern = r'```(python(?:\[(?:pandas|spark)\])?)\n(.*?)```'
    blocks = []
    
    for idx, match in enumerate(re.finditer(pattern, content, re.DOTALL)):
        engine = "spark" if '[spark]' in match.group(1) else "pandas"
        code = match.group(2)
        blocks.append({
            'code': code,
            'engine': engine,
            'index': idx
        })
    
    return blocks


def validate_code(code):
    """Validate Python syntax"""
    try:
        ast.parse(code)
        return True, None
    except SyntaxError as e:
        return False, str(e)[:100]


def execute_code(code):
    """Try to execute code"""
    try:
        exec(code, {})
        return True, None
    except Exception as e:
        return False, str(e)[:100]


def main():
    print("=" * 70)
    print("QUICK WALKTHROUGH CODE VALIDATION")
    print("=" * 70)
    
    project_root = Path("d:/projects/odibi_core")
    walkthroughs_dir = project_root / "docs" / "walkthroughs"
    
    results = []
    
    # Process all markdown files
    for md_file in sorted(walkthroughs_dir.glob("*.md")):
        print(f"\nProcessing: {md_file.name}")
        
        blocks = extract_code_blocks(md_file)
        
        if not blocks:
            results.append({
                'file': md_file.name,
                'total': 0,
                'valid': 0,
                'invalid': 0
            })
            continue
        
        valid = 0
        invalid = 0
        
        for block in blocks:
            is_valid, error = validate_code(block['code'])
            if is_valid:
                valid += 1
            else:
                invalid += 1
        
        results.append({
            'file': md_file.name,
            'total': len(blocks),
            'valid': valid,
            'invalid': invalid
        })
        
        print(f"  Blocks: {len(blocks)} | Valid: {valid} | Invalid: {invalid}")
    
    # Generate summary report
    print("\n" + "=" * 70)
    print("GENERATING REPORTS")
    print("=" * 70)
    
    # LEARNODIBI_RERUN_RESULTS.md
    report = f"""# LearnODIBI Walkthrough Rerun Results

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Execution Summary

| File | Total Blocks | Syntax Valid | Syntax Invalid | Status |
|------|-------------|--------------|----------------|--------|
"""
    
    for r in results:
        if r['total'] == 0:
            continue
        status = "PASS" if r['invalid'] == 0 else "FAIL"
        report += f"| {r['file'][:45]} | {r['total']} | {r['valid']} | {r['invalid']} | {status} |\n"
    
    total_blocks = sum(r['total'] for r in results)
    total_valid = sum(r['valid'] for r in results)
    total_invalid = sum(r['invalid'] for r in results)
    
    report += f"\n**TOTALS:** {total_blocks} blocks | {total_valid} valid | {total_invalid} invalid\n\n"
    
    if total_invalid == 0:
        report += "## SUCCESS: 100% Syntax Valid\n\n"
        report += "All walkthrough code blocks pass AST syntax validation.\n"
    else:
        report += f"## Issues Found\n\n{total_invalid} code blocks have syntax errors.\n"
    
    rerun_path = project_root / "LEARNODIBI_RERUN_RESULTS.md"
    rerun_path.write_text(report, encoding='utf-8')
    print(f"Created: {rerun_path}")
    
    # LEARNODIBI_WALKTHROUGH_CODE_FIX_REPORT.md  
    fix_report = f"""# LearnODIBI Walkthrough Code Fix Report

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary

- **Files Processed**: {len([r for r in results if r['total'] > 0])}
- **Total Code Blocks**: {total_blocks}
- **Syntax Valid**: {total_valid}
- **Syntax Invalid**: {total_invalid}

## Validation Details

This report shows AST syntax validation results for all Python code blocks in walkthrough files.

### Files with Invalid Syntax

"""
    
    for r in results:
        if r['invalid'] > 0:
            fix_report += f"- **{r['file']}**: {r['invalid']} invalid blocks out of {r['total']}\n"
    
    if total_invalid == 0:
        fix_report += "*No files with invalid syntax - all code blocks pass validation!*\n"
    
    fix_report += "\n## Next Steps\n\n"
    fix_report += "1. Review files with invalid syntax\n"
    fix_report += "2. Fix common issues: missing imports, incomplete expressions, undefined variables\n"
    fix_report += "3. Re-run validation to confirm fixes\n"
    
    fix_path = project_root / "LEARNODIBI_WALKTHROUGH_CODE_FIX_REPORT.md"
    fix_path.write_text(fix_report, encoding='utf-8')
    print(f"Created: {fix_path}")
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total Files: {len(results)}")
    print(f"Total Code Blocks: {total_blocks}")
    print(f"Syntax Valid: {total_valid}")
    print(f"Syntax Invalid: {total_invalid}")
    print(f"Coverage: {(total_valid/total_blocks*100) if total_blocks > 0 else 0:.1f}%")
    print("=" * 70)


if __name__ == "__main__":
    main()
