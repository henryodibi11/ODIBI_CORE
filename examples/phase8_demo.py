"""
Phase 8 Demo: Observability & Automation

Demonstrates structured logging, metrics export, and automation hooks.
"""

import time
import pandas as pd
from pathlib import Path

from odibi_core.observability import (
    StructuredLogger,
    LogLevel,
    MetricsExporter,
    EventBus,
    EventPriority,
)
from odibi_core.metrics import MetricsManager, MetricType


def demo_structured_logging():
    """Demonstrate structured logging"""
    print("\n" + "=" * 70)
    print("DEMO 1: Structured Logging")
    print("=" * 70)
    
    logger = StructuredLogger("demo_pipeline", log_dir="logs", user="demo_user")
    
    # Log pipeline lifecycle
    logger.log_pipeline_start("energy_efficiency")
    
    # Simulate node executions
    logger.log_node_start("read_data", "ingest", engine="pandas")
    time.sleep(0.1)
    logger.log_node_complete("read_data", duration_ms=125.5, rows=1000, cache_hit=False)
    
    logger.log_node_start("transform_data", "transform", engine="pandas")
    time.sleep(0.2)
    logger.log_node_complete("transform_data", duration_ms=200.0, rows=1000, cache_hit=True)
    
    logger.log_node_start("save_results", "publish", engine="pandas")
    time.sleep(0.05)
    logger.log_node_complete("save_results", duration_ms=50.0, rows=1000)
    
    logger.log_pipeline_complete("energy_efficiency", duration_ms=375.5, 
                                 success_count=3, failed_count=0)
    
    # Query logs
    print(f"\nLogged {logger.get_summary()['total_entries']} events")
    print(f"Log file: {logger.log_file}")
    
    # Query specific events
    cache_hits = logger.query_logs(event_type="cache_hit")
    print(f"Cache hits: {len(cache_hits)}")
    
    return logger


def demo_metrics_export():
    """Demonstrate metrics export"""
    print("\n" + "=" * 70)
    print("DEMO 2: Metrics Export")
    print("=" * 70)
    
    metrics = MetricsManager()
    
    # Record comprehensive node metrics
    metrics.record_node_execution("read_data", 125.5, True, "pandas", 1000, False)
    metrics.record_node_execution("transform_data", 200.0, True, "pandas", 1000, True)
    metrics.record_node_execution("save_results", 50.0, True, "pandas", 1000, False)
    
    # Record memory usage
    metrics.record_memory_usage("read_data", 128.5)
    metrics.record_memory_usage("transform_data", 256.0)
    
    exporter = MetricsExporter(metrics)
    
    # Create metrics directory
    Path("metrics").mkdir(exist_ok=True)
    
    # Export to different formats
    exporter.save_prometheus("metrics/demo.prom")
    exporter.save_json("metrics/demo.json")
    exporter.save_parquet("metrics/demo.parquet")
    
    print("\nMetrics exported to:")
    print("   Prometheus: metrics/demo.prom")
    print("   JSON: metrics/demo.json")
    print("   Parquet: metrics/demo.parquet")
    
    # Print report
    print("\n" + exporter.generate_report())
    
    return metrics


def demo_event_hooks():
    """Demonstrate automation hooks"""
    print("\n" + "=" * 70)
    print("DEMO 3: Event Bus & Automation Hooks")
    print("=" * 70)
    
    bus = EventBus()
    
    # Register built-in hooks
    print("\nRegistering hooks...")
    bus.register_hook("pipeline_complete", bus.create_summary_hook(), 
                     priority=EventPriority.HIGH)
    
    bus.register_hook("pipeline_complete", 
                     bus.create_metrics_export_hook("metrics/", formats=["json"]),
                     priority=EventPriority.MEDIUM)
    
    bus.register_hook("pipeline_complete", 
                     bus.create_alert_hook(threshold_failed=1),
                     priority=EventPriority.CRITICAL)
    
    # Custom hook
    def custom_notification(event_data):
        print(f"\nCustom Notification:")
        print(f"   Pipeline '{event_data['pipeline_name']}' completed")
        print(f"   Duration: {event_data['duration_ms']:.2f}ms")
    
    bus.register_hook("pipeline_complete", custom_notification, 
                     priority=EventPriority.LOW)
    
    print(f"Registered {len(bus.get_hooks('pipeline_complete'))} hooks")
    
    # Create dummy metrics
    metrics = MetricsManager()
    metrics.record(MetricType.NODE_DURATION, "demo_node", 100.0)
    
    # Emit event
    print("\nEmitting 'pipeline_complete' event...\n")
    bus.emit("pipeline_complete", {
        "pipeline_name": "demo_pipeline",
        "success_count": 3,
        "failed_count": 0,
        "duration_ms": 375.5,
        "metrics_manager": metrics
    })
    
    bus.shutdown()
    
    return bus


def demo_complete_pipeline():
    """Demonstrate complete pipeline with observability"""
    print("\n" + "=" * 70)
    print("DEMO 4: Complete Pipeline with Observability")
    print("=" * 70)
    
    # Initialize observability components
    logger = StructuredLogger("complete_demo", log_dir="logs")
    metrics = MetricsManager()
    bus = EventBus()
    
    # Register hooks
    bus.register_hook("pipeline_complete", bus.create_summary_hook())
    bus.register_hook("pipeline_complete", 
                     bus.create_metrics_export_hook("metrics/", formats=["prometheus", "json"]))
    
    # Simulate pipeline execution
    logger.log_pipeline_start("complete_demo")
    
    nodes = [
        ("ingest_csv", "ingest", 100.0, 500),
        ("validate_data", "transform", 50.0, 500),
        ("calculate_metrics", "transform", 150.0, 500),
        ("aggregate_results", "transform", 200.0, 50),
        ("export_parquet", "publish", 75.0, 50),
    ]
    
    for node_name, layer, duration, rows in nodes:
        # Log node start
        logger.log_node_start(node_name, layer, engine="pandas")
        
        # Simulate execution
        time.sleep(duration / 1000)
        
        # Record metrics
        metrics.record_node_execution(node_name, duration, True, "pandas", rows, False)
        
        # Log completion
        logger.log_node_complete(node_name, duration, rows)
    
    total_duration = sum(d for _, _, d, _ in nodes)
    
    # Log pipeline completion
    logger.log_pipeline_complete("complete_demo", total_duration, 
                                 success_count=len(nodes), failed_count=0)
    
    # Emit completion event
    bus.emit("pipeline_complete", {
        "pipeline_name": "complete_demo",
        "success_count": len(nodes),
        "failed_count": 0,
        "duration_ms": total_duration,
        "metrics_manager": metrics
    })
    
    print(f"\nPipeline completed successfully!")
    print(f"Processed {len(nodes)} nodes")
    print(f"Total duration: {total_duration:.2f}ms")
    
    bus.shutdown()


def main():
    """Run all demos"""
    print("\nODIBI CORE - Phase 8 Observability & Automation Demo")
    print("=" * 70)
    
    # Demo 1: Structured Logging
    demo_structured_logging()
    
    # Demo 2: Metrics Export
    demo_metrics_export()
    
    # Demo 3: Event Hooks
    demo_event_hooks()
    
    # Demo 4: Complete Pipeline
    demo_complete_pipeline()
    
    print("\n" + "=" * 70)
    print("All Phase 8 demos completed successfully!")
    print("=" * 70)
    print("\nCheck the following directories:")
    print("   - logs/      - Structured logs (.jsonl)")
    print("   - metrics/   - Exported metrics (.prom, .json, .parquet)")
    print("\nNext steps:")
    print("   - Review DEVELOPER_WALKTHROUGH_PHASE_8.md for detailed guide")
    print("   - Explore grafana_templates/ for dashboard setup")
    print("   - Read PHASE_8_COMPLETE.md for complete feature list")
    print()


if __name__ == "__main__":
    main()
