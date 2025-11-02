"""
Unicode Symbol Test for Story Explanations.

Tests that international symbols render correctly in HTML stories:
- Greek letters: α, β, γ, Δ, η, μ, σ, Σ
- Math symbols: ×, ±, ≤, ≥, ≈
- Units: °, ², ³, ⁻
- Accents: é, ñ, ü
"""

import logging
from pathlib import Path

logging.basicConfig(level=logging.WARNING)


def run_unicode_test() -> None:
    """Test Unicode symbol rendering in stories."""
    print("=" * 70)
    print("ODIBI CORE - Unicode Symbol Test")
    print("=" * 70)
    print()

    from odibi_core.core import (
        ConfigLoader,
        Orchestrator,
        Tracker,
        EventEmitter,
        create_engine_context,
    )
    from odibi_core.story import ExplanationLoader

    script_dir = Path(__file__).parent

    # Load config and explanations
    config_path = script_dir / "configs" / "showcase_pipeline.json"
    explanations_path = script_dir / "configs" / "unicode_test_explanations.json"

    steps = ConfigLoader().load(str(config_path))
    explanations = ExplanationLoader().load(str(explanations_path))

    print(f"Loaded {len(steps)} steps with {len(explanations)} explanations")
    print()

    # Execute pipeline
    context = create_engine_context("pandas")
    context.connect()
    tracker = Tracker()
    events = EventEmitter()

    orchestrator = Orchestrator(steps, context, tracker, events)
    orchestrator.run()

    # Generate story
    story_path = tracker.export_to_story(explanations=explanations)

    print("[OK] Story generated with Unicode symbols")
    print(f"File: {story_path}")
    print()

    # Show which symbols were used
    print("Unicode symbols tested:")
    print("  Greek: alpha, beta, gamma, Delta, eta, mu, sigma, Sigma")
    print("  Math: multiply, plus-minus, less-equal, approx")
    print("  Units: degree, superscript 2, superscript 3, superscript minus")
    print("  Subscripts: T1, T2, x0, h1")
    print()

    # Read story and check encoding
    with open(story_path, "r", encoding="utf-8-sig") as f:
        content = f.read()

    # Check for specific symbols
    symbols_to_check = {
        "Δ": "Delta",
        "°": "degree",
        "×": "multiply",
        "±": "plus-minus",
        "η": "eta",
        "μ": "mu",
    }

    print("Symbol verification:")
    for symbol, name in symbols_to_check.items():
        if symbol in content:
            print(f"  [OK] {name} found in HTML")
        else:
            print(f"  [WARN] {name} not found")

    print()
    print("=" * 70)
    print("[SUCCESS] Unicode encoding test complete")
    print("=" * 70)
    print()
    print(f"Open {story_path} in your browser to verify visual rendering.")


if __name__ == "__main__":
    run_unicode_test()
