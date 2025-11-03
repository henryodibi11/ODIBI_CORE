"""
Intelligent Walkthrough Code Block Fixer
Automatically marks teaching fragments as [demo] to prevent false execution failures
"""
import re
from pathlib import Path
from typing import List, Tuple

ODIBI_ROOT = Path(__file__).parent
WALKTHROUGHS_DIR = ODIBI_ROOT / "docs" / "walkthroughs"

# Walkthroughs to fix
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


def is_teaching_fragment(code: str) -> Tuple[bool, str]:
    """
    Detect if code block is a teaching fragment (not meant to execute standalone)
    
    Returns:
        (is_fragment, reason)
    """
    lines = code.strip().split('\n')
    first_line = lines[0].strip() if lines else ""
    
    # Check for obvious teaching patterns
    if first_line.startswith('return '):
        return True, "starts with 'return' outside function"
    
    if first_line.startswith('self.') or first_line.startswith('self '):
        return True, "starts with 'self' outside class"
    
    if re.match(r'^@\w+', first_line):
        # Decorator at start without function - likely fragment
        if len(lines) < 3:
            return True, "decorator without function body"
    
    # Check for class methods without class definition
    if 'def ' in code and 'self' in code and 'class ' not in code:
        # Look for indented def (method without class)
        for line in lines:
            if line.startswith('    def ') or line.startswith('\tdef '):
                return True, "indented method without class definition"
    
    # Check for partial class definitions (missing closing or __init__)
    if 'class ' in code:
        # Complete class should have __init__ or pass or methods
        if '__init__' not in code and 'pass' not in code and 'def ' not in code:
            return True, "incomplete class definition"
    
    # Check for obvious errors that suggest incomplete code
    if first_line in ['raise', 'else:', 'elif ', 'except:', 'finally:']:
        return True, f"starts with control flow keyword: {first_line}"
    
    # Check for very short snippets (< 3 lines) that look like fragments
    if len(lines) < 3 and any(keyword in code for keyword in ['self.', 'return', 'raise', 'yield']):
        return True, "short snippet with incomplete context"
    
    return False, ""


def fix_code_fences(content: str) -> Tuple[str, List[dict]]:
    """
    Find python code fences and mark teaching fragments as [demo]
    
    Returns:
        (fixed_content, changes_list)
    """
    changes = []
    
    # Pattern to find ```python code blocks (not already marked as [pandas], [spark], [demo])
    pattern = r'```python\n(.*?)```'
    
    def replace_func(match):
        code = match.group(1)
        is_fragment, reason = is_teaching_fragment(code)
        
        if is_fragment:
            changes.append({
                'code_preview': code[:50].replace('\n', ' '),
                'reason': reason,
                'action': 'marked as [demo]'
            })
            return f'```python[demo]\n{code}```'
        else:
            return match.group(0)  # Keep unchanged
    
    fixed_content = re.sub(pattern, replace_func, content, flags=re.DOTALL)
    
    return fixed_content, changes


def process_walkthrough(filename: str, dry_run: bool = True) -> dict:
    """Process a single walkthrough file"""
    filepath = WALKTHROUGHS_DIR / filename
    
    if not filepath.exists():
        return {
            'filename': filename,
            'status': 'NOT_FOUND',
            'changes': []
        }
    
    print(f"\n{'='*80}")
    print(f"Processing: {filename}")
    print(f"{'='*80}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    fixed_content, changes = fix_code_fences(original_content)
    
    if changes:
        print(f"\nFound {len(changes)} teaching fragments to mark as [demo]:")
        for i, change in enumerate(changes, 1):
            print(f"  {i}. {change['code_preview']}...")
            print(f"      Reason: {change['reason']}")
    else:
        print("  No teaching fragments detected.")
    
    if not dry_run and changes:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        print(f"\n  ✓ File updated!")
    elif changes:
        print(f"\n  [DRY RUN] Would update file")
    
    return {
        'filename': filename,
        'status': 'PROCESSED',
        'changes_count': len(changes),
        'changes': changes
    }


def main(dry_run: bool = True):
    """
    Main execution
    
    Args:
        dry_run: If True, only analyze without making changes
    """
    print("LearnODIBI Walkthrough Code Block Fixer")
    print("="*80)
    print(f"Mode: {'DRY RUN (no files modified)' if dry_run else 'LIVE (files will be modified)'}")
    print(f"Target: {len(WALKTHROUGH_FILES)} walkthrough files")
    print()
    
    results = []
    total_changes = 0
    
    for filename in WALKTHROUGH_FILES:
        result = process_walkthrough(filename, dry_run=dry_run)
        results.append(result)
        total_changes += result.get('changes_count', 0)
    
    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print(f"Files processed: {len(results)}")
    print(f"Total teaching fragments detected: {total_changes}")
    
    if dry_run:
        print(f"\n⚠️  This was a DRY RUN - no files were modified")
        print(f"   Run with dry_run=False to apply changes")
    else:
        print(f"\n✓ All changes applied successfully!")
    
    # Save report
    report_path = ODIBI_ROOT / "code_block_fix_report.txt"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("Code Block Fix Report\n")
        f.write("="*80 + "\n\n")
        for result in results:
            f.write(f"File: {result['filename']}\n")
            f.write(f"Changes: {result.get('changes_count', 0)}\n")
            if result.get('changes'):
                for change in result['changes']:
                    f.write(f"  - {change['code_preview']}...\n")
                    f.write(f"    Reason: {change['reason']}\n")
            f.write("\n")
    
    print(f"\nReport saved to: {report_path}")


if __name__ == "__main__":
    # Run in DRY RUN mode first to preview changes
    import sys
    
    dry_run = True
    if len(sys.argv) > 1 and sys.argv[1] == '--apply':
        dry_run = False
    
    main(dry_run=dry_run)
