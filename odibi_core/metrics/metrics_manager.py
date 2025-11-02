"""
Metrics Manager (Phase 7 + Phase 8 enhancements)

Collects and exports metrics for distributed DAG execution.

Features:
- Node-level execution metrics (duration, throughput, error rate)
- DAG-level aggregated metrics
- Cache hit/miss tracking
- Memory usage tracking (Phase 8)
- Per-node success/failure tracking (Phase 8)
- Export to JSON, Prometheus format
- Integration with Phase 6 Tracker and Phase 8 Observability

Usage:
    from odibi_core.metrics import MetricsManager, MetricType

    metrics = MetricsManager()

    # Record metrics
    metrics.record(MetricType.NODE_DURATION, "read_data", 1250.5)
    metrics.record(MetricType.THROUGHPUT, "read_data", 10000)  # rows/sec
    metrics.increment(MetricType.CACHE_HIT, "transform_step")
    metrics.record_memory_usage("transform_step", 256.5)  # MB

    # Export metrics
    summary = metrics.get_summary()
    prometheus_text = metrics.export_prometheus()
    metrics.save_to_file("metrics.json")
"""

import logging
import json
import time
from enum import Enum
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from collections import defaultdict
from pathlib import Path

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Supported metric types"""

    NODE_DURATION = "node_duration_ms"  # Node execution time
    THROUGHPUT = "throughput_rows_per_sec"  # Data throughput
    CACHE_HIT = "cache_hit"  # Cache hit count
    CACHE_MISS = "cache_miss"  # Cache miss count
    ERROR_COUNT = "error_count"  # Error count
    RETRY_COUNT = "retry_count"  # Retry count
    CHECKPOINT_SIZE = "checkpoint_size_bytes"  # Checkpoint size
    DATA_SIZE = "data_size_bytes"  # Data size
    WORKER_UTILIZATION = "worker_utilization_pct"  # Worker utilization
    MEMORY_USAGE = "memory_usage_mb"  # Memory usage in MB
    SUCCESS_COUNT = "success_count"  # Success count
    FAILURE_COUNT = "failure_count"  # Failure count


@dataclass
class Metric:
    """
    Individual metric record.

    Attributes:
        metric_type: Type of metric
        name: Metric name (e.g., node name)
        value: Metric value
        timestamp: When metric was recorded
        labels: Additional labels (e.g., {"layer": "bronze", "engine": "pandas"})
    """

    metric_type: str
    name: str
    value: float
    timestamp: float
    labels: Dict[str, str]


class MetricsManager:
    """
    Metrics manager for distributed DAG execution observability.

    Collects, aggregates, and exports metrics for:
    - Node execution performance
    - Data throughput
    - Cache efficiency
    - Error rates
    - Resource utilization

    Attributes:
        metrics: List of recorded metrics
        counters: Counter-type metrics (increment only)
        gauges: Gauge-type metrics (current value)
    """

    def __init__(self):
        """Initialize metrics manager"""
        self.metrics: List[Metric] = []
        self.counters: Dict[str, float] = defaultdict(float)
        self.gauges: Dict[str, float] = {}
        self.start_time = time.time()

    def record(
        self,
        metric_type: MetricType,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None,
    ):
        """
        Record a metric value.

        Args:
            metric_type: Type of metric
            name: Metric name (e.g., node name, DAG name)
            value: Metric value
            labels: Additional labels
        """
        metric = Metric(
            metric_type=metric_type.value,
            name=name,
            value=value,
            timestamp=time.time(),
            labels=labels or {},
        )

        self.metrics.append(metric)

        # Update gauge if applicable
        gauge_key = f"{metric_type.value}:{name}"
        self.gauges[gauge_key] = value

        logger.debug(f"Recorded metric: {metric_type.value} = {value} for {name}")

    def increment(
        self,
        metric_type: MetricType,
        name: str,
        value: float = 1.0,
        labels: Optional[Dict[str, str]] = None,
    ):
        """
        Increment a counter metric.

        Args:
            metric_type: Type of metric
            name: Metric name
            value: Increment value (default 1.0)
            labels: Additional labels
        """
        counter_key = f"{metric_type.value}:{name}"
        self.counters[counter_key] += value

        # Also record as metric for time-series tracking
        self.record(metric_type, name, self.counters[counter_key], labels)

        logger.debug(f"Incremented counter: {metric_type.value} += {value} for {name}")

    def set_gauge(
        self,
        metric_type: MetricType,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None,
    ):
        """
        Set a gauge metric (current value).

        Args:
            metric_type: Type of metric
            name: Metric name
            value: Current value
            labels: Additional labels
        """
        gauge_key = f"{metric_type.value}:{name}"
        self.gauges[gauge_key] = value

        # Also record as metric
        self.record(metric_type, name, value, labels)

        logger.debug(f"Set gauge: {metric_type.value} = {value} for {name}")

    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary of all metrics.

        Returns:
            Dictionary with aggregated metrics
        """
        summary = {
            "total_metrics": len(self.metrics),
            "uptime_seconds": time.time() - self.start_time,
            "timestamp": datetime.now().isoformat(),
            "counters": dict(self.counters),
            "gauges": dict(self.gauges),
            "aggregations": self._compute_aggregations(),
        }

        return summary

    def _compute_aggregations(self) -> Dict[str, Any]:
        """Compute aggregated statistics"""
        aggregations = {}

        # Group metrics by type
        by_type = defaultdict(list)
        for metric in self.metrics:
            by_type[metric.metric_type].append(metric.value)

        # Compute stats for each type
        for metric_type, values in by_type.items():
            if not values:
                continue

            aggregations[metric_type] = {
                "count": len(values),
                "sum": sum(values),
                "min": min(values),
                "max": max(values),
                "avg": sum(values) / len(values),
            }

        return aggregations

    def get_metrics_by_type(self, metric_type: MetricType) -> List[Metric]:
        """Get all metrics of a specific type"""
        return [m for m in self.metrics if m.metric_type == metric_type.value]

    def get_metrics_by_name(self, name: str) -> List[Metric]:
        """Get all metrics for a specific name (e.g., node name)"""
        return [m for m in self.metrics if m.name == name]

    def export_prometheus(self) -> str:
        """
        Export metrics in Prometheus text format.

        Returns:
            Prometheus-formatted metrics string
        """
        lines = []

        # Add header
        lines.append("# ODIBI CORE Metrics")
        lines.append(f"# Timestamp: {datetime.now().isoformat()}")
        lines.append("")

        # Export counters
        for counter_key, value in self.counters.items():
            metric_type, name = counter_key.split(":", 1)
            metric_name = f"odibi_{metric_type}"
            lines.append(f"# TYPE {metric_name} counter")
            lines.append(f'{metric_name}{{name="{name}"}} {value}')

        lines.append("")

        # Export gauges
        for gauge_key, value in self.gauges.items():
            metric_type, name = gauge_key.split(":", 1)
            metric_name = f"odibi_{metric_type}"
            lines.append(f"# TYPE {metric_name} gauge")
            lines.append(f'{metric_name}{{name="{name}"}} {value}')

        lines.append("")

        # Add uptime
        lines.append("# TYPE odibi_uptime_seconds gauge")
        lines.append(f"odibi_uptime_seconds {time.time() - self.start_time}")

        return "\n".join(lines)

    def export_json(self) -> str:
        """
        Export metrics in JSON format.

        Returns:
            JSON-formatted metrics string
        """
        data = {
            "summary": self.get_summary(),
            "metrics": [asdict(m) for m in self.metrics],
        }

        return json.dumps(data, indent=2)

    def save_to_file(self, filepath: str, format: str = "json"):
        """
        Save metrics to file.

        Args:
            filepath: Output file path
            format: Output format ("json" or "prometheus")
        """
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)

        if format == "json":
            content = self.export_json()
        elif format == "prometheus":
            content = self.export_prometheus()
        else:
            raise ValueError(f"Unsupported format: {format}")

        with open(filepath, "w") as f:
            f.write(content)

        logger.info(f"Metrics saved to {filepath} ({format} format)")

    def reset(self):
        """Reset all metrics"""
        self.metrics.clear()
        self.counters.clear()
        self.gauges.clear()
        self.start_time = time.time()
        logger.info("Metrics reset")

    def get_cache_hit_rate(self) -> float:
        """
        Calculate cache hit rate.

        Returns:
            Cache hit rate as percentage (0-100)
        """
        hits = sum(
            1 for m in self.metrics if m.metric_type == MetricType.CACHE_HIT.value
        )
        misses = sum(
            1 for m in self.metrics if m.metric_type == MetricType.CACHE_MISS.value
        )

        total = hits + misses
        if total == 0:
            return 0.0

        return (hits / total) * 100

    def get_error_rate(self) -> float:
        """
        Calculate error rate.

        Returns:
            Error rate as percentage of total node executions
        """
        errors = sum(
            m.value
            for m in self.metrics
            if m.metric_type == MetricType.ERROR_COUNT.value
        )

        total_nodes = len(set(m.name for m in self.metrics))

        if total_nodes == 0:
            return 0.0

        return (errors / total_nodes) * 100

    def get_avg_throughput(self) -> float:
        """
        Calculate average data throughput.

        Returns:
            Average throughput in rows/second
        """
        throughput_metrics = self.get_metrics_by_type(MetricType.THROUGHPUT)

        if not throughput_metrics:
            return 0.0

        total = sum(m.value for m in throughput_metrics)
        return total / len(throughput_metrics)

    def record_memory_usage(self, name: str, memory_mb: float) -> None:
        """
        Record memory usage for a component.

        Args:
            name: Component name
            memory_mb: Memory usage in MB
        """
        self.record(MetricType.MEMORY_USAGE, name, memory_mb)

    def record_node_execution(
        self,
        node_name: str,
        duration_ms: float,
        success: bool,
        engine: str = "pandas",
        rows: Optional[int] = None,
        cached: bool = False,
    ) -> None:
        """
        Record comprehensive node execution metrics.

        Args:
            node_name: Name of the node
            duration_ms: Execution duration in milliseconds
            success: Whether execution succeeded
            engine: Engine type (pandas, spark)
            rows: Number of rows processed
            cached: Whether result was from cache
        """
        labels = {"engine": engine}

        # Record duration
        self.record(MetricType.NODE_DURATION, node_name, duration_ms, labels)

        # Record success/failure
        if success:
            self.increment(MetricType.SUCCESS_COUNT, node_name, labels=labels)
        else:
            self.increment(MetricType.FAILURE_COUNT, node_name, labels=labels)
            self.increment(MetricType.ERROR_COUNT, node_name, labels=labels)

        # Record cache hit/miss
        if cached:
            self.increment(MetricType.CACHE_HIT, node_name, labels=labels)
        else:
            self.increment(MetricType.CACHE_MISS, node_name, labels=labels)

        # Record throughput if rows provided
        if rows and duration_ms > 0:
            rows_per_sec = (rows / duration_ms) * 1000
            self.record(MetricType.THROUGHPUT, node_name, rows_per_sec, labels)

    def get_node_stats(self, node_name: str) -> Dict[str, Any]:
        """
        Get statistics for a specific node.

        Args:
            node_name: Name of the node

        Returns:
            Dictionary with node statistics
        """
        node_metrics = self.get_metrics_by_name(node_name)

        if not node_metrics:
            return {}

        durations = [
            m.value
            for m in node_metrics
            if m.metric_type == MetricType.NODE_DURATION.value
        ]

        success_key = f"{MetricType.SUCCESS_COUNT.value}:{node_name}"
        failure_key = f"{MetricType.FAILURE_COUNT.value}:{node_name}"

        return {
            "node_name": node_name,
            "executions": len(durations),
            "avg_duration_ms": sum(durations) / len(durations) if durations else 0,
            "min_duration_ms": min(durations) if durations else 0,
            "max_duration_ms": max(durations) if durations else 0,
            "success_count": self.counters.get(success_key, 0),
            "failure_count": self.counters.get(failure_key, 0),
        }
