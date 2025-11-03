"""Debug script to find where walkthroughs are being searched"""
from pathlib import Path
import odibi_core
from odibi_core.learnodibi_ui.walkthrough_parser import get_walkthrough_parser

print("="*80)
print("DEBUGGING WALKTHROUGH LOCATION")
print("="*80)

# Check package location
pkg_path = Path(odibi_core.__file__).parent
print(f"\n1. Package installed at: {pkg_path}")

# Check where parser is looking
print(f"\n2. Parser search locations:")
odibi_root = pkg_path

candidates = [
    odibi_root / "docs" / "walkthroughs",
    odibi_root.parent / "docs" / "walkthroughs",
    odibi_root.parent.parent / "docs" / "walkthroughs",
    Path.cwd() / "docs" / "walkthroughs",
]

for i, candidate in enumerate(candidates, 1):
    exists = candidate.exists()
    if exists:
        md_files = list(candidate.glob("DEVELOPER_WALKTHROUGH_*.md"))
        print(f"   {i}. {candidate}")
        print(f"      Exists: {exists}")
        print(f"      Walkthrough files: {len(md_files)}")
    else:
        print(f"   {i}. {candidate} - Does not exist")

# Get actual parser
print(f"\n3. Testing parser:")
parser = get_walkthrough_parser()
print(f"   Parser walkthrough dir: {parser.walkthroughs_dir}")
print(f"   Dir exists: {parser.walkthroughs_dir.exists()}")

walkthroughs = parser.list_walkthroughs()
print(f"   Walkthroughs found: {len(walkthroughs)}")

if walkthroughs:
    print(f"\n4. SUCCESS! Found walkthroughs:")
    for wt in walkthroughs[:3]:
        print(f"   - {wt['title']}")
else:
    print(f"\n4. FAILED! No walkthroughs found")
    print(f"\n   Contents of {parser.walkthroughs_dir}:")
    if parser.walkthroughs_dir.exists():
        for item in parser.walkthroughs_dir.iterdir():
            print(f"   - {item.name}")
    else:
        print(f"   Directory does not exist!")

print("\n" + "="*80)
