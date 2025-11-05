# ODIBI Core - Azure Cloud Integration Notebooks

**Complete guided notebooks for using ODIBI Core with Azure cloud services**

These notebooks provide hands-on, step-by-step tutorials for building production-grade data pipelines on Azure using ODIBI Core framework.

---

## 📚 Notebook Overview

| Notebook | Focus | Complexity | Time | Prerequisites |
|----------|-------|------------|------|---------------|
| **01 - Azure Basic Setup** | CloudAdapter, basic read/write | Beginner | 30 min | Azure storage account |
| **02 - Medallion Pipeline** | Orchestrator, Bronze/Silver/Gold | Intermediate | 45 min | Multiple Azure containers |
| **03 - Databricks & Spark** | Spark engine, large-scale processing | Advanced | 60 min | Databricks workspace |

---

## 🎯 Learning Path

### For Beginners
**Start here** if you're new to ODIBI Core or Azure:
1. ✅ **Notebook 01** - Learn Azure basics and CloudAdapter
2. ✅ **Notebook 02** - Build your first medallion pipeline
3. ⏭️ Skip Notebook 03 initially (Spark/Databricks)

### For Data Engineers
**Already familiar with pipelines?**
1. ⏩ Skim Notebook 01 (review Azure setup)
2. ✅ **Notebook 02** - Focus on Orchestrator patterns
3. ✅ **Notebook 03** - Scale to Spark for production

### For Databricks Users
**Working on Databricks?**
1. ⏩ Review Notebook 01 (CloudAdapter concepts)
2. ⏩ Review Notebook 02 (medallion architecture)
3. ✅ **Notebook 03** - Your main focus (Spark engine)

---

## 📖 Detailed Notebook Descriptions

### Notebook 01: Azure Basic Setup & Read/Write

**File**: `Notebook_01_Azure_Basic_Setup.ipynb`

**What you'll learn**:
- Connect to Azure Blob Storage / ADLS Gen2
- Authenticate with account key and service principal
- Use `CloudAdapter` for direct file operations
- Read and write different formats (Parquet, CSV, JSON)
- List, check, and delete files on Azure
- Transform data and save back to Azure

**Key concepts**:
- `CloudAdapter.create("azure", ...)`
- `azure.read()` and `azure.write()`
- When to use CloudAdapter vs Orchestrator
- Azure path formats

**Output**:
- Sample data uploaded to Azure
- Understanding of CloudAdapter API
- Ready to build pipelines

---

### Notebook 02: Medallion Architecture on Azure

**File**: `Notebook_02_Azure_Medallion_Pipeline.ipynb`

**What you'll learn**:
- Build end-to-end pipelines with `Orchestrator`
- Implement Bronze → Silver → Gold layers
- Use `Steps` with SQL transformations
- Read/write directly to Azure using `abfss://` paths
- Enable checkpoints for failure recovery
- Track pipeline execution with Tracker
- Handle secrets securely

**Architecture implemented**:
```
BRONZE (raw data)  →  SILVER (cleaned)  →  GOLD (aggregated)
├─ customers          ├─ customers_clean     ├─ customer_metrics
└─ orders             └─ orders_clean        └─ sales_summary
```

**Key concepts**:
- `Orchestrator(steps=..., engine_type="pandas")`
- `Step` configuration for ingest/transform/store
- `CheckpointMode.LAYER` for resumability
- `enable_tracker=True` for lineage tracking
- Secrets management with `secrets={...}`

**Output**:
- Complete medallion pipeline on Azure
- Lineage JSON export
- Understanding of production patterns

---

### Notebook 03: Azure Databricks & Spark

**File**: `Notebook_03_Azure_Databricks_Spark.ipynb`

**What you'll learn**:
- Configure ODIBI Core for Spark engine
- Use Databricks secrets (`dbutils.secrets`)
- Process large datasets (millions of rows)
- Use Delta Lake for ACID transactions
- Partition data for query performance
- Monitor Spark execution with EventBus
- Time travel with Delta tables

**Scale demonstrated**:
- 1 million customer records
- 10 million order records
- Distributed processing across cluster

**Key concepts**:
- `engine_type="spark"` for distributed processing
- `secrets=get_databricks_secret` (callable)
- `format="delta"` for ACID transactions
- `partitionBy=[...]` for optimization
- Spark configuration via `spark_config`
- EventBus hooks for real-time monitoring

**Output**:
- Production-scale Spark pipeline
- Performance metrics and throughput analysis
- Delta Lake tables with time travel

---

## 🚀 Quick Start

### Prerequisites

1. **Azure Resources**:
   - Azure Storage Account (create in Azure Portal)
   - Containers: `bronze`, `silver`, `gold`
   - Access key or service principal credentials

2. **Python Environment**:
   ```bash
   pip install odibi-core pandas
   pip install azure-storage-file-datalake azure-identity
   ```

3. **For Databricks** (Notebook 03 only):
   - Databricks workspace
   - Cluster with ODIBI Core installed
   - Secret scope configured

### Running Notebooks

#### Option 1: Local Jupyter
```bash
# Install Jupyter
pip install jupyter

# Launch
jupyter notebook

# Open Notebook_01_Azure_Basic_Setup.ipynb
```

#### Option 2: VS Code
1. Install Python extension
2. Install Jupyter extension
3. Open `.ipynb` file
4. Select Python kernel
5. Run cells

#### Option 3: Databricks (for Notebook 03)
1. Upload notebook to Databricks workspace
2. Attach to cluster
3. Configure secret scope
4. Run cells

---

## 🔑 Configuration Guide

### Azure Setup

#### 1. Create Storage Account
```bash
# Via Azure CLI
az storage account create \
  --name mystorageaccount \
  --resource-group myresourcegroup \
  --location eastus \
  --sku Standard_LRS

# Create containers
az storage container create --name bronze --account-name mystorageaccount
az storage container create --name silver --account-name mystorageaccount
az storage container create --name gold --account-name mystorageaccount
```

#### 2. Get Access Key
```bash
az storage account keys list \
  --account-name mystorageaccount \
  --resource-group myresourcegroup
```

#### 3. Configure in Notebook
```python
AZURE_STORAGE_ACCOUNT = "mystorageaccount"
AZURE_STORAGE_KEY = "your-key-here"
```

### Databricks Setup (for Notebook 03)

#### 1. Create Secret Scope
```bash
# Via Databricks CLI
databricks secrets create-scope --scope odibi-secrets

# Add secrets
databricks secrets put --scope odibi-secrets --key azure-storage-account
databricks secrets put --scope odibi-secrets --key azure-storage-key
```

#### 2. Install ODIBI Core on Cluster
```bash
# In cluster configuration, add library:
# PyPI: odibi-core
```

---

## 📊 Comparison: CloudAdapter vs Orchestrator

| Feature | CloudAdapter (Notebook 01) | Orchestrator (Notebooks 02-03) |
|---------|---------------------------|-------------------------------|
| **Use Case** | Ad-hoc operations, exploration | Production pipelines |
| **Complexity** | Simple, direct API | Multi-step workflows |
| **Retry Logic** | ❌ No | ✅ Yes (configurable) |
| **Checkpoints** | ❌ No | ✅ Yes (resume on failure) |
| **Lineage Tracking** | ❌ No | ✅ Yes (full DAG tracking) |
| **SQL Transforms** | ❌ No | ✅ Yes (in Steps) |
| **Event Hooks** | ❌ No | ✅ Yes (EventBus) |
| **Parallelization** | ❌ No | ✅ Yes (DAG executor) |
| **Best For** | Scripts, notebooks, testing | Production, automation |

---

## 🎓 Concepts Covered

### Cloud Integration
- ✅ Azure Blob Storage / ADLS Gen2 authentication
- ✅ Service principal vs account key
- ✅ Managed identity (Databricks)
- ✅ Databricks secret management
- ✅ Azure path formats (`abfss://`)

### Data Engineering
- ✅ Medallion architecture (Bronze/Silver/Gold)
- ✅ Data quality and validation (SQL filters)
- ✅ Schema evolution and tracking
- ✅ Lineage and metadata capture
- ✅ Partitioning strategies

### Execution Engines
- ✅ Pandas engine (local, < 10 GB)
- ✅ Spark engine (distributed, > 10 GB)
- ✅ Engine-agnostic pipeline code
- ✅ When to switch engines

### Reliability
- ✅ Checkpoints (MANUAL, AUTO, LAYER modes)
- ✅ Retry logic with backoff
- ✅ Error handling and hooks
- ✅ Resume on failure

### Observability
- ✅ Tracker for lineage
- ✅ EventBus for monitoring
- ✅ Performance metrics
- ✅ Execution snapshots

### Formats & Storage
- ✅ Parquet (columnar, compressed)
- ✅ Delta Lake (ACID, time travel)
- ✅ CSV and JSON (exchange)
- ✅ Format selection criteria

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Authentication Failed
```
AuthenticationFailed: Server failed to authenticate the request
```

**Solution**:
- Verify `AZURE_STORAGE_ACCOUNT` is correct (no `.dfs.core.windows.net`)
- Check `AZURE_STORAGE_KEY` is complete (64 characters)
- Ensure storage account allows public network access
- For service principal: verify tenant ID, client ID, secret

#### 2. Container Not Found
```
ContainerNotFound: The specified container does not exist
```

**Solution**:
- Create containers in Azure Portal or CLI
- Check container name spelling (case-sensitive)
- Verify access permissions

#### 3. Module Not Found
```
ModuleNotFoundError: No module named 'odibi_core'
```

**Solution**:
```bash
pip install odibi-core
# For Databricks: install as cluster library
```

#### 4. Databricks Secrets Not Found
```
SecretNotFound: Secret does not exist
```

**Solution**:
```bash
# List scopes
databricks secrets list-scopes

# List secrets in scope
databricks secrets list --scope odibi-secrets

# Add missing secret
databricks secrets put --scope odibi-secrets --key azure-storage-key
```

#### 5. Slow Performance on Large Data
**Solution**:
- Switch from Pandas to Spark engine
- Enable partitioning: `partitionBy=["year", "month"]`
- Use Delta format instead of Parquet
- Increase Spark cluster size

---

## 📈 Performance Tips

### For Pandas Engine (Notebooks 01-02)
1. **Limit data size**: < 10 GB
2. **Use Parquet**: 5-10x faster than CSV
3. **Filter early**: Reduce data before transformations
4. **Disable cache in production**: `enable_cache=False`

### For Spark Engine (Notebook 03)
1. **Partition large tables**:
   ```python
   params={"partitionBy": ["year", "month", "country"]}
   ```

2. **Use Delta format**:
   ```python
   params={"format": "delta"}
   ```

3. **Enable adaptive execution**:
   ```python
   spark_config={
       "spark.sql.adaptive.enabled": "true",
       "spark.sql.adaptive.coalescePartitions.enabled": "true"
   }
   ```

4. **Right-size cluster**:
   - Small data (< 100 GB): 2-4 workers
   - Medium data (100 GB - 1 TB): 8-16 workers
   - Large data (> 1 TB): 32+ workers

---

## 🎯 Next Steps After Notebooks

### 1. Productionize Your Pipeline
- Move credentials to Azure Key Vault
- Schedule with Azure Data Factory or Databricks Jobs
- Add error alerting (email, Teams, Slack)
- Enable monitoring dashboards

### 2. Advanced Features
- Implement CDC (Change Data Capture)
- Add streaming with StreamManager
- Use distributed execution for parallel processing
- Register custom transformation functions

### 3. Integration
- Connect to Azure SQL Database
- Integrate with Power BI for visualization
- Export metrics to Prometheus
- Generate HTML execution reports

---

## 📚 Additional Resources

### Documentation
- [ODIBI_CORE_CLOUD_WORKFLOWS_GUIDE.md](ODIBI_CORE_CLOUD_WORKFLOWS_GUIDE.md) - Complete cloud integration guide
- [ODIBI_CORE_CONTRACT_CHEATSHEET.md](../ODIBI_CORE_CONTRACT_CHEATSHEET.md) - API reference
- [ODIBI_CORE_LEVEL_4_RELIABILITY.md](../ODIBI_CORE_LEVEL_4_RELIABILITY.md) - Checkpoints and retry

### Azure Resources
- [Azure Storage Documentation](https://docs.microsoft.com/azure/storage/)
- [Azure Databricks Documentation](https://docs.microsoft.com/azure/databricks/)
- [Delta Lake Documentation](https://docs.delta.io/)

### ODIBI Core Levels
- Level 1: Foundation
- Level 2: Building Pipelines
- Level 3: Understanding Execution
- Level 4: Reliability (checkpoints, retry)
- Level 5: Observability (metrics, events)
- Level 6: I/O Integrations (cloud storage)
- Level 7: Advanced (scheduling, streaming)

---

## 💡 Tips for Success

1. **Start Small**: Run Notebook 01 with sample data before scaling
2. **Test Locally First**: Use `simulate=True` to test without Azure
3. **Monitor Costs**: Azure storage and Databricks can be expensive
4. **Use Checkpoints**: Enable `checkpoint_mode=LAYER` for long pipelines
5. **Track Everything**: Always use `enable_tracker=True`
6. **Version Your Data**: Use Delta Lake for production
7. **Partition Wisely**: Choose partition keys based on query patterns
8. **Secure Secrets**: Never commit credentials to code

---

## 🤝 Support

- **Issues**: Open an issue on GitHub
- **Questions**: Check documentation or ask in discussions
- **Contributing**: PRs welcome for notebook improvements

---

## 📝 License

These notebooks are part of ODIBI Core and follow the same license.

---

**Ready to start?** Open [Notebook_01_Azure_Basic_Setup.ipynb](Notebook_01_Azure_Basic_Setup.ipynb) and begin your cloud data engineering journey! 🚀
