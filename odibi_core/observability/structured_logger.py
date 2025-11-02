"""
Structured Logger (Phase 8)

JSON Lines-based structured logging for DAG execution, node events, and exceptions.

Features:
- JSON Lines (.jsonl) format for each log entry
- Contextual fields: timestamp, node, engine, status, duration, error, user, cache hit
- Integration with Tracker and DAGExecutor
- Automatic log rotation support
- Query-friendly JSON structure

Usage:
    from odibi_core.observability import StructuredLogger, LogLevel

    logger = StructuredLogger("odibi_pipeline", log_dir="logs")

    # Log node execution
    logger.log_node_start("read_data", "ingest", engine="pandas")
    logger.log_node_complete("read_data", duration_ms=125.5, rows=1000)

    # Log errors
    logger.log_error("transform_step", "ValueError: Invalid column", layer="transform")

    # Log cache hits
    logger.log_cache_hit("transform_step", cache_key="abc123")
"""

import json
import logging
import psutil
from enum import Enum
from typing import Any, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class LogLevel(str, Enum):
    """Log levels for structured logging"""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class StructuredLogEntry:
    """
    Structured log entry with standard fields.

    Attributes:
        timestamp: ISO format timestamp
        level: Log level (info, error, etc.)
        event_type: Type of event (node_start, node_complete, error, etc.)
        message: Human-readable message
        node_name: Name of the node (if applicable)
        layer: Pipeline layer (if applicable)
        engine: Engine type (pandas, spark)
        status: Node status (pending, running, success, failed)
        duration_ms: Execution duration in milliseconds
        error: Error message (if applicable)
        cache_hit: Whether cache was hit
        row_count: Number of rows processed
        memory_mb: Memory usage in MB
        user: User identifier
        metadata: Additional metadata
    """

    timestamp: str
    level: str
    event_type: str
    message: str
    node_name: Optional[str] = None
    layer: Optional[str] = None
    engine: Optional[str] = None
    status: Optional[str] = None
    duration_ms: Optional[float] = None
    error: Optional[str] = None
    cache_hit: Optional[bool] = None
    row_count: Optional[int] = None
    memory_mb: Optional[float] = None
    user: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class StructuredLogger:
    """
    Structured logger for DAG execution events.

    Writes JSON Lines format to disk for easy querying and analysis.
    Integrates with Tracker, DAGExecutor, and EventBus.

    Attributes:
        name: Logger name (e.g., pipeline name)
        log_dir: Directory for log files
        log_file: Path to current log file
        max_file_size_mb: Maximum log file size before rotation
        user: User identifier for all log entries
    """

    def __init__(
        self,
        name: str,
        log_dir: str = "logs",
        max_file_size_mb: int = 100,
        user: Optional[str] = None,
    ):
        """
        Initialize structured logger.

        Args:
            name: Logger name (used in filename)
            log_dir: Directory for log files
            max_file_size_mb: Maximum file size before rotation
            user: User identifier for all entries
        """
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.max_file_size_mb = max_file_size_mb
        self.user = user

        # Create log file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"{name}_{timestamp}.jsonl"

        # Touch the file to ensure it exists
        self.log_file.touch()

        logger.info(f"StructuredLogger initialized: {self.log_file}")

    def _write_entry(self, entry: StructuredLogEntry) -> None:
        """
        Write log entry to file.

        Args:
            entry: StructuredLogEntry to write
        """
        # Check file size and rotate if needed
        if self.log_file.exists():
            file_size_mb = self.log_file.stat().st_size / (1024 * 1024)
            if file_size_mb >= self.max_file_size_mb:
                self._rotate_log()

        # Write JSON line
        with open(self.log_file, "a") as f:
            json.dump(asdict(entry), f)
            f.write("\n")

    def _rotate_log(self) -> None:
        """Rotate log file when max size reached."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_log_file = self.log_dir / f"{self.name}_{timestamp}.jsonl"

        logger.info(f"Rotating log file: {self.log_file} → {new_log_file}")
        self.log_file = new_log_file

    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        try:
            process = psutil.Process()
            return process.memory_info().rss / (1024 * 1024)
        except:
            return 0.0

    def log(self, level: LogLevel, event_type: str, message: str, **kwargs) -> None:
        """
        Log a structured event.

        Args:
            level: Log level
            event_type: Type of event
            message: Human-readable message
            **kwargs: Additional fields (node_name, layer, etc.)
        """
        entry = StructuredLogEntry(
            timestamp=datetime.now().isoformat(),
            level=level.value,
            event_type=event_type,
            message=message,
            user=self.user,
            memory_mb=self._get_memory_usage(),
            **kwargs,
        )

        self._write_entry(entry)

        # Also log to Python logger
        py_logger = logging.getLogger(self.name)
        log_method = getattr(py_logger, level.value, py_logger.info)
        log_method(f"[{event_type}] {message}")

    def log_node_start(
        self,
        node_name: str,
        layer: str,
        engine: str = "pandas",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log node execution start.

        Args:
            node_name: Name of the node
            layer: Pipeline layer
            engine: Engine type (pandas, spark)
            metadata: Additional metadata
        """
        self.log(
            LogLevel.INFO,
            "node_start",
            f"Node '{node_name}' started",
            node_name=node_name,
            layer=layer,
            engine=engine,
            status="running",
            metadata=metadata,
        )

    def log_node_complete(
        self,
        node_name: str,
        duration_ms: float,
        rows: Optional[int] = None,
        cache_hit: bool = False,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log node execution completion.

        Args:
            node_name: Name of the node
            duration_ms: Execution duration in milliseconds
            rows: Number of rows processed
            cache_hit: Whether cache was hit
            metadata: Additional metadata
        """
        self.log(
            LogLevel.INFO,
            "node_complete",
            f"Node '{node_name}' completed in {duration_ms:.2f}ms",
            node_name=node_name,
            status="success",
            duration_ms=duration_ms,
            row_count=rows,
            cache_hit=cache_hit,
            metadata=metadata,
        )

    def log_node_failed(
        self,
        node_name: str,
        error: str,
        duration_ms: Optional[float] = None,
        layer: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log node execution failure.

        Args:
            node_name: Name of the node
            error: Error message
            duration_ms: Execution duration before failure
            layer: Pipeline layer
            metadata: Additional metadata
        """
        self.log(
            LogLevel.ERROR,
            "node_failed",
            f"Node '{node_name}' failed: {error}",
            node_name=node_name,
            layer=layer,
            status="failed",
            error=error,
            duration_ms=duration_ms,
            metadata=metadata,
        )

    def log_error(
        self,
        component: str,
        error: str,
        layer: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log general error.

        Args:
            component: Component where error occurred
            error: Error message
            layer: Pipeline layer
            metadata: Additional metadata
        """
        self.log(
            LogLevel.ERROR,
            "error",
            f"Error in {component}: {error}",
            node_name=component,
            layer=layer,
            error=error,
            metadata=metadata,
        )

    def log_cache_hit(
        self, node_name: str, cache_key: str, metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log cache hit event.

        Args:
            node_name: Name of the node
            cache_key: Cache key that was hit
            metadata: Additional metadata
        """
        self.log(
            LogLevel.INFO,
            "cache_hit",
            f"Cache hit for '{node_name}' (key: {cache_key[:16]}...)",
            node_name=node_name,
            cache_hit=True,
            metadata={**(metadata or {}), "cache_key": cache_key},
        )

    def log_cache_miss(
        self, node_name: str, cache_key: str, metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log cache miss event.

        Args:
            node_name: Name of the node
            cache_key: Cache key that was missed
            metadata: Additional metadata
        """
        self.log(
            LogLevel.DEBUG,
            "cache_miss",
            f"Cache miss for '{node_name}' (key: {cache_key[:16]}...)",
            node_name=node_name,
            cache_hit=False,
            metadata={**(metadata or {}), "cache_key": cache_key},
        )

    def log_pipeline_start(
        self, pipeline_name: str, metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log pipeline execution start.

        Args:
            pipeline_name: Name of the pipeline
            metadata: Additional metadata
        """
        self.log(
            LogLevel.INFO,
            "pipeline_start",
            f"Pipeline '{pipeline_name}' started",
            metadata={**(metadata or {}), "pipeline_name": pipeline_name},
        )

    def log_pipeline_complete(
        self,
        pipeline_name: str,
        duration_ms: float,
        success_count: int,
        failed_count: int,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log pipeline execution completion.

        Args:
            pipeline_name: Name of the pipeline
            duration_ms: Total execution duration
            success_count: Number of successful nodes
            failed_count: Number of failed nodes
            metadata: Additional metadata
        """
        self.log(
            LogLevel.INFO,
            "pipeline_complete",
            f"Pipeline '{pipeline_name}' completed in {duration_ms:.2f}ms "
            f"(success: {success_count}, failed: {failed_count})",
            status="success" if failed_count == 0 else "partial_failure",
            duration_ms=duration_ms,
            metadata={
                **(metadata or {}),
                "pipeline_name": pipeline_name,
                "success_count": success_count,
                "failed_count": failed_count,
            },
        )

    def log_checkpoint_created(
        self,
        checkpoint_id: str,
        nodes_completed: int,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log checkpoint creation.

        Args:
            checkpoint_id: Checkpoint identifier
            nodes_completed: Number of nodes completed
            metadata: Additional metadata
        """
        self.log(
            LogLevel.INFO,
            "checkpoint_created",
            f"Checkpoint '{checkpoint_id}' created ({nodes_completed} nodes completed)",
            metadata={
                **(metadata or {}),
                "checkpoint_id": checkpoint_id,
                "nodes_completed": nodes_completed,
            },
        )

    def query_logs(
        self,
        event_type: Optional[str] = None,
        node_name: Optional[str] = None,
        level: Optional[LogLevel] = None,
        limit: int = 100,
    ) -> list:
        """
        Query log entries.

        Args:
            event_type: Filter by event type
            node_name: Filter by node name
            level: Filter by log level
            limit: Maximum results to return

        Returns:
            List of matching log entries as dictionaries
        """
        results = []

        if not self.log_file.exists():
            return results

        with open(self.log_file, "r") as f:
            for line in f:
                try:
                    entry = json.loads(line)

                    # Apply filters
                    if event_type and entry.get("event_type") != event_type:
                        continue
                    if node_name and entry.get("node_name") != node_name:
                        continue
                    if level and entry.get("level") != level.value:
                        continue

                    results.append(entry)

                    if len(results) >= limit:
                        break

                except json.JSONDecodeError:
                    continue

        return results

    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary of all log entries.

        Returns:
            Dictionary with log statistics
        """
        if not self.log_file.exists():
            return {}

        total_entries = 0
        by_level = {}
        by_event_type = {}
        errors = []

        with open(self.log_file, "r") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    total_entries += 1

                    # Count by level
                    level = entry.get("level", "unknown")
                    by_level[level] = by_level.get(level, 0) + 1

                    # Count by event type
                    event_type = entry.get("event_type", "unknown")
                    by_event_type[event_type] = by_event_type.get(event_type, 0) + 1

                    # Collect errors
                    if level in ("error", "critical"):
                        errors.append(
                            {
                                "timestamp": entry.get("timestamp"),
                                "node_name": entry.get("node_name"),
                                "error": entry.get("error"),
                            }
                        )

                except json.JSONDecodeError:
                    continue

        return {
            "log_file": str(self.log_file),
            "total_entries": total_entries,
            "by_level": by_level,
            "by_event_type": by_event_type,
            "errors": errors[:10],  # Last 10 errors
            "file_size_mb": (
                self.log_file.stat().st_size / (1024 * 1024)
                if self.log_file.exists()
                else 0
            ),
        }
