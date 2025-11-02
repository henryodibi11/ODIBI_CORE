"""
Example usage of LearnODIBI Backend API.

Demonstrates common use cases and patterns for UI integration.
"""

from odibi_core.learnodibi_backend import LearnODIBIBackend
import json


def example_basic_transformation():
    """Example: Run a basic transformation pipeline."""
    print("\n=== Example 1: Basic Transformation ===")

    backend = LearnODIBIBackend()

    config = {
        "steps": [
            {"type": "load", "params": {"path": "sample.csv"}},
            {"type": "transform", "function": "clean_data"},
            {"type": "save", "params": {"path": "output.csv"}},
        ]
    }

    result = backend.run_transformation(config, engine="pandas")

    if result["success"]:
        print(f"✓ Pipeline completed successfully")
        print(f"  Pipeline ID: {result['data']['pipeline_id']}")
        print(f"  Execution time: {result['execution_time_ms']:.2f}ms")
        print(f"  Summary: {result['data']['summary']}")
    else:
        print(f"✗ Pipeline failed: {result['error']}")
        print(f"  Suggestion: {result.get('recovery_suggestion')}")


def example_dataset_preview():
    """Example: Preview a dataset."""
    print("\n=== Example 2: Dataset Preview ===")

    backend = LearnODIBIBackend()

    result = backend.preview_dataset("sample.csv", rows=5)

    if result["success"]:
        print(f"✓ Dataset preview loaded")
        print(f"  Dataset: {result['data']['dataset_name']}")
        print(f"  Rows: {result['data']['rows']}")
        print(f"  Columns: {', '.join(result['data']['columns'])}")
        print(f"  Data types:")
        for col, dtype in result["data"]["dtypes"].items():
            print(f"    {col}: {dtype}")
        print(f"  Preview (first row): {result['data']['preview'][0]}")
    else:
        print(f"✗ Preview failed: {result['error']}")


def example_list_functions():
    """Example: List available functions."""
    print("\n=== Example 3: Available Functions ===")

    backend = LearnODIBIBackend()

    result = backend.get_available_functions()

    if result["success"]:
        print(f"✓ Found {result['data']['count']} functions")

        # Group by module
        by_module = {}
        for func in result["data"]["functions"]:
            module = func["module"]
            if module not in by_module:
                by_module[module] = []
            by_module[module].append(func["name"])

        for module, funcs in list(by_module.items())[:3]:
            print(f"\n  {module}:")
            for func_name in funcs[:5]:
                print(f"    - {func_name}")
            if len(funcs) > 5:
                print(f"    ... and {len(funcs) - 5} more")
    else:
        print(f"✗ Failed to load functions: {result['error']}")


def example_workflow_execution():
    """Example: Execute multi-pipeline workflow."""
    print("\n=== Example 4: Workflow Execution ===")

    backend = LearnODIBIBackend()

    workflow = {
        "name": "Data Processing Workflow",
        "engine": "pandas",
        "stop_on_error": True,
        "pipelines": [
            {
                "steps": [
                    {"type": "load", "params": {"path": "raw_data.csv"}},
                    {"type": "transform", "function": "clean_missing"},
                ]
            },
            {
                "steps": [
                    {"type": "transform", "function": "normalize_values"},
                    {"type": "save", "params": {"path": "processed_data.csv"}},
                ]
            },
        ],
    }

    result = backend.execute_workflow(workflow)

    if result["success"]:
        print(f"✓ Workflow completed successfully")
        print(f"  Workflow: {result['data']['workflow_name']}")
        print(
            f"  Success: {result['data']['successful_pipelines']}/{result['data']['total_pipelines']}"
        )
        print(f"  Total time: {result['execution_time_ms']:.2f}ms")
    else:
        print(f"✗ Workflow failed: {result['error']}")


def example_config_validation():
    """Example: Validate configuration."""
    print("\n=== Example 5: Configuration Validation ===")

    backend = LearnODIBIBackend()

    # Valid config
    valid_config = {
        "steps": [
            {"type": "load", "params": {"path": "data.csv"}},
            {"type": "transform", "function": "process"},
        ]
    }

    result = backend.validate_config(valid_config)
    print(f"Valid config: {result['data']['valid']}")
    print(f"  Errors: {result['data']['errors']}")
    print(f"  Warnings: {result['data']['warnings']}")

    # Invalid config
    invalid_config = {}

    result = backend.validate_config(invalid_config)
    print(f"\nInvalid config: {result['data']['valid']}")
    print(f"  Errors: {result['data']['errors']}")


def example_cache_management():
    """Example: Cache management."""
    print("\n=== Example 6: Cache Management ===")

    backend = LearnODIBIBackend()

    # Trigger some cached operations
    backend.get_available_functions()
    backend.list_demo_datasets()

    # Check cache stats
    stats = backend.get_cache_stats()
    print(f"Cache size: {stats['data']['size']} entries")
    print(f"Cache keys: {stats['data']['keys']}")

    # Clear cache
    result = backend.clear_cache()
    print(f"\n{result['data']['message']}")

    # Verify cleared
    stats = backend.get_cache_stats()
    print(f"Cache size after clear: {stats['data']['size']} entries")


def example_demo_resources():
    """Example: Access demo datasets and configs."""
    print("\n=== Example 7: Demo Resources ===")

    backend = LearnODIBIBackend()

    # List datasets
    datasets = backend.list_demo_datasets()
    if datasets["success"]:
        print(f"Demo datasets ({datasets['data']['count']}):")
        for ds in datasets["data"]["datasets"]:
            print(f"  - {ds['name']} ({ds['format']}, {ds['size_bytes']} bytes)")

    # List configs
    configs = backend.get_demo_pipeline_configs()
    if configs["success"]:
        print(f"\nDemo configs ({configs['data']['count']}):")
        for cfg in configs["data"]["configs"]:
            print(f"  - {cfg['name']}: {cfg['description']}")


def example_error_handling():
    """Example: Error handling patterns."""
    print("\n=== Example 8: Error Handling ===")

    backend = LearnODIBIBackend()

    # Try to preview non-existent dataset
    result = backend.preview_dataset("nonexistent.csv")

    if not result["success"]:
        print(f"Error occurred (expected):")
        print(f"  Error: {result['error']}")
        print(f"  Type: {result.get('error_type')}")
        print(f"  Suggestion: {result.get('recovery_suggestion')}")
    else:
        print("Unexpectedly succeeded")


def example_pipeline_tracking():
    """Example: Track pipeline execution."""
    print("\n=== Example 9: Pipeline Tracking ===")

    backend = LearnODIBIBackend()

    config = {"steps": [{"type": "load", "params": {"path": "sample.csv"}}]}

    # Run pipeline
    result = backend.run_transformation(config)

    if result["success"]:
        pipeline_id = result["data"]["pipeline_id"]
        print(f"Pipeline started: {pipeline_id}")

        # Check status
        status = backend.get_pipeline_status(pipeline_id)
        if status["success"]:
            print(f"  Status: {status['data']['status']}")
            print(f"  Duration: {status['data']['total_duration_ms']:.2f}ms")
            print(f"  Success count: {status['data']['success_count']}")
            print(f"  Failed count: {status['data']['failed_count']}")


def main():
    """Run all examples."""
    print("=" * 60)
    print("LearnODIBI Backend - Example Usage")
    print("=" * 60)

    examples = [
        example_basic_transformation,
        example_dataset_preview,
        example_list_functions,
        example_workflow_execution,
        example_config_validation,
        example_cache_management,
        example_demo_resources,
        example_error_handling,
        example_pipeline_tracking,
    ]

    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"\n✗ Example failed: {str(e)}")

    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
