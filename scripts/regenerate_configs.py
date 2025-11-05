"""Regenerate configs with fixed format."""
import sys
import os
sys.path.insert(0, "D:/projects/odibi_core")
os.chdir("D:/projects/odibi_core")

from odibi_core.creative.batch_planner import BatchPlanner

print("="*80)
print("Regenerating 100 Advanced Showcase Configs")
print("="*80)

planner = BatchPlanner()
planner.generate_all(
    count=100,
    out_dir="D:/projects/odibi_core/resources/configs/advanced_showcases"
)

print("\n" + "="*80)
print("DONE! Configs regenerated successfully")
print("="*80)
