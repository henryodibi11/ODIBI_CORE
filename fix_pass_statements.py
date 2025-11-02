"""
Script to remove placeholder 'pass' statements from the Functions walkthrough
"""
import re
from pathlib import Path

walkthrough_file = Path("docs/walkthroughs/DEVELOPER_WALKTHROUGH_FUNCTIONS.md")

print(f"Reading {walkthrough_file}...")
content = walkthrough_file.read_text(encoding='utf-8')

# Count original pass statements
original_pass_count = len(re.findall(r'^\s+pass\s*$', content, re.MULTILINE))
print(f"Original: {original_pass_count} standalone 'pass' statements")

# Pattern 1: Remove lines with ONLY whitespace + 'pass'
# But keep them if they're the only statement in a block (legitimate use)
lines = content.split('\n')
fixed_lines = []
skip_next_passes = False

for i, line in enumerate(lines):
    # Check if this line is a standalone 'pass'
    is_pass_line = bool(re.match(r'^\s+pass\s*$', line))
    
    if is_pass_line:
        # Look ahead - if the next non-empty line is also 'pass' or is a return/statement,
        # this is likely a placeholder
        next_lines = [l for l in lines[i+1:i+4] if l.strip()]
        if next_lines:
            next_line = next_lines[0]
            # Skip if next is also pass, or if next is return/raise (placeholder pattern)
            if re.match(r'^\s+pass\s*$', next_line) or re.match(r'^\s+(return|raise|def|class)', next_line):
                print(f"  Removing placeholder pass at line {i+1}")
                continue  # Skip this pass line
    
    fixed_lines.append(line)

content_fixed = '\n'.join(fixed_lines)

# Count remaining pass statements
final_pass_count = len(re.findall(r'^\s+pass\s*$', content_fixed, re.MULTILINE))
print(f"\nAfter fix: {final_pass_count} 'pass' statements (removed {original_pass_count - final_pass_count})")

# Write back
print(f"\nWriting fixed content to {walkthrough_file}...")
walkthrough_file.write_text(content_fixed, encoding='utf-8')

print("✅ Fixed! All placeholder 'pass' blocks removed.")
print("\nPlease restart the LearnODIBI UI to see the clean code.")
