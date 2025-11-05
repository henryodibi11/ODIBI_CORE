# LEVEL 1: Foundation

**Time**: 15-20 minutes  
**Goal**: Understand what odibi_core is, see the big picture, and run your first pipeline

---

## 🎯 What You'll Learn

- What odibi_core is and why it exists
- The big picture of all components
- Core philosophy (contract-driven, engine-agnostic)
- How data flows through the framework
- Run a simple 3-step pipeline

---

## What is odibi_core?

**odibi_core** is a data pipeline framework that lets you build ETL/ELT pipelines that can run on different engines (Pandas for local, Spark for distributed) without changing your code.

**Think of it as**:
- **Lego blocks** for data pipelines - snap together pre-built components
- **Engine-agnostic** - write once, run anywhere (Pandas or Spark)
- **Production-ready** - built-in tracking, monitoring, checkpoints, caching

---

## The Big Picture Map

```
┌─────────────────────────────────────────────────────────────────────┐
│                        ODIBI_CORE FRAMEWORK                         │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ YOU WRITE                                                           │
│ Steps = [ Step(...), Step(...), Step(...) ]                        │
│ "Read CSV → Filter data → Save Parquet"                            │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│ ORCHESTRATION                                                       │
│ ┌──────────────┐   ┌─────────────┐   ┌──────────────┐             │
│ │ DAGBuilder   │──▶│ DAG Graph   │──▶│ Orchestrator │             │
│ └──────────────┘   └─────────────┘   └──────────────┘             │
│ Converts Steps to DAG, then executes                               │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│ EXECUTION - DAGExecutor runs nodes in parallel                     │
│                                                                     │
│ ┌─────────────────────┐         ┌─────────────────────┐           │
│ │  5 NODE TYPES       │         │  2 ENGINES          │           │
│ │  ───────────────    │         │  ─────────────      │           │
│ │  • ConnectNode      │◀───────▶│  • PandasEngine     │           │
│ │  • IngestNode       │         │    (local, fast)    │           │
│ │  • TransformNode    │         │                     │           │
│ │  • StoreNode        │◀───────▶│  • SparkEngine      │           │
│ │  • PublishNode      │         │    (distributed)    │           │
│ └─────────────────────┘         └─────────────────────┘           │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│ I/O LAYER                                                           │
│ ┌──────────────┐   ┌──────────────┐   ┌──────────────┐            │
│ │ Readers      │   │ Writers      │   │ CloudAdapter │            │
│ │ CSV, Parquet │   │ CSV, Parquet │   │ Azure, S3    │            │
│ │ Delta, SQL   │   │ Delta, SQL   │   │ HDFS, Kafka  │            │
│ └──────────────┘   └──────────────┘   └──────────────┘            │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ STATE MANAGEMENT                                                    │
│ ┌──────────────┐   ┌──────────────┐   ┌──────────────┐            │
│ │ data_map     │   │ Tracker      │   │ Checkpoints  │            │
│ │ (shared      │   │ (lineage &   │   │ (resume on   │            │
│ │  DataFrames) │   │  snapshots)  │   │  failure)    │            │
│ └──────────────┘   └──────────────┘   └──────────────┘            │
│                    ┌──────────────┐                                │
│                    │ CacheManager │                                │
│                    │ (speed up    │                                │
│                    │  dev cycles) │                                │
│                    └──────────────┘                                │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ OBSERVABILITY                                                       │
│ ┌──────────────┐   ┌──────────────┐   ┌──────────────┐            │
│ │ EventBus     │   │ Metrics      │   │ HTML Stories │            │
│ │ (hooks &     │   │ (performance │   │ (visual      │            │
│ │  alerts)     │   │  tracking)   │   │  reports)    │            │
│ └──────────────┘   └──────────────┘   └──────────────┘            │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ ADVANCED (Levels 7-8)                                               │
│ • ScheduleManager (cron, interval, file-watch)                     │
│ • StreamManager (continuous processing)                            │
│ • DistributedExecutor (parallel execution)                         │
│ • Function Registry (custom transforms)                            │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Core Concepts

### 1. Everything is a Node

There are **5 types of nodes** - think of them as building blocks:

| Node Type | What It Does | Example |
|-----------|--------------|---------|
| **ConnectNode** | Establish connections to databases/systems | Connect to PostgreSQL |
| **IngestNode** | Read data from sources | Read CSV file, query database |
| **TransformNode** | Transform data (SQL or Python function) | Filter rows, add columns, aggregate |
| **StoreNode** | Save data to Bronze/Silver/Gold layers | Write to Parquet, Delta Lake |
| **PublishNode** | Export to external systems | Send to API, write to cloud |

### 2. Engines are Swappable

Choose your execution engine based on data size:

```
┌──────────────────────────────────────────────────────────┐
│ Data Size < 10 GB?                                       │
│    ├─ YES → Use PandasEngineContext (fast, local)       │
│    └─ NO  → Use SparkEngineContext (distributed)        │
└──────────────────────────────────────────────────────────┘
```

**Same pipeline code works on both engines!**

### 3. data_map is the Shared Dictionary

All nodes read from and write to a shared dictionary called `data_map`:

```python
data_map = {}  # Starts empty

# IngestNode reads CSV and writes to data_map
data_map["raw_data"] = <DataFrame>

# TransformNode reads from data_map, transforms, writes back
data_map["filtered_data"] = <DataFrame>

# StoreNode reads from data_map and saves to disk
```

**Think of data_map as a whiteboard where nodes leave data for each other.**

### 4. Contract-Driven Design

All components follow clear interfaces (ABC contracts):

- All nodes inherit from `NodeBase`
- All engines inherit from `EngineContext`
- All readers inherit from `BaseReader`
- All writers inherit from `BaseWriter`

**This ensures consistency and makes the framework extensible.**

---

## Your First Pipeline

Let's build a simple 3-step pipeline: **Read CSV → Filter data → Save as Parquet**

### Step 1: Define Your Steps

```python
from odibi_core.step import Step

steps = [
    # Step 1: Read CSV file
    Step(
        layer="ingest",
        name="read_sales_data",
        type="config_op",
        engine="pandas",
        value="data/sales.csv",
        params={"source_type": "csv", "header": True},
        outputs={"data": "raw_sales"}  # Write to data_map["raw_sales"]
    ),
    
    # Step 2: Filter data using SQL
    Step(
        layer="transform",
        name="filter_high_value",
        type="sql",
        engine="pandas",
        value="SELECT * FROM bronze WHERE amount > 100",
        inputs={"bronze": "raw_sales"},  # Read from data_map["raw_sales"]
        outputs={"data": "filtered_sales"}  # Write to data_map["filtered_sales"]
    ),
    
    # Step 3: Save as Parquet
    Step(
        layer="store",
        name="save_to_parquet",
        type="config_op",
        engine="pandas",
        value="output/sales_filtered.parquet",
        params={"format": "parquet"},
        inputs={"data": "filtered_sales"}  # Read from data_map["filtered_sales"]
    )
]
```

### Step 2: Run the Pipeline

```python
from odibi_core.orchestrator import Orchestrator

# Create orchestrator
orchestrator = Orchestrator(
    steps=steps,
    engine_type="pandas",
    enable_tracker=True  # Track execution details
)

# Execute pipeline
result = orchestrator.execute()

print(f"Pipeline completed: {result['success']}")
print(f"Nodes executed: {result['nodes_executed']}")
```

### What Just Happened?

```
1. Orchestrator created:
   ├─ PandasEngineContext (execution engine)
   ├─ DAGBuilder (converts steps to DAG)
   ├─ Tracker (captures lineage)
   └─ DAGExecutor (runs nodes)

2. DAGExecutor executed nodes in order:
   ├─ IngestNode: Read CSV → data_map["raw_sales"]
   ├─ TransformNode: SQL filter → data_map["filtered_sales"]
   └─ StoreNode: Save Parquet from data_map["filtered_sales"]

3. Result returned:
   ├─ success: True
   ├─ nodes_executed: 3
   └─ tracker: Contains execution details
```

---

## Key Takeaways

| Concept | What You Need to Know |
|---------|----------------------|
| **Nodes** | 5 types: Connect, Ingest, Transform, Store, Publish |
| **Engines** | Pandas (local) or Spark (distributed) - same code! |
| **data_map** | Shared dictionary where DataFrames live |
| **Steps** | Configuration objects you write to define pipeline |
| **Orchestrator** | Builds and executes your pipeline |
| **Contract-Driven** | Everything follows clear interfaces (ABCs) |

---

## Try It Yourself

### Exercise 1: Modify the Pipeline

Change the pipeline to:
1. Read from `data/customers.csv`
2. Filter for `age > 25`
3. Save to `output/young_customers.parquet`

### Exercise 2: Add a Third Transform

Add another TransformNode that:
1. Reads from `filtered_sales`
2. Adds a column: `SELECT *, amount * 0.1 as tax FROM bronze`
3. Writes to `sales_with_tax`
4. Save that to Parquet

### Exercise 3: Switch to Spark

Change `engine_type="pandas"` to `engine_type="spark"` in the Orchestrator.  
Same code, different engine!

---

## What's Next?

**Level 2: Building Pipelines** - Learn the 5 node types in detail, understand Step configuration, and build more complex pipelines with multiple transforms.

[Continue to Level 2 →](ODIBI_CORE_LEVEL_2_BUILDING_PIPELINES.md)

---

## Summary

✅ You understand what odibi_core is (data pipeline framework)  
✅ You've seen the big picture (Nodes, Engines, Orchestration, State, Observability)  
✅ You understand core concepts (Nodes, Engines, data_map, Contracts)  
✅ You've run your first pipeline (Read CSV → Filter → Save Parquet)

**Time to dive deeper into building pipelines!**
