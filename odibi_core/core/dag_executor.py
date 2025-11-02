"""
DAG executor for parallel, fault-tolerant pipeline execution.

Executes nodes in topological order with:
- Thread-based parallelism for independent branches
- Automatic retry on failure
- Cache-aware execution (skip nodes when cached)
- NodeContext for Spark-safe view isolation
- Streaming and incremental processing (Phase 6)
- Checkpoint/resume support (Phase 6)
"""

import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed, Future
from typing import Any, Dict, List, Optional, Set, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from odibi_core.core.node import Step, NodeState
from odibi_core.core.dag_builder import DAGBuilder, DAGNode
from odibi_core.core.cache_manager import CacheManager
from odibi_core.core.node_context import NodeContext

logger = logging.getLogger(__name__)


class ExecutionMode(str, Enum):
    """DAG execution modes."""

    BATCH = "batch"  # Standard batch execution
    STREAM = "stream"  # Continuous streaming
    RESUME = "resume"  # Resume from checkpoint


@dataclass
class NodeExecutionResult:
    """
    Result of a node execution.

    Attributes:
        node_name: Name of the node
        state: Final state (SUCCESS, FAILED, RETRY)
        duration_ms: Execution duration in milliseconds
        attempts: Number of execution attempts
        thread_id: Thread ID that executed the node
        error: Error message if failed
        cached: Whether result was loaded from cache
    """

    node_name: str
    state: NodeState
    duration_ms: float
    attempts: int
    thread_id: int
    error: Optional[str] = None
    cached: bool = False


class DAGExecutor:
    """
    Execute DAG with parallel, fault-tolerant, cache-aware execution.

    Uses ThreadPoolExecutor to run independent nodes in parallel while
    respecting dependency constraints. Supports:
    - max_workers: Control parallelism level
    - max_retries: Retry failed nodes
    - use_cache: Skip execution if cached output exists
    - NodeContext: Spark-safe view isolation per node

    Args:
        dag: Dictionary mapping step_name → DAGNode
        context: Engine context (Pandas or Spark)
        tracker: Execution tracker
        events: Event emitter
        max_workers: Maximum parallel threads (default: 4)
        max_retries: Maximum retry attempts per node (default: 2)
        retry_delay: Delay between retries in seconds (default: 1.0)
        use_cache: Enable cache lookup/storage (default: True)
        cache_manager: Optional cache manager instance

    Example:
        >>> builder = DAGBuilder(steps)
        >>> dag = builder.build()
        >>> executor = DAGExecutor(dag, pandas_context, tracker, events)
        >>> data_map = executor.execute()
        >>> print(f"Executed {len(data_map)} datasets")
    """

    def __init__(
        self,
        dag: Dict[str, DAGNode],
        context: Any,  # EngineContext
        tracker: Any,  # Tracker
        events: Any,  # EventEmitter
        max_workers: int = 4,
        max_retries: int = 2,
        retry_delay: float = 1.0,
        use_cache: bool = True,
        cache_manager: Optional[CacheManager] = None,
        checkpoint_manager: Optional[Any] = None,
        mode: ExecutionMode = ExecutionMode.BATCH,
        skip_nodes: Optional[Set[str]] = None,
    ) -> None:
        """
        Initialize DAG executor.

        Args:
            dag: Dictionary mapping step_name → DAGNode
            context: Engine context
            tracker: Execution tracker
            events: Event emitter
            max_workers: Maximum parallel threads
            max_retries: Maximum retry attempts per node
            retry_delay: Delay between retries in seconds
            use_cache: Enable cache lookup/storage
            cache_manager: Optional cache manager instance
            checkpoint_manager: Optional checkpoint manager for resume
            mode: Execution mode (batch, stream, resume)
            skip_nodes: Set of node names to skip (for resume mode)
        """
        self.dag = dag
        self.context = context
        self.tracker = tracker
        self.events = events
        self.max_workers = max_workers
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.use_cache = use_cache
        self.mode = mode
        self.skip_nodes = skip_nodes or set()

        # Cache manager
        self.cache = cache_manager or CacheManager(enabled=use_cache)

        # Checkpoint manager
        self.checkpoint_manager = checkpoint_manager

        # Execution state
        self.data_map: Dict[str, Any] = {}
        self._completed: Set[str] = set()
        self._failed: Set[str] = set()
        self._results: List[NodeExecutionResult] = []
        self._iteration = 0
        self._is_running = False

        # Thread safety
        self._lock = threading.Lock()

    def execute(self) -> Dict[str, Any]:
        """
        Execute DAG with parallel execution.

        Returns:
            data_map with all outputs

        Raises:
            RuntimeError: If any node fails after retries

        Example:
            >>> data_map = executor.execute()
            >>> print(f"Outputs: {list(data_map.keys())}")
        """
        logger.info(
            f"Starting DAG execution: {len(self.dag)} nodes, "
            f"{self.max_workers} workers, cache={'enabled' if self.use_cache else 'disabled'}"
        )

        start_time = time.time()

        # Get execution batches (nodes grouped by topological level)
        batches = self._get_parallel_batches()

        logger.info(f"Execution plan: {len(batches)} parallel levels")

        # Execute level by level
        for level, batch in enumerate(batches):
            logger.info(f"Level {level}: Executing {len(batch)} node(s) in parallel")

            self._execute_batch(batch)

            # Check for failures
            if self._failed:
                failed_nodes = ", ".join(self._failed)
                raise RuntimeError(
                    f"DAG execution failed. Failed nodes: {failed_nodes}"
                )

        # Execution complete
        duration = (time.time() - start_time) * 1000

        logger.info(
            f"DAG execution completed in {duration:.2f}ms. "
            f"Success: {len(self._completed)}, Failed: {len(self._failed)}"
        )

        return self.data_map

    def _get_parallel_batches(self) -> List[List[DAGNode]]:
        """Group nodes by topological level for parallel execution."""
        # Group by level
        levels: Dict[int, List[DAGNode]] = {}
        for node in self.dag.values():
            if node.level not in levels:
                levels[node.level] = []
            levels[node.level].append(node)

        # Convert to sorted list
        max_level = max(levels.keys()) if levels else -1
        batches = [levels.get(i, []) for i in range(max_level + 1)]

        return batches

    def _execute_batch(self, nodes: List[DAGNode]) -> None:
        """
        Execute a batch of nodes in parallel.

        Args:
            nodes: Nodes at the same topological level
        """
        if len(nodes) == 1:
            # Single node - no need for thread pool
            self._execute_node(nodes[0])
        else:
            # Parallel execution
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures: Dict[Future, DAGNode] = {}

                # Submit all nodes
                for node in nodes:
                    if node.name in self.skip_nodes:
                        logger.info(f"Skipping node (resume mode): {node.name}")
                        with self._lock:
                            self._completed.add(node.name)
                        continue

                    future = executor.submit(self._execute_node, node)
                    futures[future] = node

                # Wait for completion
                for future in as_completed(futures):
                    node = futures[future]
                    try:
                        future.result()  # Raise exception if failed
                    except Exception as e:
                        logger.error(
                            f"Node '{node.name}' failed in parallel batch: {e}"
                        )
                        # Error already logged in _execute_node

    def _execute_node(self, node: DAGNode) -> None:
        """
        Execute a single node with retry logic.

        Args:
            node: DAGNode to execute

        Raises:
            RuntimeError: If node fails after all retries
        """
        thread_id = threading.get_ident()

        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(
                    f"Executing '{node.name}' (attempt {attempt}/{self.max_retries}, "
                    f"thread {thread_id})"
                )

                # Start tracking
                self.tracker.start_step(node.name, node.step.layer)
                start_time = time.time()

                # Check cache
                cached_result = None
                if self.use_cache and attempt == 1:
                    cached_result = self._check_cache(node)

                if cached_result is not None:
                    # Cache hit
                    with self._lock:
                        self.data_map.update(cached_result)

                    duration_ms = (time.time() - start_time) * 1000

                    # Track as success
                    self.tracker.end_step(node.name, "success")

                    result = NodeExecutionResult(
                        node_name=node.name,
                        state=NodeState.SUCCESS,
                        duration_ms=duration_ms,
                        attempts=attempt,
                        thread_id=thread_id,
                        cached=True,
                    )

                    logger.info(f"Node '{node.name}' cache hit ({duration_ms:.2f}ms)")

                else:
                    # Execute node
                    result_data = self._run_node_logic(node, thread_id)

                    # Store in data_map (thread-safe)
                    with self._lock:
                        self.data_map.update(result_data)

                    # Cache result
                    if self.use_cache:
                        self._store_cache(node, result_data)

                    duration_ms = (time.time() - start_time) * 1000

                    # Track as success
                    self.tracker.end_step(node.name, "success")

                    result = NodeExecutionResult(
                        node_name=node.name,
                        state=NodeState.SUCCESS,
                        duration_ms=duration_ms,
                        attempts=attempt,
                        thread_id=thread_id,
                        cached=False,
                    )

                    logger.info(
                        f"Node '{node.name}' completed ({duration_ms:.2f}ms, thread {thread_id})"
                    )

                # Mark as completed
                with self._lock:
                    self._completed.add(node.name)
                    self._results.append(result)

                return  # Success!

            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000

                logger.error(
                    f"Node '{node.name}' failed (attempt {attempt}/{self.max_retries}): {e}"
                )

                # Track failure
                if attempt >= self.max_retries:
                    self.tracker.end_step(node.name, "failed", str(e))
                else:
                    self.tracker.end_step(node.name, "retry", str(e))

                # Last attempt failed
                if attempt >= self.max_retries:
                    result = NodeExecutionResult(
                        node_name=node.name,
                        state=NodeState.FAILED,
                        duration_ms=duration_ms,
                        attempts=attempt,
                        thread_id=thread_id,
                        error=str(e),
                    )

                    with self._lock:
                        self._failed.add(node.name)
                        self._results.append(result)

                    raise RuntimeError(f"Node '{node.name}' failed: {e}") from e

                # Retry delay
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay)

    def _run_node_logic(self, node: DAGNode, thread_id: int) -> Dict[str, Any]:
        """
        Execute node business logic.

        Args:
            node: DAGNode to execute
            thread_id: Current thread ID

        Returns:
            Dictionary of output_key → DataFrame

        Raises:
            Exception: On execution failure
        """
        # Import Node class from registry
        from odibi_core.nodes import NODE_REGISTRY

        node_class = NODE_REGISTRY.get(node.step.layer)
        if not node_class:
            raise ValueError(
                f"Unknown node type: {node.step.layer}. "
                f"Available: {list(NODE_REGISTRY.keys())}"
            )

        # Create NodeContext for view isolation
        node_context = NodeContext(node.name, self.context, thread_id)

        try:
            # Instantiate node
            node_instance = node_class(
                node.step, self.context, self.tracker, self.events
            )

            # Attach node context
            if hasattr(node_instance, "set_node_context"):
                node_instance.set_node_context(node_context)

            # Execute node with current data_map
            with self._lock:
                current_data_map = self.data_map.copy()

            result_data_map = node_instance.run(current_data_map)

            # Extract new outputs only
            new_outputs = {}
            for output_key in node.step.outputs.values():
                if output_key in result_data_map:
                    new_outputs[output_key] = result_data_map[output_key]

            return new_outputs

        finally:
            # Always cleanup views
            node_context.cleanup()

    def _check_cache(self, node: DAGNode) -> Optional[Dict[str, Any]]:
        """
        Check if cached output exists for node.

        Args:
            node: DAGNode to check

        Returns:
            Dictionary of outputs if cache hit, None otherwise
        """
        try:
            # Compute input hashes
            inputs_hash = self._compute_inputs_hash(node)

            # Compute cache key
            cache_key = self.cache.compute_cache_key(
                node.name,
                node.step.params or {},
                inputs_hash,
                node.step.value,
            )

            # Check cache
            cached_df = self.cache.get(cache_key, engine=node.step.engine)

            if cached_df is not None:
                # Build outputs dict
                outputs = {}
                for output_key in node.step.outputs.values():
                    outputs[output_key] = cached_df

                return outputs

            return None

        except Exception as e:
            logger.warning(f"Cache check failed for '{node.name}': {e}")
            return None

    def _store_cache(self, node: DAGNode, outputs: Dict[str, Any]) -> None:
        """
        Store node outputs in cache.

        Args:
            node: DAGNode that was executed
            outputs: Dictionary of output_key → DataFrame
        """
        try:
            # Compute input hashes
            inputs_hash = self._compute_inputs_hash(node)

            # Compute cache key
            cache_key = self.cache.compute_cache_key(
                node.name,
                node.step.params or {},
                inputs_hash,
                node.step.value,
            )

            # Cache first output (simplification: single output per node)
            if outputs:
                first_df = list(outputs.values())[0]
                self.cache.put(
                    cache_key,
                    first_df,
                    engine=node.step.engine,
                    metadata={"node": node.name, "outputs": list(outputs.keys())},
                )

        except Exception as e:
            logger.warning(f"Failed to cache outputs for '{node.name}': {e}")

    def _compute_inputs_hash(self, node: DAGNode) -> str:
        """
        Compute hash of node inputs.

        Args:
            node: DAGNode

        Returns:
            Hash string combining all input DataFrame hashes
        """
        input_hashes = []

        for input_key in node.step.inputs.values():
            if input_key in self.data_map:
                df = self.data_map[input_key]
                df_hash = self.cache.compute_dataframe_hash(df, node.step.engine)
                input_hashes.append(df_hash)

        # Combine all input hashes
        combined = "_".join(sorted(input_hashes))

        import hashlib

        final_hash = hashlib.sha256(combined.encode()).hexdigest()[:16]

        return final_hash

    def get_results(self) -> List[NodeExecutionResult]:
        """
        Get execution results for all nodes.

        Returns:
            List of NodeExecutionResult objects

        Example:
            >>> results = executor.get_results()
            >>> for r in results:
            ...     print(f"{r.node_name}: {r.state.value} in {r.duration_ms:.2f}ms")
        """
        return self._results.copy()

    def get_stats(self) -> Dict[str, Any]:
        """
        Get execution statistics.

        Returns:
            Dictionary with execution metrics

        Example:
            >>> stats = executor.get_stats()
            >>> print(f"Cache hits: {stats['cache_hits']}")
        """
        total_duration = sum(r.duration_ms for r in self._results)
        cache_hits = sum(1 for r in self._results if r.cached)
        total_attempts = sum(r.attempts for r in self._results)

        return {
            "total_nodes": len(self.dag),
            "completed": len(self._completed),
            "failed": len(self._failed),
            "total_duration_ms": total_duration,
            "cache_hits": cache_hits,
            "cache_hit_rate": cache_hits / len(self._results) if self._results else 0,
            "total_attempts": total_attempts,
            "avg_attempts": total_attempts / len(self._results) if self._results else 0,
            "mode": self.mode.value,
            "iteration": self._iteration,
        }

    def run_continuous(
        self,
        data_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
        max_iterations: Optional[int] = None,
        sleep_seconds: float = 5.0,
        checkpoint_interval: int = 1,
    ) -> None:
        """
        Run DAG continuously in streaming mode.

        Args:
            data_callback: Optional callback to update data_map before each iteration
            max_iterations: Maximum iterations (None = infinite)
            sleep_seconds: Sleep time between iterations
            checkpoint_interval: Create checkpoint every N iterations

        Example:
            >>> def update_data(data_map):
            ...     # Load new data
            ...     data_map['raw_data'] = stream_manager.read_batch('source1')
            >>>
            >>> executor.run_continuous(
            ...     data_callback=update_data,
            ...     max_iterations=100,
            ...     checkpoint_interval=10
            ... )
        """
        self._is_running = True
        logger.info(f"Starting continuous execution (max_iterations={max_iterations})")

        try:
            while max_iterations is None or self._iteration < max_iterations:
                if not self._is_running:
                    break

                logger.info(f"=== Iteration {self._iteration + 1} ===")

                # Reset state for new iteration
                self._completed.clear()
                self._failed.clear()

                # Update data via callback
                if data_callback:
                    try:
                        data_callback(self.data_map)
                    except Exception as e:
                        logger.error(f"Data callback failed: {e}")
                        break

                # Execute DAG
                try:
                    self.execute()
                    self._iteration += 1

                    # Create checkpoint
                    if (
                        self.checkpoint_manager
                        and self._iteration % checkpoint_interval == 0
                    ):
                        self._create_checkpoint()

                except Exception as e:
                    logger.error(f"Iteration {self._iteration + 1} failed: {e}")
                    if self.checkpoint_manager:
                        self._create_checkpoint()
                    break

                # Sleep before next iteration
                if max_iterations is None or self._iteration < max_iterations:
                    time.sleep(sleep_seconds)

        finally:
            self._is_running = False
            logger.info(
                f"Continuous execution stopped after {self._iteration} iterations"
            )

    def stop_continuous(self) -> None:
        """Stop continuous execution."""
        self._is_running = False
        logger.info("Stopping continuous execution...")

    def _create_checkpoint(self) -> None:
        """Create checkpoint of current execution state."""
        if not self.checkpoint_manager:
            return

        try:
            from odibi_core.checkpoint import NodeCheckpoint

            completed_checkpoints = [
                NodeCheckpoint(
                    node_name=r.node_name,
                    state=r.state.value,
                    completed_at=datetime.now().isoformat(),
                    duration_ms=r.duration_ms,
                    attempts=r.attempts,
                    cached=r.cached,
                    error=r.error,
                )
                for r in self._results
                if r.state == NodeState.SUCCESS
            ]

            pending_nodes = {n for n in self.dag.keys() if n not in self._completed}

            checkpoint = self.checkpoint_manager.create_checkpoint(
                dag_name=f"dag_{self._iteration}",
                completed_nodes=completed_checkpoints,
                pending_nodes=pending_nodes,
                failed_nodes=self._failed,
                mode=self.mode.value,
                iteration=self._iteration,
                metadata={"timestamp": datetime.now().isoformat()},
            )

            self.checkpoint_manager.save(checkpoint)
            logger.info(f"Checkpoint created for iteration {self._iteration}")

        except Exception as e:
            logger.error(f"Failed to create checkpoint: {e}")
