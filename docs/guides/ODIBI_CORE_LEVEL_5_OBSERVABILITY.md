# LEVEL 5: Observability & Monitoring

**Time**: 30-45 minutes  
**Goal**: Monitor pipeline performance, collect metrics, generate reports, and set up automation hooks

---

## 🎯 What You'll Learn

- Collect performance metrics with MetricsManager
- Register automation hooks with EventBus
- Generate interactive HTML execution reports (Stories)
- Export metrics to Prometheus
- Set up comprehensive pipeline monitoring

---

## The Observability Stack

```
┌────────────────────────────────────────────────────────────┐
│                    PIPELINE EXECUTION                      │
└──────────────────┬─────────────────────────────────────────┘
                   │
                   ▼
     ┌─────────────────────────────────────┐
     │   OBSERVABILITY STACK               │
     │                                     │
     ├──────────┬──────────┬──────────────┤
     │          │          │              │
     ▼          ▼          ▼              ▼
┌─────────┐┌──────────┐┌───────────┐┌─────────┐
│ Tracker ││ Metrics  ││ EventBus  ││ Logger  │
│         ││ Manager  ││           ││         │
└────┬────┘└────┬─────┘└─────┬─────┘└────┬────┘
     │          │            │           │
     ▼          ▼            ▼           ▼
┌─────────┐┌──────────┐┌───────────┐┌─────────┐
│Lineage  ││ Metrics  ││   Hooks   ││  Logs   │
│ JSON    ││   JSON   ││ (Alerts)  ││  Files  │
└────┬────┘└────┬─────┘└───────────┘└─────────┘
     │          │
     ▼          ▼
┌─────────┐┌──────────┐
│  HTML   ││Prometheus│
│ Story   ││  Format  │
└─────────┘└──────────┘
```

---

## 1. MetricsManager - Performance Tracking

### What Metrics Are Collected?

| Metric Type | Description | Example |
|-------------|-------------|---------|
| **NODE_DURATION** | Time each node takes (ms) | `read_csv: 4520ms` |
| **THROUGHPUT** | Rows processed per second | `15000 rows/sec` |
| **CACHE_HIT** | Cache hit count | `5 cache hits` |
| **CACHE_MISS** | Cache miss count | `2 cache misses` |
| **ERROR_COUNT** | Total errors | `3 errors` |
| **MEMORY_USAGE** | Memory consumed (MB) | `512 MB` |
| **DATA_SIZE** | DataFrame size (bytes) | `2.3 MB` |
| **ROW_COUNT** | Rows processed | `10000 rows` |

### Metrics Collection Flow

```
Node Execution Start
     │
     ├─ MetricsManager.record("node_start", step_name, timestamp)
     │
     ▼
Node Executing...
     │
     ├─ MetricsManager.record("memory_usage", step_name, 512)
     ├─ MetricsManager.record("row_count", step_name, 10000)
     │
     ▼
Node Execution End
     │
     ├─ MetricsManager.record("node_duration", step_name, 4520)
     ├─ MetricsManager.increment("cache_hit")  # or cache_miss
     │
     ▼
Pipeline Complete
     │
     ├─ MetricsManager.get_summary() → Returns all metrics
     ├─ MetricsManager.export_prometheus("metrics.txt")
     └─ MetricsManager.save_to_file("metrics.json")
```

### Using MetricsManager

```python
from odibi_core.orchestrator import Orchestrator
from odibi_core.metrics_manager import MetricsManager

# Create MetricsManager
metrics = MetricsManager()

# Use in orchestrator
orchestrator = Orchestrator(
    steps=steps,
    engine_type="pandas",
    metrics_manager=metrics  # Pass metrics manager
)

result = orchestrator.execute()

# Get metrics summary
summary = metrics.get_summary()

print("=== METRICS SUMMARY ===")
print(f"Total nodes: {summary['total_nodes']}")
print(f"Total duration: {summary['total_duration_ms']}ms")
print(f"Cache hit rate: {summary['cache_hit_rate']:.1%}")
print(f"Errors: {summary['error_count']}")

# Per-node metrics
for node_name, node_metrics in summary['nodes'].items():
    print(f"\n{node_name}:")
    print(f"  Duration: {node_metrics['duration_ms']}ms")
    print(f"  Rows: {node_metrics['row_count']}")
    print(f"  Memory: {node_metrics['memory_mb']}MB")
```

### Export to Prometheus

```python
# Export metrics in Prometheus format
metrics.export_prometheus("metrics_prometheus.txt")

# File content:
# # HELP odibi_node_duration_ms Node execution duration in milliseconds
# # TYPE odibi_node_duration_ms gauge
# odibi_node_duration_ms{node="read_customers"} 4520
# odibi_node_duration_ms{node="filter_data"} 1230
# 
# # HELP odibi_cache_hits Cache hit count
# # TYPE odibi_cache_hits counter
# odibi_cache_hits 5
# 
# # HELP odibi_cache_misses Cache miss count
# # TYPE odibi_cache_misses counter
# odibi_cache_misses 2
```

### Save Metrics to JSON

```python
# Save metrics as JSON
metrics.save_to_file("metrics.json")

# File content:
{
  "timestamp": "2024-05-01T12:30:00",
  "pipeline_name": "customer_pipeline",
  "total_duration_ms": 12450,
  "total_nodes": 7,
  "cache_hit_rate": 0.71,
  "error_count": 0,
  "nodes": {
    "read_customers": {
      "duration_ms": 4520,
      "row_count": 10000,
      "memory_mb": 45,
      "throughput": 2212
    },
    "filter_data": {
      "duration_ms": 1230,
      "row_count": 5000,
      "memory_mb": 22,
      "throughput": 4065
    }
  }
}
```

---

## 2. EventBus - Automation Hooks (Deep Dive)

### Event Types Reference

| Event | When | Use Cases |
|-------|------|-----------|
| **pipeline_start** | Pipeline begins | Log rotation, clear temp files, send "started" notification |
| **pipeline_complete** | Pipeline succeeds | Send success notification, trigger downstream jobs, update dashboard |
| **pipeline_error** | Pipeline fails | Send error alerts (Slack, email, PagerDuty), rollback changes |
| **node_start** | Node begins | Log node start time, update status dashboard |
| **node_complete** | Node succeeds | Update metrics, log completion, trigger node-specific actions |
| **node_error** | Node fails | Send error alert, log error details, trigger retry or fallback |

### Hook Priority System

```
EventBus processes hooks by priority:

CRITICAL (priority=1) → Executed first
HIGH     (priority=2)
MEDIUM   (priority=3) → Default
LOW      (priority=4) → Executed last
```

### Complete Hook Examples

#### Hook 1: Slack Notifications

```python
from odibi_core.event_bus import EventBus, EventPriority
import requests

def send_slack_notification(event_data):
    webhook_url = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
    
    if event_data['event_type'] == 'pipeline_start':
        message = f"🚀 Pipeline '{event_data['pipeline_name']}' started"
    elif event_data['event_type'] == 'pipeline_complete':
        message = f"✅ Pipeline completed in {event_data['duration_ms']}ms"
    elif event_data['event_type'] == 'pipeline_error':
        message = f"🚨 Pipeline FAILED: {event_data['error_message']}"
    
    payload = {"text": message}
    requests.post(webhook_url, json=payload)

# Register hook
event_bus = EventBus()
event_bus.register_hook("pipeline_start", send_slack_notification, EventPriority.HIGH)
event_bus.register_hook("pipeline_complete", send_slack_notification, EventPriority.HIGH)
event_bus.register_hook("pipeline_error", send_slack_notification, EventPriority.CRITICAL)
```

#### Hook 2: Metrics Dashboard Update

```python
def update_dashboard(event_data):
    if event_data['event_type'] == 'node_complete':
        node_name = event_data['step_name']
        duration = event_data['duration_ms']
        
        # Update Grafana/custom dashboard
        # POST to dashboard API
        dashboard_api = "https://dashboard.example.com/api/metrics"
        requests.post(dashboard_api, json={
            "node": node_name,
            "duration": duration,
            "timestamp": event_data['timestamp']
        })

event_bus.register_hook("node_complete", update_dashboard, EventPriority.MEDIUM)
```

#### Hook 3: Data Quality Alerts

```python
def data_quality_check(event_data):
    if event_data['event_type'] == 'node_complete':
        row_count = event_data.get('row_count', 0)
        
        # Alert if too few rows
        if row_count < 100:
            print(f"⚠️  WARNING: Node '{event_data['step_name']}' produced only {row_count} rows")
            # Send alert to monitoring system

event_bus.register_hook("node_complete", data_quality_check, EventPriority.HIGH)
```

#### Hook 4: Auto-Cleanup

```python
import shutil

def cleanup_temp_files(event_data):
    if event_data['event_type'] == 'pipeline_complete':
        # Clean up temporary files
        temp_dir = "temp/"
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            print(f"🧹 Cleaned up {temp_dir}")

event_bus.register_hook("pipeline_complete", cleanup_temp_files, EventPriority.LOW)
```

---

## 3. Story Generator - HTML Execution Reports

### What is a Story?

An **interactive HTML report** showing:
- Pipeline summary (duration, success/failure)
- Step-by-step execution cards
- Schema diffs (before/after)
- Sample data (first 5 rows)
- Timing breakdown
- DAG visualization (optional)

### Story Generation Flow

```
Pipeline Execution
     │
     ├─ Tracker captures lineage (before/after snapshots)
     │
     ▼
Tracker.export_lineage("lineage.json")
     │
     ▼
StoryGenerator.generate_story("lineage.json", output="story.html")
     │
     ▼
Interactive HTML Report Generated
     │
     └─ Open in browser: story.html
```

### Story Features

```
┌────────────────────────────────────────────────────────┐
│            PIPELINE EXECUTION STORY                    │
│  customer_pipeline - May 1, 2024 12:30:00             │
│  Status: ✅ SUCCESS    Duration: 12.5s                 │
├────────────────────────────────────────────────────────┤
│                                                        │
│  ┌──────────────────────────────────────────────┐    │
│  │ Step 1: read_customers                       │    │
│  │ Layer: ingest    Duration: 4.5s             │    │
│  ├──────────────────────────────────────────────┤    │
│  │ BEFORE: No data                              │    │
│  │ AFTER:  10,000 rows, 3 columns               │    │
│  │                                               │    │
│  │ Schema:                                       │    │
│  │   + customer_id (int64)                      │    │
│  │   + name (string)                            │    │
│  │   + email (string)                           │    │
│  │                                               │    │
│  │ Sample Data: [Click to expand]               │    │
│  │   customer_id | name  | email                │    │
│  │   1          | Alice | alice@example.com    │    │
│  │   2          | Bob   | bob@example.com      │    │
│  └──────────────────────────────────────────────┘    │
│                                                        │
│  ┌──────────────────────────────────────────────┐    │
│  │ Step 2: filter_active_customers              │    │
│  │ Layer: transform    Duration: 1.2s          │    │
│  ├──────────────────────────────────────────────┤    │
│  │ BEFORE: 10,000 rows, 3 columns               │    │
│  │ AFTER:  5,000 rows, 3 columns                │    │
│  │                                               │    │
│  │ Schema Diff:                                  │    │
│  │   (No schema changes)                        │    │
│  │                                               │    │
│  │ Rows: -5,000 (filtered out)                  │    │
│  └──────────────────────────────────────────────┘    │
│                                                        │
│  ... (more steps)                                     │
└────────────────────────────────────────────────────────┘
```

### Generate Story

```python
from odibi_core.orchestrator import Orchestrator
from odibi_core.story_generator import StoryGenerator

# Execute pipeline with tracker
orchestrator = Orchestrator(
    steps=steps,
    engine_type="pandas",
    enable_tracker=True
)

result = orchestrator.execute()

# Export lineage
result['tracker'].export_lineage("lineage.json")

# Generate HTML story
story_gen = StoryGenerator()
story_gen.generate_story(
    lineage_file="lineage.json",
    output_file="execution_story.html",
    title="Customer Pipeline Execution"
)

print("Story generated: execution_story.html")
# Open in browser to view
```

### Auto-Generate Story on Completion

```python
from odibi_core.event_bus import EventBus
from odibi_core.story_generator import StoryGenerator

def generate_story_hook(event_data):
    # Triggered on pipeline_complete
    tracker = event_data.get('tracker')
    if tracker:
        tracker.export_lineage("lineage.json")
        
        story_gen = StoryGenerator()
        story_gen.generate_story("lineage.json", output_file="story.html")
        
        print("✅ Story generated: story.html")

event_bus = EventBus()
event_bus.register_hook("pipeline_complete", generate_story_hook)

orchestrator = Orchestrator(
    steps=steps,
    engine_type="pandas",
    enable_tracker=True,
    event_bus=event_bus
)

result = orchestrator.execute()
# Story auto-generated on completion
```

---

## 4. Complete Observability Example

```python
from odibi_core.orchestrator import Orchestrator
from odibi_core.event_bus import EventBus, EventPriority
from odibi_core.metrics_manager import MetricsManager
from odibi_core.story_generator import StoryGenerator

# ──────────────────────────────────────────────────────
# 1. Setup MetricsManager
# ──────────────────────────────────────────────────────
metrics = MetricsManager()

# ──────────────────────────────────────────────────────
# 2. Setup EventBus with Hooks
# ──────────────────────────────────────────────────────
event_bus = EventBus()

# Hook: Log all events
def log_event(event_data):
    event_type = event_data['event_type']
    print(f"[EVENT] {event_type}: {event_data}")

event_bus.register_hook("pipeline_start", log_event)
event_bus.register_hook("pipeline_complete", log_event)
event_bus.register_hook("node_start", log_event)
event_bus.register_hook("node_complete", log_event)
event_bus.register_hook("node_error", log_event)

# Hook: Alert on errors
def error_alert(event_data):
    step_name = event_data['step_name']
    error_msg = event_data['error_message']
    print(f"🚨 CRITICAL ERROR in {step_name}: {error_msg}")
    # Send to Slack, email, etc.

event_bus.register_hook("node_error", error_alert, EventPriority.CRITICAL)

# Hook: Generate story on completion
def auto_generate_story(event_data):
    tracker = event_data.get('tracker')
    if tracker:
        tracker.export_lineage("lineage.json")
        story_gen = StoryGenerator()
        story_gen.generate_story("lineage.json", "story.html")
        print("✅ Story generated: story.html")

event_bus.register_hook("pipeline_complete", auto_generate_story)

# ──────────────────────────────────────────────────────
# 3. Create Orchestrator with Full Observability
# ──────────────────────────────────────────────────────
orchestrator = Orchestrator(
    steps=steps,
    engine_type="pandas",
    
    # Tracking
    enable_tracker=True,
    
    # Metrics
    metrics_manager=metrics,
    
    # Events & Hooks
    event_bus=event_bus
)

# ──────────────────────────────────────────────────────
# 4. Execute Pipeline
# ──────────────────────────────────────────────────────
result = orchestrator.execute()

# ──────────────────────────────────────────────────────
# 5. Export Metrics
# ──────────────────────────────────────────────────────
# Save as JSON
metrics.save_to_file("metrics.json")

# Export to Prometheus
metrics.export_prometheus("metrics_prometheus.txt")

# Print summary
summary = metrics.get_summary()
print("\n=== METRICS SUMMARY ===")
print(f"Total duration: {summary['total_duration_ms']}ms")
print(f"Cache hit rate: {summary['cache_hit_rate']:.1%}")
print(f"Errors: {summary['error_count']}")

# ──────────────────────────────────────────────────────
# 6. View Artifacts
# ──────────────────────────────────────────────────────
# - story.html (interactive execution report)
# - lineage.json (Tracker lineage)
# - metrics.json (metrics summary)
# - metrics_prometheus.txt (Prometheus format)
```

---

## Try It Yourself

### Exercise 1: Custom Metrics Hook

Create a hook that tracks the slowest node:

```python
slowest_node = {"name": None, "duration": 0}

def track_slowest_node(event_data):
    global slowest_node
    duration = event_data['duration_ms']
    step_name = event_data['step_name']
    
    if duration > slowest_node['duration']:
        slowest_node = {"name": step_name, "duration": duration}

event_bus.register_hook("node_complete", track_slowest_node)

# After execution
print(f"Slowest node: {slowest_node['name']} ({slowest_node['duration']}ms)")
```

### Exercise 2: Data Quality Monitoring

Track row counts across all nodes and alert if any node produces 0 rows:

```python
def check_row_count(event_data):
    row_count = event_data.get('row_count', 0)
    if row_count == 0:
        print(f"⚠️  WARNING: {event_data['step_name']} produced 0 rows!")

event_bus.register_hook("node_complete", check_row_count)
```

### Exercise 3: Generate and View Story

Run your pipeline with Tracker enabled, generate a story, and open it in your browser.

---

## Key Takeaways

| Concept | What You Learned |
|---------|-----------------|
| **MetricsManager** | Collect performance metrics, export to JSON/Prometheus |
| **EventBus** | 6 event types, custom hooks, priorities |
| **StoryGenerator** | Generate interactive HTML execution reports |
| **Complete Observability** | Combine Tracker + Metrics + Events + Stories |

---

## What's Next?

**Level 6: I/O & Integrations** - Work with different file formats, connect to databases, integrate with cloud storage, and manage secrets.

[Continue to Level 6 →](ODIBI_CORE_LEVEL_6_IO_INTEGRATIONS.md)

---

## Summary

✅ You can collect and export performance metrics  
✅ You can register automation hooks for alerts and actions  
✅ You can generate interactive HTML execution reports  
✅ You understand the complete observability stack  
✅ You can set up production-grade monitoring
