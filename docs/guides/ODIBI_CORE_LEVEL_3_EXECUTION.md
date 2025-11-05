# LEVEL 3: Understanding Execution

**Time**: 30-45 minutes  
**Goal**: Understand how DAGExecutor orchestrates nodes, how Tracker captures details, and EventBus lifecycle

---

## 🎯 What You'll Learn

- How DAGExecutor orchestrates node execution
- Node lifecycle and state transitions
- How Tracker captures lineage and snapshots
- EventBus hooks and lifecycle events
- Parallel execution of independent nodes

---

## Execution Flow - How It All Works

```
┌────────────────────────────────────────────────────────────────┐
│ YOU: Define Steps                                              │
│ steps = [Step(...), Step(...), Step(...)]                     │
└──────────────────────┬─────────────────────────────────────────┘
                       │
                       ▼
┌────────────────────────────────────────────────────────────────┐
│ DAGBuilder: Convert Steps → DAG Graph                         │
│                                                                 │
│ Analyzes dependencies based on inputs/outputs:                │
│ - Step A outputs "raw_data"                                   │
│ - Step B inputs "raw_data" → B depends on A                   │
│                                                                 │
│ Result: DAG with nodes and edges                              │
└──────────────────────┬─────────────────────────────────────────┘
                       │
                       ▼
┌────────────────────────────────────────────────────────────────┐
│ Orchestrator: Set Up Execution Environment                    │
│                                                                 │
│ Creates:                                                       │
│ ├─ EngineContext (PandasEngineContext or SparkEngineContext) │
│ ├─ Tracker (captures lineage & snapshots)                    │
│ ├─ EventBus (hooks & events)                                 │
│ ├─ CheckpointManager (optional - resume on failure)          │
│ ├─ CacheManager (optional - skip redundant work)             │
│ └─ data_map = {} (shared DataFrame dictionary)               │
└──────────────────────┬─────────────────────────────────────────┘
                       │
                       ▼
┌────────────────────────────────────────────────────────────────┐
│ DAGExecutor: Execute Nodes in Topological Order               │
│                                                                 │
│ LOOP until all nodes complete:                                │
│   1. Get ready nodes (no pending dependencies)                │
│   2. FOR EACH ready node (can run in parallel):               │
│      ├─ Check cache (hit? → restore to data_map, skip)       │
│      ├─ Emit event: node_start                               │
│      ├─ Tracker: start_step() - capture "before" snapshot    │
│      ├─ Execute: node.run(context, data_map)                 │
│      ├─ Tracker: end_step() - capture "after" snapshot       │
│      ├─ Save to cache (for future runs)                      │
│      ├─ Emit event: node_complete                            │
│      └─ Update dependencies (mark node complete)             │
│   3. Handle failures (retry or mark failed)                   │
│   4. Save checkpoint (if enabled)                             │
│                                                                 │
│ RETURN result (success, nodes_executed, failed_nodes, etc.)  │
└────────────────────────────────────────────────────────────────┘
```

---

## Node Lifecycle - State Transitions

Every node goes through states during execution:

```
┌──────────┐
│ PENDING  │ ◀─── Initial state: Node waiting for dependencies
└────┬─────┘
     │ Dependencies satisfied
     ▼
┌──────────┐
│ READY    │ ◀─── Node can execute (no pending dependencies)
└────┬─────┘
     │ DAGExecutor picks node
     ▼
┌──────────┐
│ RUNNING  │ ◀─── Node.run() executing
└────┬─────┘
     │
     ├───────────────┐
     │               │
     ▼               ▼
┌──────────┐    ┌─────────┐
│ CACHED   │    │EXECUTING│ ◀─── Cache miss, actually running
└────┬─────┘    └────┬────┘
     │               │
     │               ├────────────┐
     │               │            │
     │               ▼            ▼
     │          ┌─────────┐  ┌────────┐
     │          │ SUCCESS │  │ FAILED │
     │          └────┬────┘  └───┬────┘
     │               │           │
     │               │           │ Retry?
     │               │           ├─ Yes → Back to RUNNING
     │               │           └─ No  → FAILED (final)
     │               │
     └───────────────┴───────────▶ Pipeline continues
```

### State Details

| State | Description | What Happens |
|-------|-------------|--------------|
| **PENDING** | Waiting for dependencies | Node cannot run yet (upstream nodes not complete) |
| **READY** | Ready to execute | No pending dependencies, queued for execution |
| **RUNNING** | Executing | Node.run() is being called |
| **CACHED** | Cache hit | Output restored from cache, execution skipped ✓ |
| **EXECUTING** | Cache miss | Actually running the node logic |
| **SUCCESS** | Completed successfully | Output written to data_map, downstream nodes unblocked |
| **FAILED** | Execution failed | Error occurred, retry or fail pipeline |

---

## Tracker - Capturing Execution Lineage

The Tracker captures **everything** that happens during execution:

### What Tracker Captures

```
For EACH node execution, Tracker records:

┌─────────────────────────────────────────────────────────────┐
│ BEFORE Snapshot (Tracker.start_step())                     │
│ ├─ DataFrame schema (columns, types)                       │
│ ├─ Row count                                               │
│ └─ Sample data (first 5 rows)                              │
└─────────────────────────────────────────────────────────────┘
              │
              ▼  Node executes
┌─────────────────────────────────────────────────────────────┐
│ AFTER Snapshot (Tracker.end_step())                        │
│ ├─ DataFrame schema (columns, types)                       │
│ ├─ Row count                                               │
│ ├─ Sample data (first 5 rows)                              │
│ ├─ Execution time (start → end)                            │
│ ├─ Schema diff (added/removed/changed columns)             │
│ ├─ Row delta (rows added/removed)                          │
│ └─ Status (SUCCESS, FAILED, CACHED)                        │
└─────────────────────────────────────────────────────────────┘
```

### Tracker Output - Lineage JSON

After execution, Tracker can export lineage:

```json
{
  "pipeline_name": "customer_pipeline",
  "execution_id": "exec_20240501_120000",
  "start_time": "2024-05-01T12:00:00",
  "end_time": "2024-05-01T12:05:30",
  "total_duration_ms": 330000,
  "steps": [
    {
      "step_name": "read_customers",
      "layer": "ingest",
      "status": "SUCCESS",
      "start_time": "2024-05-01T12:00:01",
      "end_time": "2024-05-01T12:00:05",
      "duration_ms": 4000,
      "before_snapshot": {
        "schema": [],
        "row_count": 0,
        "sample": []
      },
      "after_snapshot": {
        "schema": ["customer_id: int64", "name: string", "email: string"],
        "row_count": 10000,
        "sample": [
          {"customer_id": 1, "name": "Alice", "email": "alice@example.com"},
          {"customer_id": 2, "name": "Bob", "email": "bob@example.com"}
        ]
      },
      "schema_diff": {
        "added": ["customer_id", "name", "email"],
        "removed": [],
        "changed": []
      },
      "row_delta": 10000
    }
  ]
}
```

### Using Tracker

```python
from odibi_core.orchestrator import Orchestrator

orchestrator = Orchestrator(
    steps=steps,
    engine_type="pandas",
    enable_tracker=True  # ← Enable Tracker
)

result = orchestrator.execute()

# Access Tracker
tracker = result['tracker']

# Export lineage
tracker.export_lineage("lineage_output.json")

# Get execution summary
print(f"Total steps: {len(tracker.step_executions)}")
for step_exec in tracker.step_executions:
    print(f"{step_exec.step_name}: {step_exec.duration_ms}ms, {step_exec.row_delta} rows")
```

---

## EventBus - Lifecycle Hooks

The EventBus emits events during pipeline execution and allows you to register hooks (callbacks).

### Event Types

| Event | When Emitted | Data Included |
|-------|--------------|---------------|
| **pipeline_start** | Pipeline begins | `pipeline_name`, `start_time`, `total_steps` |
| **pipeline_complete** | Pipeline finishes successfully | `duration_ms`, `nodes_executed`, `success_count` |
| **pipeline_error** | Pipeline fails fatally | `error_message`, `failed_step` |
| **node_start** | Node execution begins | `step_name`, `layer`, `start_time` |
| **node_complete** | Node completes successfully | `step_name`, `duration_ms`, `row_count`, `status` |
| **node_error** | Node fails | `step_name`, `error_message`, `retry_count` |

### Event Flow During Execution

```
DAGExecutor.execute()
     │
     ├─ emit("pipeline_start", {pipeline_name, start_time, total_steps})
     │       │
     │       └──▶ Registered hooks called (e.g., log rotation, send alert)
     │
     ├─ For each node:
     │    │
     │    ├─ emit("node_start", {step_name, layer})
     │    │       │
     │    │       └──▶ Hooks called (e.g., log "Starting step X")
     │    │
     │    ├─ node.run(context, data_map)
     │    │
     │    ├─ emit("node_complete", {step_name, duration_ms, status})
     │    │       │
     │    │       └──▶ Hooks called (e.g., update metrics dashboard)
     │    │
     │    └─ (if error) emit("node_error", {step_name, error_message})
     │                      │
     │                      └──▶ Hooks called (e.g., send alert to Slack)
     │
     └─ emit("pipeline_complete", {duration_ms, nodes_executed})
              │
              └──▶ Hooks called (e.g., send success notification)
```

### Registering Hooks

```python
from odibi_core.event_bus import EventBus, EventPriority

# Create EventBus
event_bus = EventBus()

# Define custom hook function
def send_slack_alert(event_data):
    print(f"[SLACK] Pipeline started: {event_data['pipeline_name']}")
    # In production: send actual Slack message

def log_node_completion(event_data):
    print(f"[LOG] Node {event_data['step_name']} completed in {event_data['duration_ms']}ms")

# Register hooks
event_bus.register_hook(
    event_type="pipeline_start",
    hook_func=send_slack_alert,
    priority=EventPriority.HIGH
)

event_bus.register_hook(
    event_type="node_complete",
    hook_func=log_node_completion,
    priority=EventPriority.MEDIUM
)

# Use in Orchestrator
orchestrator = Orchestrator(
    steps=steps,
    engine_type="pandas",
    event_bus=event_bus  # ← Pass custom EventBus
)

result = orchestrator.execute()
```

### Built-in Hook Helpers

```python
from odibi_core.event_bus import create_summary_hook, create_metrics_export_hook

# Create summary hook (prints execution summary)
summary_hook = create_summary_hook()
event_bus.register_hook("pipeline_complete", summary_hook)

# Create metrics export hook (saves metrics to file)
metrics_hook = create_metrics_export_hook(output_path="metrics.json")
event_bus.register_hook("pipeline_complete", metrics_hook)
```

---

## Parallel Execution

DAGExecutor can execute **independent nodes in parallel**:

```
Sequential Execution (default):

Layer 1:  [Node A] → done
          [Node B] → done
          [Node C] → done
          
Total Time = Time(A) + Time(B) + Time(C)

────────────────────────────────────────────────

Parallel Execution (independent nodes):

Layer 1:  [Node A] ┐
          [Node B] ├─ All run simultaneously
          [Node C] ┘
          
Total Time = max(Time(A), Time(B), Time(C))
```

### When Nodes Run in Parallel

Nodes run in parallel when:
1. They are in the same DAG layer (same dependency depth)
2. They have no dependencies on each other
3. They are READY state simultaneously

### Example

```python
steps = [
    # These 3 nodes have NO dependencies - run in parallel
    Step(layer="ingest", name="read_customers", ...),
    Step(layer="ingest", name="read_orders", ...),
    Step(layer="ingest", name="read_products", ...),
    
    # This node depends on all 3 above - waits for all to complete
    Step(layer="transform", name="join_all", inputs={
        "customers": "raw_customers",
        "orders": "raw_orders",
        "products": "raw_products"
    }, ...)
]
```

**Execution**:
1. Nodes `read_customers`, `read_orders`, `read_products` run **in parallel** (Layer 0)
2. Node `join_all` waits for all 3 to complete (Layer 1)

---

## Code Examples

### Example 1: View Tracker Snapshots

```python
orchestrator = Orchestrator(steps=steps, engine_type="pandas", enable_tracker=True)
result = orchestrator.execute()

tracker = result['tracker']

# Examine snapshots for a specific step
for step_exec in tracker.step_executions:
    if step_exec.step_name == "filter_customers":
        print(f"Before: {step_exec.before_snapshot.row_count} rows")
        print(f"After: {step_exec.after_snapshot.row_count} rows")
        print(f"Rows removed: {step_exec.before_snapshot.row_count - step_exec.after_snapshot.row_count}")
        print(f"Schema diff: {step_exec.schema_diff}")
```

### Example 2: Custom Error Alert Hook

```python
def error_alert_hook(event_data):
    step_name = event_data['step_name']
    error_msg = event_data['error_message']
    print(f"🚨 ERROR ALERT 🚨")
    print(f"Step '{step_name}' failed: {error_msg}")
    # In production: send email, Slack, PagerDuty, etc.

event_bus = EventBus()
event_bus.register_hook("node_error", error_alert_hook, priority=EventPriority.CRITICAL)

orchestrator = Orchestrator(steps=steps, engine_type="pandas", event_bus=event_bus)
result = orchestrator.execute()
```

### Example 3: Export and Visualize Lineage

```python
# Execute pipeline
orchestrator = Orchestrator(steps=steps, engine_type="pandas", enable_tracker=True)
result = orchestrator.execute()

# Export lineage
result['tracker'].export_lineage("pipeline_lineage.json")

# Later: Load and analyze
import json
with open("pipeline_lineage.json", "r") as f:
    lineage = json.load(f)

print(f"Pipeline: {lineage['pipeline_name']}")
print(f"Total duration: {lineage['total_duration_ms']}ms")
for step in lineage['steps']:
    print(f"  - {step['step_name']}: {step['duration_ms']}ms, {step['row_delta']} rows")
```

---

## Try It Yourself

### Exercise 1: Track Schema Changes

Build a pipeline that:
1. Reads a CSV
2. Adds a column using SQL (`SELECT *, 100 as new_column FROM bronze`)
3. Drops a column using SQL (`SELECT col1, col2 FROM bronze`)
4. Use Tracker to see schema diffs

### Exercise 2: Create Node Timing Hook

Register a hook that logs the duration of each node:

```python
def timing_hook(event_data):
    print(f"⏱️  {event_data['step_name']}: {event_data['duration_ms']}ms")

event_bus.register_hook("node_complete", timing_hook)
```

### Exercise 3: Parallel Execution

Create a pipeline with 3 IngestNodes that read different CSVs, then join them. Observe that the 3 reads happen in parallel.

---

## Key Takeaways

| Concept | What You Learned |
|---------|-----------------|
| **Execution Flow** | Steps → DAGBuilder → DAG → Orchestrator → DAGExecutor |
| **Node Lifecycle** | PENDING → READY → RUNNING → CACHED/EXECUTING → SUCCESS/FAILED |
| **Tracker** | Captures before/after snapshots, schema diffs, timing, lineage |
| **EventBus** | 6 event types, custom hooks, automation |
| **Parallel Execution** | Independent nodes run simultaneously for speed |

---

## What's Next?

**Level 4: Making It Reliable** - Use checkpoints to resume failed pipelines, enable caching to speed up development, and configure retry logic.

[Continue to Level 4 →](ODIBI_CORE_LEVEL_4_RELIABILITY.md)

---

## Summary

✅ You understand how DAGExecutor orchestrates execution  
✅ You know the node lifecycle states  
✅ You can use Tracker to capture and analyze lineage  
✅ You can register EventBus hooks for automation  
✅ You understand parallel execution of independent nodes
