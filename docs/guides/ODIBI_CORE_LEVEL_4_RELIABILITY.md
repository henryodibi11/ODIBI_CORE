# LEVEL 4: Making It Reliable

**Time**: 30-45 minutes  
**Goal**: Build fault-tolerant pipelines with checkpoints, caching, and retry logic

---

## 🎯 What You'll Learn

- Use checkpoints to resume failed pipelines
- Enable caching to speed up development
- Configure retry logic for transient failures
- Handle errors gracefully
- Build production-ready, resilient pipelines

---

## The Three Pillars of Reliability

```
┌────────────────────────────────────────────────────────────┐
│                   RELIABLE PIPELINE                        │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ CHECKPOINTS  │  │    CACHE     │  │    RETRY     │    │
│  │              │  │              │  │              │    │
│  │ Resume from  │  │ Skip         │  │ Automatic    │    │
│  │ failures     │  │ unchanged    │  │ retry on     │    │
│  │              │  │ steps        │  │ transient    │    │
│  │              │  │              │  │ errors       │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                            │
│  Save state      Speed up          Handle              │
│  periodically    development       temporary issues    │
└────────────────────────────────────────────────────────────┘
```

---

## 1. Checkpoint System

### What is a Checkpoint?

A checkpoint is a **snapshot of pipeline state** saved to disk. If a pipeline fails, you can resume from the last checkpoint instead of starting over.

```
Normal Execution (no checkpoints):

[Node A] → [Node B] → [Node C] → [Node D] → [Node E]
                             ❌ CRASH
                             
Restart: Start from Node A again (wasted work!)

────────────────────────────────────────────────────────

With Checkpoints:

[Node A] → [Node B] ✓ (checkpoint saved)
         → [Node C] ✓ (checkpoint saved)
         → [Node D] ❌ CRASH
         
Resume: Load checkpoint → Start from Node D (skip A, B, C)
```

### Checkpoint Modes

| Mode | When Checkpoint Saved | Use Case | Overhead |
|------|----------------------|----------|----------|
| **MANUAL** | User calls `save()` | Full control, minimal overhead | Low |
| **AUTO** | After every successful node | Maximum safety | High |
| **INTERVAL** | Every N seconds | Balance safety/performance | Medium |
| **LAYER** | After each DAG layer completes | Natural boundaries (Bronze→Silver→Gold) | Low |

### Checkpoint Architecture

```
┌────────────────────────────────────────────────────────────┐
│ During Execution                                           │
│                                                            │
│ Node completes successfully                                │
│         │                                                  │
│         ▼                                                  │
│ CheckpointManager.save()                                   │
│         │                                                  │
│         ▼                                                  │
│ Save to JSON file:                                         │
│ {                                                          │
│   "checkpoint_id": "ckpt_20240501_120530",                │
│   "pipeline_name": "customer_pipeline",                   │
│   "timestamp": "2024-05-01T12:05:30",                     │
│   "completed_nodes": ["read_csv", "filter_data"],        │
│   "pending_nodes": ["aggregate", "save_parquet"],        │
│   "failed_nodes": [],                                     │
│   "data_map_keys": ["raw_data", "filtered_data"]         │
│ }                                                          │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│ Resume Execution                                           │
│                                                            │
│ CheckpointManager.load_latest()                            │
│         │                                                  │
│         ▼                                                  │
│ Read checkpoint JSON                                       │
│         │                                                  │
│         ▼                                                  │
│ DAGExecutor resumes:                                       │
│ ├─ Skip completed_nodes (already done ✓)                  │
│ ├─ Retry failed_nodes (optional)                          │
│ └─ Execute pending_nodes (continue where left off)        │
└────────────────────────────────────────────────────────────┘
```

### Using Checkpoints

```python
from odibi_core.orchestrator import Orchestrator
from odibi_core.checkpoint_manager import CheckpointMode

# Enable AUTO checkpoints (save after every node)
orchestrator = Orchestrator(
    steps=steps,
    engine_type="pandas",
    enable_checkpoints=True,
    checkpoint_mode=CheckpointMode.AUTO,  # Save after each node
    checkpoint_dir="checkpoints/"
)

result = orchestrator.execute()
```

### Resume from Checkpoint

```python
# Pipeline failed mid-execution, now resume
orchestrator = Orchestrator(
    steps=steps,
    engine_type="pandas",
    enable_checkpoints=True,
    checkpoint_mode=CheckpointMode.AUTO,
    checkpoint_dir="checkpoints/",
    resume_from_checkpoint=True  # ← Resume from last checkpoint
)

result = orchestrator.execute()
# Skips completed nodes, continues from where it failed
```

### LAYER Checkpoints (Recommended for Medallion)

```python
# Save checkpoint after each DAG layer (e.g., after Bronze, after Silver)
orchestrator = Orchestrator(
    steps=steps,
    engine_type="spark",
    enable_checkpoints=True,
    checkpoint_mode=CheckpointMode.LAYER,  # Save per layer
    checkpoint_dir="checkpoints/"
)

# If pipeline fails in Silver, resume will skip Bronze layer
```

---

## 2. Cache System

### What is Caching?

Caching **stores node outputs** so unchanged steps can be skipped on subsequent runs. Huge time-saver during development!

```
First Run (no cache):

[Read CSV] → Execute (10s)
[Filter]   → Execute (5s)
[Aggregate]→ Execute (8s)

Total: 23 seconds

────────────────────────────────────────────────────────

Second Run (with cache, no changes):

[Read CSV] → Cache HIT ✓ (skip, <1s)
[Filter]   → Cache HIT ✓ (skip, <1s)
[Aggregate]→ Cache HIT ✓ (skip, <1s)

Total: <3 seconds (8x faster!)

────────────────────────────────────────────────────────

Third Run (change only Aggregate step):

[Read CSV] → Cache HIT ✓ (skip)
[Filter]   → Cache HIT ✓ (skip)
[Aggregate]→ Cache MISS ❌ (changed, re-execute)

Total: ~8 seconds (only Aggregate runs)
```

### How Cache Keys Work

```
Cache key calculated from:
├─ Step name
├─ Step parameters (value, params, inputs, outputs)
├─ Input data hash (hash of input DataFrames)
└─ Engine type

If ANY of these change → Cache MISS (re-execute)
If ALL match → Cache HIT (restore from cache)
```

### Cache System Types

| Type | Storage | Use Case |
|------|---------|----------|
| **Local Cache** | Disk (local filesystem) | Development, single machine |
| **Cloud Cache** | Azure Blob / S3 | Production, shared across runs/machines |

### Using Cache

```python
from odibi_core.orchestrator import Orchestrator

# Enable local cache
orchestrator = Orchestrator(
    steps=steps,
    engine_type="pandas",
    enable_cache=True,
    cache_dir="cache/"  # Local cache directory
)

result = orchestrator.execute()

# First run: All nodes execute, outputs cached
# Second run: Cache hits, nodes skipped!
```

### Cloud Cache (Azure)

```python
from odibi_core.cache_manager import CloudCacheManager

# Create cloud cache manager
cloud_cache = CloudCacheManager(
    cloud_provider="azure",
    container="pipeline-cache",
    account_name="mystorageaccount",
    account_key="..."
)

orchestrator = Orchestrator(
    steps=steps,
    engine_type="spark",
    cache_manager=cloud_cache  # Use cloud cache
)

result = orchestrator.execute()
```

### Cache Invalidation

Cache automatically invalidates when:
- Step parameters change
- Input data changes
- Step code/function changes (for function transforms)

**Manual invalidation**:

```python
from odibi_core.cache_manager import CacheManager

cache = CacheManager(cache_dir="cache/")

# Clear specific step cache
cache.invalidate("step_name")

# Clear all cache
cache.clear_all()
```

---

## 3. Retry Logic

### What is Retry?

Automatic retry on **transient failures** (network issues, temporary resource unavailability).

```
Node Execution:

Attempt 1: ❌ FAILED (network timeout)
           │
           ├─ Retry count (1) < max_retries (3)? YES
           │
Attempt 2: ❌ FAILED (connection refused)
           │
           ├─ Retry count (2) < max_retries (3)? YES
           │
Attempt 3: ✓ SUCCESS
           │
           └─ Node completes successfully

────────────────────────────────────────────────────────

Max Retries Exceeded:

Attempt 1: ❌ FAILED
Attempt 2: ❌ FAILED
Attempt 3: ❌ FAILED
           │
           ├─ Retry count (3) = max_retries (3)
           │
           └─ Mark node as FAILED (final)
                  │
                  └─ Emit "node_error" event (triggers alerts)
```

### Retry Configuration

```python
from odibi_core.orchestrator import Orchestrator

orchestrator = Orchestrator(
    steps=steps,
    engine_type="pandas",
    max_retries=3,           # Retry up to 3 times
    retry_delay=5,           # Wait 5 seconds between retries
    retry_backoff=True       # Exponential backoff (5s, 10s, 20s)
)

result = orchestrator.execute()
```

### Retry Backoff

```
Without Backoff (retry_backoff=False):

Attempt 1: Fail → Wait 5s
Attempt 2: Fail → Wait 5s
Attempt 3: Fail → Wait 5s

────────────────────────────────────────────────────────

With Backoff (retry_backoff=True):

Attempt 1: Fail → Wait 5s
Attempt 2: Fail → Wait 10s (2x)
Attempt 3: Fail → Wait 20s (4x)

Better for transient issues (gives system time to recover)
```

### Per-Node Retry Configuration

```python
# Different retry settings for different nodes
Step(
    layer="ingest",
    name="read_from_api",
    type="config_op",
    engine="pandas",
    value="https://api.example.com/data",
    params={
        "source_type": "http",
        "max_retries": 5,      # API calls: retry more
        "retry_delay": 10
    }
)

Step(
    layer="transform",
    name="aggregate_data",
    type="sql",
    engine="pandas",
    value="SELECT ...",
    params={
        "max_retries": 1       # Aggregations: retry less
    }
)
```

---

## Error Handling Strategies

### Strategy 1: Fail Fast (Default)

```python
# Any node failure → entire pipeline fails
orchestrator = Orchestrator(
    steps=steps,
    engine_type="pandas",
    fail_fast=True  # Stop on first error
)
```

### Strategy 2: Continue on Error

```python
# Continue executing independent nodes even if some fail
orchestrator = Orchestrator(
    steps=steps,
    engine_type="pandas",
    fail_fast=False  # Continue despite errors
)

result = orchestrator.execute()

# Check which nodes failed
print(f"Failed nodes: {result['failed_nodes']}")
print(f"Successful nodes: {result['successful_nodes']}")
```

### Strategy 3: Error Hooks

```python
from odibi_core.event_bus import EventBus

def error_notification(event_data):
    step_name = event_data['step_name']
    error = event_data['error_message']
    print(f"🚨 ALERT: {step_name} failed: {error}")
    # Send to Slack, email, PagerDuty, etc.

event_bus = EventBus()
event_bus.register_hook("node_error", error_notification)

orchestrator = Orchestrator(
    steps=steps,
    engine_type="pandas",
    event_bus=event_bus
)
```

---

## Complete Example: Production-Ready Pipeline

```python
from odibi_core.orchestrator import Orchestrator
from odibi_core.checkpoint_manager import CheckpointMode
from odibi_core.event_bus import EventBus, EventPriority

# Define error alert hook
def send_error_alert(event_data):
    print(f"🚨 ERROR: {event_data['step_name']} failed: {event_data['error_message']}")
    # In production: send to Slack, PagerDuty, etc.

# Setup EventBus
event_bus = EventBus()
event_bus.register_hook("node_error", send_error_alert, priority=EventPriority.CRITICAL)

# Create orchestrator with ALL reliability features
orchestrator = Orchestrator(
    steps=steps,
    engine_type="spark",
    
    # Checkpoints: Save after each layer
    enable_checkpoints=True,
    checkpoint_mode=CheckpointMode.LAYER,
    checkpoint_dir="checkpoints/",
    
    # Cache: Enable for faster dev cycles
    enable_cache=True,
    cache_dir="cache/",
    
    # Retry: 3 attempts with exponential backoff
    max_retries=3,
    retry_delay=5,
    retry_backoff=True,
    
    # Error handling
    fail_fast=False,  # Continue despite failures
    event_bus=event_bus,
    
    # Tracking
    enable_tracker=True
)

# Execute
result = orchestrator.execute()

# Check results
if result['success']:
    print(f"✅ Pipeline completed: {result['nodes_executed']} nodes")
else:
    print(f"❌ Pipeline failed: {len(result['failed_nodes'])} failures")
    for node in result['failed_nodes']:
        print(f"   - {node}")
```

---

## Try It Yourself

### Exercise 1: Test Checkpoint Resume

```python
# Create a pipeline that will fail
steps = [
    Step(...),  # Node 1: succeeds
    Step(...),  # Node 2: succeeds
    Step(...),  # Node 3: fails (bad file path)
    Step(...)   # Node 4: never runs
]

# Run with AUTO checkpoints
orchestrator = Orchestrator(
    steps=steps,
    enable_checkpoints=True,
    checkpoint_mode=CheckpointMode.AUTO
)

# First run: fails at Node 3
result = orchestrator.execute()

# Fix the bad file path in steps
# Re-run with resume=True
orchestrator.resume_from_checkpoint = True
result = orchestrator.execute()

# Should skip Nodes 1 & 2, retry Node 3, run Node 4
```

### Exercise 2: Measure Cache Speedup

```python
import time

# First run (no cache)
start = time.time()
orchestrator = Orchestrator(steps=steps, enable_cache=True)
result = orchestrator.execute()
first_run_time = time.time() - start

# Second run (with cache)
start = time.time()
result = orchestrator.execute()
second_run_time = time.time() - start

print(f"First run: {first_run_time:.2f}s")
print(f"Second run: {second_run_time:.2f}s")
print(f"Speedup: {first_run_time / second_run_time:.1f}x")
```

### Exercise 3: Retry with Backoff

```python
# Simulate transient failure
Step(
    layer="ingest",
    name="read_unreliable_api",
    type="config_op",
    engine="pandas",
    value="https://unreliable-api.example.com/data",
    params={
        "source_type": "http",
        "timeout": 5
    }
)

# Configure retry
orchestrator = Orchestrator(
    steps=[...],
    max_retries=5,
    retry_delay=2,
    retry_backoff=True
)

# Watch retry attempts in logs
```

---

## Best Practices

| Scenario | Recommendation |
|----------|---------------|
| **Development** | Enable cache, MANUAL checkpoints |
| **Production (critical)** | AUTO checkpoints, retry=3, error alerts |
| **Production (medallion)** | LAYER checkpoints, cloud cache (optional), retry=3 |
| **Production (streaming)** | INTERVAL checkpoints, no cache, retry=5 |
| **One-off scripts** | No checkpoints, local cache OK |

---

## Key Takeaways

| Concept | What You Learned |
|---------|-----------------|
| **Checkpoints** | Save pipeline state, resume from failures, 4 modes (MANUAL, AUTO, INTERVAL, LAYER) |
| **Cache** | Skip unchanged steps, huge development speedup, local or cloud |
| **Retry** | Automatic retry on transient failures, configurable backoff |
| **Error Handling** | fail_fast, error hooks, continue on error |
| **Production-Ready** | Combine all three for resilient pipelines |

---

## What's Next?

**Level 5: Observability & Monitoring** - Collect performance metrics, register automation hooks, generate HTML stories, and export to Prometheus.

[Continue to Level 5 →](ODIBI_CORE_LEVEL_5_OBSERVABILITY.md)

---

## Summary

✅ You can use checkpoints to resume failed pipelines  
✅ You can enable caching to speed up development  
✅ You understand retry logic and exponential backoff  
✅ You can handle errors gracefully with hooks  
✅ You can build production-ready, fault-tolerant pipelines
