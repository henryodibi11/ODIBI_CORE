# ODIBI Core - Azure Integration Complete Index

**Complete guide to all Azure-related documentation and examples in ODIBI Core**

Last Updated: November 2025

---

## 📚 Documentation Structure

```
odibi_core/
├── docs/
│   ├── guides/
│   │   ├── ODIBI_CORE_CLOUD_WORKFLOWS_GUIDE.md ⭐ Main Azure Guide
│   │   ├── ODIBI_CORE_LEVEL_1_FOUNDATION.md
│   │   ├── ODIBI_CORE_LEVEL_2_BUILDING_PIPELINES.md
│   │   ├── ODIBI_CORE_LEVEL_3_EXECUTION.md
│   │   ├── ODIBI_CORE_LEVEL_4_RELIABILITY.md
│   │   ├── ODIBI_CORE_LEVEL_5_OBSERVABILITY.md
│   │   ├── ODIBI_CORE_LEVEL_6_IO_INTEGRATIONS.md
│   │   ├── ODIBI_CORE_LEVEL_7_ADVANCED.md
│   │   ├── ODIBI_CORE_LEVEL_8_COMPLETE.md
│   │   └── ODIBI_CORE_VISUAL_GUIDE.md
│   │
│   ├── reference/
│   │   ├── ODIBI_CORE_CONTRACT_CHEATSHEET.md ⭐ API Reference
│   │   └── azure_adapter_fix_proposal.py (Container handling fix)
│   │
│   ├── ODIBI_CORE_MASTERY_INDEX.md ⭐ Learning Path Index
│   └── DATA_ENGINEERING_MASTERY_PLAN.md
│
└── examples/
    └── azure_notebooks/ ⭐ Hands-On Tutorials
        ├── AZURE_NOTEBOOKS_README.md (Start here!)
        ├── Notebook_01_Azure_Basic_Setup.ipynb
        ├── Notebook_02_Azure_Medallion_Pipeline.ipynb
        └── Notebook_03_Azure_Databricks_Spark.ipynb
```

---

## 🚀 Quick Start Paths

### Path 1: Complete Beginner
**"I'm new to ODIBI Core and Azure"**

1. ✅ Read: [ODIBI_CORE_LEVEL_1_FOUNDATION.md](guides/ODIBI_CORE_LEVEL_1_FOUNDATION.md) (15 min)
2. ✅ Read: [ODIBI_CORE_LEVEL_2_BUILDING_PIPELINES.md](guides/ODIBI_CORE_LEVEL_2_BUILDING_PIPELINES.md) (30 min)
3. ✅ Practice: [Notebook_01_Azure_Basic_Setup.ipynb](../examples/azure_notebooks/Notebook_01_Azure_Basic_Setup.ipynb) (30 min)
4. ✅ Build: [Notebook_02_Azure_Medallion_Pipeline.ipynb](../examples/azure_notebooks/Notebook_02_Azure_Medallion_Pipeline.ipynb) (45 min)

**Total Time**: ~2 hours

### Path 2: Production Engineer
**"I need to build production pipelines on Azure"**

1. ⏩ Skim: [ODIBI_CORE_MASTERY_INDEX.md](ODIBI_CORE_MASTERY_INDEX.md)
2. ✅ Read: [ODIBI_CORE_CLOUD_WORKFLOWS_GUIDE.md](guides/ODIBI_CORE_CLOUD_WORKFLOWS_GUIDE.md) (30 min)
3. ✅ Reference: [ODIBI_CORE_CONTRACT_CHEATSHEET.md](reference/ODIBI_CORE_CONTRACT_CHEATSHEET.md)
4. ✅ Build: [Notebook_02_Azure_Medallion_Pipeline.ipynb](../examples/azure_notebooks/Notebook_02_Azure_Medallion_Pipeline.ipynb)
5. ✅ Read: [ODIBI_CORE_LEVEL_4_RELIABILITY.md](guides/ODIBI_CORE_LEVEL_4_RELIABILITY.md) (Checkpoints, retry)

**Total Time**: ~1.5 hours

### Path 3: Databricks User
**"I'm working on Azure Databricks with Spark"**

1. ⏩ Skim: [ODIBI_CORE_CLOUD_WORKFLOWS_GUIDE.md](guides/ODIBI_CORE_CLOUD_WORKFLOWS_GUIDE.md) (Azure setup)
2. ✅ Focus: [Notebook_03_Azure_Databricks_Spark.ipynb](../examples/azure_notebooks/Notebook_03_Azure_Databricks_Spark.ipynb) (60 min)
3. ✅ Read: [ODIBI_CORE_LEVEL_6_IO_INTEGRATIONS.md](guides/ODIBI_CORE_LEVEL_6_IO_INTEGRATIONS.md) (Delta Lake, formats)
4. ✅ Reference: [ODIBI_CORE_CONTRACT_CHEATSHEET.md](reference/ODIBI_CORE_CONTRACT_CHEATSHEET.md)

**Total Time**: ~1.5 hours

---

## 📖 Documentation Guide

### Core Guides (Learning Path)

| Document | Focus | Level | Time | Prerequisites |
|----------|-------|-------|------|---------------|
| [ODIBI_CORE_LEVEL_1_FOUNDATION.md](guides/ODIBI_CORE_LEVEL_1_FOUNDATION.md) | Framework overview, first pipeline | Beginner | 15 min | None |
| [ODIBI_CORE_LEVEL_2_BUILDING_PIPELINES.md](guides/ODIBI_CORE_LEVEL_2_BUILDING_PIPELINES.md) | 5 node types, Steps, data_map | Beginner | 30 min | Level 1 |
| [ODIBI_CORE_LEVEL_3_EXECUTION.md](guides/ODIBI_CORE_LEVEL_3_EXECUTION.md) | DAG executor, Tracker, EventBus | Intermediate | 30 min | Level 2 |
| [ODIBI_CORE_LEVEL_4_RELIABILITY.md](guides/ODIBI_CORE_LEVEL_4_RELIABILITY.md) | Checkpoints, cache, retry logic | Intermediate | 30 min | Level 3 |
| [ODIBI_CORE_LEVEL_5_OBSERVABILITY.md](guides/ODIBI_CORE_LEVEL_5_OBSERVABILITY.md) | Metrics, events, HTML stories | Intermediate | 30 min | Level 4 |
| [ODIBI_CORE_LEVEL_6_IO_INTEGRATIONS.md](guides/ODIBI_CORE_LEVEL_6_IO_INTEGRATIONS.md) | Formats, cloud storage, databases | Intermediate | 45 min | Level 5 |
| [ODIBI_CORE_LEVEL_7_ADVANCED.md](guides/ODIBI_CORE_LEVEL_7_ADVANCED.md) | Scheduling, streaming, distributed | Advanced | 45 min | Level 6 |
| [ODIBI_CORE_LEVEL_8_COMPLETE.md](guides/ODIBI_CORE_LEVEL_8_COMPLETE.md) | Complete patterns, best practices | Advanced | 60 min | Level 7 |

### Azure-Specific Guides

| Document | Focus | Audience | Key Topics |
|----------|-------|----------|------------|
| [ODIBI_CORE_CLOUD_WORKFLOWS_GUIDE.md](guides/ODIBI_CORE_CLOUD_WORKFLOWS_GUIDE.md) ⭐ | Complete Azure workflows | All | Authentication, medallion architecture, Spark vs Pandas |
| [Notebook_01_Azure_Basic_Setup.ipynb](../examples/azure_notebooks/Notebook_01_Azure_Basic_Setup.ipynb) | CloudAdapter basics | Beginner | Read/write, file operations, formats |
| [Notebook_02_Azure_Medallion_Pipeline.ipynb](../examples/azure_notebooks/Notebook_02_Azure_Medallion_Pipeline.ipynb) | Production pipeline | Intermediate | Orchestrator, Steps, Bronze/Silver/Gold |
| [Notebook_03_Azure_Databricks_Spark.ipynb](../examples/azure_notebooks/Notebook_03_Azure_Databricks_Spark.ipynb) | Large-scale processing | Advanced | Spark engine, Delta Lake, partitioning |

### Reference Documentation

| Document | Purpose | Use When |
|----------|---------|----------|
| [ODIBI_CORE_CONTRACT_CHEATSHEET.md](reference/ODIBI_CORE_CONTRACT_CHEATSHEET.md) | API reference, contracts | Need specific API details |
| [ODIBI_CORE_MASTERY_INDEX.md](ODIBI_CORE_MASTERY_INDEX.md) | Learning path overview | Planning learning journey |
| [azure_adapter_fix_proposal.py](reference/azure_adapter_fix_proposal.py) | Container handling design | Understanding adapter internals |

---

## 🔑 Key Concepts by Document

### CloudAdapter vs Orchestrator

**Use CloudAdapter** (see Notebook 01):
- Ad-hoc scripts
- Data exploration
- Direct file operations
- Simple read/write

**Use Orchestrator** (see Notebooks 02-03):
- Production pipelines
- Multi-step workflows
- Retry logic needed
- Checkpoint/resume
- Lineage tracking

### Engine Selection

**Pandas Engine** (see Notebook 02):
- Data size < 10 GB
- Single machine
- Fast for small data
- Local development

**Spark Engine** (see Notebook 03):
- Data size > 10 GB
- Distributed cluster
- Horizontal scaling
- Production large-scale

### Azure Authentication

**Account Key** (simplest):
```python
CloudAdapter.create("azure", account_name="...", account_key="...")
```

**Service Principal** (production):
```python
CloudAdapter.create("azure", 
    tenant_id="...", client_id="...", client_secret="...")
```

**Databricks Secrets** (Databricks):
```python
secrets = lambda key: dbutils.secrets.get("scope", key)
Orchestrator(..., secrets=secrets)
```

---

## ⚡ Important Updates

### Container Handling Fix (November 2025)

**What Changed**: The `container` parameter in `CloudAdapter.__init__()` now works as expected!

**Before** (confusing):
```python
azure = CloudAdapter.create("azure", container="bronze")
azure.read("bronze/data/file.parquet")  # Had to repeat container!
```

**After** (fixed):
```python
azure = CloudAdapter.create("azure", container="bronze")
azure.read("data/file.parquet")  # Path relative to bronze container ✅
```

**See**: [azure_adapter_fix_proposal.py](reference/azure_adapter_fix_proposal.py) for implementation details.

**Affected Documents**:
- ✅ CloudAdapter implementation updated
- ✅ Notebook_01 updated with examples
- ✅ CLOUD_WORKFLOWS_GUIDE reflects new behavior
- ✅ All notebooks use correct patterns

---

## 🎯 Common Tasks

### Task: First-Time Azure Setup
1. Read: [AZURE_NOTEBOOKS_README.md](../examples/azure_notebooks/AZURE_NOTEBOOKS_README.md) (Setup section)
2. Create Azure Storage Account
3. Get access key
4. Run: [Notebook_01_Azure_Basic_Setup.ipynb](../examples/azure_notebooks/Notebook_01_Azure_Basic_Setup.ipynb)

### Task: Build Medallion Pipeline
1. Read: [ODIBI_CORE_CLOUD_WORKFLOWS_GUIDE.md](guides/ODIBI_CORE_CLOUD_WORKFLOWS_GUIDE.md) (Medallion section)
2. Review: [ODIBI_CORE_LEVEL_2_BUILDING_PIPELINES.md](guides/ODIBI_CORE_LEVEL_2_BUILDING_PIPELINES.md)
3. Follow: [Notebook_02_Azure_Medallion_Pipeline.ipynb](../examples/azure_notebooks/Notebook_02_Azure_Medallion_Pipeline.ipynb)

### Task: Scale to Databricks
1. Setup Databricks cluster
2. Configure secret scope
3. Follow: [Notebook_03_Azure_Databricks_Spark.ipynb](../examples/azure_notebooks/Notebook_03_Azure_Databricks_Spark.ipynb)

### Task: Add Reliability (Checkpoints, Retry)
1. Read: [ODIBI_CORE_LEVEL_4_RELIABILITY.md](guides/ODIBI_CORE_LEVEL_4_RELIABILITY.md)
2. Enable in Orchestrator:
   ```python
   Orchestrator(
       enable_checkpoints=True,
       checkpoint_mode=CheckpointMode.LAYER,
       max_retries=3,
       retry_backoff=True
   )
   ```

### Task: Monitor Pipeline Execution
1. Read: [ODIBI_CORE_LEVEL_5_OBSERVABILITY.md](guides/ODIBI_CORE_LEVEL_5_OBSERVABILITY.md)
2. Enable Tracker: `enable_tracker=True`
3. Register EventBus hooks for alerts

---

## 📊 Feature Coverage Matrix

| Feature | Notebook 01 | Notebook 02 | Notebook 03 | Guide Reference |
|---------|-------------|-------------|-------------|-----------------|
| **CloudAdapter** | ✅ Main focus | ❌ | ❌ | CLOUD_WORKFLOWS_GUIDE |
| **Orchestrator** | ❌ | ✅ Main focus | ✅ Main focus | LEVEL_2, LEVEL_3 |
| **Pandas Engine** | ✅ | ✅ | ❌ | LEVEL_1, LEVEL_2 |
| **Spark Engine** | ❌ | ❌ | ✅ | LEVEL_6, Notebook 03 |
| **Azure ADLS** | ✅ | ✅ | ✅ | CLOUD_WORKFLOWS_GUIDE |
| **Databricks** | ❌ | ❌ | ✅ | Notebook 03 |
| **Checkpoints** | ❌ | ✅ | ✅ | LEVEL_4 |
| **Tracker** | ❌ | ✅ | ✅ | LEVEL_3, LEVEL_5 |
| **EventBus** | ❌ | ❌ | ✅ | LEVEL_3, LEVEL_5 |
| **Delta Lake** | ❌ | ❌ | ✅ | LEVEL_6, Notebook 03 |
| **Partitioning** | ❌ | ❌ | ✅ | Notebook 03 |
| **Secrets** | ✅ Env vars | ✅ Dict | ✅ Databricks | CLOUD_WORKFLOWS_GUIDE |

---

## 🔗 Related Resources

### ODIBI Core Framework
- [Main Documentation](index.md)
- [Walkthroughs](walkthroughs/)
- [API Reference](reference/)

### Azure Resources
- [Azure Storage Documentation](https://docs.microsoft.com/azure/storage/)
- [Azure Databricks Documentation](https://docs.microsoft.com/azure/databricks/)
- [Delta Lake Documentation](https://docs.delta.io/)

### Other Projects in Workspace
- `odibi_de_v2/`: Production data engineering framework (Pandas/Spark medallion)
- `Energy Efficiency/`: Databricks medallion pipeline example
- `global-utils/`: Shared Databricks utilities

---

## 📝 Document Maintenance

### Last Updates
- **2025-11**: Azure adapter container fix applied
- **2025-11**: All Azure notebooks created
- **2025-11**: CLOUD_WORKFLOWS_GUIDE comprehensive rewrite
- **2025-11**: Complete documentation reorganization

### Next Updates Needed
- [ ] Add AWS S3 full implementation (currently simulated)
- [ ] Add HDFS adapter implementation
- [ ] Add Kafka streaming examples
- [ ] Add Azure SQL integration examples
- [ ] Add Key Vault integration examples

---

## 🤝 Contributing

Found an issue or want to improve documentation?
1. Check existing [walkthroughs](walkthroughs/)
2. Follow [WALKTHROUGH_AUTHORING_GUIDE.md](WALKTHROUGH_AUTHORING_GUIDE.md)
3. Submit PR with updates

---

## 💡 Tips for Success

1. **Start Small**: Run Notebook 01 before building production pipelines
2. **Use Checkpoints**: Always enable for production (`checkpoint_mode=LAYER`)
3. **Track Everything**: Enable `enable_tracker=True` for lineage
4. **Secure Secrets**: Never commit credentials, use Key Vault or Databricks secrets
5. **Choose Right Engine**: Pandas for < 10 GB, Spark for larger
6. **Partition Wisely**: Partition large datasets by frequently-queried columns
7. **Use Delta**: Delta Lake for production (ACID, time travel)

---

**Questions?** See [AZURE_NOTEBOOKS_README.md](../examples/azure_notebooks/AZURE_NOTEBOOKS_README.md) troubleshooting section.

**Ready to start?** Open [Notebook_01_Azure_Basic_Setup.ipynb](../examples/azure_notebooks/Notebook_01_Azure_Basic_Setup.ipynb)! 🚀
