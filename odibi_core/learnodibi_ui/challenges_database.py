"""
Hands-on Challenges Database - Practical exercises for learners
"""

CHALLENGES = {
    "DEVELOPER_WALKTHROUGH_PHASE_1.md": [
        {
            "step": 8,
            "title": "Create Your First ConnectNode",
            "difficulty": "Beginner",
            "task": """
**Your Task:**
Create a ConnectNode that connects to a local CSV file.

**Requirements:**
1. Import the ConnectNode class
2. Create an instance with a file path
3. Test the connection
4. Handle any errors gracefully

**Hints:**
- Use a CSV file you have locally (or create a sample)
- The connection should validate the file exists
- Print a success message when connected
            """,
            "starter_code": """# Your code here
from odibi_core.nodes import ConnectNode

# TODO: Create ConnectNode instance
# TODO: Test connection
# TODO: Print result
""",
            "solution": """from odibi_core.nodes import ConnectNode
import os

# Create connection to CSV file
csv_path = "data/sample.csv"

# Validate file exists
if os.path.exists(csv_path):
    conn = ConnectNode(source=csv_path, source_type="csv")
    print(f"✅ Connected to {csv_path}")
else:
    print(f"❌ File not found: {csv_path}")
"""
        },
        {
            "step": 12,
            "title": "Build a Simple Ingest Pipeline",
            "difficulty": "Beginner",
            "task": """
**Your Task:**
Create a pipeline that connects to a CSV and reads it into a DataFrame.

**Requirements:**
1. Use ConnectNode to establish connection
2. Use IngestNode to read data
3. Display the first 5 rows
4. Print the DataFrame shape

**Expected Output:**
- First 5 rows displayed
- Message: "Loaded X rows and Y columns"
            """,
            "starter_code": """from odibi_core.nodes import ConnectNode, IngestNode

# TODO: Create connection
# TODO: Read data with IngestNode
# TODO: Display first 5 rows
# TODO: Print shape
""",
            "solution": """from odibi_core.nodes import ConnectNode, IngestNode

# Step 1: Connect
conn = ConnectNode(source="data/sales.csv", source_type="csv")

# Step 2: Ingest
ingest = IngestNode(connection=conn)
df = ingest.read()

# Step 3: Display
print(df.head())
print(f"\\n✅ Loaded {len(df)} rows and {len(df.columns)} columns")
"""
        }
    ],
    
    "DEVELOPER_WALKTHROUGH_PHASE_2.md": [
        {
            "step": 8,
            "title": "Write Engine-Agnostic Code",
            "difficulty": "Intermediate",
            "task": """
**Your Task:**
Write a function that works on both Pandas and Spark DataFrames.

**Requirements:**
1. Create a function that adds a new column
2. Use detect_engine() to identify DataFrame type
3. Implement both Pandas and Spark logic
4. Test with both engine types

**Function Signature:**
```python
def add_margin_column(df, revenue_col, cost_col, margin_col):
    # Your implementation
    pass
```
            """,
            "starter_code": """from odibi_core.functions import detect_engine
import numpy as np

def add_margin_column(df, revenue_col, cost_col, margin_col):
    engine = detect_engine(df)
    
    if engine == "pandas":
        # TODO: Pandas implementation
        pass
    else:
        # TODO: Spark implementation
        pass
    
    return df
""",
            "solution": """from odibi_core.functions import detect_engine
import numpy as np
from pyspark.sql import functions as F

def add_margin_column(df, revenue_col, cost_col, margin_col):
    engine = detect_engine(df)
    
    if engine == "pandas":
        # Pandas: Simple division
        df[margin_col] = df[revenue_col] - df[cost_col]
    else:
        # Spark: Use column expressions
        df = df.withColumn(
            margin_col,
            F.col(revenue_col) - F.col(cost_col)
        )
    
    return df
"""
        }
    ],
    
    "DEVELOPER_WALKTHROUGH_PHASE_3.md": [
        {
            "step": 5,
            "title": "Create a Config-Driven Pipeline",
            "difficulty": "Intermediate",
            "task": """
**Your Task:**
Build a pipeline that reads its configuration from a JSON file.

**Requirements:**
1. Create a config.json with source, transformations, target
2. Read the config file
3. Build pipeline based on config
4. Execute the pipeline

**Config Structure:**
```json
{
  "source": "data/input.csv",
  "transformations": ["clean", "validate"],
  "target": "data/output.csv"
}
```
            """,
            "starter_code": """import json

# TODO: Load config from JSON
# TODO: Create nodes based on config
# TODO: Execute pipeline
# TODO: Validate output
""",
            "solution": """import json
from odibi_core.nodes import ConnectNode, IngestNode, TransformNode, StoreNode

# Load config
with open("config.json") as f:
    config = json.load(f)

# Build pipeline from config
conn = ConnectNode(source=config["source"])
ingest = IngestNode(connection=conn)
df = ingest.read()

# Apply transformations
for transform in config["transformations"]:
    transformer = TransformNode(operation=transform)
    df = transformer.apply(df)

# Save output
store = StoreNode(target=config["target"])
store.write(df)

print("✅ Pipeline executed successfully!")
"""
        }
    ],
    
    "DEVELOPER_WALKTHROUGH_FUNCTIONS.md": [
        {
            "step": 5,
            "title": "Build safe_divide() from Scratch",
            "difficulty": "Beginner",
            "task": """
**Your Task:**
Implement the safe_divide() function that handles division by zero.

**Requirements:**
1. Accept DataFrame, numerator column, denominator column
2. Handle division by zero with fill_value
3. Support both Pandas and Spark
4. Return DataFrame with new column

**Test Case:**
```python
df = pd.DataFrame({'revenue': [100, 200], 'cost': [50, 0]})
result = safe_divide(df, 'revenue', 'cost', 'margin', fill_value=0)
# Should return: margin = [2.0, 0.0]
```
            """,
            "starter_code": """import pandas as pd
import numpy as np

def safe_divide(df, numerator, denominator, result_col, fill_value=0):
    # TODO: Implement safe division
    pass

# Test it
df = pd.DataFrame({'revenue': [100, 200], 'cost': [50, 0]})
result = safe_divide(df, 'revenue', 'cost', 'margin', fill_value=0)
print(result)
""",
            "solution": """import pandas as pd
import numpy as np
from odibi_core.functions import detect_engine

def safe_divide(df, numerator, denominator, result_col, fill_value=0):
    engine = detect_engine(df)
    
    if engine == "pandas":
        df[result_col] = np.where(
            df[denominator] != 0,
            df[numerator] / df[denominator],
            fill_value
        )
    else:
        from pyspark.sql import functions as F
        df = df.withColumn(
            result_col,
            F.when(F.col(denominator) != 0, 
                   F.col(numerator) / F.col(denominator)
            ).otherwise(fill_value)
        )
    
    return df

# Test
df = pd.DataFrame({'revenue': [100, 200], 'cost': [50, 0]})
result = safe_divide(df, 'revenue', 'cost', 'margin', fill_value=0)
print(result)
# Output: margin = [2.0, 0.0] ✅
"""
        }
    ],
    
    "DEVELOPER_WALKTHROUGH_PHASE_6.md": [
        {
            "step": 5,
            "title": "Build a File Watch Stream",
            "difficulty": "Intermediate",
            "task": """
**Your Task:**
Create a StreamManager that monitors a directory for new CSV files and processes them incrementally.

**Requirements:**
1. Setup a StreamManager with FILE_WATCH mode
2. Configure it to watch for *.csv files
3. Implement batch reading with watermark tracking
4. Print the number of rows in each batch

**Expected Behavior:**
- Monitor specified directory
- Process only new files since last run
- Track processed files to avoid reprocessing
            """,
            "starter_code": """from odibi_core.streaming import StreamManager, StreamMode
from pathlib import Path

# TODO: Create test directory
# TODO: Setup StreamManager with FILE_WATCH mode
# TODO: Process batches
# TODO: Track watermark
""",
            "solution": """from odibi_core.streaming import StreamManager, StreamMode
from pathlib import Path
import pandas as pd

# Create test directory
test_dir = Path("data/incoming")
test_dir.mkdir(parents=True, exist_ok=True)

# Create sample files
for i in range(3):
    df = pd.DataFrame({"id": [i*100+j for j in range(10)]})
    df.to_csv(test_dir / f"data_{i}.csv", index=False)

# Setup stream manager
stream = StreamManager.from_source(
    format="csv",
    path=str(test_dir),
    mode="file_watch",
    pattern="*.csv",
    name="csv_watcher"
)

# Process batches
for batch in stream.read(max_iterations=1):
    if batch is not None:
        print(f"✅ Processed batch: {len(batch)} rows")
"""
        },
        {
            "step": 10,
            "title": "Implement Checkpoint Resume Pattern",
            "difficulty": "Advanced",
            "task": """
**Your Task:**
Build a pipeline with checkpoint/resume capability that can recover from failures.

**Requirements:**
1. Create CheckpointManager instance
2. Execute a multi-step pipeline
3. Save checkpoint after each step
4. Simulate a failure and resume from checkpoint
5. Verify only remaining steps are executed

**Test Scenario:**
- Pipeline has 5 steps
- Failure occurs at step 3
- Resume should skip steps 1-2, execute 3-5
            """,
            "starter_code": """from odibi_core.checkpoint import CheckpointManager, NodeCheckpoint
from datetime import datetime

# TODO: Create CheckpointManager
# TODO: Simulate pipeline execution with checkpoints
# TODO: Save checkpoint state
# TODO: Load and resume from checkpoint
""",
            "solution": """from odibi_core.checkpoint import CheckpointManager, NodeCheckpoint
from datetime import datetime

# Create checkpoint manager
checkpoint_mgr = CheckpointManager(checkpoint_dir="artifacts/checkpoints")

# Simulate pipeline steps
steps = ["read_data", "transform", "validate", "aggregate", "write"]
completed = []

# Execute until step 3 (simulate failure)
for i, step_name in enumerate(steps[:2]):
    print(f"Executing {step_name}...")
    node_checkpoint = NodeCheckpoint(
        node_name=step_name,
        state="SUCCESS",
        completed_at=datetime.now().isoformat(),
        duration_ms=100.0 * (i+1),
        attempts=1
    )
    completed.append(node_checkpoint)

# Save checkpoint before failure
checkpoint = checkpoint_mgr.create_checkpoint(
    dag_name="test_pipeline",
    completed_nodes=completed,
    pending_nodes=set(steps[2:]),
    mode="batch"
)
checkpoint_mgr.save(checkpoint)
print(f"✅ Checkpoint saved: {checkpoint.checkpoint_id}")

# Resume from checkpoint
loaded = checkpoint_mgr.load_latest("test_pipeline")
skip_nodes = checkpoint_mgr.get_resume_point(loaded)
print(f"Resume: Skip {skip_nodes}, Execute {loaded.pending_nodes}")
"""
        },
        {
            "step": 14,
            "title": "Create Scheduled Pipeline Execution",
            "difficulty": "Intermediate",
            "task": """
**Your Task:**
Build a scheduled job that runs every 5 seconds and exports metrics after each run.

**Requirements:**
1. Create ScheduleManager
2. Define a pipeline function
3. Schedule it to run every 5 seconds
4. Track execution count
5. Stop after 3 executions

**Bonus:**
Add error handling and logging for each execution
            """,
            "starter_code": """from odibi_core.scheduler import ScheduleManager
import time

# TODO: Create pipeline function
# TODO: Setup scheduler
# TODO: Schedule interval execution
# TODO: Track executions
""",
            "solution": """from odibi_core.scheduler import ScheduleManager
import time

execution_count = [0]

def my_pipeline():
    execution_count[0] += 1
    print(f"Pipeline execution #{execution_count[0]}")
    # Simulate work
    time.sleep(0.5)
    return {"status": "success", "execution": execution_count[0]}

# Create scheduler
scheduler = ScheduleManager(check_interval=1)

# Schedule to run every 5 seconds
scheduler.schedule_interval(
    seconds=5,
    function=my_pipeline,
    name="metrics_pipeline"
)

# Start and run for 16 seconds (should execute 3 times)
scheduler.start(daemon=False)
time.sleep(16)
scheduler.stop()

print(f"✅ Total executions: {execution_count[0]}")
"""
        }
    ],
    
    "DEVELOPER_WALKTHROUGH_PHASE_7.md": [
        {
            "step": 3,
            "title": "Build Multi-Cloud Adapter Pattern",
            "difficulty": "Advanced",
            "task": """
**Your Task:**
Use CloudAdapter to interact with cloud storage in a provider-agnostic way.

**Requirements:**
1. Create CloudAdapter with simulation mode
2. Write a DataFrame to cloud storage
3. Read it back and verify data integrity
4. List files in the cloud path
5. Delete the test file

**Expected Output:**
- Successful round-trip write/read
- File listed in directory
- Clean deletion
            """,
            "starter_code": """from odibi_core.cloud import CloudAdapter
import pandas as pd

# TODO: Create CloudAdapter with simulate=True
# TODO: Create test DataFrame
# TODO: Write to cloud storage
# TODO: Read back and verify
# TODO: Clean up
""",
            "solution": """from odibi_core.cloud import CloudAdapter
import pandas as pd

# Create simulated Azure adapter
adapter = CloudAdapter.create("azure", account_name="test", simulate=True)
adapter.connect()

# Create test data
test_data = pd.DataFrame({
    "id": [1, 2, 3],
    "value": [100, 200, 300]
})

# Write to cloud
path = "test-container/data.parquet"
adapter.write(test_data, path, format="parquet")
print(f"✅ Written to {path}")

# Read back
read_data = adapter.read(path, format="parquet")
print(f"✅ Read {len(read_data)} rows")

# Verify
assert len(read_data) == len(test_data)
assert list(read_data.columns) == list(test_data.columns)

# List files
files = adapter.list("test-container/")
print(f"✅ Files in container: {files}")

# Delete
adapter.delete(path)
print("✅ Test file deleted")
"""
        },
        {
            "step": 8,
            "title": "Implement Cloud Caching Strategy",
            "difficulty": "Advanced",
            "task": """
**Your Task:**
Build a cloud-based cache with content-addressed keys and TTL expiration.

**Requirements:**
1. Create CloudCacheManager
2. Compute deterministic cache key
3. Use get_or_compute pattern
4. Verify cache hit on second call
5. Test TTL expiration

**Metrics to Track:**
- Cache hits vs misses
- Computation avoided
            """,
            "starter_code": """from odibi_core.cloud import CloudAdapter
from odibi_core.cache import CloudCacheManager
from odibi_core.metrics import MetricsManager

# TODO: Setup adapter and cache manager
# TODO: Define expensive computation
# TODO: Test get_or_compute
# TODO: Verify cache hit
""",
            "solution": """from odibi_core.cloud import CloudAdapter
from odibi_core.cache import CloudCacheManager
from odibi_core.metrics import MetricsManager
import time

# Setup
adapter = CloudAdapter.create("azure", account_name="test", simulate=True)
adapter.connect()
metrics = MetricsManager()

cache = CloudCacheManager(
    adapter=adapter,
    prefix="cache/",
    default_ttl_s=3600,
    metrics=metrics
)

# Expensive computation
computation_count = [0]

def expensive_transform():
    computation_count[0] += 1
    time.sleep(0.1)  # Simulate work
    return b"expensive_result"

# Compute key
key = cache.compute_key(
    namespace="transform",
    inputs={"file": "data.csv"},
    version="v1"
)

# First call - cache miss
result1 = cache.get_or_compute(key, expensive_transform, ttl_s=60)
print(f"First call: {computation_count[0]} computations")

# Second call - cache hit
result2 = cache.get_or_compute(key, expensive_transform, ttl_s=60)
print(f"Second call: {computation_count[0]} computations")

# Verify
assert computation_count[0] == 1, "Should only compute once!"
print(f"✅ Cache working: {metrics.counters.get('cache_hit', 0)} hits")
"""
        }
    ],
    
    "DEVELOPER_WALKTHROUGH_PHASE_8.md": [
        {
            "step": 3,
            "title": "Build Structured Logging System",
            "difficulty": "Intermediate",
            "task": """
**Your Task:**
Create a StructuredLogger and log various pipeline events with rich metadata.

**Requirements:**
1. Initialize StructuredLogger
2. Log node start, complete, and error events
3. Query logs by level
4. Display summary statistics

**Log Events:**
- 3 node start events
- 2 successful completions
- 1 error event
            """,
            "starter_code": """from odibi_core.observability import StructuredLogger, LogLevel

# TODO: Create logger
# TODO: Log events
# TODO: Query logs
# TODO: Get summary
""",
            "solution": """from odibi_core.observability import StructuredLogger, LogLevel

# Create logger
logger = StructuredLogger("test_pipeline", log_dir="logs")

# Log events
logger.log_node_start("read_data", "ingest", engine="pandas")
logger.log_node_complete("read_data", duration_ms=125.5, rows=1000)

logger.log_node_start("transform", "transform", engine="pandas")
logger.log_node_complete("transform", duration_ms=89.2, rows=1000)

logger.log_node_start("write_data", "storage", engine="pandas")
logger.log_error("write_data", "Connection timeout to database")

# Query logs
errors = logger.query_logs(level=LogLevel.ERROR)
print(f"✅ Errors logged: {len(errors)}")

# Get summary
summary = logger.get_summary()
print(f"Total events: {summary['total_events']}")
print(f"Errors: {summary['error_count']}")
print(f"Event types: {summary['event_types']}")
"""
        },
        {
            "step": 6,
            "title": "Export Metrics in Multiple Formats",
            "difficulty": "Intermediate",
            "task": """
**Your Task:**
Collect pipeline metrics and export them in Prometheus, JSON, and Parquet formats.

**Requirements:**
1. Record various metric types (duration, throughput, cache)
2. Create MetricsExporter
3. Export to all three formats
4. Verify file creation

**Metrics to Record:**
- 3 node durations
- 2 cache hits, 1 miss
- 1 error count
            """,
            "starter_code": """from odibi_core.metrics import MetricsManager, MetricType
from odibi_core.observability import MetricsExporter

# TODO: Create MetricsManager
# TODO: Record metrics
# TODO: Export to formats
""",
            "solution": """from odibi_core.metrics import MetricsManager, MetricType
from odibi_core.observability import MetricsExporter
from pathlib import Path

# Create manager
metrics = MetricsManager()

# Record metrics
metrics.record(MetricType.NODE_DURATION, "read_data", 125.5, {"engine": "pandas"})
metrics.record(MetricType.NODE_DURATION, "transform", 89.2, {"engine": "pandas"})
metrics.record(MetricType.NODE_DURATION, "write", 201.3, {"engine": "pandas"})

metrics.increment(MetricType.CACHE_HIT, "transform", labels={"engine": "pandas"})
metrics.increment(MetricType.CACHE_HIT, "transform", labels={"engine": "pandas"})
metrics.increment(MetricType.CACHE_MISS, "read_data", labels={"engine": "pandas"})
metrics.increment(MetricType.ERROR_COUNT, "write", labels={"engine": "pandas"})

# Export
exporter = MetricsExporter(metrics)

# Prometheus
prom_file = Path("metrics.prom")
exporter.save_prometheus(str(prom_file))
print(f"✅ Prometheus: {prom_file.stat().st_size} bytes")

# JSON
json_file = Path("metrics.json")
exporter.save_json(str(json_file))
print(f"✅ JSON: {json_file.stat().st_size} bytes")

# Parquet
parquet_file = Path("metrics.parquet")
exporter.save_parquet(str(parquet_file))
print(f"✅ Parquet: {parquet_file.stat().st_size} bytes")
"""
        },
        {
            "step": 9,
            "title": "Create EventBus Automation Hooks",
            "difficulty": "Advanced",
            "task": """
**Your Task:**
Build an EventBus with multiple priority hooks for pipeline automation.

**Requirements:**
1. Create EventBus
2. Register summary hook (normal priority)
3. Register alert hook (high priority) 
4. Register custom metrics export hook
5. Emit pipeline_complete event
6. Verify hooks execute in priority order

**Expected Behavior:**
- High priority hooks run first
- All hooks execute without blocking
            """,
            "starter_code": """from odibi_core.observability import EventBus, EventPriority

# TODO: Create EventBus
# TODO: Register hooks with priorities
# TODO: Emit event
# TODO: Verify execution order
""",
            "solution": """from odibi_core.observability import EventBus, EventPriority

# Create bus
bus = EventBus()

# Track execution order
execution_order = []

# Custom hook
def custom_hook(data):
    execution_order.append("custom")
    print(f"Custom hook: {data}")

# Register hooks with priorities
bus.register_hook(
    "pipeline_complete",
    bus.create_alert_hook(threshold_failed=1),
    priority=EventPriority.HIGH  # Runs first
)

bus.register_hook(
    "pipeline_complete",
    bus.create_summary_hook(),
    priority=EventPriority.NORMAL  # Runs second
)

bus.register_hook(
    "pipeline_complete",
    custom_hook,
    priority=EventPriority.LOW  # Runs last
)

# Emit event
bus.emit("pipeline_complete", {
    "pipeline_name": "test",
    "success_count": 5,
    "failed_count": 0,
    "duration_ms": 1000.0
})

# Verify
print(f"✅ Registered hooks: {len(bus.get_hooks('pipeline_complete'))}")
bus.shutdown()
"""
        }
    ]
}


def get_challenge_for_step(lesson_id: str, step_number: int):
    """Get challenge for a specific step if it exists"""
    challenges = CHALLENGES.get(lesson_id, [])
    for challenge in challenges:
        if challenge["step"] == step_number:
            return challenge
    return None


def get_all_challenges_for_lesson(lesson_id: str):
    """Get all challenges for a lesson"""
    return CHALLENGES.get(lesson_id, [])
