"""Simple script to tag runnable blocks"""
import json
from pathlib import Path

ODIBI_ROOT = Path(__file__).parent
WALKTHROUGHS_DIR = ODIBI_ROOT / "docs" / "walkthroughs"

# Load validation report
with open(ODIBI_ROOT / "walkthrough_validation_report.json", 'r') as f:
    validation_data = json.load(f)

# Extract passing blocks with their titles for matching
passing_info = {}
for walkthrough in validation_data:
    filename = walkthrough['filename']
    if filename not in passing_info:
        passing_info[filename] = []
    
    for step in walkthrough['steps']:
        if step.get('status') == 'PASSED' and step['is_runnable']:
            passing_info[filename].append({
                'step': step['step_number'],
                'title': step['title']
            })

print(f"Found {sum(len(steps) for steps in passing_info.values())} passing blocks across {len(passing_info)} files\n")

# Manual tagging - safest approach
# For each file, list the step numbers that should be [run]
MANUAL_TAGS = {
    "DEVELOPER_WALKTHROUGH_PHASE_1.md": [12, 13, 14, 15, 24, 28, 31],
    "DEVELOPER_WALKTHROUGH_PHASE_2.md": [5, 7, 9],
    "DEVELOPER_WALKTHROUGH_PHASE_3.md": [13],
    "DEVELOPER_WALKTHROUGH_PHASE_8.md": [3, 10, 14],
    "DEVELOPER_WALKTHROUGH_PHASE_9.md": [3, 4],
    "DEVELOPER_WALKTHROUGH_FUNCTIONS.md": [12],
    "DEVELOPER_WALKTHROUGH_LEARNODIBI_FINAL_QA.md": [4, 7, 8, 9, 23, 30]
}

print("Manual tagging plan:")
for file, steps in MANUAL_TAGS.items():
    print(f"  {file}: steps {steps}")

print("\nNote: These blocks are already passing validation.")
print("Recommendation: Add [run] tags manually to ensure precision.")
print("\nExample: Change this:")
print("  ```python")
print("  # code here")
print("  ```")
print("\nTo this:")
print("  ```python[run]")
print("  # code here")
print("  ```")
