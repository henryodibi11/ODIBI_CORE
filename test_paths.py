"""
Quick test to verify paths and manifest loading
"""
from pathlib import Path
import sys

# Setup paths
ODIBI_ROOT = Path(__file__).parent
print(f"ODIBI_ROOT: {ODIBI_ROOT}")
print(f"Exists: {ODIBI_ROOT.exists()}")

# Check walkthroughs dir
walkthroughs_dir = ODIBI_ROOT / "docs" / "walkthroughs"
print(f"\nWalkthroughs dir: {walkthroughs_dir}")
print(f"Exists: {walkthroughs_dir.exists()}")

if walkthroughs_dir.exists():
    # List DEVELOPER_WALKTHROUGH files
    files = list(walkthroughs_dir.glob("DEVELOPER_WALKTHROUGH_*.md"))
    print(f"\nFound {len(files)} DEVELOPER_WALKTHROUGH files:")
    for f in sorted(files):
        print(f"  - {f.name}")

# Check manifest
manifest_path = ODIBI_ROOT / "walkthrough_manifest.json"
print(f"\nManifest path: {manifest_path}")
print(f"Exists: {manifest_path.exists()}")

# Try to load manifest
if manifest_path.exists():
    import json
    with open(manifest_path) as f:
        data = json.load(f)
    print(f"\nManifest has {data.get('total_walkthroughs', 0)} walkthroughs")
    print(f"Walkthroughs:")
    for wt in data.get('walkthroughs', [])[:3]:
        print(f"  - {wt['filename']}: {wt['title']}")

# Try importing the teaching engine
sys.path.insert(0, str(ODIBI_ROOT))

try:
    from odibi_core.learnodibi_ui.ui_teaching_engine import TeachingEngine
    print("\n✅ TeachingEngine import successful")
    
    engine = TeachingEngine(ODIBI_ROOT)
    print(f"✅ TeachingEngine initialized")
    
    lessons = engine.get_all_lessons()
    print(f"✅ Got {len(lessons)} lessons")
    
    for lesson in lessons[:3]:
        print(f"  - {lesson.title}")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
