"""
Metrics Exporter (Phase 8)

Export metrics in various formats (Prometheus, JSON, Parquet) for external consumption.

Features:
- Prometheus text format for scraping
- JSON export for dashboards
- Parquet export for long-term storage
- Per-node metrics aggregation
- Cache hit rate calculation
- Memory usage tracking (simulated)

Usage:
    from odibi_core.metrics import MetricsManager, MetricType
    from odibi_core.observability import MetricsExporter

    metrics = MetricsManager()
    # ... record metrics ...

    exporter = MetricsExporter(metrics)

    # Export to Prometheus format
    prom_text = exporter.export_prometheus()
    exporter.save_prometheus("metrics.prom")

    # Export to JSON
    json_data = exporter.export_json()
    exporter.save_json("metrics.json")

    # Export to Parquet
    exporter.save_parquet("metrics.parquet")
"""

import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class MetricsExporter:
    """
    Export metrics from MetricsManager to various formats.

    Supports:
    - Prometheus text format (for scraping)
    - JSON (for dashboards and APIs)
    - Parquet (for long-term storage)

    Attributes:
        metrics_manager: MetricsManager instance to export from
    """

    def __init__(self, metrics_manager: Any):
        """
        Initialize metrics exporter.

        Args:
            metrics_manager: MetricsManager instance
        """
        self.metrics_manager = metrics_manager

    def export_prometheus(self, include_help: bool = True) -> str:
        """
        Export metrics in Prometheus text format.

        Args:
            include_help: Include HELP and TYPE comments

        Returns:
            Prometheus-formatted metrics string

        Example:
            >>> exporter = MetricsExporter(metrics)
            >>> prom_text = exporter.export_prometheus()
            >>> print(prom_text)
        """
        lines = []

        # Add header
        if include_help:
            lines.append("# ODIBI CORE Metrics Export")
            lines.append(f"# Generated: {datetime.now().isoformat()}")
            lines.append("")

        # Get summary
        summary = self.metrics_manager.get_summary()

        # Export node duration metrics
        if include_help:
            lines.append(
                "# HELP odibi_node_duration_ms Node execution duration in milliseconds"
            )
            lines.append("# TYPE odibi_node_duration_ms gauge")

        for metric in self.metrics_manager.metrics:
            if metric.metric_type == "node_duration_ms":
                labels = self._format_prometheus_labels(metric.name, metric.labels)
                lines.append(f"odibi_node_duration_ms{labels} {metric.value}")

        lines.append("")

        # Export throughput metrics
        if include_help:
            lines.append(
                "# HELP odibi_throughput_rows_per_sec Data throughput in rows per second"
            )
            lines.append("# TYPE odibi_throughput_rows_per_sec gauge")

        for metric in self.metrics_manager.metrics:
            if metric.metric_type == "throughput_rows_per_sec":
                labels = self._format_prometheus_labels(metric.name, metric.labels)
                lines.append(f"odibi_throughput_rows_per_sec{labels} {metric.value}")

        lines.append("")

        # Export cache hit/miss counters
        cache_hits = sum(
            1 for m in self.metrics_manager.metrics if m.metric_type == "cache_hit"
        )
        cache_misses = sum(
            1 for m in self.metrics_manager.metrics if m.metric_type == "cache_miss"
        )

        if include_help:
            lines.append("# HELP odibi_cache_hits_total Total cache hits")
            lines.append("# TYPE odibi_cache_hits_total counter")
        lines.append(f"odibi_cache_hits_total {cache_hits}")

        if include_help:
            lines.append("# HELP odibi_cache_misses_total Total cache misses")
            lines.append("# TYPE odibi_cache_misses_total counter")
        lines.append(f"odibi_cache_misses_total {cache_misses}")

        # Cache hit rate
        cache_hit_rate = self.metrics_manager.get_cache_hit_rate()
        if include_help:
            lines.append(
                "# HELP odibi_cache_hit_rate Cache hit rate percentage (0-100)"
            )
            lines.append("# TYPE odibi_cache_hit_rate gauge")
        lines.append(f"odibi_cache_hit_rate {cache_hit_rate:.2f}")

        lines.append("")

        # Export error count
        error_count = sum(
            m.value
            for m in self.metrics_manager.metrics
            if m.metric_type == "error_count"
        )

        if include_help:
            lines.append("# HELP odibi_errors_total Total errors")
            lines.append("# TYPE odibi_errors_total counter")
        lines.append(f"odibi_errors_total {error_count}")

        lines.append("")

        # Export uptime
        uptime = summary.get("uptime_seconds", 0)
        if include_help:
            lines.append("# HELP odibi_uptime_seconds Uptime in seconds")
            lines.append("# TYPE odibi_uptime_seconds gauge")
        lines.append(f"odibi_uptime_seconds {uptime:.2f}")

        lines.append("")

        # Export total metrics
        if include_help:
            lines.append("# HELP odibi_metrics_total Total metrics recorded")
            lines.append("# TYPE odibi_metrics_total counter")
        lines.append(f'odibi_metrics_total {summary.get("total_metrics", 0)}')

        return "\n".join(lines)

    def _format_prometheus_labels(
        self, name: str, labels: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Format Prometheus labels.

        Args:
            name: Metric name (used as 'node' label)
            labels: Additional labels

        Returns:
            Formatted label string like {node="name",engine="pandas"}
        """
        all_labels = {"node": name}
        if labels:
            all_labels.update(labels)

        label_pairs = [f'{k}="{v}"' for k, v in all_labels.items()]
        return "{" + ",".join(label_pairs) + "}"

    def export_json(self, pretty: bool = True) -> str:
        """
        Export metrics in JSON format.

        Args:
            pretty: Pretty-print JSON with indentation

        Returns:
            JSON string

        Example:
            >>> exporter = MetricsExporter(metrics)
            >>> json_data = exporter.export_json()
        """
        summary = self.metrics_manager.get_summary()

        # Organize metrics by node
        by_node = {}
        for metric in self.metrics_manager.metrics:
            node_name = metric.name
            if node_name not in by_node:
                by_node[node_name] = {"node_name": node_name, "metrics": []}

            by_node[node_name]["metrics"].append(
                {
                    "type": metric.metric_type,
                    "value": metric.value,
                    "timestamp": metric.timestamp,
                    "labels": metric.labels,
                }
            )

        # Build export structure
        export_data = {
            "export_time": datetime.now().isoformat(),
            "summary": {
                "total_metrics": summary.get("total_metrics", 0),
                "uptime_seconds": summary.get("uptime_seconds", 0),
                "cache_hit_rate": self.metrics_manager.get_cache_hit_rate(),
                "error_rate": self.metrics_manager.get_error_rate(),
                "avg_throughput": self.metrics_manager.get_avg_throughput(),
            },
            "aggregations": summary.get("aggregations", {}),
            "by_node": list(by_node.values()),
            "counters": summary.get("counters", {}),
            "gauges": summary.get("gauges", {}),
        }

        indent = 2 if pretty else None
        return json.dumps(export_data, indent=indent)

    def export_dataframe(self) -> Any:
        """
        Export metrics as Pandas DataFrame.

        Returns:
            Pandas DataFrame with all metrics

        Example:
            >>> df = exporter.export_dataframe()
            >>> df.to_parquet("metrics.parquet")
        """
        import pandas as pd

        data = []
        for metric in self.metrics_manager.metrics:
            row = {
                "metric_type": metric.metric_type,
                "name": metric.name,
                "value": metric.value,
                "timestamp": datetime.fromtimestamp(metric.timestamp),
            }

            # Add labels as columns
            if metric.labels:
                for key, value in metric.labels.items():
                    row[f"label_{key}"] = value

            data.append(row)

        return pd.DataFrame(data)

    def save_prometheus(self, filepath: str) -> None:
        """
        Save metrics in Prometheus text format.

        Args:
            filepath: Output file path

        Example:
            >>> exporter.save_prometheus("metrics/odibi.prom")
        """
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)

        content = self.export_prometheus()

        with open(filepath, "w") as f:
            f.write(content)

        logger.info(f"Prometheus metrics saved to {filepath}")

    def save_json(self, filepath: str, pretty: bool = True) -> None:
        """
        Save metrics in JSON format.

        Args:
            filepath: Output file path
            pretty: Pretty-print JSON

        Example:
            >>> exporter.save_json("metrics/odibi_metrics.json")
        """
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)

        content = self.export_json(pretty=pretty)

        with open(filepath, "w") as f:
            f.write(content)

        logger.info(f"JSON metrics saved to {filepath}")

    def save_parquet(self, filepath: str) -> None:
        """
        Save metrics in Parquet format.

        Args:
            filepath: Output file path

        Example:
            >>> exporter.save_parquet("metrics/odibi_metrics.parquet")
        """
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)

        df = self.export_dataframe()
        df.to_parquet(filepath, index=False)

        logger.info(f"Parquet metrics saved to {filepath} ({len(df)} rows)")

    def get_node_summary(self, node_name: str) -> Dict[str, Any]:
        """
        Get summary statistics for a specific node.

        Args:
            node_name: Name of the node

        Returns:
            Dictionary with node statistics

        Example:
            >>> summary = exporter.get_node_summary("read_data")
            >>> print(f"Avg duration: {summary['avg_duration_ms']}ms")
        """
        node_metrics = self.metrics_manager.get_metrics_by_name(node_name)

        if not node_metrics:
            return {}

        # Calculate statistics
        durations = [
            m.value for m in node_metrics if m.metric_type == "node_duration_ms"
        ]
        throughputs = [
            m.value for m in node_metrics if m.metric_type == "throughput_rows_per_sec"
        ]

        summary = {
            "node_name": node_name,
            "total_executions": len(
                [m for m in node_metrics if m.metric_type == "node_duration_ms"]
            ),
            "avg_duration_ms": sum(durations) / len(durations) if durations else 0,
            "min_duration_ms": min(durations) if durations else 0,
            "max_duration_ms": max(durations) if durations else 0,
            "avg_throughput": sum(throughputs) / len(throughputs) if throughputs else 0,
        }

        return summary

    def generate_report(self) -> str:
        """
        Generate human-readable metrics report.

        Returns:
            Formatted report string

        Example:
            >>> print(exporter.generate_report())
        """
        summary = self.metrics_manager.get_summary()

        lines = [
            "=" * 70,
            "ODIBI CORE Metrics Report",
            "=" * 70,
            f"Generated: {datetime.now().isoformat()}",
            f"Uptime: {summary.get('uptime_seconds', 0):.2f}s",
            f"Total Metrics: {summary.get('total_metrics', 0)}",
            "",
            "Summary Statistics:",
            "-" * 70,
            f"Cache Hit Rate: {self.metrics_manager.get_cache_hit_rate():.1f}%",
            f"Error Rate: {self.metrics_manager.get_error_rate():.1f}%",
            f"Avg Throughput: {self.metrics_manager.get_avg_throughput():.2f} rows/sec",
            "",
        ]

        # Per-node statistics
        nodes = set(m.name for m in self.metrics_manager.metrics)
        if nodes:
            lines.append("Per-Node Statistics:")
            lines.append("-" * 70)

            for node in sorted(nodes):
                node_summary = self.get_node_summary(node)
                if node_summary:
                    lines.append(
                        f"{node:<30} "
                        f"Avg: {node_summary['avg_duration_ms']:>8.2f}ms  "
                        f"Executions: {node_summary['total_executions']:>3}"
                    )

        lines.append("=" * 70)

        return "\n".join(lines)
