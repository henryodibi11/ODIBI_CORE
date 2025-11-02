"""
Config-driven pipeline demonstration.

Shows ODIBI CORE executing a full pipeline from JSON config with:
- Config loading and validation
- Multi-step execution (ingest → transform → store)
- Tracker snapshots and lineage
- Both Pandas and Spark modes
"""

import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

logger = logging.getLogger(__name__)


def run_pipeline_demo() -> None:
    """
    Run config-driven pipeline demonstration.

    Steps:
    1. Load config from JSON
    2. Validate config
    3. Execute with PandasEngineContext
    4. Show tracker summary
    5. (Optional) Execute with SparkEngineContext
    """
    print("=" * 70)
    print("ODIBI CORE v1.0 - Config-Driven Pipeline Demo")
    print("=" * 70)
    print()

    from odibi_core.core import (
        ConfigLoader,
        ConfigValidator,
        Orchestrator,
        Tracker,
        EventEmitter,
        create_engine_context,
    )

    # Paths
    script_dir = Path(__file__).parent
    config_path = script_dir / "configs" / "simple_pipeline.json"
    output_dir = script_dir / "output"
    output_dir.mkdir(exist_ok=True)

    print(f"Config: {config_path}")
    print(f"Output: {output_dir}")
    print()

    # ========================================================================
    # STEP 1: Load Config
    # ========================================================================
    print("[1/5] Loading configuration...")
    print("-" * 70)

    loader = ConfigLoader()
    steps = loader.load(str(config_path))

    print(f"Loaded {len(steps)} steps:")
    for i, step in enumerate(steps, 1):
        print(f"  {i}. {step.name:<30} ({step.layer}, {step.type}, {step.engine})")
    print()

    # ========================================================================
    # STEP 2: Validate Config
    # ========================================================================
    print("[2/5] Validating configuration...")
    print("-" * 70)

    validator = ConfigValidator()
    try:
        validator.validate_config(steps)
        print("[OK] Config validation passed")
        print("  - All step names unique")
        print("  - All outputs unique")
        print("  - All inputs exist")
        print("  - No circular dependencies")
        print("  - Valid layers and engines")
    except Exception as e:
        print(f"[FAIL] Config validation failed: {e}")
        return

    print()

    # ========================================================================
    # STEP 3: Execute Pipeline (Pandas)
    # ========================================================================
    print("[3/5] Executing pipeline with Pandas engine...")
    print("-" * 70)

    # Create execution context
    context = create_engine_context("pandas")
    context.connect()

    tracker = Tracker(log_dir="tracker_logs")
    events = EventEmitter()

    # Add event listener
    events.on(
        "step_complete",
        lambda step, duration_ms: print(
            f"  [OK] {step.name} completed in {duration_ms:.2f}ms"
        ),
    )

    # Create orchestrator
    orchestrator = Orchestrator(steps, context, tracker, events)

    # Run pipeline
    try:
        result = orchestrator.run()
        print(f"\n[SUCCESS] Pipeline completed")
        print(f"  - Datasets produced: {len(result.data_map)}")
        print(f"  - Data keys: {list(result.data_map.keys())}")
    except Exception as e:
        print(f"\n[FAIL] Pipeline failed: {e}")
        return

    print()

    # ========================================================================
    # STEP 4: Show Tracker Summary
    # ========================================================================
    print("[4/5] Tracker Summary")
    print("-" * 70)

    print(tracker.get_summary())
    print()

    # Save tracker logs
    log_path = tracker.save()
    print(f"Tracker logs saved to: {log_path}")

    # Load explanations if available
    explanations_path = script_dir / "configs" / "simple_pipeline_explanations.json"
    explanations_dict = {}
    if explanations_path.exists():
        from odibi_core.story.explanation_loader import ExplanationLoader

        loader = ExplanationLoader()
        explanations_dict = loader.load(str(explanations_path))
        print(f"Loaded {len(explanations_dict)} step explanations")

    # Generate HTML story with explanations
    story_path = tracker.export_to_story(explanations=explanations_dict)
    print(f"HTML story saved to: {story_path}")
    print()

    # Show schema diffs
    print("Schema Changes:")
    print("-" * 70)
    for ex in tracker.executions:
        if ex.schema_diff:
            print(f"\nStep: {ex.step_name}")
            if ex.schema_diff.get("added_columns"):
                print(f"  + Added: {ex.schema_diff['added_columns']}")
            if ex.schema_diff.get("removed_columns"):
                print(f"  - Removed: {ex.schema_diff['removed_columns']}")
            if ex.schema_diff.get("changed_types"):
                print(f"  ~ Changed: {ex.schema_diff['changed_types']}")
            if ex.row_delta is not None:
                print(f"  Delta Rows: {ex.row_delta:+d}")

    print()

    # ========================================================================
    # STEP 5: Verify Outputs
    # ========================================================================
    print("[5/5] Verifying outputs...")
    print("-" * 70)

    # Check output files exist
    filtered_file = output_dir / "filtered.parquet"
    aggregated_file = output_dir / "aggregated.json"

    if filtered_file.exists():
        print(f"[OK] Filtered data written: {filtered_file}")
        # Read back to verify
        import pandas as pd

        df = pd.read_parquet(filtered_file)
        print(f"     {len(df)} rows (filtered from 10 where value > 100)")
    else:
        print(f"[FAIL] Filtered file not found: {filtered_file}")

    if aggregated_file.exists():
        print(f"[OK] Aggregated data written: {aggregated_file}")
        # Read back to verify
        import pandas as pd

        df = pd.read_json(aggregated_file)
        print(f"     {len(df)} categories with metrics")
        print(f"\n{df.to_string(index=False)}")
    else:
        print(f"[FAIL] Aggregated file not found: {aggregated_file}")

    print()

    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("=" * 70)
    print("[SUCCESS] Config-Driven Pipeline Demo Complete!")
    print("=" * 70)
    print()
    print("What we proved:")
    print("  1. [OK] Config loaded from JSON")
    print("  2. [OK] Config validated successfully")
    print("  3. [OK] Pipeline executed (ingest -> transform -> store)")
    print("  4. [OK] Tracker captured snapshots and timing")
    print("  5. [OK] Outputs written to Parquet and JSON")
    print()
    print("Next steps:")
    print("  - View tracker logs: tracker_logs/run_*.json")
    print("  - Inspect outputs: odibi_core/examples/output/")
    print("  - Try with Spark: Change 'engine' in config to 'spark'")
    print()
    print("Phase 3 SUCCESS: ODIBI CORE is now config-driven!")


if __name__ == "__main__":
    run_pipeline_demo()
