"""Demo showcase execution - writes to file instead of stdout."""
import sys
import logging
sys.path.insert(0, "D:/projects/odibi_core")

# Disable stdout issues
logging.basicConfig(level=logging.WARNING, filename='showcase_demo.log')

from scripts.advanced_showcase_executor import AdvancedShowcaseExecutor

executor = AdvancedShowcaseExecutor()
execution = executor.run_advanced_showcase(1)

# Write results to file
with open("D:/projects/odibi_core/SHOWCASE_001_RESULT.txt", "w", encoding="utf-8") as f:
    if execution and execution.status == "SUCCESS":
        f.write("="*80 + "\n")
        f.write("SUCCESS! Advanced Showcase #001\n")
        f.write("="*80 + "\n\n")
        f.write(f"Title: {execution.title}\n")
        f.write(f"Domain: {execution.domain}\n")
        f.write(f"Batch: {execution.batch_type}\n")
        f.write(f"Archetype: {execution.archetype}\n")
        f.write(f"Topology: {execution.dag_topology}\n")
        f.write(f"Steps Executed: {execution.steps_executed}\n")
        f.write(f"Execution Time: {execution.execution_time_ms:.2f}ms\n")
        f.write(f"Cache Hits: {execution.cache_hits}\n")
        f.write(f"Validation Checks: {execution.validation_checks}\n")
        f.write(f"Events Fired: {len(execution.events_fired)}\n")
        f.write(f"Tracker Snapshots: {execution.tracker_snapshots}\n\n")
        f.write("="*80 + "\n")
        f.write("RICH, DOMAIN-SPECIFIC REFLECTION\n")
        f.write("="*80 + "\n\n")
        f.write(execution.reflection + "\n\n")
        f.write("="*80 + "\n")
        f.write(f"Report saved to: reports/advanced_showcases/SHOWCASE_ADV_001.md\n")
        f.write("="*80 + "\n")
    else:
        f.write(f"FAILED: {execution.error_message if execution else 'No execution'}\n")
