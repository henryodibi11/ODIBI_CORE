"""
Events Bus (Phase 8)

Lightweight event bus for automation hooks and post-run actions.

Features:
- Priority-based event dispatching
- Asynchronous hook execution
- Built-in hooks: log rotation, metric aggregation, email alerts
- Custom hook registration
- Error isolation (hooks don't fail pipelines)

Usage:
    from odibi_core.observability import EventBus, EventPriority, AutomationHook

    bus = EventBus()

    # Register built-in hooks
    bus.register_hook("pipeline_complete", bus.create_summary_hook())
    bus.register_hook("pipeline_complete", bus.create_metrics_export_hook("metrics/"))

    # Register custom hook
    def custom_alert(event_data):
        if event_data.get("failed_count", 0) > 0:
            print(f"ALERT: {event_data['failed_count']} nodes failed!")

    bus.register_hook("pipeline_complete", custom_alert, priority=EventPriority.HIGH)

    # Emit events
    bus.emit("pipeline_complete", {
        "pipeline_name": "energy_efficiency",
        "success_count": 10,
        "failed_count": 0
    })
"""

import logging
import time
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)


class EventPriority(int, Enum):
    """Event hook priority levels (lower = higher priority)"""

    CRITICAL = 0
    HIGH = 1
    MEDIUM = 2
    LOW = 3


@dataclass
class AutomationHook:
    """
    Automation hook for event-driven actions.

    Attributes:
        name: Hook name
        callback: Function to call when event fires
        priority: Execution priority
        async_execution: Whether to run in background thread
        enabled: Whether hook is active
    """

    name: str
    callback: Callable[[Dict[str, Any]], None]
    priority: EventPriority = EventPriority.MEDIUM
    async_execution: bool = False
    enabled: bool = True


class EventBus:
    """
    Event bus for automation hooks and post-run actions.

    Provides a simple pub-sub system for triggering actions at pipeline
    lifecycle events (start, complete, error, node events, etc.).

    Attributes:
        hooks: Registered hooks by event name
        max_workers: Maximum threads for async hooks
        execution_timeout: Timeout for hook execution in seconds
    """

    def __init__(self, max_workers: int = 4, execution_timeout: float = 30.0):
        """
        Initialize event bus.

        Args:
            max_workers: Maximum concurrent threads for async hooks
            execution_timeout: Timeout for hook execution in seconds
        """
        self.hooks: Dict[str, List[AutomationHook]] = {}
        self.max_workers = max_workers
        self.execution_timeout = execution_timeout
        self._executor = ThreadPoolExecutor(max_workers=max_workers)

        logger.info("EventBus initialized")

    def register_hook(
        self,
        event_name: str,
        callback: Callable[[Dict[str, Any]], None],
        name: Optional[str] = None,
        priority: EventPriority = EventPriority.MEDIUM,
        async_execution: bool = False,
    ) -> AutomationHook:
        """
        Register a hook for an event.

        Args:
            event_name: Event to listen for
            callback: Function to call when event fires
            name: Hook name (default: function name)
            priority: Execution priority
            async_execution: Run in background thread

        Returns:
            Registered AutomationHook

        Example:
            >>> def my_hook(data):
            ...     print(f"Pipeline completed: {data['pipeline_name']}")
            >>> bus.register_hook("pipeline_complete", my_hook)
        """
        hook_name = name or callback.__name__

        hook = AutomationHook(
            name=hook_name,
            callback=callback,
            priority=priority,
            async_execution=async_execution,
        )

        if event_name not in self.hooks:
            self.hooks[event_name] = []

        self.hooks[event_name].append(hook)

        # Sort by priority
        self.hooks[event_name].sort(key=lambda h: h.priority.value)

        logger.info(
            f"Registered hook '{hook_name}' for event '{event_name}' (priority: {priority.name})"
        )

        return hook

    def emit(
        self, event_name: str, event_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Emit an event to all registered hooks.

        Args:
            event_name: Event to emit
            event_data: Data to pass to hooks

        Example:
            >>> bus.emit("pipeline_complete", {
            ...     "pipeline_name": "demo",
            ...     "success_count": 5
            ... })
        """
        if event_name not in self.hooks:
            logger.debug(f"No hooks registered for event '{event_name}'")
            return

        event_data = event_data or {}
        event_data["_event_name"] = event_name
        event_data["_event_time"] = datetime.now().isoformat()

        hooks = [h for h in self.hooks[event_name] if h.enabled]

        if not hooks:
            logger.debug(f"No enabled hooks for event '{event_name}'")
            return

        logger.info(f"Emitting event '{event_name}' to {len(hooks)} hook(s)")

        # Execute hooks by priority
        sync_hooks = [h for h in hooks if not h.async_execution]
        async_hooks = [h for h in hooks if h.async_execution]

        # Execute synchronous hooks first
        for hook in sync_hooks:
            self._execute_hook(hook, event_data)

        # Execute asynchronous hooks in background
        if async_hooks:
            for hook in async_hooks:
                self._executor.submit(self._execute_hook, hook, event_data)

    def _execute_hook(self, hook: AutomationHook, event_data: Dict[str, Any]) -> None:
        """
        Execute a single hook with error handling.

        Args:
            hook: Hook to execute
            event_data: Event data
        """
        try:
            logger.debug(f"Executing hook '{hook.name}'")
            start_time = time.time()

            hook.callback(event_data)

            duration = (time.time() - start_time) * 1000
            logger.debug(f"Hook '{hook.name}' completed in {duration:.2f}ms")

        except Exception as e:
            # Isolate errors - don't let hook failures break pipeline
            logger.error(f"Hook '{hook.name}' failed: {e}", exc_info=True)

    def disable_hook(self, event_name: str, hook_name: str) -> None:
        """
        Disable a specific hook.

        Args:
            event_name: Event name
            hook_name: Hook name to disable
        """
        if event_name in self.hooks:
            for hook in self.hooks[event_name]:
                if hook.name == hook_name:
                    hook.enabled = False
                    logger.info(f"Disabled hook '{hook_name}' for event '{event_name}'")
                    return

    def enable_hook(self, event_name: str, hook_name: str) -> None:
        """
        Enable a specific hook.

        Args:
            event_name: Event name
            hook_name: Hook name to enable
        """
        if event_name in self.hooks:
            for hook in self.hooks[event_name]:
                if hook.name == hook_name:
                    hook.enabled = True
                    logger.info(f"Enabled hook '{hook_name}' for event '{event_name}'")
                    return

    def clear_hooks(self, event_name: Optional[str] = None) -> None:
        """
        Clear registered hooks.

        Args:
            event_name: Specific event to clear, or None for all
        """
        if event_name is None:
            self.hooks.clear()
            logger.info("Cleared all hooks")
        elif event_name in self.hooks:
            del self.hooks[event_name]
            logger.info(f"Cleared hooks for event '{event_name}'")

    def get_hooks(self, event_name: str) -> List[AutomationHook]:
        """
        Get registered hooks for an event.

        Args:
            event_name: Event name

        Returns:
            List of registered hooks
        """
        return self.hooks.get(event_name, [])

    # Built-in hook factories

    def create_summary_hook(self) -> Callable[[Dict[str, Any]], None]:
        """
        Create a hook that prints pipeline summary.

        Returns:
            Hook function

        Example:
            >>> bus.register_hook("pipeline_complete", bus.create_summary_hook())
        """

        def summary_hook(event_data: Dict[str, Any]) -> None:
            print("\n" + "=" * 70)
            print("Pipeline Execution Summary")
            print("=" * 70)
            print(f"Pipeline: {event_data.get('pipeline_name', 'unknown')}")
            print(f"Success: {event_data.get('success_count', 0)}")
            print(f"Failed: {event_data.get('failed_count', 0)}")
            print(f"Duration: {event_data.get('duration_ms', 0):.2f}ms")
            print("=" * 70 + "\n")

        return summary_hook

    def create_metrics_export_hook(
        self, export_dir: str, formats: Optional[List[str]] = None
    ) -> Callable[[Dict[str, Any]], None]:
        """
        Create a hook that exports metrics to files.

        Args:
            export_dir: Directory for metric exports
            formats: List of formats ("prometheus", "json", "parquet")

        Returns:
            Hook function

        Example:
            >>> hook = bus.create_metrics_export_hook("metrics/", ["json", "prometheus"])
            >>> bus.register_hook("pipeline_complete", hook)
        """
        formats = formats or ["json", "prometheus"]

        def metrics_export_hook(event_data: Dict[str, Any]) -> None:
            try:
                from odibi_core.metrics import MetricsManager
                from odibi_core.observability import MetricsExporter

                # Get metrics manager from event data
                metrics_manager = event_data.get("metrics_manager")
                if not metrics_manager:
                    logger.warning("No metrics_manager in event data")
                    return

                exporter = MetricsExporter(metrics_manager)

                Path(export_dir).mkdir(parents=True, exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

                if "json" in formats:
                    filepath = Path(export_dir) / f"metrics_{timestamp}.json"
                    exporter.save_json(str(filepath))

                if "prometheus" in formats:
                    filepath = Path(export_dir) / f"metrics_{timestamp}.prom"
                    exporter.save_prometheus(str(filepath))

                if "parquet" in formats:
                    filepath = Path(export_dir) / f"metrics_{timestamp}.parquet"
                    exporter.save_parquet(str(filepath))

                logger.info(f"Metrics exported to {export_dir}")

            except Exception as e:
                logger.error(f"Failed to export metrics: {e}")

        return metrics_export_hook

    def create_log_rotation_hook(
        self, log_dir: str, max_files: int = 10
    ) -> Callable[[Dict[str, Any]], None]:
        """
        Create a hook that rotates old log files.

        Args:
            log_dir: Log directory to clean
            max_files: Maximum log files to keep

        Returns:
            Hook function

        Example:
            >>> hook = bus.create_log_rotation_hook("logs/", max_files=5)
            >>> bus.register_hook("pipeline_complete", hook)
        """

        def log_rotation_hook(event_data: Dict[str, Any]) -> None:
            try:
                log_path = Path(log_dir)
                if not log_path.exists():
                    return

                # Get all .jsonl files sorted by modification time
                log_files = sorted(
                    log_path.glob("*.jsonl"),
                    key=lambda p: p.stat().st_mtime,
                    reverse=True,
                )

                # Delete old files
                for log_file in log_files[max_files:]:
                    logger.info(f"Rotating old log file: {log_file}")
                    log_file.unlink()

            except Exception as e:
                logger.error(f"Failed to rotate logs: {e}")

        return log_rotation_hook

    def create_alert_hook(
        self, threshold_failed: int = 1
    ) -> Callable[[Dict[str, Any]], None]:
        """
        Create a hook that alerts on failures.

        Args:
            threshold_failed: Number of failures to trigger alert

        Returns:
            Hook function

        Example:
            >>> hook = bus.create_alert_hook(threshold_failed=3)
            >>> bus.register_hook("pipeline_complete", hook, priority=EventPriority.HIGH)
        """

        def alert_hook(event_data: Dict[str, Any]) -> None:
            failed_count = event_data.get("failed_count", 0)

            if failed_count >= threshold_failed:
                print(f"\n{'!' * 70}")
                print(
                    f"ALERT: Pipeline '{event_data.get('pipeline_name')}' had {failed_count} failed nodes!"
                )
                print(f"{'!' * 70}\n")
                logger.critical(f"Pipeline failure alert: {failed_count} nodes failed")

        return alert_hook

    def create_cache_stats_hook(self) -> Callable[[Dict[str, Any]], None]:
        """
        Create a hook that prints cache statistics.

        Returns:
            Hook function

        Example:
            >>> bus.register_hook("pipeline_complete", bus.create_cache_stats_hook())
        """

        def cache_stats_hook(event_data: Dict[str, Any]) -> None:
            cache_manager = event_data.get("cache_manager")
            if not cache_manager:
                return

            stats = cache_manager.get_stats()

            print("\nCache Statistics:")
            print("-" * 40)
            print(f"Hits: {stats.get('hits', 0)}")
            print(f"Misses: {stats.get('misses', 0)}")
            print(f"Hit Rate: {stats.get('hit_rate', 0):.1f}%")
            print(f"Size: {stats.get('size_mb', 0):.2f} MB")
            print("-" * 40 + "\n")

        return cache_stats_hook

    def shutdown(self) -> None:
        """Shutdown event bus and wait for async hooks to complete."""
        logger.info("Shutting down EventBus...")
        self._executor.shutdown(wait=True)
        logger.info("EventBus shutdown complete")
