"""Regenerate walkthrough manifest with validation"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from odibi_core.learnodibi_ui.walkthrough_validator import WalkthroughValidator
import json

# Set paths
ODIBI_ROOT = Path(__file__).parent
walkthroughs_dir = ODIBI_ROOT / "odibi_core" / "docs" / "walkthroughs"
manifest_path = ODIBI_ROOT / "odibi_core" / "resources" / "walkthrough_manifest.json"

# Run validator
print("Validating walkthroughs...")
validator = WalkthroughValidator(walkthroughs_dir)
report = validator.generate_report()

# Save manifest
manifest_path.parent.mkdir(exist_ok=True)
with open(manifest_path, 'w', encoding='utf-8') as f:
    json.dump(report, f, indent=2, ensure_ascii=False)

print(f"\n✅ Manifest regenerated: {manifest_path}")
print(f"Total walkthroughs: {report['total_walkthroughs']}")
print(f"Total code blocks: {report['totals']['total_code_blocks']}")
print(f"Valid code blocks: {report['totals']['valid_code_blocks']}")
print(f"Validity: {report['totals']['valid_code_blocks']/max(report['totals']['total_code_blocks'],1)*100:.1f}%")
