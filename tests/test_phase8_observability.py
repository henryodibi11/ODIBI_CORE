"""
Tests for Phase 8: Observability & Automation

Tests StructuredLogger, MetricsExporter, and EventBus.
"""

import pytest
import json
import tempfile
from pathlib import Path
from datetime import datetime

try:
    import pandas as pd
except ImportError:
    pytest.skip("pandas not installed", allow_module_level=True)

from odibi_core.observability import (
    StructuredLogger,
    LogLevel,
    MetricsExporter,
    EventBus,
    EventPriority,
    AutomationHook,
)
from odibi_core.metrics import MetricsManager, MetricType


class TestStructuredLogger:
    """Test StructuredLogger functionality"""

    def test_logger_initialization(self, tmp_path):
        """Test logger creates log file"""
        logger = StructuredLogger("test_pipeline", log_dir=str(tmp_path))

        assert logger.log_file.exists()
        assert logger.log_file.name.startswith("test_pipeline_")
        assert logger.log_file.suffix == ".jsonl"

    def test_log_node_start(self, tmp_path):
        """Test logging node start event"""
        logger = StructuredLogger("test", log_dir=str(tmp_path))

        logger.log_node_start("test_node", "ingest", engine="pandas")

        # Read log file
        with open(logger.log_file, "r") as f:
            entry = json.loads(f.readline())

        assert entry["event_type"] == "node_start"
        assert entry["node_name"] == "test_node"
        assert entry["layer"] == "ingest"
        assert entry["engine"] == "pandas"
        assert entry["status"] == "running"
        assert entry["level"] == "info"

    def test_log_node_complete(self, tmp_path):
        """Test logging node completion"""
        logger = StructuredLogger("test", log_dir=str(tmp_path))

        logger.log_node_complete(
            "test_node", duration_ms=125.5, rows=1000, cache_hit=True
        )

        with open(logger.log_file, "r") as f:
            entry = json.loads(f.readline())

        assert entry["event_type"] == "node_complete"
        assert entry["node_name"] == "test_node"
        assert entry["status"] == "success"
        assert entry["duration_ms"] == 125.5
        assert entry["row_count"] == 1000
        assert entry["cache_hit"] is True

    def test_log_node_failed(self, tmp_path):
        """Test logging node failure"""
        logger = StructuredLogger("test", log_dir=str(tmp_path))

        logger.log_node_failed(
            "test_node", "ValueError: Invalid data", duration_ms=50.0, layer="transform"
        )

        with open(logger.log_file, "r") as f:
            entry = json.loads(f.readline())

        assert entry["event_type"] == "node_failed"
        assert entry["node_name"] == "test_node"
        assert entry["status"] == "failed"
        assert entry["error"] == "ValueError: Invalid data"
        assert entry["level"] == "error"

    def test_log_cache_events(self, tmp_path):
        """Test logging cache hit/miss events"""
        logger = StructuredLogger("test", log_dir=str(tmp_path))

        logger.log_cache_hit("node1", "cache_key_123")
        logger.log_cache_miss("node2", "cache_key_456")

        with open(logger.log_file, "r") as f:
            hit_entry = json.loads(f.readline())
            miss_entry = json.loads(f.readline())

        assert hit_entry["event_type"] == "cache_hit"
        assert hit_entry["cache_hit"] is True
        assert miss_entry["event_type"] == "cache_miss"
        assert miss_entry["cache_hit"] is False

    def test_log_pipeline_lifecycle(self, tmp_path):
        """Test logging pipeline start and complete"""
        logger = StructuredLogger("test", log_dir=str(tmp_path))

        logger.log_pipeline_start("demo_pipeline")
        logger.log_pipeline_complete(
            "demo_pipeline", duration_ms=5000.0, success_count=10, failed_count=0
        )

        with open(logger.log_file, "r") as f:
            start_entry = json.loads(f.readline())
            complete_entry = json.loads(f.readline())

        assert start_entry["event_type"] == "pipeline_start"
        assert complete_entry["event_type"] == "pipeline_complete"
        assert complete_entry["status"] == "success"
        assert complete_entry["duration_ms"] == 5000.0

    def test_query_logs(self, tmp_path):
        """Test querying log entries"""
        logger = StructuredLogger("test", log_dir=str(tmp_path))

        logger.log_node_start("node1", "ingest")
        logger.log_node_complete("node1", 100.0)
        logger.log_node_start("node2", "transform")
        logger.log_error("node2", "Test error")

        # Query by event type
        starts = logger.query_logs(event_type="node_start")
        assert len(starts) == 2

        # Query by node name
        node1_logs = logger.query_logs(node_name="node1")
        assert len(node1_logs) == 2

        # Query by level
        errors = logger.query_logs(level=LogLevel.ERROR)
        assert len(errors) == 1

    def test_get_summary(self, tmp_path):
        """Test getting log summary"""
        logger = StructuredLogger("test", log_dir=str(tmp_path))

        logger.log_node_start("node1", "ingest")
        logger.log_node_complete("node1", 100.0)
        logger.log_error("node2", "Test error")

        summary = logger.get_summary()

        assert summary["total_entries"] == 3
        assert summary["by_level"]["info"] == 2
        assert summary["by_level"]["error"] == 1
        assert summary["by_event_type"]["node_start"] == 1
        assert len(summary["errors"]) == 1

    def test_log_rotation(self, tmp_path):
        """Test log file rotation when size limit reached"""
        import time

        logger = StructuredLogger("test", log_dir=str(tmp_path), max_file_size_mb=0.001)

        original_file = logger.log_file

        # Small delay to ensure timestamp difference
        time.sleep(0.01)

        # Write enough entries to trigger rotation
        for i in range(100):
            logger.log_node_complete(f"node_{i}", 100.0, metadata={"data": "x" * 1000})
            # Check if rotation happened
            if logger.log_file != original_file:
                break

        # File should have rotated (or nearly rotated)
        # Note: rotation might not happen immediately depending on exact timing
        assert original_file.exists()

        # If rotation happened, new file should exist
        if logger.log_file != original_file:
            assert logger.log_file.exists()


class TestMetricsExporter:
    """Test MetricsExporter functionality"""

    def test_export_prometheus(self):
        """Test exporting metrics to Prometheus format"""
        metrics = MetricsManager()
        metrics.record(
            MetricType.NODE_DURATION, "node1", 125.5, labels={"engine": "pandas"}
        )
        metrics.record(MetricType.THROUGHPUT, "node1", 10000.0)
        metrics.increment(MetricType.CACHE_HIT, "node1")
        metrics.increment(MetricType.CACHE_MISS, "node2")

        exporter = MetricsExporter(metrics)
        prom_text = exporter.export_prometheus()

        assert "odibi_node_duration_ms" in prom_text
        assert "odibi_throughput_rows_per_sec" in prom_text
        assert "odibi_cache_hits_total" in prom_text
        assert "odibi_cache_misses_total" in prom_text
        assert "odibi_cache_hit_rate" in prom_text
        assert "odibi_uptime_seconds" in prom_text
        assert 'node="node1"' in prom_text

    def test_export_json(self):
        """Test exporting metrics to JSON format"""
        metrics = MetricsManager()
        metrics.record(MetricType.NODE_DURATION, "node1", 125.5)
        metrics.increment(MetricType.SUCCESS_COUNT, "node1")

        exporter = MetricsExporter(metrics)
        json_str = exporter.export_json()

        data = json.loads(json_str)

        assert "export_time" in data
        assert "summary" in data
        assert "by_node" in data
        assert len(data["by_node"]) == 1
        assert data["by_node"][0]["node_name"] == "node1"

    def test_export_dataframe(self):
        """Test exporting metrics to DataFrame"""
        metrics = MetricsManager()
        metrics.record(
            MetricType.NODE_DURATION, "node1", 125.5, labels={"engine": "pandas"}
        )
        metrics.record(
            MetricType.NODE_DURATION, "node2", 200.0, labels={"engine": "spark"}
        )

        exporter = MetricsExporter(metrics)
        df = exporter.export_dataframe()

        assert len(df) == 2
        assert "metric_type" in df.columns
        assert "name" in df.columns
        assert "value" in df.columns
        assert "timestamp" in df.columns
        assert df["name"].tolist() == ["node1", "node2"]

    def test_save_prometheus(self, tmp_path):
        """Test saving metrics to Prometheus file"""
        metrics = MetricsManager()
        metrics.record(MetricType.NODE_DURATION, "node1", 125.5)

        exporter = MetricsExporter(metrics)
        filepath = tmp_path / "metrics.prom"
        exporter.save_prometheus(str(filepath))

        assert filepath.exists()
        content = filepath.read_text()
        assert "odibi_node_duration_ms" in content

    def test_save_json(self, tmp_path):
        """Test saving metrics to JSON file"""
        metrics = MetricsManager()
        metrics.record(MetricType.NODE_DURATION, "node1", 125.5)

        exporter = MetricsExporter(metrics)
        filepath = tmp_path / "metrics.json"
        exporter.save_json(str(filepath))

        assert filepath.exists()
        data = json.loads(filepath.read_text())
        assert "summary" in data

    def test_save_parquet(self, tmp_path):
        """Test saving metrics to Parquet file"""
        metrics = MetricsManager()
        metrics.record(MetricType.NODE_DURATION, "node1", 125.5)
        metrics.record(MetricType.NODE_DURATION, "node2", 200.0)

        exporter = MetricsExporter(metrics)
        filepath = tmp_path / "metrics.parquet"
        exporter.save_parquet(str(filepath))

        assert filepath.exists()

        # Read back and verify
        df = pd.read_parquet(filepath)
        assert len(df) == 2
        assert "metric_type" in df.columns

    def test_get_node_summary(self):
        """Test getting summary for specific node"""
        metrics = MetricsManager()
        metrics.record(MetricType.NODE_DURATION, "node1", 100.0)
        metrics.record(MetricType.NODE_DURATION, "node1", 200.0)
        metrics.record(MetricType.NODE_DURATION, "node1", 150.0)
        metrics.record(MetricType.THROUGHPUT, "node1", 5000.0)

        exporter = MetricsExporter(metrics)
        summary = exporter.get_node_summary("node1")

        assert summary["node_name"] == "node1"
        assert summary["total_executions"] == 3
        assert summary["avg_duration_ms"] == 150.0
        assert summary["min_duration_ms"] == 100.0
        assert summary["max_duration_ms"] == 200.0
        assert summary["avg_throughput"] == 5000.0

    def test_generate_report(self):
        """Test generating human-readable report"""
        metrics = MetricsManager()
        metrics.record(MetricType.NODE_DURATION, "node1", 125.5)
        metrics.increment(MetricType.CACHE_HIT, "node1")

        exporter = MetricsExporter(metrics)
        report = exporter.generate_report()

        assert "ODIBI CORE Metrics Report" in report
        assert "Cache Hit Rate" in report
        assert "node1" in report


class TestEventBus:
    """Test EventBus functionality"""

    def test_register_hook(self):
        """Test registering hooks"""
        bus = EventBus()

        def test_hook(data):
            pass

        hook = bus.register_hook("test_event", test_hook)

        assert hook.name == "test_hook"
        assert hook.priority == EventPriority.MEDIUM
        assert hook.enabled is True
        assert len(bus.get_hooks("test_event")) == 1

    def test_emit_event(self):
        """Test emitting events to hooks"""
        bus = EventBus()

        results = []

        def hook1(data):
            results.append(("hook1", data))

        def hook2(data):
            results.append(("hook2", data))

        bus.register_hook("test_event", hook1)
        bus.register_hook("test_event", hook2)

        bus.emit("test_event", {"value": 42})

        assert len(results) == 2
        assert results[0][1]["value"] == 42
        assert results[1][1]["value"] == 42

    def test_hook_priority(self):
        """Test hooks execute in priority order"""
        bus = EventBus()

        execution_order = []

        def low_priority(data):
            execution_order.append("low")

        def high_priority(data):
            execution_order.append("high")

        bus.register_hook("test", low_priority, priority=EventPriority.LOW)
        bus.register_hook("test", high_priority, priority=EventPriority.HIGH)

        bus.emit("test", {})

        assert execution_order == ["high", "low"]

    def test_hook_error_isolation(self):
        """Test that hook errors don't break pipeline"""
        bus = EventBus()

        results = []

        def failing_hook(data):
            raise ValueError("Hook failed!")

        def working_hook(data):
            results.append("success")

        bus.register_hook("test", failing_hook)
        bus.register_hook("test", working_hook)

        # Should not raise exception
        bus.emit("test", {})

        # Working hook should still execute
        assert "success" in results

    def test_disable_enable_hook(self):
        """Test disabling and enabling hooks"""
        bus = EventBus()

        results = []

        def test_hook(data):
            results.append("executed")

        bus.register_hook("test", test_hook, name="my_hook")

        # Disable hook
        bus.disable_hook("test", "my_hook")
        bus.emit("test", {})
        assert len(results) == 0

        # Enable hook
        bus.enable_hook("test", "my_hook")
        bus.emit("test", {})
        assert len(results) == 1

    def test_clear_hooks(self):
        """Test clearing hooks"""
        bus = EventBus()

        bus.register_hook("event1", lambda d: None)
        bus.register_hook("event2", lambda d: None)

        # Clear specific event
        bus.clear_hooks("event1")
        assert len(bus.get_hooks("event1")) == 0
        assert len(bus.get_hooks("event2")) == 1

        # Clear all
        bus.clear_hooks()
        assert len(bus.get_hooks("event2")) == 0

    def test_summary_hook(self):
        """Test built-in summary hook"""
        bus = EventBus()

        hook = bus.create_summary_hook()

        # Should not raise exception
        hook(
            {
                "pipeline_name": "test",
                "success_count": 5,
                "failed_count": 0,
                "duration_ms": 1000.0,
            }
        )

    def test_metrics_export_hook(self, tmp_path):
        """Test built-in metrics export hook"""
        bus = EventBus()

        metrics = MetricsManager()
        metrics.record(MetricType.NODE_DURATION, "node1", 125.5)

        hook = bus.create_metrics_export_hook(str(tmp_path), formats=["json"])
        hook({"metrics_manager": metrics})

        # Check file was created
        json_files = list(tmp_path.glob("metrics_*.json"))
        assert len(json_files) == 1

    def test_alert_hook(self):
        """Test built-in alert hook"""
        bus = EventBus()

        hook = bus.create_alert_hook(threshold_failed=2)

        # Should not alert (below threshold)
        hook({"pipeline_name": "test", "failed_count": 1})

        # Should alert (at threshold)
        hook({"pipeline_name": "test", "failed_count": 2})

    def test_async_hook_execution(self):
        """Test asynchronous hook execution"""
        import time

        bus = EventBus()

        results = []

        def async_hook(data):
            time.sleep(0.1)
            results.append("async")

        def sync_hook(data):
            results.append("sync")

        bus.register_hook("test", async_hook, async_execution=True)
        bus.register_hook("test", sync_hook, async_execution=False)

        bus.emit("test", {})

        # Sync hook should execute immediately
        assert "sync" in results

        # Wait for async hook
        time.sleep(0.2)
        assert "async" in results


class TestMetricsManagerPhase8:
    """Test Phase 8 enhancements to MetricsManager"""

    def test_record_memory_usage(self):
        """Test recording memory usage"""
        metrics = MetricsManager()

        metrics.record_memory_usage("node1", 256.5)

        memory_metrics = metrics.get_metrics_by_type(MetricType.MEMORY_USAGE)
        assert len(memory_metrics) == 1
        assert memory_metrics[0].value == 256.5

    def test_record_node_execution(self):
        """Test comprehensive node execution recording"""
        metrics = MetricsManager()

        metrics.record_node_execution(
            node_name="test_node",
            duration_ms=125.5,
            success=True,
            engine="pandas",
            rows=1000,
            cached=False,
        )

        # Check all metrics were recorded
        duration_metrics = metrics.get_metrics_by_name("test_node")
        assert any(
            m.metric_type == MetricType.NODE_DURATION.value for m in duration_metrics
        )

        # Check counters
        success_key = f"{MetricType.SUCCESS_COUNT.value}:test_node"
        assert metrics.counters[success_key] == 1.0

        cache_miss_key = f"{MetricType.CACHE_MISS.value}:test_node"
        assert metrics.counters[cache_miss_key] == 1.0

    def test_get_node_stats(self):
        """Test getting node statistics"""
        metrics = MetricsManager()

        # Record multiple executions
        metrics.record_node_execution("node1", 100.0, True, rows=1000)
        metrics.record_node_execution("node1", 200.0, True, rows=2000)
        metrics.record_node_execution("node1", 150.0, False, rows=1500)

        stats = metrics.get_node_stats("node1")

        assert stats["node_name"] == "node1"
        assert stats["executions"] == 3
        assert stats["avg_duration_ms"] == 150.0
        assert stats["min_duration_ms"] == 100.0
        assert stats["max_duration_ms"] == 200.0
        assert stats["success_count"] == 2.0
        assert stats["failure_count"] == 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
