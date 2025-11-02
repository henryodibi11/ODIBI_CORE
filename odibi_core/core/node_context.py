"""
Node-scoped context for Spark-safe view isolation.

Implements namespace-scoped temporary view management to prevent collisions
in parallel DAG execution. Works in any Spark environment including Databricks.
"""

import logging
import threading
import uuid
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class NodeContext:
    """
    Node-scoped execution context for temp view isolation.

    In parallel DAG execution, multiple nodes may execute simultaneously
    in different threads. This class ensures that:
    - Each node gets unique view names (prefixed with node name + UUID + thread ID)
    - All registered views are tracked and cleaned up after node execution
    - No view name collisions occur between parallel branches
    - Works in Databricks and local Spark environments

    Args:
        node_name: Name of the node (used as namespace prefix)
        context: Engine context (PandasEngineContext or SparkEngineContext)
        thread_id: Optional thread identifier (auto-detected if None)

    Example:
        >>> node_ctx = NodeContext("calc_efficiency", spark_context)
        >>> # Register temp view with auto-prefixed name
        >>> view_name = node_ctx.register_view("input_data", df)
        >>> # view_name = "calc_efficiency_a3f4_12345_input_data"
        >>> # ... execute SQL using view_name ...
        >>> node_ctx.cleanup()  # Remove all views
    """

    def __init__(
        self,
        node_name: str,
        context: Any,  # EngineContext
        thread_id: Optional[int] = None,
    ) -> None:
        """
        Initialize node context.

        Args:
            node_name: Node identifier
            context: Engine context for execution
            thread_id: Thread ID (auto-detected if None)
        """
        self.node_name = node_name
        self.context = context
        self.thread_id = thread_id or threading.get_ident()
        self.session_id = str(uuid.uuid4())[:8]  # Short unique ID

        # Track all registered views for cleanup
        self._registered_views: Set[str] = set()

        logger.debug(
            f"Created NodeContext: node={node_name}, "
            f"session={self.session_id}, thread={self.thread_id}"
        )

    def get_view_name(self, logical_name: str) -> str:
        """
        Generate unique view name for this node context.

        Format: {node_name}_{session_id}_{thread_id}_{logical_name}

        Args:
            logical_name: Logical name from SQL or config

        Returns:
            Globally unique view name

        Example:
            >>> ctx = NodeContext("transform_gold", spark_ctx)
            >>> view_name = ctx.get_view_name("silver_data")
            >>> # "transform_gold_a3f4_12345_silver_data"
        """
        # Sanitize node name (replace spaces/special chars with underscores)
        safe_node_name = self.node_name.replace(" ", "_").replace("-", "_")

        view_name = (
            f"{safe_node_name}_{self.session_id}_{self.thread_id}_{logical_name}"
        )

        return view_name

    def register_view(self, logical_name: str, df: Any) -> str:
        """
        Register DataFrame as temporary view with unique name.

        Args:
            logical_name: Logical name for the view
            df: DataFrame to register (Pandas or Spark)

        Returns:
            Actual view name (with namespace prefix)

        Raises:
            Exception: If view registration fails

        Example:
            >>> df = spark.read.parquet("data.parquet")
            >>> view_name = node_ctx.register_view("input", df)
            >>> spark.sql(f"SELECT * FROM {view_name}")
        """
        view_name = self.get_view_name(logical_name)

        try:
            # Register view via engine context
            self.context.register_temp_view(view_name, df)

            # Track for cleanup
            self._registered_views.add(view_name)

            logger.debug(f"Registered view: {view_name} (logical: {logical_name})")

            return view_name

        except Exception as e:
            logger.error(f"Failed to register view '{view_name}': {e}")
            raise

    def unregister_view(self, view_name: str) -> None:
        """
        Unregister a specific temporary view.

        Args:
            view_name: View name to remove

        Example:
            >>> node_ctx.unregister_view("my_node_a3f4_12345_temp_view")
        """
        try:
            self.context.unregister_temp_view(view_name)
            self._registered_views.discard(view_name)
            logger.debug(f"Unregistered view: {view_name}")
        except Exception as e:
            logger.warning(f"Failed to unregister view '{view_name}': {e}")

    def cleanup(self) -> None:
        """
        Clean up all registered temporary views.

        This method is safe to call in Databricks environments where
        temp views may be scoped to the global catalog.

        Example:
            >>> try:
            ...     node_ctx.register_view("data", df)
            ...     # ... execute SQL ...
            ... finally:
            ...     node_ctx.cleanup()
        """
        logger.debug(
            f"Cleaning up {len(self._registered_views)} views "
            f"for node '{self.node_name}'"
        )

        for view_name in list(self._registered_views):
            try:
                self.context.unregister_temp_view(view_name)
                logger.debug(f"Cleaned up view: {view_name}")
            except Exception as e:
                # Non-fatal: view may have been auto-dropped or not exist
                logger.debug(f"Could not cleanup view '{view_name}': {e}")

        self._registered_views.clear()

    def __enter__(self) -> "NodeContext":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit - auto cleanup."""
        self.cleanup()

    def get_stats(self) -> Dict[str, Any]:
        """
        Get context statistics.

        Returns:
            Dict with view count and metadata

        Example:
            >>> stats = node_ctx.get_stats()
            >>> print(f"Active views: {stats['view_count']}")
        """
        return {
            "node_name": self.node_name,
            "session_id": self.session_id,
            "thread_id": self.thread_id,
            "view_count": len(self._registered_views),
            "registered_views": list(self._registered_views),
        }
