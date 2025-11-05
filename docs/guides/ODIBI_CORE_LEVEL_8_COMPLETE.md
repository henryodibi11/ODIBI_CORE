# LEVEL 8: Putting It All Together

**Time**: 60+ minutes  
**Goal**: Build complete production-ready pipelines with best practices and real-world patterns

---

## 🎯 What You'll Learn

- Complete pipeline patterns (Medallion, Streaming, Cloud)
- Production best practices checklist
- Troubleshooting guide
- 4 complete production-ready examples
- How to combine all features

---

## Complete Pipeline Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                  PRODUCTION PIPELINE                           │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│ USER DEFINES STEPS                                             │
│ steps = [Step(...), Step(...), ...]                           │
└──────────────────────┬─────────────────────────────────────────┘
                       │
                       ▼
┌────────────────────────────────────────────────────────────────┐
│ ORCHESTRATOR SETUP                                             │
│ ┌────────────┐  ┌────────────┐  ┌────────────┐                │
│ │ Engine     │  │ Tracker    │  │ EventBus   │                │
│ │ Context    │  │ (lineage)  │  │ (hooks)    │                │
│ └────────────┘  └────────────┘  └────────────┘                │
│ ┌────────────┐  ┌────────────┐  ┌────────────┐                │
│ │Checkpoint  │  │ Cache      │  │ Metrics    │                │
│ │ Manager    │  │ Manager    │  │ Manager    │                │
│ └────────────┘  └────────────┘  └────────────┘                │
└──────────────────────┬─────────────────────────────────────────┘
                       │
                       ▼
┌────────────────────────────────────────────────────────────────┐
│ DAGEXECUTOR / DISTRIBUTEDEXECUTOR                              │
│ ├─ Parallel execution (THREAD_POOL / PROCESS_POOL)            │
│ ├─ Cache lookup before execution                              │
│ ├─ Checkpoint after each layer                                │
│ ├─ Retry on failure (max 3 times)                             │
│ └─ Emit events for monitoring                                 │
└──────────────────────┬─────────────────────────────────────────┘
                       │
                       ▼
┌────────────────────────────────────────────────────────────────┐
│ POST-EXECUTION                                                 │
│ ├─ Export metrics (JSON + Prometheus)                         │
│ ├─ Generate HTML story                                        │
│ ├─ Trigger completion hooks                                   │
│ └─ Save final checkpoint                                      │
└────────────────────────────────────────────────────────────────┘
```

---

## Production Best Practices Checklist

### ✅ Configuration

- [ ] Use meaningful step names (not "step1", "step2")
- [ ] Set appropriate engine (Pandas for <10GB, Spark for >10GB)
- [ ] Configure retry logic (`max_retries=3`)
- [ ] Set checkpoint mode (`CheckpointMode.LAYER` for medallion)
- [ ] Define secrets management strategy

### ✅ Reliability

- [ ] Enable checkpoints for long-running pipelines
- [ ] Enable cache for development environments
- [ ] Configure retry with exponential backoff
- [ ] Set up error alert hooks
- [ ] Test failure scenarios and resume logic

### ✅ Observability

- [ ] Enable Tracker for all production pipelines
- [ ] Register error alert hooks (Slack, email, PagerDuty)
- [ ] Export metrics to monitoring system
- [ ] Generate execution stories for debugging
- [ ] Set up dashboard for pipeline metrics

### ✅ Data Quality

- [ ] Validate data schemas
- [ ] Check row counts (alert on 0 rows)
- [ ] Monitor data freshness
- [ ] Track schema changes over time
- [ ] Set up data quality tests

### ✅ Security

- [ ] Never hardcode secrets in code
- [ ] Use `context.get_secret()` for credentials
- [ ] Store secrets in Key Vault / Secrets Manager
- [ ] Don't log sensitive data
- [ ] Use managed identities when possible

### ✅ Performance

- [ ] Use Parquet for large datasets
- [ ] Partition data appropriately
- [ ] Enable distributed execution for independent nodes
- [ ] Use Delta Lake for ACID guarantees
- [ ] Monitor memory usage

### ✅ Operations

- [ ] Document pipeline dependencies
- [ ] Set up scheduled execution if needed
- [ ] Configure alerting for failures
- [ ] Test rollback procedures
- [ ] Maintain runbooks for common issues

---

## Common Pipeline Patterns

### Pattern 1: Medallion Architecture (Bronze → Silver → Gold)

```
┌─────────────────────────────────────────────────────────┐
│ MEDALLION ARCHITECTURE                                  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ BRONZE (Raw Data)                                       │
│   ├─ IngestNode: Read from source                      │
│   ├─ StoreNode: Save as-is (Parquet/Delta)            │
│   └─ Checkpoint: After Bronze layer                    │
│                                                         │
│ SILVER (Cleaned Data)                                   │
│   ├─ TransformNode: Clean, dedupe, validate           │
│   ├─ TransformNode: Add business logic                │
│   ├─ StoreNode: Save cleaned (Delta recommended)      │
│   └─ Checkpoint: After Silver layer                    │
│                                                         │
│ GOLD (Aggregated/Business-Ready)                        │
│   ├─ TransformNode: Aggregate, join, enrich           │
│   ├─ TransformNode: Business calculations              │
│   ├─ StoreNode: Save aggregated (Delta)               │
│   └─ PublishNode: Export to BI tools                  │
└─────────────────────────────────────────────────────────┘
```

### Pattern 2: Streaming/Continuous

```
┌─────────────────────────────────────────────────────────┐
│ STREAMING PIPELINE                                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ StreamManager (INCREMENTAL mode)                       │
│   ├─ Read data > watermark                            │
│   ├─ Process batch                                     │
│   ├─ Update watermark                                  │
│   ├─ Save checkpoint (iteration N)                    │
│   └─ Loop forever                                      │
│                                                         │
│ OR: File Watch Mode                                    │
│   ├─ Monitor landing directory                        │
│   ├─ New file appears → Process                       │
│   ├─ Move to processed/                               │
│   └─ Wait for next file                               │
└─────────────────────────────────────────────────────────┘
```

### Pattern 3: Cloud Integration

```
┌─────────────────────────────────────────────────────────┐
│ CLOUD PIPELINE                                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ Azure ADLS Source                                       │
│   ├─ CloudAdapter: Authenticate (managed identity)    │
│   ├─ IngestNode: Read from ADLS                       │
│   └─ Spark engine for large data                      │
│                                                         │
│ Transform (Distributed)                                 │
│   ├─ DistributedExecutor (THREAD_POOL)                │
│   ├─ Complex transformations                           │
│   └─ Multiple parallel branches                        │
│                                                         │
│ Write Back to Cloud                                     │
│   ├─ StoreNode: Delta Lake on ADLS                    │
│   ├─ Partitioned by date                              │
│   └─ ACID guarantees                                   │
└─────────────────────────────────────────────────────────┘
```

### Pattern 4: Scheduled Batch

```
┌─────────────────────────────────────────────────────────┐
│ SCHEDULED BATCH PIPELINE                                │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ ScheduleManager (CRON: "0 2 * * *")                   │
│   └─ Trigger daily at 2:00 AM                         │
│                                                         │
│ Full Pipeline Execution:                                │
│   ├─ Read yesterday's data                            │
│   ├─ Transform and aggregate                          │
│   ├─ Save to data warehouse                           │
│   ├─ Generate reports                                 │
│   └─ Send completion notification                     │
│                                                         │
│ Error Handling:                                         │
│   ├─ Retry up to 3 times                              │
│   ├─ Send alert if all retries fail                   │
│   └─ Save checkpoint for manual recovery              │
└─────────────────────────────────────────────────────────┘
```

---

## Complete Production Examples

### Example 1: Simple Development Pipeline

**Scenario**: Local CSV processing for testing

```python
from odibi_core.step import Step
from odibi_core.orchestrator import Orchestrator

# Steps
steps = [
    # 1. Read CSV
    Step(
        layer="ingest",
        name="read_sales_csv",
        type="config_op",
        engine="pandas",
        value="data/sales.csv",
        params={"source_type": "csv", "header": True},
        outputs={"data": "raw_sales"}
    ),
    
    # 2. Filter high-value sales
    Step(
        layer="transform",
        name="filter_high_value",
        type="sql",
        engine="pandas",
        value="SELECT * FROM bronze WHERE amount > 100",
        inputs={"bronze": "raw_sales"},
        outputs={"data": "filtered_sales"}
    ),
    
    # 3. Add tax column
    Step(
        layer="transform",
        name="add_tax",
        type="sql",
        engine="pandas",
        value="SELECT *, amount * 0.1 as tax FROM bronze",
        inputs={"bronze": "filtered_sales"},
        outputs={"data": "sales_with_tax"}
    ),
    
    # 4. Save to Parquet
    Step(
        layer="store",
        name="save_parquet",
        type="config_op",
        engine="pandas",
        value="output/sales_processed.parquet",
        params={"format": "parquet"},
        inputs={"data": "sales_with_tax"}
    )
]

# Orchestrator (development config)
orchestrator = Orchestrator(
    steps=steps,
    engine_type="pandas",
    enable_tracker=True,
    enable_cache=True,  # Speed up dev cycles
    cache_dir="cache/"
)

# Execute
result = orchestrator.execute()

# Generate story
result['tracker'].export_lineage("lineage.json")
from odibi_core.story_generator import StoryGenerator
story_gen = StoryGenerator()
story_gen.generate_story("lineage.json", "story.html")

print(f"✅ Pipeline completed: {result['success']}")
print(f"📊 Story generated: story.html")
```

---

### Example 2: Production Medallion Pipeline

**Scenario**: Bronze → Silver → Gold with full observability

```python
from odibi_core.step import Step
from odibi_core.orchestrator import Orchestrator
from odibi_core.checkpoint_manager import CheckpointMode
from odibi_core.event_bus import EventBus, EventPriority
from odibi_core.metrics_manager import MetricsManager

# ──────────────────────────────────────────────
# STEPS
# ──────────────────────────────────────────────
steps = [
    # === BRONZE LAYER ===
    Step(
        layer="bronze",
        name="ingest_customers",
        type="config_op",
        engine="spark",
        value="abfss://raw@storage.dfs.core.windows.net/customers.csv",
        params={"source_type": "csv", "header": True},
        outputs={"data": "raw_customers"}
    ),
    
    Step(
        layer="bronze",
        name="save_bronze_customers",
        type="config_op",
        engine="spark",
        value="data/bronze/customers",
        params={"format": "delta", "mode": "overwrite"},
        inputs={"data": "raw_customers"}
    ),
    
    # === SILVER LAYER ===
    Step(
        layer="silver",
        name="clean_customers",
        type="sql",
        engine="spark",
        value="""
            SELECT 
                customer_id,
                TRIM(UPPER(name)) as name,
                LOWER(email) as email,
                age,
                status
            FROM bronze 
            WHERE customer_id IS NOT NULL 
              AND email IS NOT NULL
        """,
        inputs={"bronze": "raw_customers"},
        outputs={"data": "clean_customers"}
    ),
    
    Step(
        layer="silver",
        name="dedupe_customers",
        type="sql",
        engine="spark",
        value="""
            SELECT * FROM (
                SELECT *, 
                       ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY age DESC) as rn
                FROM bronze
            ) WHERE rn = 1
        """,
        inputs={"bronze": "clean_customers"},
        outputs={"data": "dedupe_customers"}
    ),
    
    Step(
        layer="silver",
        name="save_silver_customers",
        type="config_op",
        engine="spark",
        value="data/silver/customers",
        params={"format": "delta", "mode": "overwrite", "partitionBy": ["status"]},
        inputs={"data": "dedupe_customers"}
    ),
    
    # === GOLD LAYER ===
    Step(
        layer="gold",
        name="aggregate_by_status",
        type="sql",
        engine="spark",
        value="""
            SELECT 
                status,
                COUNT(*) as customer_count,
                AVG(age) as avg_age,
                CURRENT_TIMESTAMP() as processed_at
            FROM bronze
            GROUP BY status
        """,
        inputs={"bronze": "dedupe_customers"},
        outputs={"data": "customer_summary"}
    ),
    
    Step(
        layer="gold",
        name="save_gold_summary",
        type="config_op",
        engine="spark",
        value="data/gold/customer_summary",
        params={"format": "delta", "mode": "overwrite"},
        inputs={"data": "customer_summary"}
    )
]

# ──────────────────────────────────────────────
# OBSERVABILITY SETUP
# ──────────────────────────────────────────────
metrics = MetricsManager()
event_bus = EventBus()

# Alert on errors
def error_alert(event_data):
    print(f"🚨 CRITICAL: {event_data['step_name']} failed!")
    print(f"   Error: {event_data['error_message']}")
    # In production: Send to Slack/PagerDuty

event_bus.register_hook("node_error", error_alert, EventPriority.CRITICAL)

# Log layer completions
def log_layer_complete(event_data):
    if event_data.get('layer_complete'):
        print(f"✅ Layer '{event_data['layer']}' completed")

event_bus.register_hook("node_complete", log_layer_complete)

# ──────────────────────────────────────────────
# ORCHESTRATOR
# ──────────────────────────────────────────────
orchestrator = Orchestrator(
    steps=steps,
    engine_type="spark",
    
    # Reliability
    enable_checkpoints=True,
    checkpoint_mode=CheckpointMode.LAYER,  # Checkpoint after each layer
    checkpoint_dir="checkpoints/",
    max_retries=3,
    retry_backoff=True,
    
    # Observability
    enable_tracker=True,
    metrics_manager=metrics,
    event_bus=event_bus,
    
    # Performance
    distributed=True,
    distributed_max_workers=10
)

# ──────────────────────────────────────────────
# EXECUTE
# ──────────────────────────────────────────────
result = orchestrator.execute()

# ──────────────────────────────────────────────
# POST-EXECUTION
# ──────────────────────────────────────────────
# Export metrics
metrics.save_to_file("metrics.json")
metrics.export_prometheus("metrics_prometheus.txt")

# Generate story
result['tracker'].export_lineage("lineage.json")
from odibi_core.story_generator import StoryGenerator
story_gen = StoryGenerator()
story_gen.generate_story("lineage.json", "medallion_story.html")

print(f"\n{'='*60}")
print(f"Pipeline Status: {'✅ SUCCESS' if result['success'] else '❌ FAILED'}")
print(f"Nodes Executed: {result['nodes_executed']}")
print(f"Duration: {metrics.get_summary()['total_duration_ms']}ms")
print(f"{'='*60}")
```

---

### Example 3: Streaming File Processor

**Scenario**: Watch directory, process new files continuously

```python
from odibi_core.step import Step
from odibi_core.stream_manager import StreamManager, StreamMode, StreamConfig

# Steps (same as batch)
steps = [
    Step(
        layer="ingest",
        name="read_events",
        type="config_op",
        engine="pandas",
        value="data/landing/",  # Will be replaced by StreamManager
        params={"source_type": "csv", "header": True},
        outputs={"data": "raw_events"}
    ),
    
    Step(
        layer="transform",
        name="filter_important",
        type="sql",
        engine="pandas",
        value="SELECT * FROM bronze WHERE priority = 'HIGH'",
        inputs={"bronze": "raw_events"},
        outputs={"data": "important_events"}
    ),
    
    Step(
        layer="store",
        name="append_to_processed",
        type="config_op",
        engine="pandas",
        value="data/processed/events.parquet",
        params={"format": "parquet", "mode": "append"},
        inputs={"data": "important_events"}
    )
]

# Stream config
stream_config = StreamConfig(
    source_path="data/landing/",
    file_pattern="*.csv",
    format="csv",
    batch_size=None  # Process entire file
)

# Stream manager
stream_manager = StreamManager(
    steps=steps,
    engine_type="pandas",
    stream_mode=StreamMode.FILE_WATCH,
    stream_config=stream_config,
    checkpoint_dir="stream_checkpoints/",
    enable_tracker=True
)

# Start (runs forever)
print("🔄 Starting file watcher...")
print("Drop CSV files into data/landing/ to process them")
stream_manager.start()
```

---

### Example 4: Scheduled Cloud Pipeline

**Scenario**: Daily Azure ADLS → Transform → Delta, scheduled

```python
from odibi_core.step import Step
from odibi_core.orchestrator import Orchestrator
from odibi_core.schedule_manager import ScheduleManager, ScheduleMode
from odibi_core.cloud_adapter import CloudAdapter
from odibi_core.checkpoint_manager import CheckpointMode

# Cloud adapter
adapter = CloudAdapter.create(
    provider="azure",
    account_name="mystorageaccount",
    use_managed_identity=True  # Databricks
)

# Steps
steps = [
    Step(
        layer="ingest",
        name="read_azure_sales",
        type="config_op",
        engine="spark",
        value="abfss://raw@storage.dfs.core.windows.net/sales/{date}.parquet",
        params={"source_type": "parquet", "cloud_adapter": adapter},
        outputs={"data": "raw_sales"}
    ),
    
    Step(
        layer="transform",
        name="aggregate_daily",
        type="sql",
        engine="spark",
        value="""
            SELECT 
                DATE(sale_date) as date,
                product_id,
                SUM(amount) as total_amount,
                COUNT(*) as sale_count
            FROM bronze
            GROUP BY DATE(sale_date), product_id
        """,
        inputs={"bronze": "raw_sales"},
        outputs={"data": "daily_summary"}
    ),
    
    Step(
        layer="store",
        name="save_delta",
        type="config_op",
        engine="spark",
        value="abfss://processed@storage.dfs.core.windows.net/sales_summary",
        params={
            "format": "delta",
            "mode": "append",
            "partitionBy": ["date"],
            "cloud_adapter": adapter
        },
        inputs={"data": "daily_summary"}
    )
]

# Pipeline function
def run_daily_pipeline():
    orchestrator = Orchestrator(
        steps=steps,
        engine_type="spark",
        enable_checkpoints=True,
        checkpoint_mode=CheckpointMode.LAYER,
        enable_tracker=True,
        max_retries=3
    )
    
    result = orchestrator.execute()
    
    if not result['success']:
        print(f"❌ Pipeline failed: {result['failed_nodes']}")
        # Send alert
    else:
        print(f"✅ Pipeline completed successfully")

# Schedule daily at 2:00 AM
scheduler = ScheduleManager()
scheduler.schedule(
    mode=ScheduleMode.CRON,
    cron_expression="0 2 * * *",  # Daily at 2 AM
    func=run_daily_pipeline,
    name="daily_sales_pipeline"
)

print("📅 Scheduler started - will run daily at 2:00 AM")
scheduler.start()
```

---

## Troubleshooting Guide

| Problem | Likely Cause | Solution |
|---------|-------------|----------|
| **Pipeline fails mid-execution** | Transient error | Enable checkpoints, resume with `resume_from_checkpoint=True` |
| **Slow repeated runs during dev** | Re-executing unchanged steps | Enable `CacheManager` to skip unchanged steps |
| **Can't figure out what went wrong** | Lack of visibility | Check Tracker lineage, generate HTML story |
| **Node keeps failing** | Permanent error | Check `retry_count`, examine error in Tracker, add error hook |
| **Out of memory** | Dataset too large for Pandas | Switch to `SparkEngineContext`, use distributed execution |
| **Secrets exposed in logs** | Hardcoded credentials | Use `context.get_secret()`, never print secrets |
| **Data quality issues** | No validation | Add data quality checks in transform steps or hooks |
| **Pipeline too slow** | Sequential execution | Enable distributed execution with `THREAD_POOL` or `PROCESS_POOL` |
| **Checkpoint not resuming** | Wrong checkpoint mode | Use `CheckpointMode.AUTO` or `LAYER`, check `checkpoint_dir` |
| **Cache not hitting** | Input data changed | Cache invalidates on data changes - expected behavior |

---

## Key Takeaways

✅ You know the complete pipeline architecture  
✅ You have a production best practices checklist  
✅ You understand common pipeline patterns  
✅ You have 4 complete production-ready examples  
✅ You know how to troubleshoot common issues  
✅ You can build production pipelines using ALL odibi_core features

---

## Congratulations! 🎉

You've completed the odibi_core mastery guide! You now have the skills to:

- Build pipelines with 5 node types
- Execute on Pandas or Spark
- Use checkpoints, cache, and retry for reliability
- Monitor with Tracker, Metrics, Events, and Stories
- Integrate with databases and cloud storage
- Schedule and stream data
- Distribute execution for performance
- Create custom transform functions

**Next Steps:**
- Build your own production pipeline
- Explore the [Contract Cheatsheet](ODIBI_CORE_CONTRACT_CHEATSHEET.md) for API details
- Share your pipelines and patterns with the team

---

[← Back to Index](ODIBI_CORE_MASTERY_INDEX.md)
