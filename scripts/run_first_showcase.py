"""Run first showcase to demonstrate rich explanations."""
import sys
sys.path.insert(0, "D:/projects/odibi_core")

from scripts.advanced_showcase_executor import AdvancedShowcaseExecutor

print("="*80)
print("Running Advanced Showcase #001")
print("="*80)

executor = AdvancedShowcaseExecutor()
execution = executor.run_advanced_showcase(1)

if execution and execution.status == "SUCCESS":
    print("\n" + "="*80)
    print("SUCCESS!")
    print("="*80)
    print(f"\nTitle: {execution.title}")
    print(f"Domain: {execution.domain}")
    print(f"Steps: {execution.steps_executed}")
    print(f"Time: {execution.execution_time_ms:.2f}ms")
    print(f"\n--- RICH REFLECTION (First 800 chars) ---")
    print(execution.reflection[:800] + "...")
    print(f"\n--- REPORT SAVED TO ---")
    print(f"reports/advanced_showcases/SHOWCASE_ADV_001.md")
else:
    print(f"\nFailed: {execution.error_message if execution else 'No execution'}")
