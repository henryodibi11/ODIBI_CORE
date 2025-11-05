# LEVEL 7: Advanced Features

**Time**: 45-60 minutes  
**Goal**: Master scheduling, streaming, distributed execution, and custom functions

---

## 🎯 What You'll Learn

- Schedule pipelines with cron expressions
- Build streaming/continuous pipelines
- Use distributed execution for parallelism
- Register and use custom transform functions
- Choose the right execution backend

---

## 1. Scheduling Pipelines

### ScheduleManager Architecture

```
┌────────────────────────────────────────────────────────┐
│ ScheduleManager                                        │
│ ├─ CRON: "0 * * * *" (every hour)                    │
│ ├─ INTERVAL: Every 300 seconds                       │
│ ├─ FILE_WATCH: Monitor directory for new files       │
│ └─ HYBRID: Combine time + event conditions           │
└──────────────────┬─────────────────────────────────────┘
                   │
                   ▼
     Background thread checks schedules
                   │
                   ├─ Cron: Check if time matches expression
                   ├─ Interval: Check if N seconds elapsed
                   ├─ File Watch: Check for new files
                   └─ Hybrid: Check time AND file presence
                   │
                   ▼
           Condition met? Execute function
                   │
                   └─ run_pipeline() or custom function
```

### Cron Expressions Guide

```
Cron format:  MINUTE  HOUR  DAY  MONTH  DAY_OF_WEEK

Field:           0      *     *     *        *
Meaning:      Minute  Hour  Day  Month  Weekday

Examples:

  0 * * * *        Every hour (at minute 0)
  */5 * * * *      Every 5 minutes
  0 9 * * *        Every day at 9:00 AM
  0 9 * * 1-5      Weekdays at 9:00 AM
  0 0 1 * *        1st of every month at midnight
  30 14 * * 0      Every Sunday at 2:30 PM
  0 */6 * * *      Every 6 hours
  0 0,12 * * *     Twice daily (midnight and noon)
```

### Using ScheduleManager

```python
from odibi_core.schedule_manager import ScheduleManager, ScheduleMode
from odibi_core.orchestrator import Orchestrator

# Define your pipeline
def run_pipeline():
    orchestrator = Orchestrator(
        steps=steps,
        engine_type="pandas"
    )
    result = orchestrator.execute()
    print(f"Pipeline completed: {result['success']}")

# Create ScheduleManager
scheduler = ScheduleManager()

# Schedule 1: Run every hour (CRON)
scheduler.schedule(
    mode=ScheduleMode.CRON,
    cron_expression="0 * * * *",  # Every hour
    func=run_pipeline,
    name="hourly_pipeline"
)

# Schedule 2: Run every 5 minutes (INTERVAL)
scheduler.schedule_interval(
    interval_seconds=300,  # 5 minutes
    func=run_pipeline,
    name="5min_pipeline"
)

# Schedule 3: Run when new files appear (FILE_WATCH)
scheduler.schedule_file_watch(
    watch_path="data/landing/",
    file_pattern="*.csv",  # Watch for new CSV files
    func=run_pipeline,
    name="file_watcher"
)

# Start scheduler (blocking)
scheduler.start()

# To run in background:
# scheduler.start_background()
# ... do other work ...
# scheduler.stop()
```

### Cron Examples

```python
from odibi_core.schedule_manager import ScheduleManager, ScheduleMode

scheduler = ScheduleManager()

# Daily at 2:00 AM
scheduler.schedule(
    mode=ScheduleMode.CRON,
    cron_expression="0 2 * * *",
    func=run_daily_pipeline
)

# Every weekday at 9:00 AM
scheduler.schedule(
    mode=ScheduleMode.CRON,
    cron_expression="0 9 * * 1-5",
    func=run_weekday_pipeline
)

# Every 30 minutes
scheduler.schedule(
    mode=ScheduleMode.CRON,
    cron_expression="*/30 * * * *",
    func=run_frequent_pipeline
)

# First day of month at midnight
scheduler.schedule(
    mode=ScheduleMode.CRON,
    cron_expression="0 0 1 * *",
    func=run_monthly_pipeline
)

scheduler.start()
```

---

## 2. Streaming Pipelines

### Stream Modes

```
┌────────────────────────────────────────────────────────┐
│ StreamManager - Continuous Data Processing            │
├────────────────────────────────────────────────────────┤
│                                                        │
│ FILE_WATCH Mode:                                       │
│   Monitor directory → New file appears → Process      │
│                                                        │
│ INTERVAL Mode:                                         │
│   Poll every N seconds → Read new data → Process      │
│                                                        │
│ INCREMENTAL Mode:                                      │
│   Read records > last watermark → Process → Update    │
│   watermark                                            │
│                                                        │
│ EVENT Mode:                                            │
│   External event triggers → Process                   │
└────────────────────────────────────────────────────────┘
```

### Streaming Architecture

```
StreamManager.start()
     │
     ▼
┌────────────────────────────────────────────────┐
│ Iteration Loop (continuous)                   │
│                                                │
│ 1. Read new data (batch)                      │
│    ├─ FILE_WATCH: Check for new files         │
│    ├─ INCREMENTAL: WHERE timestamp > watermark│
│    └─ INTERVAL: Read all, filter new          │
│                                                │
│ 2. Update data_map with new batch             │
│                                                │
│ 3. DAGExecutor.run_continuous(iteration)      │
│    └─ Execute pipeline on this batch          │
│                                                │
│ 4. Update watermark                            │
│    └─ Save max(timestamp) for next iteration  │
│                                                │
│ 5. Save checkpoint                             │
│    └─ checkpoint_iteration_N.json              │
│                                                │
│ 6. Wait (optional delay)                      │
│                                                │
│ 7. Loop back to step 1                        │
└────────────────────────────────────────────────┘
```

### Incremental Streaming (Watermark-Based)

```python
from odibi_core.stream_manager import StreamManager, StreamMode, StreamConfig

# Define streaming config
stream_config = StreamConfig(
    source_path="data/events.parquet",
    watermark_column="event_timestamp",  # Column to track progress
    batch_size=1000,  # Process 1000 records at a time
    format="parquet"
)

# Define pipeline steps (same as batch)
steps = [
    Step(
        layer="ingest",
        name="read_events",
        type="config_op",
        engine="pandas",
        value=stream_config.source_path,
        params={"source_type": stream_config.format},
        outputs={"data": "raw_events"}
    ),
    Step(
        layer="transform",
        name="filter_important",
        type="sql",
        engine="pandas",
        value="SELECT * FROM bronze WHERE importance > 5",
        inputs={"bronze": "raw_events"},
        outputs={"data": "important_events"}
    ),
    Step(
        layer="store",
        name="save_processed",
        type="config_op",
        engine="pandas",
        value="output/processed_events.parquet",
        params={"format": "parquet", "mode": "append"},
        inputs={"data": "important_events"}
    )
]

# Create StreamManager
stream_manager = StreamManager(
    steps=steps,
    engine_type="pandas",
    stream_mode=StreamMode.INCREMENTAL,
    stream_config=stream_config,
    checkpoint_dir="stream_checkpoints/"
)

# Start streaming (runs continuously)
stream_manager.start()

# Execution:
# Iteration 1: Read records where event_timestamp > null → Process → Save watermark
# Iteration 2: Read records where event_timestamp > last_watermark → Process
# Iteration 3: ...
```

### File Watch Streaming

```python
from odibi_core.stream_manager import StreamManager, StreamMode, StreamConfig

stream_config = StreamConfig(
    source_path="data/landing/",  # Watch this directory
    file_pattern="*.csv",         # Process CSV files
    format="csv",
    batch_size=None  # Process entire file
)

steps = [...]  # Define your pipeline steps

stream_manager = StreamManager(
    steps=steps,
    engine_type="pandas",
    stream_mode=StreamMode.FILE_WATCH,
    stream_config=stream_config
)

# Start watching
stream_manager.start()

# Execution:
# Iteration 1: No new files → Wait
# Iteration 2: new_file.csv appears → Process → Move to processed/
# Iteration 3: No new files → Wait
# Iteration 4: another_file.csv appears → Process
```

### Continuous Execution with DAGExecutor

```python
from odibi_core.dag_executor import DAGExecutor

# For custom streaming logic
executor = DAGExecutor(...)

iteration = 0
while True:
    # Read new batch
    new_data = read_incremental_data(watermark)
    
    # Update data_map
    data_map["new_batch"] = new_data
    
    # Execute pipeline on this batch
    result = executor.run_continuous(iteration=iteration)
    
    # Update watermark
    watermark = new_data['timestamp'].max()
    
    # Save checkpoint
    save_checkpoint(iteration, watermark)
    
    iteration += 1
    time.sleep(10)  # Wait 10 seconds before next iteration
```

---

## 3. Distributed Execution

### Execution Backends

```
┌────────────────────────────────────────────────────────┐
│ ExecutionBackend                                       │
├────────────────────────────────────────────────────────┤
│                                                        │
│ THREAD_POOL (I/O-bound tasks)                         │
│   ├─ Good for: Reading files, API calls, DB queries  │
│   ├─ Max workers: 10-20                               │
│   └─ Python GIL: Doesn't block I/O                   │
│                                                        │
│ PROCESS_POOL (CPU-bound tasks)                        │
│   ├─ Good for: Heavy computations, transformations   │
│   ├─ Max workers: CPU count                          │
│   └─ Bypasses Python GIL                             │
│                                                        │
│ RAY (Multi-machine clusters) [FUTURE]                 │
│   ├─ Good for: Massive scale, distributed compute    │
│   └─ Not yet implemented                              │
└────────────────────────────────────────────────────────┘
```

### Sequential vs Distributed

```
Sequential Execution (Base DAGExecutor):

Layer 0: [Node A] ──▶ 10s
         [Node B] ──▶ 8s
         [Node C] ──▶ 12s

Total Time = 10s + 8s + 12s = 30 seconds

────────────────────────────────────────────────────

Distributed Execution (DistributedExecutor):

Layer 0: [Node A] ┐
         [Node B] ├─ All run in parallel (ThreadPool)
         [Node C] ┘

Total Time = max(10s, 8s, 12s) = 12 seconds

Speedup: 30s / 12s = 2.5x
```

### Using DistributedExecutor

```python
from odibi_core.orchestrator import Orchestrator
from odibi_core.distributed_executor import ExecutionBackend

# Create orchestrator with distributed execution
orchestrator = Orchestrator(
    steps=steps,
    engine_type="pandas",
    
    # Enable distributed execution
    distributed=True,
    execution_backend=ExecutionBackend.THREAD_POOL,  # or PROCESS_POOL
    distributed_max_workers=10  # Number of parallel workers
)

result = orchestrator.execute()
```

### Thread Pool (I/O-Bound)

```python
# Good for pipelines with lots of file I/O
steps = [
    Step(...),  # Read CSV from disk
    Step(...),  # Read Parquet from S3
    Step(...),  # Query database
    Step(...),  # API call
]

orchestrator = Orchestrator(
    steps=steps,
    engine_type="pandas",
    distributed=True,
    execution_backend=ExecutionBackend.THREAD_POOL,
    distributed_max_workers=10  # 10 concurrent I/O operations
)
```

### Process Pool (CPU-Bound)

```python
# Good for pipelines with heavy transformations
steps = [
    Step(...),  # Read data
    Step(...),  # Complex aggregation
    Step(...),  # ML model inference
    Step(...),  # Feature engineering
]

orchestrator = Orchestrator(
    steps=steps,
    engine_type="pandas",
    distributed=True,
    execution_backend=ExecutionBackend.PROCESS_POOL,
    distributed_max_workers=4  # Use 4 CPU cores
)
```

### When to Use Distributed Execution

| Scenario | Backend | Why |
|----------|---------|-----|
| **Many file reads** | THREAD_POOL | I/O-bound, no GIL issues |
| **Database queries** | THREAD_POOL | I/O-bound, waiting for DB |
| **API calls** | THREAD_POOL | I/O-bound, network latency |
| **Complex transformations** | PROCESS_POOL | CPU-bound, bypasses GIL |
| **ML inference** | PROCESS_POOL | CPU-bound computation |
| **Mixed workload** | THREAD_POOL | More flexible, lower overhead |

---

## 4. Custom Transform Functions

### Function Registry

```
┌────────────────────────────────────────────────────────┐
│ Function Registry                                      │
│                                                        │
│ resolve_function(dotted_path)                         │
│   ├─ "my_module.calculate_metrics" → function object │
│   └─ Dynamic import by dotted path                   │
│                                                        │
│ register_function(name, func)                         │
│   └─ Manual registration                              │
└────────────────────────────────────────────────────────┘
```

### Creating Custom Functions

```python
# my_functions.py

def calculate_efficiency(df):
    """Calculate efficiency metric."""
    df['efficiency'] = df['output'] / df['input'] * 100
    return df

def add_date_features(df):
    """Add date-based features."""
    import pandas as pd
    df['year'] = pd.to_datetime(df['date']).dt.year
    df['month'] = pd.to_datetime(df['date']).dt.month
    df['day_of_week'] = pd.to_datetime(df['date']).dt.dayofweek
    return df

def clean_names(df):
    """Clean name column."""
    df['name'] = df['name'].str.strip().str.title()
    return df
```

### Using Custom Functions in Pipeline

```python
# Use function by dotted path
Step(
    layer="transform",
    name="calculate_efficiency",
    type="function",
    engine="pandas",
    value="my_functions.calculate_efficiency",  # ← Dotted path
    inputs={"data": "raw_sales"},
    outputs={"data": "sales_with_efficiency"}
)

Step(
    layer="transform",
    name="add_date_features",
    type="function",
    engine="pandas",
    value="my_functions.add_date_features",
    inputs={"data": "sales_with_efficiency"},
    outputs={"data": "sales_with_dates"}
)
```

### Manual Function Registration

```python
from odibi_core.functions import register_function

def custom_transform(df):
    # Your custom logic
    df['new_column'] = df['col1'] + df['col2']
    return df

# Register function
register_function("custom.transform", custom_transform)

# Use in pipeline
Step(
    layer="transform",
    name="apply_custom",
    type="function",
    engine="pandas",
    value="custom.transform",  # Uses registered function
    inputs={"data": "raw_data"},
    outputs={"data": "transformed_data"}
)
```

### Function Best Practices

```python
def good_transform_function(df):
    """
    Best practices for transform functions:
    
    1. Accept DataFrame, return DataFrame
    2. Don't modify input (use .copy() if needed)
    3. Handle edge cases (empty df, missing columns)
    4. Add docstring
    5. Type hints (optional but helpful)
    """
    import pandas as pd
    
    # Validate input
    if df.empty:
        return df
    
    # Work on copy if modifying
    result = df.copy()
    
    # Your transformation
    result['metric'] = result['value'] * 100
    
    return result
```

---

## Try It Yourself

### Exercise 1: Schedule a Pipeline

```python
# Create a scheduled pipeline that runs every 5 minutes
scheduler = ScheduleManager()

def my_pipeline():
    print(f"Running at {datetime.now()}")
    # ... your pipeline code

scheduler.schedule_interval(interval_seconds=300, func=my_pipeline)
scheduler.start()
```

### Exercise 2: Build a Streaming Pipeline

```python
# Create a file-watch streaming pipeline
# 1. Create a landing directory
# 2. Set up file watcher
# 3. Drop files into directory
# 4. Watch them get processed

stream_config = StreamConfig(
    source_path="data/landing/",
    file_pattern="*.csv",
    format="csv"
)

stream_manager = StreamManager(
    steps=steps,
    engine_type="pandas",
    stream_mode=StreamMode.FILE_WATCH,
    stream_config=stream_config
)

stream_manager.start()
```

### Exercise 3: Distributed Execution

```python
# Compare sequential vs distributed execution times
import time

# Sequential
start = time.time()
orchestrator = Orchestrator(steps=steps, distributed=False)
orchestrator.execute()
sequential_time = time.time() - start

# Distributed
start = time.time()
orchestrator = Orchestrator(
    steps=steps,
    distributed=True,
    execution_backend=ExecutionBackend.THREAD_POOL,
    distributed_max_workers=10
)
orchestrator.execute()
distributed_time = time.time() - start

print(f"Sequential: {sequential_time:.2f}s")
print(f"Distributed: {distributed_time:.2f}s")
print(f"Speedup: {sequential_time / distributed_time:.1f}x")
```

### Exercise 4: Custom Function

```python
# Create a custom transform function
def my_custom_transform(df):
    df['double_value'] = df['value'] * 2
    return df

# Use it in a pipeline
Step(
    layer="transform",
    name="double_values",
    type="function",
    engine="pandas",
    value="my_module.my_custom_transform",
    inputs={"data": "raw_data"},
    outputs={"data": "doubled_data"}
)
```

---

## Key Takeaways

| Concept | What You Learned |
|---------|-----------------|
| **Scheduling** | Cron expressions, INTERVAL, FILE_WATCH modes |
| **Streaming** | Watermark-based incremental, continuous execution |
| **Distributed** | THREAD_POOL (I/O), PROCESS_POOL (CPU), speedup benefits |
| **Custom Functions** | Create and register transform functions |

---

## What's Next?

**Level 8: Putting It All Together** - Build complete production pipelines with best practices, patterns, troubleshooting, and real-world examples.

[Continue to Level 8 →](ODIBI_CORE_LEVEL_8_COMPLETE.md)

---

## Summary

✅ You can schedule pipelines with cron expressions  
✅ You can build streaming pipelines with watermarks  
✅ You understand distributed execution backends  
✅ You can create and use custom transform functions  
✅ You know when to use each advanced feature
