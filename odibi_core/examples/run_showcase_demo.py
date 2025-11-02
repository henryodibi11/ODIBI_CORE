"""
Story Explanation Showcase Demo.

Demonstrates rich Markdown explanations in HTML stories with:
1. Plain text with bullets
2. Formula tables
3. Code snippets
4. Rich narrative text
5. Unicode symbols and technical notation
"""

import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")


def run_showcase_demo() -> None:
    """
    Run showcase demo with rich explanations.
    """
    print("=" * 70)
    print("ODIBI CORE v1.0 - Story Explanation Showcase")
    print("=" * 70)
    print()
    print("This demo showcases 5 types of step explanations:")
    print("  1. Plain text with bullet points")
    print("  2. Formula tables with calculations")
    print("  3. Code snippets (Python/SQL)")
    print("  4. Rich narrative with bold/italic")
    print("  5. Unicode symbols (degrees, multiply, delta)")
    print()

    from odibi_core.core import (
        ConfigLoader,
        ConfigValidator,
        Orchestrator,
        Tracker,
        EventEmitter,
        create_engine_context,
    )
    from odibi_core.story import ExplanationLoader

    # Paths
    script_dir = Path(__file__).parent
    config_path = script_dir / "configs" / "showcase_pipeline.json"
    explanations_path = script_dir / "configs" / "showcase_explanations.json"
    output_dir = script_dir / "output"
    output_dir.mkdir(exist_ok=True)

    # Load config
    print("[1/4] Loading configuration and explanations...")
    print("-" * 70)

    loader = ConfigLoader()
    steps = loader.load(str(config_path))
    print(f"[OK] Loaded {len(steps)} steps")

    # Load explanations
    exp_loader = ExplanationLoader()
    explanations = exp_loader.load(str(explanations_path))
    print(f"[OK] Loaded {len(explanations)} step explanations")
    print()

    # Validate
    print("[2/4] Validating configuration...")
    print("-" * 70)

    validator = ConfigValidator()
    validator.validate_config(steps)
    print("[OK] Config validation passed")
    print()

    # Execute
    print("[3/4] Executing pipeline...")
    print("-" * 70)

    context = create_engine_context("pandas")
    context.connect()

    tracker = Tracker(log_dir="tracker_logs")
    events = EventEmitter()

    # Add progress listener
    events.on(
        "step_complete",
        lambda step, duration_ms: print(f"  [OK] {step.name} ({duration_ms:.0f}ms)"),
    )

    orchestrator = Orchestrator(steps, context, tracker, events)
    result = orchestrator.run()

    print()
    print(
        f"[OK] Pipeline completed in {tracker.get_stats()['total_duration_ms']:.0f}ms"
    )
    print()

    # Generate story
    print("[4/4] Generating HTML story with explanations...")
    print("-" * 70)

    story_path = tracker.export_to_story(story_dir="stories", explanations=explanations)

    print(f"[OK] Story saved to: {story_path}")
    print()

    # Summary
    print("=" * 70)
    print("Showcase Demo Complete!")
    print("=" * 70)
    print()
    print("Generated files:")
    print(f"  • Tracker log:  {tracker.log_dir}/run_*.json")
    print(f"  • HTML story:   {story_path}")
    print(f"  • Gold output:  odibi_core/examples/output/gold_metrics.json")
    print()
    print("To view the showcase story:")
    print(f"  1. Open {story_path} in your browser")
    print("  2. Expand each 'Step Explanation' section")
    print("  3. Observe 5 different explanation styles:")
    print("     - Plain text (ingest_sensor_data)")
    print("     - Formulas (calculate_efficiency)")
    print("     - Code snippets (apply_python_function)")
    print("     - Rich narrative (aggregate_metrics)")
    print("     - Unicode symbols (publish_gold_metrics)")
    print()
    print("SUCCESS: Story Explanation System is working!")


if __name__ == "__main__":
    run_showcase_demo()
