"""Quick test of advanced showcase system with first showcase only."""
import sys
sys.path.insert(0, "D:/projects/odibi_core")

from odibi_core.creative.batch_planner import BatchPlanner
from scripts.advanced_showcase_executor import AdvancedShowcaseExecutor

# Generate 5 showcases
print("Generating 5 test showcases...")
planner = BatchPlanner()
planner.generate_all(count=5, out_dir="D:/projects/odibi_core/resources/configs/test_showcases")

# Execute first showcase
print("\nExecuting showcase #1...")
executor = AdvancedShowcaseExecutor(base_path="D:/projects/odibi_core")
executor.config_path = executor.base_path / "resources/configs/test_showcases"
executor.output_path = executor.base_path / "resources/output/test_showcases"
executor.report_path = executor.base_path / "reports/test_showcases"

execution = executor.run_advanced_showcase(1)

if execution and execution.status == "SUCCESS":
    print(f"\nSUCCESS! Check the report at:")
    print(f"  {executor.report_path / 'SHOWCASE_ADV_001.md'}")
    print(f"\nReflection preview:")
    print(execution.reflection[:500])
else:
    print(f"\nFailed: {execution.error_message if execution else 'No execution'}")
