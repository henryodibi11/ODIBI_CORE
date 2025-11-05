# ODIBI CORE MASTERY GUIDE

**Learn to build production data pipelines with odibi_core**

This is a visual-first, progressive learning guide that teaches you how to use ALL features of odibi_core through maps, decision trees, simple diagrams, and tables. By the end, you'll be able to build production-ready pipelines using the complete framework.

---

## 🎯 What You'll Master

- **5 Node Types**: Connect, Ingest, Transform, Store, Publish
- **2 Execution Engines**: Pandas (local) and Spark (distributed)
- **Orchestration**: Steps → DAG → Parallel Execution
- **State Management**: data_map, Tracker, Checkpoints, Cache
- **Observability**: Events, Metrics, HTML Stories
- **I/O**: CSV, Parquet, Delta, SQL, Cloud Storage (Azure/S3)
- **Advanced**: Scheduling, Streaming, Distributed Execution, Custom Functions

---

## 📚 Learning Path

### LEVEL 1: Foundation (15-20 min)
**File**: [ODIBI_CORE_LEVEL_1_FOUNDATION.md](ODIBI_CORE_LEVEL_1_FOUNDATION.md)

Understand what odibi_core is, see the big picture, and run your first pipeline.

**You'll Learn**:
- What odibi_core is and why it exists
- The big picture of all components
- Core philosophy (contract-driven, engine-agnostic)
- How to run a simple 3-step pipeline

---

### LEVEL 2: Building Pipelines (30-45 min)
**File**: [ODIBI_CORE_LEVEL_2_BUILDING_PIPELINES.md](ODIBI_CORE_LEVEL_2_BUILDING_PIPELINES.md)

Master the 5 node types, understand Step configuration, and build working pipelines.

**You'll Learn**:
- The 5 node types and when to use each
- Step configuration structure
- How data flows through data_map
- Build complete working pipelines

---

### LEVEL 3: Understanding Execution (30-45 min)
**File**: [ODIBI_CORE_LEVEL_3_EXECUTION.md](ODIBI_CORE_LEVEL_3_EXECUTION.md)

Understand how DAGExecutor orchestrates nodes, how Tracker captures details, and the EventBus lifecycle.

**You'll Learn**:
- How DAGExecutor orchestrates execution
- Node lifecycle and state transitions
- How Tracker captures lineage and snapshots
- EventBus hooks and automation

---

### LEVEL 4: Making It Reliable (30-45 min)
**File**: [ODIBI_CORE_LEVEL_4_RELIABILITY.md](ODIBI_CORE_LEVEL_4_RELIABILITY.md)

Use checkpoints to resume pipelines, enable caching, and handle errors gracefully.

**You'll Learn**:
- Checkpoint modes and resume logic
- Cache system for faster development
- Retry configuration and error handling
- Building fault-tolerant pipelines

---

### LEVEL 5: Observability & Monitoring (30-45 min)
**File**: [ODIBI_CORE_LEVEL_5_OBSERVABILITY.md](ODIBI_CORE_LEVEL_5_OBSERVABILITY.md)

Collect metrics, register automation hooks, generate HTML stories, and export to Prometheus.

**You'll Learn**:
- MetricsManager for performance tracking
- EventBus hooks for alerts and automation
- Generate interactive HTML execution reports
- Export metrics to Prometheus

---

### LEVEL 6: I/O & Integrations (45-60 min)
**File**: [ODIBI_CORE_LEVEL_6_IO_INTEGRATIONS.md](ODIBI_CORE_LEVEL_6_IO_INTEGRATIONS.md)

Work with different file formats, connect to databases, integrate with cloud storage, and manage secrets.

**You'll Learn**:
- CSV, Parquet, Delta, AVRO formats
- Database connections (SQLite, PostgreSQL, JDBC)
- Cloud storage integration (Azure ADLS, S3)
- Secure secrets management

---

### LEVEL 7: Advanced Features (45-60 min)
**File**: [ODIBI_CORE_LEVEL_7_ADVANCED.md](ODIBI_CORE_LEVEL_7_ADVANCED.md)

Schedule pipelines, build streaming systems, use distributed execution, and create custom functions.

**You'll Learn**:
- Schedule pipelines with cron expressions
- Build streaming/continuous pipelines
- Distributed execution with thread/process pools
- Register and use custom transform functions

---

### LEVEL 8: Putting It All Together (60+ min)
**File**: [ODIBI_CORE_LEVEL_8_COMPLETE.md](ODIBI_CORE_LEVEL_8_COMPLETE.md)

Build complete production-ready pipelines with best practices, patterns, and real-world examples.

**You'll Learn**:
- Complete pipeline patterns (Medallion, Streaming, Cloud)
- Best practices checklist
- Troubleshooting guide
- 4 complete production examples

---

## 🚀 Quick Start

**New to odibi_core?** Start with Level 1 and work through sequentially.

**Have some experience?** Jump to the level that matches your knowledge:
- Know the basics? → Level 3 (Execution)
- Building production pipelines? → Level 4 (Reliability)
- Need advanced features? → Level 7 (Advanced)

**Need a reference?** Check [ODIBI_CORE_CONTRACT_CHEATSHEET.md](ODIBI_CORE_CONTRACT_CHEATSHEET.md) for detailed API documentation.

---

## 📖 How to Use This Guide

1. **Follow the levels sequentially** - Each builds on the previous
2. **Run the code examples** - Don't just read, practice!
3. **Complete the exercises** - Reinforce your learning
4. **Experiment** - Modify examples to see what happens
5. **Refer back** - Use as a reference when building pipelines

---

## 🎓 Philosophy

odibi_core is built on three core principles:

1. **Contract-Driven**: Everything follows clear interfaces (ABC contracts)
2. **Engine-Agnostic**: Write once, run on Pandas or Spark
3. **Observable**: Built-in tracking, metrics, and monitoring

This guide teaches you to think in these patterns, not just memorize APIs.

---

## ✅ Prerequisites

- Python 3.8+
- Basic understanding of DataFrames (Pandas or Spark)
- Basic SQL knowledge
- Familiarity with command line

---

**Ready to start? Go to [Level 1: Foundation](ODIBI_CORE_LEVEL_1_FOUNDATION.md)**
