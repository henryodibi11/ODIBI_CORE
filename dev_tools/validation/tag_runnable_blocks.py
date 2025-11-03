"""
Tag Runnable Blocks Script
Marks the 23 known-passing code blocks as [run], leaving rest as teaching demos
"""
import json
from pathlib import Path
import re

ODIBI_ROOT = Path(__file__).parent
WALKTHROUGHS_DIR = ODIBI_ROOT / "docs" / "walkthroughs"

# Load validation report to find passing blocks
with open(ODIBI_ROOT / "walkthrough_validation_report.json", 'r') as f:
    validation_data = json.load(f)

# Extract list of passing blocks: (filename, step_number, step_title)
passing_blocks = []
for walkthrough in validation_data:
    filename = walkthrough['filename']
    for step in walkthrough['steps']:
        if step.get('status') == 'PASSED' and step['is_runnable']:
            passing_blocks.append({
                'file': filename,
                'step': step['step_number'],
                'title': step['title']
            })

print(f"Found {len(passing_blocks)} passing code blocks to tag as [run]")
print("\nPassing blocks:")
for block in passing_blocks:
    print(f"  - {block['file']}: Step {block['step']} - {block['title']}")

# Now we need to mark these specific blocks
# Strategy: Find the code block in each step and change ```python to ```python[run]

def tag_runnable_in_walkthrough(filename: str, step_numbers: list, dry_run=True):
    """Tag specific steps as runnable in a walkthrough"""
    filepath = WALKTHROUGHS_DIR / filename
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all step sections with their code blocks
    # Pattern: ### Step X: Title ... code block
    step_pattern = r'###\s+(Mission|Step|Exercise)\s+(\d+(?:\.\d+)*)(?::|[-–]\s*|\s+)\s*(.+?)\n+((?:(?!###).)+)'
    
    modified = False
    new_content = content
    
    for match in re.finditer(step_pattern, content, re.DOTALL):
        step_type, step_num, title, body = match.groups()
        step_number = int(step_num.split('.')[0])  # Get primary step number
        
        if step_number in step_numbers:
            # Find first ```python code block in this step and mark as [run]
            # Only mark if not already marked as [pandas], [spark], [demo], [run]
            code_pattern = r'```python\n'
            if re.search(code_pattern, body):
                # Replace FIRST occurrence in this step
                new_body = re.sub(code_pattern, '```python[run]\n', body, count=1)
                new_content = new_content.replace(match.group(0), match.group(0).replace(body, new_body))
                modified = True
                print(f"  Tagged Step {step_number}: {title[:50]}...")
    
    if modified and not dry_run:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    
    return modified


def main(dry_run=True):
    """Main execution"""
    print("\n" + "="*80)
    print("TAGGING RUNNABLE BLOCKS")
    print("="*80)
    print(f"Mode: {'DRY RUN' if dry_run else 'APPLY CHANGES'}\n")
    
    # Group by file
    files_to_update = {}
    for block in passing_blocks:
        if block['file'] not in files_to_update:
            files_to_update[block['file']] = []
        files_to_update[block['file']].append(block['step'])
    
    print(f"\nFiles to update: {len(files_to_update)}")
    
    for filename, step_numbers in files_to_update.items():
        print(f"\n{filename}:")
        print(f"  Steps to tag: {sorted(step_numbers)}")
        modified = tag_runnable_in_walkthrough(filename, step_numbers, dry_run=dry_run)
        if modified:
            print(f"  {'[DRY RUN] Would update' if dry_run else '✓ Updated'}")
    
    print("\n" + "="*80)
    if dry_run:
        print("DRY RUN COMPLETE - Run with --apply to make changes")
    else:
        print("ALL CHANGES APPLIED")
    print("="*80)


if __name__ == "__main__":
    import sys
    dry_run = '--apply' not in sys.argv
    main(dry_run=dry_run)
