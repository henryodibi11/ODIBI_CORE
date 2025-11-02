"""
Phase 9 SDK Demo - Quick Start Examples

Demonstrates the new SDK and CLI capabilities introduced in Phase 9.
"""

import sys
import os

# Fix Windows console encoding
if sys.platform == "win32":
    os.system("chcp 65001 > nul")
    sys.stdout.reconfigure(encoding='utf-8')


def demo_quick_execution():
    """Demo 1: Quick execution with ODIBI.run()"""
    print("\n" + "=" * 60)
    print("Demo 1: Quick Execution")
    print("=" * 60)

    try:
        from odibi_core.sdk import ODIBI

        # NOTE: Replace with actual config path
        config_path = "examples/demo_pipeline.json"

        if not os.path.exists(config_path):
            print(f"⚠️  Config not found: {config_path}")
            print("   Create a simple config to test this demo")
            return

        # One-line execution
        result = ODIBI.run(config_path, engine="pandas")

        # Print summary
        print("\n" + result.summary())

    except Exception as e:
        print(f"❌ Error: {e}")


def demo_pipeline_class():
    """Demo 2: Advanced usage with Pipeline class"""
    print("\n" + "=" * 60)
    print("Demo 2: Pipeline Class with Method Chaining")
    print("=" * 60)

    try:
        from odibi_core.sdk import Pipeline

        config_path = "examples/demo_pipeline.json"

        if not os.path.exists(config_path):
            print(f"⚠️  Config not found: {config_path}")
            return

        # Create pipeline with fluent API
        pipeline = Pipeline.from_config(config_path)
        pipeline.set_engine("pandas")
        pipeline.set_parallelism(max_workers=4)

        # Add secrets (example)
        secrets = {
            "db_pass": "example_password",
            "api_key": "example_key"
        }
        pipeline.set_secrets(secrets)

        # Execute
        result = pipeline.execute()

        # Inspect results
        print(f"\n{'Status:':<20} {'✅ SUCCESS' if result.is_success() else '❌ FAILED'}")
        print(f"{'Success Count:':<20} {result.success_count}")
        print(f"{'Failed Count:':<20} {result.failed_count}")
        print(f"{'Duration:':<20} {result.total_duration_ms:.2f}ms")

    except Exception as e:
        print(f"❌ Error: {e}")


def demo_config_validation():
    """Demo 3: Configuration validation"""
    print("\n" + "=" * 60)
    print("Demo 3: Configuration Validation")
    print("=" * 60)

    try:
        from odibi_core.sdk.config_validator import ConfigValidator

        config_path = "examples/demo_pipeline.json"

        if not os.path.exists(config_path):
            print(f"⚠️  Config not found: {config_path}")
            return

        # Create validator
        validator = ConfigValidator()

        # Validate
        is_valid = validator.validate(config_path)

        # Print results
        if is_valid:
            print("\n✅ Configuration is valid")
        else:
            print("\n❌ Configuration has issues:")
            validator.print_issues()

        # Print summary
        print(f"\n{validator.get_summary()}")

    except Exception as e:
        print(f"❌ Error: {e}")


def demo_version_info():
    """Demo 4: Version and feature information"""
    print("\n" + "=" * 60)
    print("Demo 4: Version Information")
    print("=" * 60)

    try:
        from odibi_core.__version__ import __version__, __phase__, __supported_engines__
        from odibi_core.sdk import ODIBI
        import json
        from pathlib import Path

        # Display version info
        print(f"\n{'ODIBI CORE Version:':<25} {__version__}")
        print(f"{'Phase:':<25} {__phase__}")
        print(f"{'Supported Engines:':<25} {', '.join(__supported_engines__)}")

        # SDK version method
        print(f"{'SDK Version:':<25} {ODIBI.version()}")

        # Load manifest
        manifest_path = Path(__file__).parent.parent / "manifest.json"
        if manifest_path.exists():
            with open(manifest_path, "r") as f:
                manifest = json.load(f)

            print(f"\n{'Features:'}")
            for feature, enabled in manifest.get("features", {}).items():
                icon = "✅" if enabled else "❌"
                feature_name = feature.replace("_", " ").title()
                print(f"  {icon} {feature_name}")

    except Exception as e:
        print(f"❌ Error: {e}")


def demo_programmatic_steps():
    """Demo 5: Building pipeline programmatically"""
    print("\n" + "=" * 60)
    print("Demo 5: Programmatic Pipeline Creation")
    print("=" * 60)

    try:
        from odibi_core.sdk import Pipeline
        from odibi_core.core.node import Step

        # Build steps programmatically
        steps = [
            Step(
                layer="ingest",
                name="demo_read",
                type="config_op",
                engine="pandas",
                value="examples/sample_data.csv",
                outputs={"data": "raw_data"}
            ),
            Step(
                layer="transform",
                name="demo_filter",
                type="sql",
                engine="pandas",
                value="SELECT * FROM data WHERE id > 0",
                inputs={"data": "raw_data"},
                outputs={"data": "filtered_data"}
            )
        ]

        print("\n✅ Created 2 steps programmatically:")
        for step in steps:
            print(f"  - {step.layer}/{step.name} ({step.type})")

        # Create pipeline
        pipeline = Pipeline(steps, name="programmatic_demo")
        pipeline.set_engine("pandas")

        print(f"\n✅ Pipeline '{pipeline.name}' ready to execute")
        print("   (Execute with: result = pipeline.execute())")

    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Run all demos"""
    print("\n" + "=" * 70)
    print(" " * 15 + "ODIBI CORE Phase 9 SDK Demos")
    print("=" * 70)

    demos = [
        demo_version_info,
        demo_config_validation,
        # demo_quick_execution,  # Uncomment when demo_pipeline.json exists
        # demo_pipeline_class,   # Uncomment when demo_pipeline.json exists
        demo_programmatic_steps,
    ]

    for demo in demos:
        try:
            demo()
        except Exception as e:
            print(f"\n❌ Demo failed: {e}")

    print("\n" + "=" * 70)
    print("Demo complete! See DEVELOPER_WALKTHROUGH_PHASE_9.md for more examples.")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
