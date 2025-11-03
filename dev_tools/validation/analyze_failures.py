"""Analyze all failures to create targeted fixes"""
import json
from pathlib import Path
from collections import defaultdict

# Load validation report
with open('walkthrough_validation_report.json', 'r') as f:
    data = json.load(f)

failures_by_type = defaultdict(list)

for walkthrough in data:
    filename = walkthrough['filename']
    for step in walkthrough['steps']:
        if step.get('status') in ['SYNTAX_ERROR', 'RUNTIME_ERROR'] and step.get('is_runnable'):
            error = step.get('error', '')
            error_type = error.split(':')[0] if error else 'Unknown'
            
            failures_by_type[error_type].append({
                'file': filename,
                'step': step['step_number'],
                'title': step['title'],
                'error': error[:150]
            })

# Print summary
print("FAILURE ANALYSIS")
print("="*80)
for error_type, failures in sorted(failures_by_type.items(), key=lambda x: -len(x[1])):
    print(f"\n{error_type}: {len(failures)} failures")
    for f in failures[:3]:  # Show first 3 of each type
        print(f"  - {f['file']} Step {f['step']}: {f['title'][:40]}")
        print(f"    {f['error'][:100]}")

print(f"\n\nTOTAL FAILURES: {sum(len(v) for v in failures_by_type.values())}")

# Save detailed report
with open('failure_details.json', 'w') as f:
    json.dump(dict(failures_by_type), f, indent=2)

print("\nDetailed report saved to: failure_details.json")
