"""
Test HTML Story Generation for Creative Showcases
"""

import sys
sys.path.insert(0, "D:/projects/odibi_core")

from creative_showcase_executor import CreativeShowcaseExecutor

# Test with just 3 showcases
executor = CreativeShowcaseExecutor()

print("\n" + "="*80)
print("Testing HTML Story Generation")
print("="*80 + "\n")

for showcase_id in [1, 50, 87]:
    print(f"\nGenerating showcase #{showcase_id}...")
    executor.run_creative_showcase(showcase_id)

print("\n" + "="*80)
print("✅ Test Complete - Check D:/projects/odibi_core/resources/output/creative_showcases/")
print("="*80)
