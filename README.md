# ODIBI CORE v1.0

**Node-centric, Engine-agnostic, Config-driven Data Engineering Framework**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) v1.0

**A Node-centric, engine-agnostic, config-driven data engineering framework.**

## 🎯 Mission

ODIBI CORE v1.0 enables data engineers to build production-grade data pipelines that run on **both Pandas (local) and Spark (distributed)** with identical behavior, using declarative configuration instead of imperative code.

## 🧩 Core Principles

| Principle | Description |
|-----------|-------------|
| **Node is Law** | Every operation—connect, ingest, store, transform, publish—is a Node |
| **Config Drives All** | Pipelines are defined by configs (SQL tables or JSON), not code |
| **Engine Agnostic** | Spark and Pandas share identical Node contracts |
| **Truth Preserving** | Each Node logs before/after snapshots, schema diffs, timing, lineage |
| **Composable** | Any Node can run, swap, or replay independently |
| **Self-Improving** | AMP can inspect runs, validate parity, suggest improvements |

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/yourorg/odibi_core.git
cd odibi_core

# Option 1: Install with all dependencies (recommended)
pip install -e ".[dev]"

# Option 2: Minimal install (pandas only)
pip install -e .

# Verify installation
odibi version
```

**See [INSTALL.md](INSTALL.md) for detailed installation instructions.**

### Optional Dependencies

For advanced engineering calculations, install optional packages:

```bash
# Psychrometric calculations (air properties)
pip install psychrolib

# Steam and water properties (IAPWS-97)
pip install iapws

# Physical unit conversions (extended support)
pip install pint
```

**Note**: Functions work with fallback approximations when optional dependencies are unavailable.

### CLI Usage (Recommended)

```bash
# Execute a pipeline
odibi run --config pipeline.json --engine pandas

# Execute with Spark
odibi run --config pipeline.json --engine spark --workers 8

# Validate configuration
odibi validate --config pipeline.json

# Check version and features
odibi version
```

### SDK Usage (Programmatic)

```python
from odibi_core.sdk import ODIBI, Pipeline

# Quick execution
result = ODIBI.run("pipeline.json", engine="pandas")
print(result.summary())

# Advanced usage with configuration
pipeline = Pipeline.from_config("pipeline.json")
pipeline.set_engine("pandas")
pipeline.set_secrets({"db_pass": "secret"})
pipeline.set_parallelism(max_workers=8)

result = pipeline.execute()
print(f"Status: {'✅ SUCCESS' if result.is_success() else '❌ FAILED'}")
print(f"Duration: {result.total_duration_ms:.2f}ms")
```

### Legacy API (Still Supported)

```python
from odibi_core.core import ConfigLoader, Orchestrator
from odibi_core.engine import PandasEngineContext
from odibi_core.core import Tracker, EventEmitter

# Load config
loader = ConfigLoader()
steps = loader.load("pipeline.json")

# Setup execution context
context = PandasEngineContext(secrets={"db_pass": "secret"})
tracker = Tracker()
events = EventEmitter()

# Execute pipeline
orchestrator = Orchestrator(steps, context, tracker, events)
result = orchestrator.run()

# View results
print(f"Processed {len(result.data_map)} datasets")
print(f"Total duration: {tracker.get_stats()['total_duration_ms']}ms")
```

**For functions module walkthrough, see [DEVELOPER_WALKTHROUGH_FUNCTIONS.md](docs/walkthroughs/DEVELOPER_WALKTHROUGH_FUNCTIONS.md)**

## 📁 Project Structure

```
odibi_core/
├── core/               # Base abstractions (Node, Orchestrator, Tracker)
├── nodes/              # 5 canonical Node types (Connect, Ingest, Store, Transform, Publish)
├── engine/             # Engine contexts (Pandas, Spark) ✅ Phase 2
├── functions/          # Pure computational functions (thermo, psychro, physics, math)
├── story/              # HTML story generation
├── io/                 # Data readers/writers
└── examples/           # Demo pipelines
```

## 🧩 Architecture

### Node Model

Every operation is a **Node** that:
1. Receives a `data_map` (dict of logical name → DataFrame)
2. Reads from `inputs` (references to data_map keys)
3. Executes via `EngineContext` (Pandas or Spark)
4. Writes to `outputs` (new entries in data_map)
5. Updates `NodeState` (PENDING → SUCCESS/FAILED)

### 5 Canonical Node Types

| Node Type | Purpose | Example |
|-----------|---------|---------|
| **ConnectNode** | Establish connections | PostgreSQL, Azure Blob |
| **IngestNode** | Read raw data | CSV, Parquet, SQL |
| **StoreNode** | Persist to Bronze/Silver/Gold | Write Parquet, Delta |
| **TransformNode** | Apply business logic | SQL queries, Python functions |
| **PublishNode** | Export to downstream systems | API, Delta Lake |

### Engine Contexts (Phase 2 ✅)

Both **PandasEngineContext** and **SparkEngineContext** implement the same contract:

| Method | Pandas | Spark |
|--------|--------|-------|
| `connect(**kwargs)` | Initialize DuckDB | Initialize SparkSession (local[*]) |
| `read(source, **kwargs)` | CSV, Parquet, SQLite | CSV, Parquet |
| `write(df, target, **kwargs)` | CSV, Parquet | CSV, Parquet |
| `execute_sql(query)` | DuckDB SQL | Spark SQL |
| `register_temp(name, df)` | DuckDB temp table | Spark temp view |
| `collect_sample(df, n)` | `df.head(n)` | `df.limit(n).toPandas()` |

#### Pandas Engine (Local Development)

```python
from odibi_core.engine import PandasEngineContext

ctx = PandasEngineContext()
ctx.connect()

# Read CSV
df = ctx.read("data.csv")

# SQL with DuckDB
ctx.register_temp("data", df)
result = ctx.execute_sql("SELECT * FROM data WHERE value > 100")

# Write Parquet
ctx.write(result, "output.parquet")
```

#### Spark Engine (Local Testing)

```python
from odibi_core.engine import SparkEngineContext

ctx = SparkEngineContext()  # Uses local[*] by default
ctx.connect()

# Read CSV
df = ctx.read("data.csv")

# SQL with Spark
ctx.register_temp("data", df)
result = ctx.execute_sql("SELECT * FROM data WHERE value > 100")

# Write Parquet
ctx.write(result, "output.parquet")

# Cleanup
ctx.stop()
```

**Note**: Spark on Windows requires Hadoop winutils.exe. For Windows development, use PandasEngineContext. Spark works perfectly on Linux, Mac, and cloud platforms (Databricks, EMR).

#### Engine Selection

```python
from odibi_core.core import create_engine_context

# Create context by name
pandas_ctx = create_engine_context("pandas")
spark_ctx = create_engine_context("spark", spark_config={"spark.master": "local[2]"})
```

## 📝 Configuration

### JSON Format

```json
[
  {
    "layer": "ingest",
    "name": "read_bronze",
    "type": "config_op",
    "engine": "pandas",
    "value": "data/bronze.csv",
    "outputs": {"data": "raw_data"}
  },
  {
    "layer": "transform",
    "name": "filter_quality",
    "type": "sql",
    "engine": "pandas",
    "value": "SELECT * FROM data WHERE quality_score > 0.8",
    "inputs": {"data": "raw_data"},
    "outputs": {"data": "filtered_data"}
  },
  {
    "layer": "store",
    "name": "write_silver",
    "type": "config_op",
    "engine": "pandas",
    "value": "output/silver.parquet",
    "inputs": {"data": "filtered_data"}
  }
]
```

### SQLite Schema

```sql
CREATE TABLE transformation_config (
    Layer TEXT,              -- connect, ingest, store, transform, publish
    StepName TEXT,           -- unique identifier
    StepType TEXT,           -- sql, function, config_op, api
    Engine TEXT,             -- pandas, spark
    Value TEXT,              -- SQL or function reference
    Params TEXT,             -- JSON params
    Inputs TEXT,             -- JSON inputs mapping
    Outputs TEXT,            -- JSON outputs mapping
    Metadata TEXT            -- JSON metadata
);
```

## 📊 Observability & Automation (Phase 8)

ODIBI CORE provides production-grade observability with structured logging, metrics export, and automation hooks.

### Structured Logging

```python
from odibi_core.observability import StructuredLogger

logger = StructuredLogger("my_pipeline", log_dir="logs")

# Logs written in JSON Lines format (.jsonl)
logger.log_node_start("read_data", "ingest", engine="pandas")
logger.log_node_complete("read_data", duration_ms=125.5, rows=1000)

# Query logs
errors = logger.query_logs(level=LogLevel.ERROR)
summary = logger.get_summary()
```

### Metrics Export

```python
from odibi_core.metrics import MetricsManager
from odibi_core.observability import MetricsExporter

metrics = MetricsManager()
# ... run pipeline, collect metrics ...

exporter = MetricsExporter(metrics)

# Export to multiple formats
exporter.save_prometheus("metrics/odibi.prom")  # For Prometheus/Grafana
exporter.save_json("metrics/odibi.json")        # For dashboards
exporter.save_parquet("metrics/odibi.parquet")  # For long-term storage

# Human-readable report
print(exporter.generate_report())
```

### Automation Hooks

```python
from odibi_core.observability import EventBus, EventPriority

bus = EventBus()

# Register built-in hooks
bus.register_hook("pipeline_complete", bus.create_summary_hook())
bus.register_hook("pipeline_complete", bus.create_metrics_export_hook("metrics/"))
bus.register_hook("pipeline_complete", bus.create_alert_hook(threshold_failed=3))

# Emit events
bus.emit("pipeline_complete", {
    "pipeline_name": "demo",
    "success_count": 10,
    "failed_count": 0,
    "metrics_manager": metrics
})
```

**See [DEVELOPER_WALKTHROUGH_PHASE_8.md](docs/walkthroughs/DEVELOPER_WALKTHROUGH_PHASE_8.md) for complete guide.**

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_pandas_engine.py
pytest tests/test_spark_engine.py
pytest tests/test_phase8_observability.py

# Run with coverage
pytest --cov=odibi_core --cov-report=html

# Run parity demo (Phase 2)
python -m odibi_core.examples.parity_demo
```

### Parity Testing (Phase 2 ✅)

ODIBI CORE ensures Pandas and Spark produce identical results:

```python
# Run the parity demo
python -m odibi_core.examples.parity_demo
```

**Expected output:**
```
🐼 PANDAS ENGINE
✓ Read CSV: 10 rows
✓ Executed SQL filter: 5 rows
✓ Aggregation: 3 categories

⚡ SPARK ENGINE  
✓ Read CSV: 10 rows
✓ Executed SQL filter: 5 rows
✓ Aggregation: 3 categories

🔍 PARITY VERIFICATION
✅ Row counts match
✅ Categories match
✅ Averages match (within tolerance)
✅ Parquet files match

Phase 2 SUCCESS: Engines are functionally equivalent! 🎉
```

## 📚 Documentation

### Documentation Structure

- **docs/walkthroughs/** - Developer guides and phase completion reports
- **docs/changelogs/** - Version history and roadmap
- **docs/reference/** - Technical reference guides

### Key Documents

- **[ROADMAP_V1.1_REASSESSMENT.md](docs/changelogs/ROADMAP_V1.1_REASSESSMENT.md)** - Revised 10-phase roadmap
- **[PHASE_9_COMPLETE.md](docs/walkthroughs/PHASE_9_COMPLETE.md)** - Latest phase completion report
- **[Engineering Plan](../ODIBI_CORE_V1_ENGINEERING_PLAN.md)** - Complete v1.0 design
- **[FORMAT_SUPPORT.md](docs/reference/FORMAT_SUPPORT.md)** - File format reference
- **[SQL_DATABASE_SUPPORT.md](docs/reference/SQL_DATABASE_SUPPORT.md)** - Database support guide
- **API Reference** - Auto-generated from docstrings (Phase 10)
- **Migration Guide** - Convert v2 → v1 (Phase 10)
- **LearnODIBI Guide** - Tutorial platform (Phase 10)

## 🔄 Development Phases

### ✅ Phase 1: Foundation & Scaffolding (COMPLETE)
- [x] Project structure and module organization
- [x] Base classes (Node, EngineContext, Tracker, Orchestrator)
- [x] 5 canonical Node types
- [x] Testing infrastructure

### ✅ Phase 2: Engine Contexts & Parity (COMPLETE)
- [x] PandasEngineContext with DuckDB
- [x] SparkEngineContext with local Spark
- [x] Parity tests and demo
- [x] CSV/Parquet I/O for both engines
- [x] SQL execution on both engines

### ✅ Phase 3: Config Loader & Validation (COMPLETE)
- [x] SQLite/JSON/CSV loaders
- [x] Config validation and schema checking
- [x] Circular dependency detection

### ✅ Phase 4: Node Implementation (COMPLETE)
- [x] ConnectNode (databases, Azure Blob, APIs)
- [x] IngestNode (CSV, Parquet, SQL)
- [x] StoreNode (Bronze/Silver/Gold writes)
- [x] TransformNode (SQL, Python functions)
- [x] PublishNode (API, Delta Lake exports)

### ✅ Phase 5: DAG Orchestration & Execution (COMPLETE)
- [x] DAGExecutor with topological sorting
- [x] Parallel execution with worker pools
- [x] Dependency resolution and validation
- [x] Fault tolerance and retry logic
- [x] Event-driven execution hooks

### ✅ Phase 6: Streaming & Scheduling (COMPLETE)
- [x] StreamManager (file_watch, incremental, interval modes)
- [x] CheckpointManager (DAG state persistence, resume)
- [x] ScheduleManager (cron, interval, file-watch triggers)
- [x] Continuous DAG execution
- [x] Watermark-based incremental processing

### ✅ Phase 7: Distributed & Cloud Integration (COMPLETE)
- [x] Cloud storage connectors (Azure Blob, S3, HDFS)
- [x] Distributed checkpoint system
- [x] Multi-node DAG execution
- [x] Stream connectors (Kafka, Kinesis, Event Hubs)
- [x] CloudCacheManager with content-addressed caching
- [x] MetricsManager for cache/execution metrics

**Note**: Simulation cache does not persist between runs; this is expected behavior for testing without cloud infrastructure.

### ✅ Phase 8: Observability & Automation
- [x] Structured logging with JSON Lines format
- [x] Prometheus metrics exporter
- [x] Grafana dashboard templates
- [x] Event bus for automation hooks
- [x] Multi-format metrics export (JSON, Parquet, Prometheus)
- [x] Per-node metrics and cache tracking
- [x] Memory usage monitoring

### ✅ Phase 9: SDK & Productization (COMPLETE)
- [x] CLI tool (`odibi` command) with run, validate, version commands
- [x] SDK layer with `ODIBI` and `Pipeline` classes
- [x] Config validator with circular dependency detection
- [x] `pip install .` packaging via pyproject.toml
- [x] Manifest.json for framework metadata
- [x] Version tracking with __version__.py
- [ ] PyPI publishing (Phase 10)
- [ ] Docker/Helm packaging (out of scope - local/Databricks focus)
- [ ] REST API for remote execution (Phase 10)

### 🔜 Phase 10: Learning Ecosystem & Community
- [ ] LearnODIBI tutorial platform
- [ ] Auto-generated API documentation
- [ ] Migration tools (v2 → v1)
- [ ] Sample projects and templates
- [ ] Community building (GitHub Discussions, talks)

## 📚 Documentation

### Quick Links

- **[Installation Guide](INSTALL.md)** — Detailed setup instructions
- **[Launch Studio](docs/guides/LAUNCH_LEARNODIBI_NOW.md)** — Start LearnODIBI teaching platform
- **[Docker Guide](docs/guides/DOCKER_QUICKSTART.md)** — Container deployment
- **[UI User Guide](docs/guides/UI_USER_GUIDE.md)** — LearnODIBI Studio features

### Learning Path

ODIBI CORE includes **11 comprehensive walkthroughs** (39.5 hours) covering:

1. **Beginner Track** (12h): Scaffolding → Dual-Engine → Orchestration
2. **Intermediate Track** (18h): Documentation → Parallelism → Streaming → Functions
3. **Advanced Track** (9.5h): Cloud → Observability → SDK/CLI

**Start Learning**: [View Walkthroughs](docs/walkthroughs/)  
**Manifest**: [walkthrough_manifest_v2.json](walkthrough_manifest_v2.json)

### Project Structure

```
odibi_core/
├── odibi_core/          # Core framework code
├── tests/               # Test suite
├── docs/                # Documentation
│   ├── walkthroughs/    # 11 teaching walkthroughs
│   ├── guides/          # User guides
│   ├── reports/         # Validation reports
│   └── reference/       # API reference
├── deploy/              # Deployment configs
│   ├── docker/          # Docker files
│   └── scripts/         # Launch scripts
├── scripts/             # Utility scripts
├── examples/            # Example pipelines
└── artifacts/           # Build outputs, logs
```

### Reports & Validation

- **[Teaching Overhaul](docs/reports/LEARNODIBI_TEACHING_OVERHAUL_FINAL.md)** — v2.0 teaching transformation
- **[Phase 10 Complete](docs/reports/PHASE_10_LEARNODIBI_COMPLETE.md)** — LearnODIBI Studio completion
- **[All Reports](docs/reports/)** — Validation, testing, audit reports

## 🤝 Contributing

Custom Nodes and functions can be registered dynamically:

```python
from odibi_core.nodes import register_node
from odibi_core.core.node import NodeBase

@register_node("custom_transform")
class CustomTransformNode(NodeBase):
    def run(self, data_map):
        # Custom logic
        return data_map
```

## 📄 License

MIT License - See LICENSE file for details

## 👤 Author

Henry Odibi - Data Engineering Framework Designer

---

**Status**: Functions Validation Complete - v1.0.4 Ready  
**Next**: Phase 10 - Learning Ecosystem & Community  
**Version**: 1.0.4
