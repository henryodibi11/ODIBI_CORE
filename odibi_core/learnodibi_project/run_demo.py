"""
Run the Learn ODIBI Project demo pipeline.

Usage:
    python -m odibi_core.learnodibi_project.run_demo
"""

import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def main():
    """Run the demo pipeline with all layers."""
    print("=" * 80)
    print("ODIBI CORE - Learn Project Demo")
    print("Bronze → Silver → Gold Pipeline Demonstration")
    print("=" * 80)
    print()

    from odibi_core.learnodibi_project import DemoPipeline

    # Create pipeline
    pipeline = DemoPipeline()

    # Show pipeline description
    print(pipeline.describe())
    print()
    print("=" * 80)
    print()

    # Run Bronze layer
    print("[1/4] Running Bronze Layer (Ingestion)...")
    print("-" * 80)
    bronze_result = pipeline.run_bronze()
    print(f"✓ Bronze complete: {len(bronze_result.data_map)} datasets")
    print(f"  Datasets: {list(bronze_result.data_map.keys())}")
    print()

    # Run Silver layer
    print("[2/4] Running Silver Layer (Bronze + Transformation)...")
    print("-" * 80)
    silver_result = pipeline.run_silver()
    print(f"✓ Silver complete: {len(silver_result.data_map)} datasets")
    
    # Show silver data sample
    if 'silver_energy_weather' in silver_result.data_map:
        df = silver_result.data_map['silver_energy_weather']
        print(f"  silver_energy_weather: {len(df)} rows")
        print(f"  Columns: {list(df.columns)}")
    print()

    # Run Gold layer
    print("[3/4] Running Gold Layer (Bronze + Silver + Aggregation)...")
    print("-" * 80)
    gold_result = pipeline.run_gold()
    print(f"✓ Gold complete: {len(gold_result.data_map)} datasets")
    
    # Show gold metrics
    if 'gold_efficiency_report' in gold_result.data_map:
        df = gold_result.data_map['gold_efficiency_report']
        print(f"  gold_efficiency_report: {len(df)} facilities")
        print()
        print("  Efficiency Metrics:")
        print(df.to_string(index=False))
    print()

    # Run full pipeline with publishing
    print("[4/4] Running Full Pipeline (All Layers + Publish)...")
    print("-" * 80)
    full_result = pipeline.run_full()
    print(f"✓ Full pipeline complete: {len(full_result.data_map)} datasets")
    print()

    # Check output files
    output_dir = Path(__file__).parent / "output"
    print("Output Files:")
    print("-" * 80)
    
    files = [
        "gold_daily_summary.parquet",
        "gold_efficiency_report.json",
        "gold_maintenance_costs.csv"
    ]
    
    for filename in files:
        filepath = output_dir / filename
        if filepath.exists():
            size_kb = filepath.stat().st_size / 1024
            print(f"  ✓ {filename} ({size_kb:.2f} KB)")
        else:
            print(f"  ✗ {filename} (not found)")
    
    print()
    print("=" * 80)
    print("Demo Complete!")
    print("=" * 80)
    print()
    print("Next steps:")
    print("  • View outputs in: odibi_core/learnodibi_project/output/")
    print("  • Check tracker logs for lineage and metrics")
    print("  • Modify configs to customize transformations")
    print("  • Try with Spark: DemoPipeline(engine='spark')")
    print()


if __name__ == "__main__":
    main()
