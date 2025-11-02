"""
Pipeline orchestrator for DAG execution.

Builds dependency graph from config and executes Nodes in topological order.
Phase 5: Upgraded with parallel DAG execution, caching, and retries.
"""

from typing import Any, Dict, List, Optional, Set, Union
from odibi_core.core.node import Step
from odibi_core.core.dag_builder import DAGBuilder
from odibi_core.core.dag_executor import DAGExecutor
from odibi_core.core.cache_manager import CacheManager


def create_engine_context(engine: str, **kwargs: Any) -> Any:
    """
    Factory function to create engine context by name.

    Args:
        engine: Engine name ("pandas" or "spark")
        **kwargs: Engine-specific configuration

    Returns:
        EngineContext instance

    Raises:
        ValueError: If engine name is unknown

    Example:
        >>> ctx = create_engine_context("pandas")
        >>> ctx = create_engine_context("spark", spark_config={"spark.master": "local[2]"})
    """
    if engine == "pandas":
        from odibi_core.engine.pandas_context import PandasEngineContext

        return PandasEngineContext(**kwargs)
    elif engine == "spark":
        from odibi_core.engine.spark_context import SparkEngineContext

        return SparkEngineContext(**kwargs)
    else:
        raise ValueError(f"Unknown engine: {engine}. Supported: pandas, spark")


class Orchestrator:
    """
    Pipeline orchestrator with DAG-based parallel execution.

    Responsibilities:
    - Build DAG from Step configs
    - Detect circular dependencies
    - Execute Nodes in topological order with parallel execution
    - Track execution time and lineage
    - Handle errors and retries
    - Cache management for optimized re-execution

    Args:
        steps: List of Step configurations
        context: Engine context (Pandas or Spark)
        tracker: Execution tracker
        events: Event emitter
        parallel: Enable parallel execution (default: True)
        max_workers: Maximum parallel threads (default: 4)
        use_cache: Enable caching (default: True)
        max_retries: Maximum retry attempts (default: 2)
        retry_delay: Delay between retries in seconds (default: 1.0)

    Example:
        >>> config = load_config("pipeline.json")
        >>> orchestrator = Orchestrator(config, pandas_context, tracker, events,
        ...                             parallel=True, max_workers=4)
        >>> results = orchestrator.run()
        >>> print(f"Processed {len(results.data_map)} datasets")
    """

    def __init__(
        self,
        steps: List[Step],
        context: Any,  # EngineContext
        tracker: Any,  # Tracker
        events: Any,  # EventEmitter
        parallel: bool = True,
        max_workers: int = 4,
        use_cache: bool = True,
        max_retries: int = 2,
        retry_delay: float = 1.0,
    ) -> None:
        """
        Initialize orchestrator.

        Args:
            steps: List of pipeline steps
            context: Engine context for execution
            tracker: Tracker for snapshots
            events: Event emitter for hooks
            parallel: Enable parallel DAG execution
            max_workers: Maximum parallel workers
            use_cache: Enable cache management
            max_retries: Maximum retry attempts
            retry_delay: Delay between retries
        """
        self.steps = steps
        self.context = context
        self.tracker = tracker
        self.events = events
        self.parallel = parallel
        self.max_workers = max_workers
        self.use_cache = use_cache
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        self.data_map: Dict[str, Any] = {}
        self._execution_order: Optional[List[Step]] = None
        self._dag_builder: Optional[DAGBuilder] = None
        self._dag_executor: Optional[DAGExecutor] = None
        self._cache_manager: Optional[CacheManager] = None

    def build_dag(self) -> List[Step]:
        """
        Build DAG and return execution order via topological sort.

        Returns:
            List of steps in execution order

        Raises:
            ValueError: If circular dependencies detected
        """
        import logging

        logger = logging.getLogger(__name__)

        # Build DAG
        self._dag_builder = DAGBuilder(self.steps)
        dag = self._dag_builder.build()

        # Get execution order
        self._execution_order = self._dag_builder.get_execution_order()

        logger.info(
            f"DAG built successfully: {len(dag)} nodes, "
            f"max depth: {max((n.level for n in dag.values()), default=0)}"
        )

        return self._execution_order

    def detect_cycles(self) -> bool:
        """
        Detect circular dependencies in pipeline.

        Returns:
            True if cycles detected, False otherwise
        """
        try:
            self.build_dag()
            return False
        except ValueError as e:
            if "circular" in str(e).lower() or "cycle" in str(e).lower():
                return True
            raise

    def run(self) -> "OrchestrationResult":
        """
        Execute pipeline with DAG-based parallel execution.

        Returns:
            OrchestrationResult with data_map and execution stats

        Raises:
            Exception: On pipeline failure
        """
        import logging

        logger = logging.getLogger(__name__)

        # Start pipeline tracking
        self.tracker.start_pipeline("odibi_pipeline")
        self.events.emit("pipeline_start", steps=self.steps)

        try:
            if self.parallel:
                # Phase 5: Parallel DAG execution
                logger.info("Using parallel DAG execution mode")
                self._run_parallel()
            else:
                # Sequential execution (backward compatibility)
                logger.info("Using sequential execution mode")
                self._run_sequential()

            # Pipeline completed successfully
            self.events.emit("pipeline_complete", data_map=self.data_map)
            logger.info(
                f"Pipeline completed successfully - {len(self.data_map)} datasets produced"
            )

        except Exception as e:
            self.events.emit("pipeline_error", error=e)
            logger.error(f"Pipeline failed: {e}")
            raise

        return OrchestrationResult(
            data_map=self.data_map,
            tracker=self.tracker,
            dag_builder=self._dag_builder,
            dag_executor=self._dag_executor,
        )

    def _run_parallel(self) -> None:
        """Execute pipeline using parallel DAG executor."""
        import logging

        logger = logging.getLogger(__name__)

        # Build DAG
        dag = self.build_dag()

        # Log execution plan
        batches = self._dag_builder.get_parallel_batches()
        logger.info(f"Execution plan: {len(batches)} parallel levels")
        for i, batch in enumerate(batches):
            logger.info(f"  Level {i}: {[s.name for s in batch]}")

        # Initialize cache manager
        if self.use_cache:
            self._cache_manager = CacheManager(enabled=True)

        # Create executor
        self._dag_executor = DAGExecutor(
            dag=self._dag_builder.dag,
            context=self.context,
            tracker=self.tracker,
            events=self.events,
            max_workers=self.max_workers,
            max_retries=self.max_retries,
            retry_delay=self.retry_delay,
            use_cache=self.use_cache,
            cache_manager=self._cache_manager,
        )

        # Execute DAG
        self.data_map = self._dag_executor.execute()

        # Log stats
        stats = self._dag_executor.get_stats()
        logger.info(
            f"DAG execution stats: "
            f"nodes={stats['total_nodes']}, "
            f"completed={stats['completed']}, "
            f"failed={stats['failed']}, "
            f"cache_hits={stats['cache_hits']} ({stats['cache_hit_rate']*100:.1f}%)"
        )

    def _run_sequential(self) -> None:
        """Execute pipeline sequentially (legacy mode)."""
        for step in self.steps:
            self.run_step(step)

    def run_step(self, step: Step) -> None:
        """
        Execute a single step.

        Args:
            step: Step configuration

        Raises:
            Exception: On step failure
        """
        import logging

        logger = logging.getLogger(__name__)

        # Import Node class from registry
        from odibi_core.nodes import NODE_REGISTRY

        node_class = NODE_REGISTRY.get(step.layer)
        if not node_class:
            raise ValueError(
                f"Unknown node type: {step.layer}. Available: {list(NODE_REGISTRY.keys())}"
            )

        # Start tracking
        self.tracker.start_step(step.name, step.layer)
        self.events.emit("step_start", step=step)

        try:
            # Instantiate node
            node = node_class(step, self.context, self.tracker, self.events)

            # Execute node
            self.data_map = node.run(self.data_map)

            # End tracking (success)
            self.tracker.end_step(step.name, "success")
            self.events.emit(
                "step_complete",
                step=step,
                duration_ms=self.tracker.executions[-1].duration_ms,
            )

            logger.info(f"Step '{step.name}' completed successfully")

        except Exception as e:
            # End tracking (failed)
            self.tracker.end_step(step.name, "failed", str(e))
            self.events.emit("step_error", step=step, error=e)

            logger.error(f"Step '{step.name}' failed: {e}")
            raise

    def validate_inputs(self, step: Step) -> bool:
        """
        Validate that all step inputs are available in data_map.

        Args:
            step: Step to validate

        Returns:
            True if all inputs available, False otherwise
        """
        # TODO Phase 3: Implement input validation
        for logical_name, dataset_key in step.inputs.items():
            if dataset_key not in self.data_map:
                return False
        return True


class OrchestrationResult:
    """
    Result of pipeline execution.

    Attributes:
        data_map: Dictionary of all DataFrames produced
        tracker: Tracker with execution history
        dag_builder: DAG builder instance (if parallel execution used)
        dag_executor: DAG executor instance (if parallel execution used)
    """

    def __init__(
        self,
        data_map: Dict[str, Any],
        tracker: Any,
        dag_builder: Optional[DAGBuilder] = None,
        dag_executor: Optional[DAGExecutor] = None,
    ) -> None:
        """
        Initialize result.

        Args:
            data_map: Final data_map after execution
            tracker: Tracker with execution history
            dag_builder: DAG builder instance
            dag_executor: DAG executor instance
        """
        self.data_map = data_map
        self.tracker = tracker
        self.dag_builder = dag_builder
        self.dag_executor = dag_executor

    def get_execution_stats(self) -> Dict[str, Any]:
        """
        Get execution statistics.

        Returns:
            Dictionary with execution metrics
        """
        stats = self.tracker.get_stats()

        if self.dag_executor:
            dag_stats = self.dag_executor.get_stats()
            stats.update(
                {
                    "cache_hits": dag_stats.get("cache_hits", 0),
                    "cache_hit_rate": dag_stats.get("cache_hit_rate", 0),
                    "parallel_execution": True,
                }
            )
        else:
            stats["parallel_execution"] = False

        return stats
