"""
LearnODIBI Backend - API for UI Integration.

Provides method-based endpoints for pipeline execution, dataset management,
and configuration validation with caching and error handling.

Quick Start:
    >>> from odibi_core.learnodibi_backend import LearnODIBIBackend
    >>>
    >>> backend = LearnODIBIBackend()
    >>>
    >>> # Run transformation
    >>> config = {"steps": [{"type": "load", "params": {"path": "data.csv"}}]}
    >>> result = backend.run_transformation(config, engine="pandas")
    >>>
    >>> # Preview dataset
    >>> preview = backend.preview_dataset("sample.csv", rows=10)
    >>>
    >>> # Get available functions
    >>> functions = backend.get_available_functions()

API Response Format:
    All methods return a standardized response:
    {
        "success": True/False,
        "data": {...},
        "error": None or error message,
        "execution_time_ms": 123.45,
        "metadata": {...}
    }

Available Methods:
    - run_transformation(config, engine="pandas")
    - get_available_functions()
    - preview_dataset(dataset_name, rows=10)
    - execute_workflow(workflow_config)
    - validate_config(config)
    - get_pipeline_status(pipeline_id)
    - list_demo_datasets()
    - get_demo_pipeline_configs()
    - clear_cache()
    - get_cache_stats()
"""

from odibi_core.learnodibi_backend.api import LearnODIBIBackend
from odibi_core.learnodibi_backend.cache import ResultCache
from odibi_core.learnodibi_backend.error_handler import (
    BackendError,
    ConfigurationError,
    ExecutionError,
    DatasetError,
    safe_execute,
    get_user_friendly_message,
    get_recovery_suggestion,
)

__all__ = [
    "LearnODIBIBackend",
    "ResultCache",
    "BackendError",
    "ConfigurationError",
    "ExecutionError",
    "DatasetError",
    "safe_execute",
    "get_user_friendly_message",
    "get_recovery_suggestion",
]
