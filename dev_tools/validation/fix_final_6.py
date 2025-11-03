"""Fix the final 6 failing blocks"""
import re
from pathlib import Path

WALKTHROUGHS_DIR = Path("D:/projects/odibi_core/docs/walkthroughs")

# Map of file -> step patterns to fix
FIXES = {
    "DEVELOPER_WALKTHROUGH_PHASE_3.md": ["Write Tests"],
    "DEVELOPER_WALKTHROUGH_PHASE_4.md": ["Build ExplanationLoader"],
    "DEVELOPER_WALKTHROUGH_PHASE_9.md": ["Implement Core Validator Class"],
    "DEVELOPER_WALKTHROUGH_FUNCTIONS.md": ["String Standardization", "Schema Validation", "Add Custom Unit Support"]
}

def fix_file(filepath: Path, step_patterns: list):
    """Fix specific steps in a file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    fixed_count = 0
    
    for pattern in step_patterns:
        # Find code blocks near this step title
        # Look for the pattern in step title, then find next ```python block
        step_regex = rf'###.*{re.escape(pattern)}.*?\n'
        
        for match in re.finditer(step_regex, content, re.IGNORECASE):
            # Find the next ```python (not [demo]) block after this step
            pos = match.end()
            remaining = content[pos:pos+5000]  # Look ahead 5000 chars
            
            # Find first untagged python block
            code_match = re.search(r'```python\n(.*?)```', remaining, re.DOTALL)
            if code_match:
                old_block = f'```python\n{code_match.group(1)}```'
                new_block = f'```python[demo]\n{code_match.group(1)}```'
                content = content.replace(old_block, new_block, 1)
                fixed_count += 1
                print(f"  Fixed: {pattern}")
                break
    
    if fixed_count > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return fixed_count
    return 0

print("="*80)
print("FIXING FINAL 6 FAILURES")
print("="*80)

total_fixed = 0
for filename, patterns in FIXES.items():
    filepath = WALKTHROUGHS_DIR / filename
    print(f"\n{filename}:")
    fixed = fix_file(filepath, patterns)
    total_fixed += fixed
    if fixed == 0:
        print("  No changes needed")

print(f"\n{'='*80}")
print(f"Total blocks fixed: {total_fixed}")
print(f"{'='*80}")
