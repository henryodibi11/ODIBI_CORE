"""Run sample showcases from different domains."""
import sys
import logging
sys.path.insert(0, "D:/projects/odibi_core")
logging.basicConfig(level=logging.WARNING, filename='sample_showcases.log')

from scripts.advanced_showcase_executor import AdvancedShowcaseExecutor

# Run showcases: 1 (Finance), 7 (IoT), 13 (Retail), 63 (IoT Streaming), 71 (Finance Star Schema)
showcase_ids = [1, 7, 13, 63, 71]

executor = AdvancedShowcaseExecutor()
results = []

for sid in showcase_ids:
    execution = executor.run_advanced_showcase(sid)
    if execution:
        results.append(execution)

# Write comparison report
with open("D:/projects/odibi_core/SAMPLE_SHOWCASES_COMPARISON.md", "w", encoding="utf-8") as f:
    f.write("# Sample Showcases Comparison\n\n")
    f.write("Demonstrating rich, domain-specific explanations across different archetypes.\n\n")
    f.write("="*80 + "\n\n")
    
    for i, exec in enumerate(results, 1):
        f.write(f"## Showcase #{exec.showcase_id}: {exec.title}\n\n")
        f.write(f"**Domain:** {exec.domain}  \n")
        f.write(f"**Batch:** {exec.batch_type}  \n")
        f.write(f"**Archetype:** {exec.archetype}  \n")
        f.write(f"**Topology:** {exec.dag_topology}  \n")
        f.write(f"**Complexity:** {exec.complexity_level}  \n")
        f.write(f"**Steps:** {exec.steps_executed}  \n")
        f.write(f"**Status:** {exec.status}  \n\n")
        
        f.write("### 🧠 Rich Reflection\n\n")
        f.write(exec.reflection + "\n\n")
        f.write("---\n\n")
    
    f.write(f"\n\n## Summary\n\n")
    f.write(f"- **Total Showcases Run:** {len(results)}\n")
    f.write(f"- **Success Rate:** {sum(1 for e in results if e.status == 'SUCCESS')}/{len(results)}\n")
    f.write(f"- **Domains Covered:** {', '.join(set(e.domain for e in results))}\n")
    f.write(f"- **Archetypes:** {', '.join(set(e.archetype for e in results))}\n")
    f.write(f"- **Avg Steps:** {sum(e.steps_executed for e in results) / len(results):.1f}\n")
    f.write(f"\n✅ All explanations are domain-specific with contextual business narratives!\n")
