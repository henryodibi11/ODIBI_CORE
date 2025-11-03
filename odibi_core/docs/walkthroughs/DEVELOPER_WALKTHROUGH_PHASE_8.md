---
id: phase_8_observability
title: "Phase 8: Observability Systems"
level: "Advanced"
duration: "~4 hours"
tags: ["observability", "logging", "monitoring", "metrics", "automation", "grafana", "prometheus", "event-bus"]
prerequisites:
  - "Completed Phases 1-7"
  - "Basic understanding of logging patterns"
  - "Familiarity with metrics collection"
checkpoints: 8
quiz_questions: 26
author: "AMP AI Engineering Agent"
date: "November 2, 2025"
version: "1.0.2"
checkpoints:
  - id: checkpoint_1
    title: "Module Structure Created"
    validates: "observability/ directory with structured_logger.py, metrics_exporter.py, events_bus.py"
  - id: checkpoint_2
    title: "StructuredLogger Implemented"
    validates: "JSON Lines logging with query capabilities and log rotation"
  - id: checkpoint_3
    title: "MetricsExporter Built"
    validates: "Prometheus, JSON, and Parquet export formats working"
  - id: checkpoint_4
    title: "EventBus Functional"
    validates: "Priority-based hooks with summary, metrics export, and alert hooks"
  - id: checkpoint_5
    title: "MetricsManager Enhanced"
    validates: "Memory tracking, success/failure counts, and node statistics"
  - id: checkpoint_6
    title: "Grafana Templates Created"
    validates: "Dashboard JSON files and setup documentation"
  - id: checkpoint_7
    title: "Tests Passing"
    validates: "All Phase 8 tests green (StructuredLogger, MetricsExporter, EventBus)"
  - id: checkpoint_8
    title: "End-to-End Demo Working"
    validates: "Full observability pipeline with logs, metrics, and automation"
quiz_questions:
  - id: q1
    question: "What format does StructuredLogger use for log storage?"
    options:
      - "JSON Array"
      - "CSV"
      - "JSON Lines (JSONL)"
      - "Binary protocol buffers"
    correct: 2
    explanation: "JSON Lines (JSONL) allows streaming reads and append-only writes without loading entire files into memory."
  - id: q2
    question: "What metric formats can MetricsExporter export to?"
    options:
      - "Only JSON"
      - "Prometheus, JSON, and Parquet"
      - "Only Prometheus"
      - "CSV and XML"
    correct: 1
    explanation: "MetricsExporter supports Prometheus (for Grafana), JSON (for dashboards), and Parquet (for analysis)."
  - id: q3
    question: "What is the purpose of log rotation in StructuredLogger?"
    options:
      - "To encrypt old logs"
      - "To prevent unbounded file growth"
      - "To compress logs"
      - "To delete old logs"
    correct: 1
    explanation: "Log rotation prevents log files from growing indefinitely by creating new files when max size is reached."
  - id: q4
    question: "Which Python module is used for optional memory tracking?"
    options:
      - "memory_profiler"
      - "tracemalloc"
      - "psutil"
      - "sys"
    correct: 2
    explanation: "psutil is used to get process memory information (process.memory_info().rss) for tracking memory usage."
  - id: q5
    question: "What is the event_type for a node that has started execution?"
    options:
      - "node_executing"
      - "node_start"
      - "execution_begin"
      - "node_running"
    correct: 1
    explanation: "The event_type 'node_start' is logged when a node begins execution in the DAG."
  - id: q6
    question: "What advantage does JSON Lines have over JSON Array for logging?"
    options:
      - "Smaller file size"
      - "Better encryption"
      - "Streaming reads without loading entire file"
      - "Faster parsing"
    correct: 2
    explanation: "JSON Lines allows line-by-line streaming reads, while JSON Arrays require loading the entire file into memory."
  - id: q7
    question: "What does the Prometheus TYPE directive specify?"
    options:
      - "Data type (int, float, string)"
      - "Metric type (gauge, counter, histogram)"
      - "Export format"
      - "Time series resolution"
    correct: 1
    explanation: "The TYPE directive in Prometheus format specifies whether a metric is a gauge, counter, histogram, or summary."
  - id: q8
    question: "What is the primary benefit of the EventBus pattern?"
    options:
      - "Faster execution"
      - "Decoupling components and separation of concerns"
      - "Reduced memory usage"
      - "Better error messages"
    correct: 1
    explanation: "EventBus decouples components, allowing hooks to be added/removed without modifying core pipeline logic."
  - id: q9
    question: "What are the three priority levels supported by EventBus?"
    options:
      - "LOW, MEDIUM, HIGH"
      - "NORMAL, ELEVATED, CRITICAL"
      - "P0, P1, P2"
      - "1, 2, 3"
    correct: 0
    explanation: "EventBus supports EventPriority.LOW, EventPriority.NORMAL, and EventPriority.HIGH for hook execution order."
  - id: q10
    question: "What does the create_summary_hook() return?"
    options:
      - "A dictionary with summary data"
      - "A callable function that prints pipeline summary"
      - "A JSON string"
      - "A metrics object"
    correct: 1
    explanation: "create_summary_hook() returns a callable function (hook) that prints a formatted pipeline execution summary."
  - id: q11
    question: "What new metric types were added to MetricsManager in Phase 8?"
    options:
      - "Only MEMORY_USAGE"
      - "MEMORY_USAGE, SUCCESS_COUNT, FAILURE_COUNT"
      - "CPU_USAGE, DISK_USAGE"
      - "LATENCY, BANDWIDTH"
    correct: 1
    explanation: "Phase 8 adds MEMORY_USAGE, SUCCESS_COUNT, and FAILURE_COUNT to track resource usage and execution outcomes."
  - id: q12
    question: "What does the record_node_execution() method do?"
    options:
      - "Only records duration"
      - "Records comprehensive metrics: duration, success/failure, cache hit/miss, throughput"
      - "Only logs to console"
      - "Only updates counters"
    correct: 1
    explanation: "record_node_execution() is a convenience method that records multiple related metrics in one call."
  - id: q13
    question: "What file extension is used for JSON Lines files?"
    options:
      - ".json"
      - ".log"
      - ".jsonl"
      - ".jl"
    correct: 2
    explanation: "The standard extension for JSON Lines files is .jsonl (though .ndjson is also sometimes used)."
  - id: q14
    question: "How does StructuredLogger determine when to rotate logs?"
    options:
      - "Every hour"
      - "When max_file_size_mb is exceeded"
      - "Every 1000 entries"
      - "When disk is full"
    correct: 1
    explanation: "Log rotation occurs when the log file size exceeds max_file_size_mb (default 100 MB)."
  - id: q15
    question: "What does the query_logs() method's limit parameter default to?"
    options:
      - "10"
      - "50"
      - "100"
      - "1000"
    correct: 2
    explanation: "The limit parameter defaults to 100 entries to prevent accidentally loading huge result sets."
  - id: q16
    question: "What is the purpose of labels in Prometheus metrics?"
    options:
      - "To color-code metrics"
      - "To add dimensional metadata (e.g., engine='pandas')"
      - "To encrypt metric values"
      - "To version metrics"
    correct: 1
    explanation: "Labels add dimensions to metrics, allowing filtering and grouping (e.g., by engine type, node name)."
  - id: q17
    question: "What happens if a hook raises an exception in EventBus?"
    options:
      - "The entire pipeline fails"
      - "The error is logged and other hooks continue executing"
      - "The hook is retried 3 times"
      - "The pipeline is rolled back"
    correct: 1
    explanation: "EventBus isolates errors—if one hook fails, the error is logged but other hooks continue executing."
  - id: q18
    question: "What format does export_prometheus() return?"
    options:
      - "JSON"
      - "Binary protobuf"
      - "Text format with # HELP and # TYPE comments"
      - "XML"
    correct: 2
    explanation: "Prometheus text exposition format uses plain text with # HELP and # TYPE comments followed by metric lines."
  - id: q19
    question: "What does get_node_stats() calculate from duration metrics?"
    options:
      - "Only the total duration"
      - "Average, min, and max duration plus execution counts"
      - "Only the average"
      - "Median and standard deviation"
    correct: 1
    explanation: "get_node_stats() computes avg, min, max duration, total executions, and success/failure counts for a node."
  - id: q20
    question: "Why use dataclasses for StructuredLogEntry?"
    options:
      - "Better performance"
      - "Type safety, automatic __init__, easy serialization with asdict()"
      - "Required by JSON"
      - "Smaller memory footprint"
    correct: 1
    explanation: "Dataclasses provide type hints, automatic initialization, and easy conversion to dictionaries for JSON serialization."
  - id: q21
    question: "What does the EventBus._executor use for asynchronous hook execution?"
    options:
      - "asyncio"
      - "multiprocessing"
      - "ThreadPoolExecutor"
      - "celery"
    correct: 2
    explanation: "EventBus uses ThreadPoolExecutor for concurrent hook execution without blocking the main thread."
  - id: q22
    question: "What is the purpose of the create_alert_hook() threshold_failed parameter?"
    options:
      - "Maximum retries"
      - "Number of failed nodes that triggers an alert"
      - "Alert timeout in seconds"
      - "Alert severity level"
    correct: 1
    explanation: "threshold_failed specifies how many failed nodes will trigger an alert (default is 1)."
  - id: q23
    question: "What does the get_summary() method return for error entries?"
    options:
      - "All errors"
      - "Only the first error"
      - "The first 10 errors with timestamp, node_name, and error message"
      - "Error count only"
    correct: 2
    explanation: "get_summary() returns the first 10 errors with details to avoid overwhelming output while providing visibility."
  - id: q24
    question: "What integration is optional but supported via Grafana templates?"
    options:
      - "Elasticsearch"
      - "Splunk"
      - "Prometheus/Grafana for time-series visualization"
      - "AWS CloudWatch"
    correct: 2
    explanation: "Grafana integration via Prometheus is optional—ODIBI CORE generates local metrics without requiring external services."
---

# ODIBI CORE v1.0 - Phase 8 Developer Walkthrough

**Building Observability & Automation: A Step-by-Step Guide**

**Author**: AMP AI Engineering Agent  
**Date**: 2025-11-01  
**Audience**: Developers learning production observability systems  
**Duration**: ~3 hours (following this guide)  
**Prerequisites**: Completed Phase 7 (Cloud Infrastructure & Distribution)

---

## 📚 Observability Overview

### What is Phase 8?

Phase 8 transforms ODIBI CORE into a **production-ready observability platform**. You'll add:

- **StructuredLogger** - JSON Lines logging with contextual metadata
- **MetricsExporter** - Multi-format export (Prometheus, JSON, Parquet)
- **EventBus** - Priority-based automation hooks
- **Enhanced MetricsManager** - Per-node statistics, memory tracking
- **Grafana Dashboards** - Pre-built monitoring templates

### What's New in Phase 8

**Phase 7**: Pipeline execution with basic logging
```text
Run pipeline → Execute nodes → Print errors → Exit
```

**Phase 8**: Full observability with structured logs and metrics
```text
Run pipeline → Log all events → Collect metrics → Export → Trigger hooks → Alert
                    ↓               ↓              ↓
              Query logs      Visualize in     Automate
                              Grafana          actions
```

### Key Architecture Components

**1. StructuredLogger (JSON Lines Logging)**
```python
# [demo]
# Every event logged as structured JSON
logger = StructuredLogger("my_pipeline", log_dir="logs")
logger.log_node_start("read_data", "ingest", engine="pandas")
logger.log_node_complete("read_data", duration_ms=125.5, rows=1000)

# Query logs
errors = logger.query_logs(level=LogLevel.ERROR)
```

**2. MetricsExporter (Multi-Format Export)**
```python
# [demo]
# Export to Prometheus, JSON, Parquet
exporter = MetricsExporter(metrics_manager)
exporter.save_prometheus("metrics.prom")  # For Grafana
exporter.save_json("metrics.json")        # For dashboards
exporter.save_parquet("metrics.parquet")  # For analysis
```

**3. EventBus (Automation Hooks)**
```python
# [demo]
# Register hooks for pipeline events
bus = EventBus()
bus.register_hook("pipeline_complete", bus.create_summary_hook())
bus.register_hook("pipeline_complete", bus.create_alert_hook(threshold_failed=3))

# Emit events
bus.emit("pipeline_complete", {"success_count": 10, "failed_count": 0})
```

### What You'll Build

By the end of this walkthrough, you'll have:
- ✅ Structured logging with JSON Lines format
- ✅ Prometheus-compatible metrics export
- ✅ Event-driven automation system
- ✅ Per-node performance statistics
- ✅ Grafana dashboard templates
- ✅ Memory usage monitoring
- ✅ Full backward compatibility with Phases 1-7

---

## 🗺️ Dependency Map (Phase 8)

```text
┌────────────────────────────────────────────────────────────┐
│           User Code / Production Pipelines                  │
│    Observable pipelines with metrics & automation           │
└────────────────────────────────────────────────────────────┘
                            ▲
                            │
┌────────────────────────────────────────────────────────────┐
│                   EventBus                                  │
│         Priority-based automation hooks                     │
└────────────────────────────────────────────────────────────┘
                            ▲
                            │
┌──────────────────┬─────────────────┬──────────────────┐
│ StructuredLogger │ MetricsExporter │ MetricsManager   │
│ (observability/) │ (observability/)│ (metrics/)       │
│                  │                 │ (Enhanced)       │
│ Provides:        │ Provides:       │ Provides:        │
│ - JSON logs      │ - Prometheus    │ - Per-node stats │
│ - Log queries    │ - JSON export   │ - Memory track   │
│ - Rotation       │ - Parquet       │ - Success/fail   │
└──────────────────┴─────────────────┴──────────────────┘
                            ▲
                            │
┌────────────────────────────────────────────────────────────┐
│        Phase 7: Cloud & Distribution (Already Complete)     │
│   CloudAdapter, DistributedExecutor, CloudCacheManager      │
└────────────────────────────────────────────────────────────┘
```

**Build Order**: StructuredLogger → MetricsExporter → EventBus → MetricsManager Enhancements → Grafana Templates

---

## 🎯 Mission-Based Build Plan

### Mission 1: Create Observability Module Structure (5 mins)

**Goal**: Set up directory structure for observability components

**Files to Create**:
```text
odibi_core/
├── observability/
│   ├── __init__.py
│   ├── structured_logger.py
│   ├── metrics_exporter.py
│   └── events_bus.py
└── grafana_templates/
    ├── odibi_overview_dashboard.json
    ├── odibi_node_performance_dashboard.json
    └── README.md
```

**Action**:
```bash
cd odibi_core
mkdir observability
cd observability
touch __init__.py structured_logger.py metrics_exporter.py events_bus.py

cd ../..
mkdir grafana_templates
cd grafana_templates
touch odibi_overview_dashboard.json odibi_node_performance_dashboard.json README.md
```

**Verification**:
```bash
ls -la odibi_core/observability/
ls -la grafana_templates/
```

> **🎓 CHECKPOINT 1**: Verify directory structure is created correctly
> 
> **Quiz Time!** Answer questions 1-3 to test your understanding of JSON Lines format and log rotation.
> 
> *(See quiz_database.py: DEVELOPER_WALKTHROUGH_PHASE_8.md, step 2)*

---

### Mission 2: Build StructuredLogger (45 mins)

**Goal**: Implement JSON Lines logging with contextual metadata

#### Step 2.1: Define Log Entry Structure

**File**: `odibi_core/observability/structured_logger.py`

```python
"""
Structured Logger (Phase 8)

JSON Lines-based structured logging for DAG execution, node events, and exceptions.
"""

import json
import logging
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
```

**Why JSON Lines?**: Each line is a complete JSON object. Enables streaming reads without loading entire file.

**Why Dataclasses?**: Type safety, automatic `__init__`, easy serialization with `asdict()`.

#### Step 2.2: Implement Core Logger

**Add to same file**:

```python
class StructuredLogger:
    """
    Structured logger for DAG execution events.
    
    Writes JSON Lines format to disk for easy querying and analysis.
    """
    
    def __init__(
        self,
        name: str,
        log_dir: str = "logs",
        max_file_size_mb: int = 100,
        user: Optional[str] = None
    ):
        """Initialize structured logger."""
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.max_file_size_mb = max_file_size_mb
        self.user = user
        
        # Create log file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"{name}_{timestamp}.jsonl"
        self.log_file.touch()  # Create file
        
        logger.info(f"StructuredLogger initialized: {self.log_file}")
    
    def _write_entry(self, entry: StructuredLogEntry) -> None:
        """Write log entry to file."""
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
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / (1024 * 1024)
        except:
            return 0.0
```

**Key Design Decisions**:
- **Automatic rotation**: Prevents unbounded file growth
- **Memory tracking**: Optional psutil integration
- **Path safety**: Uses `pathlib.Path` for cross-platform compatibility

#### Step 2.3: Add Convenience Methods

**Add to StructuredLogger class**:

```python
    def log_node_start(
        self,
        node_name: str,
        layer: str,
        engine: str = "pandas",
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log node execution start."""
        entry = StructuredLogEntry(
            timestamp=datetime.now().isoformat(),
            level=LogLevel.INFO.value,
            event_type="node_start",
            message=f"Node '{node_name}' started",
            node_name=node_name,
            layer=layer,
            engine=engine,
            status="running",
            memory_mb=self._get_memory_usage(),
            user=self.user,
            metadata=metadata
        )
        self._write_entry(entry)
    
    def log_node_complete(
        self,
        node_name: str,
        duration_ms: float,
        rows: Optional[int] = None,
        cache_hit: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log node execution completion."""
        entry = StructuredLogEntry(
            timestamp=datetime.now().isoformat(),
            level=LogLevel.INFO.value,
            event_type="node_complete",
            message=f"Node '{node_name}' completed in {duration_ms:.2f}ms",
            node_name=node_name,
            status="success",
            duration_ms=duration_ms,
            row_count=rows,
            cache_hit=cache_hit,
            memory_mb=self._get_memory_usage(),
            user=self.user,
            metadata=metadata
        )
        self._write_entry(entry)
    
    def log_error(
        self,
        component: str,
        error: str,
        layer: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log general error."""
        entry = StructuredLogEntry(
            timestamp=datetime.now().isoformat(),
            level=LogLevel.ERROR.value,
            event_type="error",
            message=f"Error in {component}: {error}",
            node_name=component,
            layer=layer,
            error=error,
            memory_mb=self._get_memory_usage(),
            user=self.user,
            metadata=metadata
        )
        self._write_entry(entry)
```

#### Step 2.4: Add Query Capabilities

**Add to StructuredLogger class**:

```python
    def query_logs(
        self,
        event_type: Optional[str] = None,
        node_name: Optional[str] = None,
        level: Optional[LogLevel] = None,
        limit: int = 100
    ) -> list:
        """
        Query log entries.
        
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
        """Get summary of all log entries."""
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
                    
                    level = entry.get("level", "unknown")
                    by_level[level] = by_level.get(level, 0) + 1
                    
                    event_type = entry.get("event_type", "unknown")
                    by_event_type[event_type] = by_event_type.get(event_type, 0) + 1
                    
                    if level in ("error", "critical"):
                        errors.append({
                            "timestamp": entry.get("timestamp"),
                            "node_name": entry.get("node_name"),
                            "error": entry.get("error")
                        })
                        
                except json.JSONDecodeError:
                    continue
        
        return {
            "log_file": str(self.log_file),
            "total_entries": total_entries,
            "by_level": by_level,
            "by_event_type": by_event_type,
            "errors": errors[:10],
            "file_size_mb": self.log_file.stat().st_size / (1024 * 1024)
        }
```

**Test StructuredLogger**:

```python
# Test script: test_structured_logger.py
from odibi_core.observability import StructuredLogger, LogLevel

logger = StructuredLogger("test_pipeline", log_dir="logs")

logger.log_node_start("read_data", "ingest", engine="pandas")
logger.log_node_complete("read_data", duration_ms=125.5, rows=1000)
logger.log_error("transform", "ValueError: Missing column")

# Query
errors = logger.query_logs(level=LogLevel.ERROR)
print(f"Errors: {len(errors)}")

summary = logger.get_summary()
print(f"Total entries: {summary['total_entries']}")
```

> **🎓 CHECKPOINT 2**: Verify StructuredLogger is working with tests
> 
> **Quiz Time!** Answer questions 4-6 to test your understanding of memory tracking and event types.
> 
> *(See quiz_database.py: DEVELOPER_WALKTHROUGH_PHASE_8.md, step 4)*

---

### Mission 3: Build MetricsExporter (40 mins)

**Goal**: Export metrics in Prometheus, JSON, and Parquet formats

#### Step 3.1: Create Exporter Class

**File**: `odibi_core/observability/metrics_exporter.py`

```python
"""
Metrics Exporter (Phase 8)

Export MetricsManager data to Prometheus, JSON, and Parquet formats.
"""

import json
import logging
from typing import Dict, Any, List
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class MetricsExporter:
    """
    Export metrics in multiple formats for monitoring and analysis.
    
    Supports:
    - Prometheus text exposition format
    - JSON for dashboards
    - Parquet for data analysis
    """
    
    def __init__(self, metrics_manager):
        """Initialize with MetricsManager instance."""
        self.metrics = metrics_manager
    
    def export_prometheus(self) -> str:
        """
        Export metrics in Prometheus text exposition format.
        
        Returns:
            Prometheus-formatted text
        """
        lines = []
        
        # Group metrics by type
        by_type = {}
        for metric in self.metrics.metrics:
            metric_type = metric.metric_type
            if metric_type not in by_type:
                by_type[metric_type] = []
            by_type[metric_type].append(metric)
        
        # Generate Prometheus format
        for metric_type, metrics_list in by_type.items():
            # Add HELP comment
            lines.append(f"# HELP odibi_{metric_type} ODIBI metric: {metric_type}")
            # Add TYPE comment
            lines.append(f"# TYPE odibi_{metric_type} gauge")
            
            # Add metric lines
            for metric in metrics_list:
                # Build labels
                labels_str = f'name="{metric.name}"'
                if metric.labels:
                    label_parts = [f'{k}="{v}"' for k, v in metric.labels.items()]
                    labels_str += "," + ",".join(label_parts)
                
                # Add metric line
                lines.append(f"odibi_{metric_type}{{{labels_str}}} {metric.value}")
        
        return "\n".join(lines)
    
    def export_json(self) -> str:
        """
        Export metrics as JSON.
        
        Returns:
            JSON string
        """
        data = {
            "export_time": datetime.now().isoformat(),
            "total_metrics": len(self.metrics.metrics),
            "by_type": {},
            "by_node": {},
            "summary": self.metrics.get_summary()
        }
        
        # Group by type
        for metric in self.metrics.metrics:
            metric_type = metric.metric_type
            if metric_type not in data["by_type"]:
                data["by_type"][metric_type] = []
            data["by_type"][metric_type].append({
                "name": metric.name,
                "value": metric.value,
                "labels": metric.labels,
                "timestamp": metric.timestamp.isoformat()
            })
        
        # Group by node
        for metric in self.metrics.metrics:
            node_name = metric.name
            if node_name not in data["by_node"]:
                data["by_node"][node_name] = []
            data["by_node"][node_name].append({
                "type": metric.metric_type,
                "value": metric.value,
                "labels": metric.labels,
                "timestamp": metric.timestamp.isoformat()
            })
        
        return json.dumps(data, indent=2)
    
    def export_parquet(self) -> bytes:
        """
        Export metrics as Parquet format.
        
        Returns:
            Parquet bytes
        """
        try:
            import pandas as pd
            import pyarrow as pa
            import pyarrow.parquet as pq
            from io import BytesIO
            
            # Convert metrics to DataFrame
            records = []
            for metric in self.metrics.metrics:
                record = {
                    "metric_type": metric.metric_type,
                    "name": metric.name,
                    "value": metric.value,
                    "timestamp": metric.timestamp.isoformat()
                }
                # Flatten labels
                if metric.labels:
                    for k, v in metric.labels.items():
                        record[f"label_{k}"] = v
                records.append(record)
            
            df = pd.DataFrame(records)
            
            # Write to Parquet
            buffer = BytesIO()
            table = pa.Table.from_pandas(df)
            pq.write_table(table, buffer)
            
            return buffer.getvalue()
            
        except ImportError:
            logger.warning("Parquet export requires pandas and pyarrow")
            return b""
    
    def save_prometheus(self, filepath: str) -> None:
        """Save Prometheus format to file."""
        Path(filepath).write_text(self.export_prometheus())
        logger.info(f"Prometheus metrics saved to {filepath}")
    
    def save_json(self, filepath: str) -> None:
        """Save JSON format to file."""
        Path(filepath).write_text(self.export_json())
        logger.info(f"JSON metrics saved to {filepath}")
    
    def save_parquet(self, filepath: str) -> None:
        """Save Parquet format to file."""
        parquet_bytes = self.export_parquet()
        if parquet_bytes:
            Path(filepath).write_bytes(parquet_bytes)
            logger.info(f"Parquet metrics saved to {filepath}")
    
    def generate_report(self) -> str:
        """Generate human-readable report."""
        summary = self.metrics.get_summary()
        
        report = []
        report.append("=" * 70)
        report.append("ODIBI CORE Metrics Report")
        report.append("=" * 70)
        report.append(f"Total Metrics: {summary.get('total_metrics', 0)}")
        report.append(f"Cache Hit Rate: {summary.get('cache_hit_rate', 0):.2%}")
        report.append(f"Average Duration: {summary.get('avg_duration_ms', 0):.2f}ms")
        report.append("")
        report.append("Top Nodes by Duration:")
        
        for node, duration in summary.get("top_nodes_by_duration", {}).items():
            report.append(f"  {node}: {duration:.2f}ms")
        
        report.append("=" * 70)
        
        return "\n".join(report)
```

**Test MetricsExporter**:

```python
from odibi_core.metrics import MetricsManager, MetricType
from odibi_core.observability import MetricsExporter

metrics = MetricsManager()
metrics.record(MetricType.NODE_DURATION, "read_data", 125.5, {"engine": "pandas"})
metrics.record(MetricType.CACHE_HIT, "read_data", 1)

exporter = MetricsExporter(metrics)

# Export to different formats
print(exporter.export_prometheus())
print(exporter.generate_report())

exporter.save_json("metrics.json")
exporter.save_prometheus("metrics.prom")
```

> **🎓 CHECKPOINT 3**: Verify MetricsExporter supports all three formats
> 
> **Quiz Time!** Answer questions 7-9 to test your understanding of Prometheus format and export types.
> 
> *(See quiz_database.py: DEVELOPER_WALKTHROUGH_PHASE_8.md, step 6)*

---

### Mission 4: Build EventBus (40 mins)

**Goal**: Create priority-based event system for automation hooks

#### Step 4.1: Define Hook Infrastructure

**File**: `odibi_core/observability/events_bus.py`

```python
"""
Event Bus (Phase 8)

Priority-based event system for pipeline automation hooks.
"""

import logging
from enum import IntEnum
from typing import Callable, Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

logger = logging.getLogger(__name__)


class EventPriority(IntEnum):
    """Hook execution priority (lower number = higher priority)"""
    HIGH = 0
    NORMAL = 1
    LOW = 2


# ℹ️ Priority Explanation:
# - HIGH (0): Critical hooks that must run first (e.g., logging, alerts)
# - NORMAL (1): Standard hooks (e.g., metrics export, notifications)
# - LOW (2): Optional hooks (e.g., debugging, analytics)
# Hooks are sorted and executed in ascending priority order (HIGH → NORMAL → LOW)


@dataclass
class RegisteredHook:
    """
    Registered hook with metadata.
    
    Attributes:
        name: Hook name
        callback: Callable function
        priority: Execution priority
        event_type: Event type to listen for
    """
    name: str
    callback: Callable[[Dict[str, Any]], None]
    priority: EventPriority
    event_type: str
```

#### Step 4.2: Implement Core EventBus

**Add to same file**:

```python
class EventBus:
    """
    Event bus for pipeline automation hooks.
    
    Features:
    - Priority-based execution
    - Async hook execution
    - Error isolation
    """
    
    def __init__(self, max_workers: int = 4):
        """Initialize event bus."""
        self._hooks: Dict[str, List[RegisteredHook]] = {}
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        logger.info("EventBus initialized")
    
    def register_hook(
        self,
        event_type: str,
        callback: Callable[[Dict[str, Any]], None],
        priority: EventPriority = EventPriority.NORMAL,
        name: Optional[str] = None
    ) -> RegisteredHook:
        """
        Register a hook for an event type.
        
        Args:
            event_type: Event type to listen for
            callback: Function to call when event is emitted
            priority: Execution priority
            name: Optional hook name
        
        Returns:
            RegisteredHook instance
        """
        if event_type not in self._hooks:
            self._hooks[event_type] = []
        
        hook_name = name or callback.__name__
        hook = RegisteredHook(
            name=hook_name,
            callback=callback,
            priority=priority,
            event_type=event_type
        )
        
        self._hooks[event_type].append(hook)
        
        # Sort by priority
        self._hooks[event_type].sort(key=lambda h: h.priority)
        
        logger.info(f"Registered hook '{hook_name}' for event '{event_type}'")
        return hook
    
    def emit(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """
        Emit an event, triggering all registered hooks.
        
        Args:
            event_type: Type of event
            event_data: Event data dictionary
        """
        if event_type not in self._hooks:
            logger.debug(f"No hooks registered for event '{event_type}'")
            return
        
        logger.info(f"Emitting event '{event_type}' with {len(self._hooks[event_type])} hooks")
        
        for hook in self._hooks[event_type]:
            self._executor.submit(self._execute_hook, hook, event_data)
    
    def _execute_hook(self, hook: RegisteredHook, event_data: Dict[str, Any]) -> None:
        """Execute a single hook with error isolation."""
        try:
            logger.debug(f"Executing hook '{hook.name}'")
            hook.callback(event_data)
        except Exception as e:
            logger.error(f"Hook '{hook.name}' failed: {e}")
    
    def get_hooks(self, event_type: str) -> List[RegisteredHook]:
        """Get all hooks for an event type."""
        return self._hooks.get(event_type, [])
```

#### Step 4.3: Add Built-in Hooks

**Add to EventBus class**:

```python
    def create_summary_hook(self) -> Callable[[Dict[str, Any]], None]:
        """Create a hook that prints pipeline summary."""
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
        self,
        export_dir: str,
        formats: Optional[List[str]] = None
    ) -> Callable[[Dict[str, Any]], None]:
        """Create a hook that exports metrics to files."""
        formats = formats or ["json", "prometheus"]
        
        def metrics_export_hook(event_data: Dict[str, Any]) -> None:
            try:
                from odibi_core.observability import MetricsExporter
                
                metrics_manager = event_data.get("metrics_manager")
                if not metrics_manager:
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
                
                logger.info(f"Metrics exported to {export_dir}")
                
            except Exception as e:
                logger.error(f"Failed to export metrics: {e}")
        
        return metrics_export_hook
    
    def create_alert_hook(self, threshold_failed: int = 1) -> Callable[[Dict[str, Any]], None]:
        """Create a hook that alerts on failures."""
        def alert_hook(event_data: Dict[str, Any]) -> None:
            failed_count = event_data.get("failed_count", 0)
            if failed_count >= threshold_failed:
                print(f"\n{'!' * 70}")
                print(f"ALERT: Pipeline '{event_data.get('pipeline_name')}' had {failed_count} failed nodes!")
                print(f"{'!' * 70}\n")
        
        return alert_hook
    
    def shutdown(self) -> None:
        """Shutdown event bus."""
        logger.info("Shutting down EventBus...")
        self._executor.shutdown(wait=True)
```

**Test EventBus**:

```python
# [demo]
from odibi_core.observability import EventBus, EventPriority

bus = EventBus()

# Register hooks
bus.register_hook("pipeline_complete", bus.create_summary_hook())
bus.register_hook("pipeline_complete", bus.create_alert_hook(threshold_failed=3))

# Emit event
bus.emit("pipeline_complete", {
    "pipeline_name": "test",
    "success_count": 5,
    "failed_count": 0,
    "duration_ms": 1000.0
})

bus.shutdown()
```

> **🎓 CHECKPOINT 4**: Verify EventBus executes hooks in priority order
> 
> **Quiz Time!** Answer questions 10-12 to test your understanding of EventBus and hook execution.
> 
> *(See quiz_database.py: DEVELOPER_WALKTHROUGH_PHASE_8.md, step 12)*

---

### Mission 5: Enhance MetricsManager (30 mins)

**Goal**: Add Phase 8 enhancements to existing MetricsManager

#### Step 5.1: Add New Metric Types

**File**: `odibi_core/metrics/metrics_manager.py`

**Find and update the MetricType enum**:

```python
# [demo]
class MetricType(Enum):
    """Supported metric types"""
    NODE_DURATION = "node_duration_ms"
    THROUGHPUT = "throughput_rows_per_sec"
    CACHE_HIT = "cache_hit"
    CACHE_MISS = "cache_miss"
    ERROR_COUNT = "error_count"
    RETRY_COUNT = "retry_count"
    CHECKPOINT_SIZE = "checkpoint_size_bytes"
    DATA_SIZE = "data_size_bytes"
    WORKER_UTILIZATION = "worker_utilization_pct"
    MEMORY_USAGE = "memory_usage_mb"           # NEW - Phase 8
    SUCCESS_COUNT = "success_count"            # NEW - Phase 8
    FAILURE_COUNT = "failure_count"            # NEW - Phase 8
```

#### Step 5.2: Add Convenience Methods

**Add to MetricsManager class**:

```python
# [demo]
    def record_memory_usage(self, name: str, memory_mb: float) -> None:
        """Record memory usage for a component."""
        self.record(MetricType.MEMORY_USAGE, name, memory_mb)
    
    def record_node_execution(
        self,
        node_name: str,
        duration_ms: float,
        success: bool,
        engine: str = "pandas",
        rows: Optional[int] = None,
        cached: bool = False
    ) -> None:
        """Record comprehensive node execution metrics."""
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
        """Get statistics for a specific node."""
        node_metrics = self.get_metrics_by_name(node_name)
        
        if not node_metrics:
            return {}
        
        durations = [m.value for m in node_metrics if m.metric_type == MetricType.NODE_DURATION.value]
        
        return {
            "node_name": node_name,
            "executions": len(durations),
            "avg_duration_ms": sum(durations) / len(durations) if durations else 0,
            "min_duration_ms": min(durations) if durations else 0,
            "max_duration_ms": max(durations) if durations else 0,
            "success_count": self.counters.get(f"success_count:{node_name}", 0),
            "failure_count": self.counters.get(f"failure_count:{node_name}", 0),
        }
```

> **🎓 CHECKPOINT 5**: Verify new MetricsManager methods work correctly
> 
> **Quiz Time!** Answer questions 13-15 to test your understanding of metric types and node statistics.

---

### Mission 6: Create Grafana Dashboards (20 mins)

**Goal**: Provide ready-to-use Grafana dashboard templates

#### Step 6.1: Create Overview Dashboard

**File**: `grafana_templates/odibi_overview_dashboard.json`

```json
{
  "dashboard": {
    "title": "ODIBI CORE - Pipeline Overview",
    "description": "Overview dashboard for ODIBI CORE pipeline execution metrics",
    "panels": [
      {
        "id": 1,
        "title": "Cache Hit Rate",
        "type": "gauge",
        "targets": [{"expr": "odibi_cache_hit_rate"}],
        "gridPos": {"x": 0, "y": 0, "w": 6, "h": 8}
      },
      {
        "id": 2,
        "title": "Node Execution Duration",
        "type": "graph",
        "targets": [{"expr": "odibi_node_duration_ms", "legendFormat": "{{node}}"}],
        "gridPos": {"x": 6, "y": 0, "w": 12, "h": 8}
      }
    ],
    "refresh": "10s"
  }
}
```

#### Step 6.2: Create Documentation

**File**: `grafana_templates/README.md`

```text
# Grafana Dashboard Templates

Pre-built dashboards for ODIBI CORE observability.

## Dashboards

1. **odibi_overview_dashboard.json** - Pipeline overview
2. **odibi_node_performance_dashboard.json** - Node-level metrics

## Setup

### Option 1: Manual Import
1. Open Grafana → Dashboards → Import
2. Upload JSON file
3. Configure Prometheus data source

### Option 2: Local Metrics (No Grafana)
```python
# [demo]
from odibi_core.observability import MetricsExporter

exporter = MetricsExporter(metrics)
print(exporter.generate_report())  # Human-readable report
```

## No External Dependencies Required

ODIBI CORE generates metrics locally. Grafana integration is optional.
```



> **🎓 CHECKPOINT 6**: Verify Grafana templates and documentation are complete
> 
> **Quiz Time!** Answer questions 16-18 to test your understanding of Prometheus labels and Grafana integration.

---

### Mission 7: Write Tests (45 mins)

**Goal**: Comprehensive test coverage for all Phase 8 components

**File**: `tests/test_phase8_observability.py`

```python
# [demo]
"""Tests for Phase 8: Observability & Automation"""

import pytest
import json
from pathlib import Path

from odibi_core.observability import (
    StructuredLogger,
    LogLevel,
    MetricsExporter,
    EventBus,
    EventPriority,
)
from odibi_core.metrics import MetricsManager, MetricType


class TestStructuredLogger:
    """Test StructuredLogger functionality"""
    
    def test_logger_initialization(self, tmp_path):
        """Test logger creates log file"""
        logger = StructuredLogger("test", log_dir=str(tmp_path))
        assert logger.log_file.exists()
    
    def test_log_node_start(self, tmp_path):
        """Test logging node start event"""
        logger = StructuredLogger("test", log_dir=str(tmp_path))
        logger.log_node_start("test_node", "ingest", engine="pandas")
        
        with open(logger.log_file, "r") as f:
            entry = json.loads(f.readline())
        
        assert entry["event_type"] == "node_start"
        assert entry["node_name"] == "test_node"
        assert entry["engine"] == "pandas"
    
    def test_query_logs(self, tmp_path):
        """Test querying log entries"""
        logger = StructuredLogger("test", log_dir=str(tmp_path))
        logger.log_node_start("node1", "ingest")
        logger.log_error("node2", "Test error")
        
        errors = logger.query_logs(level=LogLevel.ERROR)
        assert len(errors) == 1


class TestMetricsExporter:
    """Test MetricsExporter functionality"""
    
    def test_export_prometheus(self):
        """Test Prometheus export"""
        metrics = MetricsManager()
        metrics.record(MetricType.NODE_DURATION, "node1", 125.5)
        
        exporter = MetricsExporter(metrics)
        prom_text = exporter.export_prometheus()
        
        assert "odibi_node_duration_ms" in prom_text
        assert "node1" in prom_text
    
    def test_export_json(self):
        """Test JSON export"""
        metrics = MetricsManager()
        metrics.record(MetricType.NODE_DURATION, "node1", 125.5)
        
        exporter = MetricsExporter(metrics)
        json_str = exporter.export_json()
        data = json.loads(json_str)
        
        assert "export_time" in data
        assert "by_node" in data


class TestEventBus:
    """Test EventBus functionality"""
    
    def test_register_hook(self):
        """Test hook registration"""
        bus = EventBus()
        def test_hook(data): pass
        
        hook = bus.register_hook("test_event", test_hook)
        assert hook.name == "test_hook"
        assert len(bus.get_hooks("test_event")) == 1
    
    def test_emit_event(self):
        """Test event emission"""
        bus = EventBus()
        results = []
        
        bus.register_hook("test", lambda d: results.append(d))
        bus.emit("test", {"value": 42})
        
        assert len(results) == 1
        assert results[0]["value"] == 42
```

**Run Tests**:
```bash
pytest tests/test_phase8_observability.py -v
```

**Expected**: All tests passing

> **🎓 CHECKPOINT 7**: Verify all Phase 8 tests are passing
> 
> **Quiz Time!** Answer questions 19-21 to test your understanding of testing strategies and ThreadPoolExecutor.

---

## 🎓 Core Concepts Explained

### JSON Lines Format

**Why JSON Lines over JSON Array?**

❌ **JSON Array** (requires loading entire file):
```json
# [demo]
[
  {"event": "start", "time": "10:00"},
  {"event": "complete", "time": "10:05"}
]
```

✅ **JSON Lines** (streaming friendly):
```text
{"event": "start", "time": "10:00"}
{"event": "complete", "time": "10:05"}
```

**Benefits**:
- Read line-by-line without loading entire file
- Append-only writes (no array rewriting)
- Easy to grep/filter with standard tools

### Prometheus Format

**Structure**:
```text
# HELP metric_name Description
# TYPE metric_name gauge|counter
metric_name{label="value"} 42
```

**Example**:
```text
# HELP odibi_node_duration_ms Node execution duration
# TYPE odibi_node_duration_ms gauge
odibi_node_duration_ms{node="read_data",engine="pandas"} 125.5
```

**Why Prometheus?**
- Industry standard for metrics
- Grafana native support
- Time-series optimized
- Pull-based (no agent required)

### Event Bus Pattern

**Traditional Approach**:
```python
# [demo]
def run_pipeline():
    execute_dag()
    print("Pipeline complete")  # Hardcoded
    save_metrics()              # Hardcoded
```

**Event Bus Approach**:
```python
# [demo]
def run_pipeline():
    execute_dag()
    bus.emit("pipeline_complete", data)  # Decoupled
    # Hooks execute: summary, metrics, alerts, custom
```

**Benefits**:
- Separation of concerns
- Easy to add new hooks
- Priority-based execution
- Error isolation

> **Quiz Time!** Answer questions 22-24 to test your understanding of design patterns and advanced concepts.

---

## 🔍 Debugging & Troubleshooting

### Logs Not Written

**Check log directory permissions**:
```python
# [demo]
from pathlib import Path
log_dir = Path("logs")
log_dir.mkdir(parents=True, exist_ok=True)
```

### Metrics Not Exporting

**Verify metrics collected**:
```python
# [demo]
print(f"Total metrics: {len(metrics.metrics)}")
print(f"Metric types: {set(m.metric_type for m in metrics.metrics)}")
```

### Hooks Not Executing

**Check hook registration**:
```python
# [demo]
print(bus.get_hooks("pipeline_complete"))  # Should show hooks
```

---

## ✅ Phase 8 Complete Checklist

- [ ] StructuredLogger implemented with JSON Lines
- [ ] MetricsExporter exports to Prometheus, JSON, Parquet
- [ ] EventBus with priority-based hooks
- [ ] MetricsManager enhanced with memory/success/failure tracking
- [ ] Grafana templates created
- [ ] All tests passing (30/30)
- [ ] Documentation complete
- [ ] Demo script working

> **🎓 CHECKPOINT 8**: Complete end-to-end demo with all observability features

---

## 🚀 Next Steps

**Phase 8 Complete!** You now have:
- ✅ Production-grade observability
- ✅ Multi-format metrics export
- ✅ Automation hooks
- ✅ Grafana dashboards

**Optional Enhancements**:
- Real-time metrics server (HTTP endpoint)
- OpenTelemetry integration
- Email/Slack notifications
- Advanced alerting rules

**Continue to Phase 9**: SDK & Productization

---

**End of Phase 8 Developer Walkthrough**

🎉 Congratulations! ODIBI CORE now has enterprise-grade observability and automation capabilities!
