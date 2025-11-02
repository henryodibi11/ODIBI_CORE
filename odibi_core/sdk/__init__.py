"""
ODIBI CORE SDK - Developer-friendly API.

Simplifies common tasks with a clean, intuitive interface while keeping
full access to internal modules for advanced users.

Quick Start:
    >>> from odibi_core.sdk import ODIBI
    >>>
    >>> # Execute a pipeline
    >>> ODIBI.run(config_path="pipeline.json", engine="pandas")
    >>>
    >>> # Validate configuration
    >>> ODIBI.validate(config_path="pipeline.json")

Advanced Usage:
    >>> from odibi_core.sdk import Pipeline
    >>>
    >>> # Create custom pipeline
    >>> pipeline = Pipeline.from_config("pipeline.json")
    >>> pipeline.set_engine("pandas")
    >>> pipeline.set_secrets({"db_pass": "secret"})
    >>> result = pipeline.execute()
    >>> print(result.summary())
"""

from typing import Any, Dict, List, Optional
import logging
from pathlib import Path

from odibi_core.core.config_loader import ConfigLoader
from odibi_core.core.dag_builder import DAGBuilder
from odibi_core.core.dag_executor import DAGExecutor
from odibi_core.core.tracker import Tracker
from odibi_core.core.events import EventEmitter
from odibi_core.observability.structured_logger import StructuredLogger
from odibi_core.metrics.metrics_manager import MetricsManager
from odibi_core.__version__ import __version__

logger = logging.getLogger(__name__)


class Pipeline:
    """
    High-level pipeline orchestration API.

    Example:
        >>> pipeline = Pipeline.from_config("pipeline.json")
        >>> pipeline.set_engine("pandas")
        >>> result = pipeline.execute()
        >>> print(result.summary())
    """

    def __init__(self, steps: List[Any], name: str = "pipeline"):
        """
        Initialize pipeline from steps.

        Args:
            steps: List of Step objects
            name: Pipeline name for logging
        """
        self.steps = steps
        self.name = name
        self.engine_name = "pandas"
        self.secrets: Dict[str, str] = {}
        self.max_workers = 4
        self.max_retries = 2
        self.enable_cache = True
        self._context = None
        self._tracker = None
        self._events = None
        self._logger = None
        self._metrics = None

    @classmethod
    def from_config(cls, config_path: str, **kwargs: Any) -> "Pipeline":
        """
        Load pipeline from configuration file.

        Args:
            config_path: Path to JSON, SQLite, or CSV config
            **kwargs: Additional ConfigLoader parameters

        Returns:
            Pipeline instance

        Example:
            >>> pipeline = Pipeline.from_config("pipeline.json")
        """
        loader = ConfigLoader()
        steps = loader.load(config_path, **kwargs)
        name = Path(config_path).stem
        return cls(steps, name=name)

    def set_engine(self, engine: str, **engine_config: Any) -> "Pipeline":
        """
        Set execution engine.

        Args:
            engine: "pandas" or "spark"
            **engine_config: Engine-specific configuration

        Returns:
            self (for method chaining)
        """
        self.engine_name = engine
        self.engine_config = engine_config
        return self

    def set_secrets(self, secrets: Dict[str, str]) -> "Pipeline":
        """
        Set secrets for pipeline execution.

        Args:
            secrets: Dictionary of secret key-value pairs

        Returns:
            self (for method chaining)
        """
        self.secrets = secrets
        return self

    def set_parallelism(self, max_workers: int) -> "Pipeline":
        """
        Set parallel worker count.

        Args:
            max_workers: Maximum concurrent workers

        Returns:
            self (for method chaining)
        """
        self.max_workers = max_workers
        return self

    def execute(self, **kwargs: Any) -> "PipelineResult":
        """
        Execute the pipeline.

        Args:
            **kwargs: Additional execution parameters

        Returns:
            PipelineResult with execution summary

        Example:
            >>> result = pipeline.execute()
            >>> print(result.success_count)
        """
        from odibi_core.core import create_engine_context

        # Initialize components
        self._context = create_engine_context(
            self.engine_name, secrets=self.secrets, **getattr(self, "engine_config", {})
        )
        self._tracker = Tracker()
        self._events = EventEmitter()
        self._logger = StructuredLogger(self.name, log_dir="logs")
        self._metrics = MetricsManager()

        self._logger.log_pipeline_start(self.name, engine=self.engine_name)

        # Build DAG
        builder = DAGBuilder()
        dag = builder.build(self.steps)

        # Execute
        executor = DAGExecutor(
            dag=dag,
            context=self._context,
            tracker=self._tracker,
            events=self._events,
            max_workers=self.max_workers,
            max_retries=self.max_retries,
            use_cache=self.enable_cache,
        )

        data_map, results = executor.execute()

        # Calculate summary
        success = sum(1 for r in results if r.state == "SUCCESS")
        failed = sum(1 for r in results if r.state == "FAILED")
        duration_ms = sum(r.duration_ms for r in results)

        self._logger.log_pipeline_complete(
            self.name,
            success_count=success,
            failed_count=failed,
            duration_ms=duration_ms,
        )

        return PipelineResult(
            pipeline_name=self.name,
            success_count=success,
            failed_count=failed,
            total_duration_ms=duration_ms,
            results=results,
            data_map=data_map,
            tracker=self._tracker,
            logger=self._logger,
        )


class PipelineResult:
    """
    Pipeline execution result.

    Attributes:
        pipeline_name: Name of the pipeline
        success_count: Number of successful nodes
        failed_count: Number of failed nodes
        total_duration_ms: Total execution time
        results: List of NodeExecutionResult objects
        data_map: Output data dictionary
        tracker: Tracker instance
        logger: StructuredLogger instance
    """

    def __init__(
        self,
        pipeline_name: str,
        success_count: int,
        failed_count: int,
        total_duration_ms: float,
        results: List[Any],
        data_map: Dict[str, Any],
        tracker: Tracker,
        logger: StructuredLogger,
    ):
        self.pipeline_name = pipeline_name
        self.success_count = success_count
        self.failed_count = failed_count
        self.total_duration_ms = total_duration_ms
        self.results = results
        self.data_map = data_map
        self.tracker = tracker
        self.logger = logger

    def summary(self) -> str:
        """
        Generate human-readable summary.

        Returns:
            Summary string
        """
        return f"""
Pipeline: {self.pipeline_name}
Status: {'✅ SUCCESS' if self.failed_count == 0 else '❌ FAILED'}
Nodes: {self.success_count} success, {self.failed_count} failed
Duration: {self.total_duration_ms:.2f}ms
        """.strip()

    def is_success(self) -> bool:
        """Check if pipeline succeeded."""
        return self.failed_count == 0


class ODIBI:
    """
    Main SDK entry point for quick operations.

    Example:
        >>> from odibi_core.sdk import ODIBI
        >>> ODIBI.run("pipeline.json", engine="pandas")
    """

    @staticmethod
    def run(
        config_path: str,
        engine: str = "pandas",
        secrets: Optional[Dict[str, str]] = None,
        max_workers: int = 4,
        **kwargs: Any,
    ) -> PipelineResult:
        """
        Execute a pipeline from config file.

        Args:
            config_path: Path to configuration file
            engine: "pandas" or "spark"
            secrets: Secret key-value pairs
            max_workers: Parallel worker count
            **kwargs: Additional parameters

        Returns:
            PipelineResult

        Example:
            >>> result = ODIBI.run("pipeline.json", engine="pandas")
            >>> print(result.summary())
        """
        pipeline = Pipeline.from_config(config_path, **kwargs)
        pipeline.set_engine(engine)
        if secrets:
            pipeline.set_secrets(secrets)
        pipeline.set_parallelism(max_workers)
        return pipeline.execute()

    @staticmethod
    def validate(config_path: str) -> bool:
        """
        Validate configuration file.

        Args:
            config_path: Path to configuration file

        Returns:
            True if valid, raises exception otherwise

        Example:
            >>> ODIBI.validate("pipeline.json")
        """
        from odibi_core.sdk.config_validator import ConfigValidator

        validator = ConfigValidator()
        return validator.validate(config_path)

    @staticmethod
    def version() -> str:
        """Get ODIBI CORE version."""
        return __version__


__all__ = ["ODIBI", "Pipeline", "PipelineResult"]
