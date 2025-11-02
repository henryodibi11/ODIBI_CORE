# LearnODIBI Backend

API module providing method-based endpoints for the LearnODIBI UI with caching, error handling, and standardized response format.

## Overview

The `learnodibi_backend` module provides a clean API interface for UI integration without HTTP overhead. All methods return standardized responses with comprehensive error handling and performance optimization through caching.

## Installation

```python
from odibi_core.learnodibi_backend import LearnODIBIBackend

backend = LearnODIBIBackend(cache_ttl_seconds=300)
```

## Response Format

All methods return a standardized response:

```python
{
    "success": True/False,          # Operation success status
    "data": {...},                  # Response data
    "error": None or str,           # Error message if failed
    "execution_time_ms": 123.45,    # Execution time in milliseconds
    "metadata": {...}               # Additional metadata
}
```

## API Methods

### 1. run_transformation

Execute a transformation pipeline from configuration.

```python
config = {
    "steps": [
        {"type": "load", "params": {"path": "data.csv"}},
        {"type": "transform", "function": "clean_data"}
    ],
    "secrets": {"api_key": "xxx"},
    "max_workers": 4
}

result = backend.run_transformation(config, engine="pandas")

# Response:
{
    "success": True,
    "data": {
        "pipeline_id": "uuid-string",
        "pipeline_name": "pipeline_name",
        "success_count": 2,
        "failed_count": 0,
        "outputs": {
            "output_key": {
                "rows": 100,
                "columns": ["col1", "col2"],
                "preview": [{...}, {...}]
            }
        },
        "summary": "Pipeline execution summary"
    },
    "execution_time_ms": 234.56,
    "metadata": {"engine": "pandas", "steps_count": 2}
}
```

### 2. get_available_functions

Get list of all available transformation functions.

```python
result = backend.get_available_functions()

# Response:
{
    "success": True,
    "data": {
        "functions": [
            {
                "name": "clean_data",
                "module": "data_ops",
                "full_path": "data_ops.clean_data",
                "docstring": "Clean dataset..."
            },
            ...
        ],
        "count": 50
    },
    "execution_time_ms": 12.34,
    "metadata": {"cached": False}
}
```

**Caching**: Static cache (no TTL)

### 3. preview_dataset

Preview dataset with specified number of rows.

```python
result = backend.preview_dataset("sample.csv", rows=10)

# Response:
{
    "success": True,
    "data": {
        "dataset_name": "sample.csv",
        "rows": 10,
        "columns": ["col1", "col2", "col3"],
        "dtypes": {"col1": "int64", "col2": "object"},
        "preview": [
            {"col1": 1, "col2": "value1"},
            {"col1": 2, "col2": "value2"}
        ]
    },
    "execution_time_ms": 45.67,
    "metadata": {"total_rows_requested": 10}
}
```

**Caching**: 5 minutes TTL

**Supported Formats**: CSV, Parquet, Excel (.xlsx, .xls)

### 4. execute_workflow

Execute complete workflow with multiple pipelines.

```python
workflow = {
    "name": "ETL Workflow",
    "pipelines": [
        {"steps": [...]},
        {"steps": [...]}
    ],
    "engine": "pandas",
    "stop_on_error": True
}

result = backend.execute_workflow(workflow)

# Response:
{
    "success": True,
    "data": {
        "workflow_id": "uuid-string",
        "workflow_name": "ETL Workflow",
        "pipeline_results": [
            {"pipeline_index": 0, "success": True, ...},
            {"pipeline_index": 1, "success": True, ...}
        ],
        "total_pipelines": 2,
        "successful_pipelines": 2
    },
    "execution_time_ms": 567.89,
    "metadata": {"engine": "pandas"}
}
```

### 5. validate_config

Validate pipeline configuration.

```python
config = {"steps": [...]}

result = backend.validate_config(config)

# Response:
{
    "success": True,
    "data": {
        "valid": True,
        "errors": [],
        "warnings": ["Configuration has no secrets defined"]
    },
    "execution_time_ms": 5.67,
    "metadata": {"steps_count": 3}
}
```

### 6. get_pipeline_status

Get status of executed pipeline.

```python
result = backend.get_pipeline_status("pipeline-uuid")

# Response:
{
    "success": True,
    "data": {
        "pipeline_id": "pipeline-uuid",
        "status": "success",
        "success_count": 5,
        "failed_count": 0,
        "total_duration_ms": 234.56,
        "timestamp": 1699123456.789,
        "engine": "pandas"
    },
    "execution_time_ms": 1.23
}
```

### 7. list_demo_datasets

List available demo datasets.

```python
result = backend.list_demo_datasets()

# Response:
{
    "success": True,
    "data": {
        "datasets": [
            {
                "name": "sample.csv",
                "path": "odibi_core/examples/data/sample.csv",
                "size_bytes": 1024,
                "format": "csv"
            }
        ],
        "count": 1
    },
    "execution_time_ms": 8.90,
    "metadata": {"cached": False}
}
```

**Caching**: 5 minutes TTL

### 8. get_demo_pipeline_configs

Get pre-configured demo pipeline configurations.

```python
result = backend.get_demo_pipeline_configs()

# Response:
{
    "success": True,
    "data": {
        "configs": [
            {
                "name": "energy_efficiency",
                "path": "odibi_core/examples/configs/energy_efficiency.json",
                "description": "Energy efficiency pipeline",
                "config": {...}
            }
        ],
        "count": 1
    },
    "execution_time_ms": 12.34,
    "metadata": {"cached": False}
}
```

**Caching**: Static cache (no TTL)

### 9. clear_cache

Clear all cached data.

```python
result = backend.clear_cache()

# Response:
{
    "success": True,
    "data": {"message": "Cache cleared successfully"},
    "execution_time_ms": 0
}
```

### 10. get_cache_stats

Get cache statistics.

```python
result = backend.get_cache_stats()

# Response:
{
    "success": True,
    "data": {
        "size": 5,
        "keys": ["preview_sample.csv_10", "available_functions", ...]
    },
    "execution_time_ms": 0
}
```

## Error Handling

All methods use the `@safe_execute` decorator for comprehensive error handling:

```python
# Error response format:
{
    "success": False,
    "data": None,
    "error": "User-friendly error message",
    "error_type": "ConfigurationError",
    "recovery_suggestion": "Check that all required fields are present.",
    "stack_trace": "Full stack trace for debugging"
}
```

### Error Types

- `ConfigurationError`: Invalid configuration
- `ExecutionError`: Pipeline execution failures
- `DatasetError`: Dataset access/loading errors
- `BackendError`: General backend errors

## Caching Strategy

The backend uses intelligent caching to optimize performance:

| Method | Cache Key | TTL | Notes |
|--------|-----------|-----|-------|
| `get_available_functions()` | `available_functions` | Static | Functions rarely change |
| `preview_dataset()` | `preview_{name}_{rows}` | 5 min | Dataset content may change |
| `list_demo_datasets()` | `demo_datasets` | 5 min | File list may change |
| `get_demo_pipeline_configs()` | `demo_configs` | Static | Configs rarely change |

### Cache Management

```python
# Clear all cache
backend.clear_cache()

# Get cache statistics
stats = backend.get_cache_stats()

# Cache auto-cleanup (run periodically)
removed = backend.cache.cleanup_expired()
```

## Integration Examples

### Basic Pipeline Execution

```python
from odibi_core.learnodibi_backend import LearnODIBIBackend

backend = LearnODIBIBackend()

config = {
    "steps": [
        {
            "type": "load",
            "params": {"path": "data.csv"}
        },
        {
            "type": "transform",
            "function": "data_ops.clean_missing"
        }
    ]
}

result = backend.run_transformation(config)

if result["success"]:
    print(f"Pipeline completed: {result['data']['summary']}")
    pipeline_id = result["data"]["pipeline_id"]
    
    # Check status later
    status = backend.get_pipeline_status(pipeline_id)
else:
    print(f"Error: {result['error']}")
    print(f"Suggestion: {result.get('recovery_suggestion')}")
```

### Dataset Explorer

```python
backend = LearnODIBIBackend()

# List available datasets
datasets_result = backend.list_demo_datasets()
for dataset in datasets_result["data"]["datasets"]:
    print(f"- {dataset['name']} ({dataset['format']})")
    
    # Preview each dataset
    preview = backend.preview_dataset(dataset["name"], rows=5)
    if preview["success"]:
        print(f"  Columns: {preview['data']['columns']}")
        print(f"  Rows: {preview['data']['rows']}")
```

### Function Browser

```python
backend = LearnODIBIBackend()

functions_result = backend.get_available_functions()

# Group by module
from collections import defaultdict
by_module = defaultdict(list)

for func in functions_result["data"]["functions"]:
    by_module[func["module"]].append(func["name"])

for module, funcs in by_module.items():
    print(f"\n{module}:")
    for func_name in funcs:
        print(f"  - {func_name}")
```

## Testing

Run the included test suite:

```bash
python -m pytest odibi_core/learnodibi_backend/test_backend.py
```

Or run standalone tests:

```bash
python odibi_core/learnodibi_backend/test_backend.py
```

## Architecture

```
learnodibi_backend/
├── __init__.py          # Module exports
├── api.py               # Main LearnODIBIBackend class
├── cache.py             # ResultCache for performance
├── error_handler.py     # Error handling utilities
├── test_backend.py      # Test suite
└── README.md           # This file
```

### Dependencies

- `odibi_core.sdk`: ODIBI and Pipeline classes
- `odibi_core.functions.registry`: Function registry
- `pandas`: DataFrame operations
- Standard library: `time`, `logging`, `uuid`, `pathlib`

## Performance Considerations

1. **Caching**: Functions and datasets are cached to reduce repeated computation
2. **Lazy Loading**: Datasets preview only requested rows
3. **Thread Safety**: Cache operations are thread-safe with locks
4. **Auto Cleanup**: Expired cache entries are automatically removed

## Security

- All exceptions are caught and sanitized before returning to UI
- Stack traces are logged but only user-friendly messages exposed
- No secrets or sensitive data in responses
- File access limited to configured data directories

## Future Enhancements

- [ ] Async/await support for concurrent operations
- [ ] WebSocket support for real-time pipeline status
- [ ] Enhanced pipeline visualization data
- [ ] Performance metrics and profiling
- [ ] Dataset schema validation
- [ ] Custom function registration API
- [ ] Pipeline templates library
