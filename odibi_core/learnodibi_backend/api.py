"""
Main API class for LearnODIBI backend.

Provides method-based endpoints for UI integration with caching,
error handling, and standardized response format.
"""

import time
import logging
import uuid
from typing import Any, Dict, List, Optional
from pathlib import Path
import pandas as pd
import importlib.util

from odibi_core.sdk import ODIBI, Pipeline
from odibi_core.functions.registry import FUNCTION_REGISTRY
from odibi_core.learnodibi_backend.cache import ResultCache
from odibi_core.learnodibi_backend.error_handler import (
    safe_execute,
    ConfigurationError,
    ExecutionError,
    DatasetError,
    ErrorContext,
)

logger = logging.getLogger(__name__)


class LearnODIBIBackend:
    """
    Backend API for LearnODIBI UI.

    Provides method-based endpoints for pipeline execution, dataset management,
    and configuration validation with caching and error handling.

    Attributes:
        cache: ResultCache instance for performance optimization
        session_pipelines: Dictionary tracking active pipeline sessions

    Example:
        >>> backend = LearnODIBIBackend()
        >>> result = backend.run_transformation(config, engine="pandas")
        >>> datasets = backend.list_demo_datasets()
    """

    def __init__(self, cache_ttl_seconds: int = 300):
        """
        Initialize backend API.

        Args:
            cache_ttl_seconds: Default cache TTL in seconds (default: 300)
        """
        self.cache = ResultCache(default_ttl_seconds=cache_ttl_seconds)
        self.session_pipelines: Dict[str, Dict[str, Any]] = {}
        logger.info("LearnODIBIBackend initialized")

    @safe_execute
    def run_transformation(self, config: Dict[str, Any], engine: str = "pandas") -> Dict[str, Any]:
        """
        Execute transformation pipeline from configuration.

        Args:
            config: Pipeline configuration dictionary
            engine: Execution engine ("pandas" or "spark")

        Returns:
            Standardized response with execution results

        Example:
            >>> config = {
            ...     "steps": [{"type": "load", "params": {"path": "data.csv"}}]
            ... }
            >>> result = backend.run_transformation(config, engine="pandas")
        """
        start_time = time.time()

        with ErrorContext("Pipeline execution", ExecutionError):
            if not config:
                raise ConfigurationError("Configuration cannot be empty")

            if "steps" not in config:
                raise ConfigurationError("Configuration must include 'steps' key")

            pipeline_id = str(uuid.uuid4())
            logger.info(f"Running transformation pipeline {pipeline_id} with {engine} engine")

            try:
                pipeline = Pipeline(steps=config.get("steps", []))
                pipeline.set_engine(engine)

                if "secrets" in config:
                    pipeline.set_secrets(config["secrets"])

                if "max_workers" in config:
                    pipeline.set_parallelism(config["max_workers"])

                result = pipeline.execute()

                execution_time_ms = (time.time() - start_time) * 1000

                self.session_pipelines[pipeline_id] = {
                    "config": config,
                    "result": result,
                    "timestamp": time.time(),
                    "engine": engine,
                }

                data_outputs = {}
                if hasattr(result, "data_map") and result.data_map:
                    for key, value in result.data_map.items():
                        if isinstance(value, pd.DataFrame):
                            data_outputs[key] = {
                                "rows": len(value),
                                "columns": list(value.columns),
                                "preview": value.head(5).to_dict(orient="records"),
                            }
                        else:
                            data_outputs[key] = str(value)

                return {
                    "success": result.is_success(),
                    "data": {
                        "pipeline_id": pipeline_id,
                        "pipeline_name": result.pipeline_name,
                        "success_count": result.success_count,
                        "failed_count": result.failed_count,
                        "outputs": data_outputs,
                        "summary": result.summary(),
                    },
                    "error": None,
                    "execution_time_ms": execution_time_ms,
                    "metadata": {"engine": engine, "steps_count": len(config.get("steps", []))},
                }

            except Exception as e:
                raise ExecutionError(f"Pipeline execution failed: {str(e)}") from e

    @safe_execute
    def get_available_functions(self) -> Dict[str, Any]:
        """
        Get list of all available transformation functions.

        Returns:
            Standardized response with function metadata

        Example:
            >>> result = backend.get_available_functions()
            >>> for func in result["data"]["functions"]:
            ...     print(func["name"])
        """
        start_time = time.time()

        cache_key = "available_functions"
        cached = self.cache.get(cache_key)
        if cached is not None:
            logger.debug("Returning cached function list")
            return cached

        with ErrorContext("Loading function registry"):
            functions = []

            for module_name in [
                "data_ops",
                "math_utils",
                "string_utils",
                "datetime_utils",
                "validation_utils",
                "conversion_utils",
                "unit_conversion",
                "thermo_utils",
                "psychro_utils",
                "reliability_utils",
            ]:
                try:
                    module = __import__(
                        f"odibi_core.functions.{module_name}",
                        fromlist=[module_name],
                    )

                    module_functions = [
                        name
                        for name in dir(module)
                        if callable(getattr(module, name)) and not name.startswith("_")
                    ]

                    for func_name in module_functions:
                        func = getattr(module, func_name)
                        functions.append(
                            {
                                "name": func_name,
                                "module": module_name,
                                "full_path": f"{module_name}.{func_name}",
                                "docstring": func.__doc__ or "No documentation available",
                            }
                        )

                except ImportError as e:
                    logger.warning(f"Could not import {module_name}: {e}")
                    continue

            execution_time_ms = (time.time() - start_time) * 1000

            response = {
                "success": True,
                "data": {"functions": functions, "count": len(functions)},
                "error": None,
                "execution_time_ms": execution_time_ms,
                "metadata": {"cached": False},
            }

            self.cache.set(cache_key, response, ttl=None)

            return response

    @safe_execute
    def preview_dataset(self, dataset_name: str, rows: int = 10) -> Dict[str, Any]:
        """
        Preview dataset with specified number of rows.

        Args:
            dataset_name: Name or path of dataset
            rows: Number of rows to preview (default: 10)

        Returns:
            Standardized response with dataset preview

        Example:
            >>> result = backend.preview_dataset("sample.csv", rows=5)
            >>> print(result["data"]["preview"])
        """
        start_time = time.time()

        cache_key = f"preview_{dataset_name}_{rows}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            logger.debug(f"Returning cached preview for {dataset_name}")
            return cached

        with ErrorContext("Loading dataset", DatasetError):
            dataset_path = Path(dataset_name)

            if not dataset_path.exists():
                examples_path = Path("odibi_core/examples/data") / dataset_name
                if examples_path.exists():
                    dataset_path = examples_path
                else:
                    raise DatasetError(f"Dataset not found: {dataset_name}")

            if dataset_path.suffix == ".csv":
                df = pd.read_csv(dataset_path, nrows=rows)
            elif dataset_path.suffix in [".parquet", ".pq"]:
                df = pd.read_parquet(dataset_path)
                df = df.head(rows)
            elif dataset_path.suffix in [".xlsx", ".xls"]:
                df = pd.read_excel(dataset_path, nrows=rows)
            else:
                raise DatasetError(f"Unsupported file format: {dataset_path.suffix}")

            execution_time_ms = (time.time() - start_time) * 1000

            response = {
                "success": True,
                "data": {
                    "dataset_name": dataset_name,
                    "rows": len(df),
                    "columns": list(df.columns),
                    "dtypes": df.dtypes.astype(str).to_dict(),
                    "preview": df.to_dict(orient="records"),
                },
                "error": None,
                "execution_time_ms": execution_time_ms,
                "metadata": {"total_rows_requested": rows},
            }

            self.cache.set(cache_key, response, ttl=300)

            return response

    @safe_execute
    def execute_workflow(self, workflow_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute complete workflow with multiple pipelines.

        Args:
            workflow_config: Workflow configuration with multiple steps

        Returns:
            Standardized response with workflow results

        Example:
            >>> workflow = {
            ...     "name": "ETL Workflow",
            ...     "pipelines": [{"steps": [...]}, {"steps": [...]}]
            ... }
            >>> result = backend.execute_workflow(workflow)
        """
        start_time = time.time()

        with ErrorContext("Workflow execution", ExecutionError):
            if "pipelines" not in workflow_config:
                raise ConfigurationError("Workflow must include 'pipelines' key")

            workflow_id = str(uuid.uuid4())
            workflow_name = workflow_config.get("name", f"workflow_{workflow_id[:8]}")
            engine = workflow_config.get("engine", "pandas")

            logger.info(f"Executing workflow {workflow_name} ({workflow_id})")

            pipeline_results = []
            all_success = True

            for idx, pipeline_config in enumerate(workflow_config["pipelines"]):
                logger.info(f"Executing pipeline {idx + 1}/{len(workflow_config['pipelines'])}")

                result = self.run_transformation(pipeline_config, engine=engine)

                pipeline_results.append(
                    {
                        "pipeline_index": idx,
                        "success": result.get("success", False),
                        "execution_time_ms": result.get("execution_time_ms", 0),
                        "data": result.get("data"),
                    }
                )

                if not result.get("success", False):
                    all_success = False
                    if workflow_config.get("stop_on_error", True):
                        logger.warning(f"Stopping workflow due to pipeline {idx} failure")
                        break

            execution_time_ms = (time.time() - start_time) * 1000

            return {
                "success": all_success,
                "data": {
                    "workflow_id": workflow_id,
                    "workflow_name": workflow_name,
                    "pipeline_results": pipeline_results,
                    "total_pipelines": len(workflow_config["pipelines"]),
                    "successful_pipelines": sum(1 for r in pipeline_results if r["success"]),
                },
                "error": None if all_success else "One or more pipelines failed",
                "execution_time_ms": execution_time_ms,
                "metadata": {"engine": engine},
            }

    @safe_execute
    def validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate pipeline configuration.

        Args:
            config: Configuration to validate

        Returns:
            Standardized response with validation results

        Example:
            >>> result = backend.validate_config(config)
            >>> if result["data"]["valid"]:
            ...     print("Configuration is valid")
        """
        start_time = time.time()

        with ErrorContext("Configuration validation", ConfigurationError):
            errors = []
            warnings = []

            if not config:
                errors.append("Configuration cannot be empty")
                return {
                    "success": False,
                    "data": {"valid": False, "errors": errors, "warnings": warnings},
                    "error": "Invalid configuration",
                    "execution_time_ms": (time.time() - start_time) * 1000,
                    "metadata": {},
                }

            if "steps" not in config:
                errors.append("Configuration must include 'steps' key")

            if "steps" in config:
                if not isinstance(config["steps"], list):
                    errors.append("'steps' must be a list")
                elif len(config["steps"]) == 0:
                    warnings.append("Configuration has no steps")

            execution_time_ms = (time.time() - start_time) * 1000

            is_valid = len(errors) == 0

            return {
                "success": True,
                "data": {
                    "valid": is_valid,
                    "errors": errors,
                    "warnings": warnings,
                },
                "error": None,
                "execution_time_ms": execution_time_ms,
                "metadata": {"steps_count": len(config.get("steps", []))},
            }

    @safe_execute
    def get_pipeline_status(self, pipeline_id: str) -> Dict[str, Any]:
        """
        Get status of executed pipeline.

        Args:
            pipeline_id: Pipeline ID from run_transformation

        Returns:
            Standardized response with pipeline status

        Example:
            >>> result = backend.get_pipeline_status("abc-123-def")
            >>> print(result["data"]["status"])
        """
        start_time = time.time()

        with ErrorContext("Getting pipeline status"):
            if pipeline_id not in self.session_pipelines:
                raise ValueError(f"Pipeline not found: {pipeline_id}")

            pipeline_info = self.session_pipelines[pipeline_id]
            result = pipeline_info["result"]

            execution_time_ms = (time.time() - start_time) * 1000

            return {
                "success": True,
                "data": {
                    "pipeline_id": pipeline_id,
                    "status": "success" if result.is_success() else "failed",
                    "success_count": result.success_count,
                    "failed_count": result.failed_count,
                    "total_duration_ms": result.total_duration_ms,
                    "timestamp": pipeline_info["timestamp"],
                    "engine": pipeline_info["engine"],
                },
                "error": None,
                "execution_time_ms": execution_time_ms,
                "metadata": {},
            }

    @safe_execute
    def list_demo_datasets(self) -> Dict[str, Any]:
        """
        List available demo datasets.

        Returns:
            Standardized response with dataset list

        Example:
            >>> result = backend.list_demo_datasets()
            >>> for dataset in result["data"]["datasets"]:
            ...     print(dataset["name"])
        """
        start_time = time.time()

        cache_key = "demo_datasets"
        cached = self.cache.get(cache_key)
        if cached is not None:
            logger.debug("Returning cached dataset list")
            return cached

        with ErrorContext("Listing demo datasets"):
            datasets = []

            examples_data_path = Path("odibi_core/examples/data")
            if examples_data_path.exists():
                for file_path in examples_data_path.glob("*"):
                    if file_path.suffix in [".csv", ".parquet", ".xlsx", ".pq"]:
                        datasets.append(
                            {
                                "name": file_path.name,
                                "path": str(file_path),
                                "size_bytes": file_path.stat().st_size,
                                "format": file_path.suffix.lstrip("."),
                            }
                        )

            execution_time_ms = (time.time() - start_time) * 1000

            response = {
                "success": True,
                "data": {"datasets": datasets, "count": len(datasets)},
                "error": None,
                "execution_time_ms": execution_time_ms,
                "metadata": {"cached": False},
            }

            self.cache.set(cache_key, response, ttl=300)

            return response

    @safe_execute
    def get_demo_pipeline_configs(self) -> Dict[str, Any]:
        """
        Get pre-configured demo pipeline configurations.

        Returns:
            Standardized response with demo configurations

        Example:
            >>> result = backend.get_demo_pipeline_configs()
            >>> for config in result["data"]["configs"]:
            ...     print(config["name"])
        """
        start_time = time.time()

        cache_key = "demo_configs"
        cached = self.cache.get(cache_key)
        if cached is not None:
            logger.debug("Returning cached demo configs")
            return cached

        with ErrorContext("Loading demo configurations"):
            configs = []

            examples_config_path = Path("odibi_core/examples/configs")
            if examples_config_path.exists():
                for config_file in examples_config_path.glob("*.json"):
                    try:
                        import json

                        with open(config_file, "r") as f:
                            config_data = json.load(f)

                        configs.append(
                            {
                                "name": config_file.stem,
                                "path": str(config_file),
                                "description": config_data.get("description", "No description"),
                                "config": config_data,
                            }
                        )
                    except Exception as e:
                        logger.warning(f"Could not load config {config_file}: {e}")

            execution_time_ms = (time.time() - start_time) * 1000

            response = {
                "success": True,
                "data": {"configs": configs, "count": len(configs)},
                "error": None,
                "execution_time_ms": execution_time_ms,
                "metadata": {"cached": False},
            }

            self.cache.set(cache_key, response, ttl=None)

            return response

    def clear_cache(self) -> Dict[str, Any]:
        """
        Clear all cached data.

        Returns:
            Standardized response

        Example:
            >>> result = backend.clear_cache()
        """
        self.cache.clear()
        return {
            "success": True,
            "data": {"message": "Cache cleared successfully"},
            "error": None,
            "execution_time_ms": 0,
            "metadata": {},
        }

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Standardized response with cache stats

        Example:
            >>> result = backend.get_cache_stats()
            >>> print(result["data"]["size"])
        """
        return {
            "success": True,
            "data": {
                "size": self.cache.size(),
                "keys": self.cache.keys(),
            },
            "error": None,
            "execution_time_ms": 0,
            "metadata": {},
        }
