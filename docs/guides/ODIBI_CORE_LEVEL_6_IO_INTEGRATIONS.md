# LEVEL 6: I/O & Integrations

**Time**: 45-60 minutes  
**Goal**: Master file formats, database connections, cloud storage, and secrets management

---

## 🎯 What You'll Learn

- Use different file formats (CSV, Parquet, Delta, AVRO, JSON)
- Connect to databases (SQLite, PostgreSQL, JDBC)
- Integrate with cloud storage (Azure ADLS, S3)
- Manage secrets securely
- Choose the right format for your use case

---

## File Format Decision Tree

```
What format should I use?

├─ Development / Testing?
│  ├─ Need to inspect data manually?
│  │  └─ CSV (human-readable, easy to debug)
│  │
│  └─ Performance matters?
│     └─ Parquet (fast, columnar, compressed)
│
├─ Production Bronze Layer?
│  ├─ Match source format (if CSV → CSV, if JSON → JSON)
│  └─ OR standardize to Parquet (recommended)
│
├─ Production Silver/Gold Layer?
│  ├─ Need ACID transactions / time travel?
│  │  └─ Delta Lake (Spark only, ACID guarantees)
│  │
│  └─ No ACID needed?
│     └─ Parquet (efficient, widely compatible)
│
├─ Analytics / ML?
│  └─ Parquet (columnar queries, fast aggregations)
│
└─ Streaming / Event Data?
   ├─ JSON (flexible schema, easy to parse)
   └─ AVRO (schema evolution, compact)
```

---

## Pandas vs Spark I/O Comparison

### Formats Supported

| Format | Pandas Read | Pandas Write | Spark Read | Spark Write |
|--------|-------------|--------------|------------|-------------|
| **CSV** | ✅ `pd.read_csv()` | ✅ `df.to_csv()` | ✅ `spark.read.csv()` | ✅ `df.write.csv()` |
| **JSON** | ✅ `pd.read_json()` | ✅ `df.to_json()` | ✅ `spark.read.json()` | ✅ `df.write.json()` |
| **Parquet** | ✅ `pd.read_parquet()` | ✅ `df.to_parquet()` | ✅ `spark.read.parquet()` | ✅ `df.write.parquet()` |
| **AVRO** | ⚠️  Via `fastavro` | ⚠️  Via `fastavro` | ✅ `spark.read.format("avro")` | ✅ `df.write.format("avro")` |
| **ORC** | ❌ Not supported | ❌ Not supported | ✅ `spark.read.orc()` | ✅ `df.write.orc()` |
| **Delta** | ⚠️  Read as Parquet | ⚠️  Write as Parquet (no ACID) | ✅ `spark.read.format("delta")` | ✅ `df.write.format("delta")` |
| **Excel** | ✅ `pd.read_excel()` | ✅ `df.to_excel()` | ❌ Not supported | ❌ Not supported |
| **SQL** | ✅ `pd.read_sql()` | ✅ `df.to_sql()` | ✅ Via JDBC | ✅ Via JDBC |

---

## 1. File I/O - Examples

### CSV

```python
# Read CSV
Step(
    layer="ingest",
    name="read_csv",
    type="config_op",
    engine="pandas",
    value="data/customers.csv",
    params={
        "source_type": "csv",
        "header": True,
        "delimiter": ",",
        "encoding": "utf-8"
    },
    outputs={"data": "raw_customers"}
)

# Write CSV
Step(
    layer="store",
    name="save_csv",
    type="config_op",
    engine="pandas",
    value="output/customers.csv",
    params={
        "format": "csv",
        "index": False,
        "header": True
    },
    inputs={"data": "processed_customers"}
)
```

### Parquet (Recommended for Production)

```python
# Read Parquet
Step(
    layer="ingest",
    name="read_parquet",
    type="config_op",
    engine="pandas",  # or "spark"
    value="data/customers.parquet",
    params={"source_type": "parquet"},
    outputs={"data": "raw_customers"}
)

# Write Parquet (Pandas)
Step(
    layer="store",
    name="save_parquet",
    type="config_op",
    engine="pandas",
    value="output/customers.parquet",
    params={
        "format": "parquet",
        "compression": "snappy",  # or "gzip", "lz4"
        "index": False
    },
    inputs={"data": "processed_customers"}
)

# Write Parquet (Spark - partitioned)
Step(
    layer="store",
    name="save_parquet_partitioned",
    type="config_op",
    engine="spark",
    value="output/customers_partitioned.parquet",
    params={
        "format": "parquet",
        "mode": "overwrite",
        "partitionBy": ["year", "month"]  # Partition by year and month
    },
    inputs={"data": "processed_customers"}
)
```

### Delta Lake (Spark Only)

```python
# Read Delta
Step(
    layer="ingest",
    name="read_delta",
    type="config_op",
    engine="spark",
    value="data/delta/customers",
    params={"source_type": "delta"},
    outputs={"data": "raw_customers"}
)

# Write Delta
Step(
    layer="store",
    name="save_delta",
    type="config_op",
    engine="spark",
    value="data/delta/customers",
    params={
        "format": "delta",
        "mode": "overwrite",  # or "append", "merge"
        "partitionBy": ["country"]
    },
    inputs={"data": "processed_customers"}
)

# Delta with merge (upsert)
Step(
    layer="store",
    name="merge_delta",
    type="config_op",
    engine="spark",
    value="data/delta/customers",
    params={
        "format": "delta",
        "mode": "merge",
        "merge_key": "customer_id"  # Merge on this column
    },
    inputs={"data": "updated_customers"}
)
```

### JSON

```python
# Read JSON
Step(
    layer="ingest",
    name="read_json",
    type="config_op",
    engine="pandas",
    value="data/events.json",
    params={
        "source_type": "json",
        "lines": True  # JSON Lines format (one object per line)
    },
    outputs={"data": "raw_events"}
)

# Write JSON
Step(
    layer="store",
    name="save_json",
    type="config_op",
    engine="pandas",
    value="output/events.json",
    params={
        "format": "json",
        "orient": "records",  # Array of objects
        "lines": True
    },
    inputs={"data": "processed_events"}
)
```

---

## 2. Database Connections

### SQLite (Pandas)

```python
# Read from SQLite
Step(
    layer="ingest",
    name="read_sqlite",
    type="config_op",
    engine="pandas",
    value="SELECT * FROM customers WHERE active = 1",
    params={
        "source_type": "sqlite",
        "database": "data/mydatabase.db"
    },
    outputs={"data": "raw_customers"}
)

# Write to SQLite
Step(
    layer="store",
    name="save_sqlite",
    type="config_op",
    engine="pandas",
    value="customers_clean",  # Table name
    params={
        "format": "sqlite",
        "database": "data/mydatabase.db",
        "if_exists": "replace"  # or "append", "fail"
    },
    inputs={"data": "clean_customers"}
)
```

### PostgreSQL (Pandas)

```python
# Read from PostgreSQL
Step(
    layer="ingest",
    name="read_postgres",
    type="config_op",
    engine="pandas",
    value="SELECT * FROM customers",
    params={
        "source_type": "sql",
        "connection_string": "postgresql://user:password@localhost:5432/mydb"
    },
    outputs={"data": "raw_customers"}
)

# Write to PostgreSQL
Step(
    layer="store",
    name="save_postgres",
    type="config_op",
    engine="pandas",
    value="customers_clean",  # Table name
    params={
        "format": "sql",
        "connection_string": "postgresql://user:password@localhost:5432/mydb",
        "if_exists": "replace"
    },
    inputs={"data": "clean_customers"}
)
```

### JDBC (Spark)

```python
# Read from database via JDBC
Step(
    layer="ingest",
    name="read_jdbc",
    type="config_op",
    engine="spark",
    value="(SELECT * FROM customers) as customers",
    params={
        "source_type": "jdbc",
        "jdbc_url": "jdbc:postgresql://localhost:5432/mydb",
        "table": "(SELECT * FROM customers WHERE active = 1) as customers",
        "driver": "org.postgresql.Driver",
        "user": "myuser",
        "password": "mypassword"
    },
    outputs={"data": "raw_customers"}
)

# Write to database via JDBC
Step(
    layer="store",
    name="save_jdbc",
    type="config_op",
    engine="spark",
    value="customers_clean",  # Table name
    params={
        "format": "jdbc",
        "jdbc_url": "jdbc:postgresql://localhost:5432/mydb",
        "table": "customers_clean",
        "driver": "org.postgresql.Driver",
        "user": "myuser",
        "password": "mypassword",
        "mode": "overwrite"
    },
    inputs={"data": "clean_customers"}
)
```

---

## 3. Cloud Storage Integration

### Cloud Adapter Architecture

```
┌────────────────────────────────────────────────────────┐
│ CloudAdapter Factory                                   │
│ CloudAdapter.create(provider, **config)               │
└──────────────────┬─────────────────────────────────────┘
                   │
        ┌──────────┴──────────┬──────────────┬───────────┐
        │                     │              │           │
        ▼                     ▼              ▼           ▼
┌──────────────┐  ┌──────────────┐  ┌────────────┐  ┌────────────┐
│ AzureAdapter │  │  S3Adapter   │  │HDFSAdapter │  │KafkaAdapter│
│   (FULL)     │  │   (STUB)     │  │  (STUB)    │  │  (STUB)    │
└──────────────┘  └──────────────┘  └────────────┘  └────────────┘
       │
       ├─ read(path) → DataFrame
       ├─ write(df, path)
       ├─ exists(path) → bool
       ├─ list(path) → [files]
       ├─ delete(path)
       └─ get_secret(vault, key) → secret value
```

**Note**: Only AzureAdapter is FULLY implemented. S3, HDFS, Kafka are stubs (simulation mode).

### Azure ADLS (Azure Data Lake Storage)

#### Authentication Methods

```python
# Method 1: Account Key
from odibi_core.cloud_adapter import CloudAdapter

adapter = CloudAdapter.create(
    provider="azure",
    account_name="mystorageaccount",
    account_key="..."
)

# Method 2: Service Principal
adapter = CloudAdapter.create(
    provider="azure",
    account_name="mystorageaccount",
    tenant_id="...",
    client_id="...",
    client_secret="..."
)

# Method 3: Managed Identity (Databricks, Azure VMs)
adapter = CloudAdapter.create(
    provider="azure",
    account_name="mystorageaccount",
    use_managed_identity=True
)
```

#### Read from Azure ADLS

```python
# Read Parquet from ADLS
Step(
    layer="ingest",
    name="read_azure_parquet",
    type="config_op",
    engine="spark",
    value="abfss://container@storageaccount.dfs.core.windows.net/data/customers.parquet",
    params={
        "source_type": "parquet",
        "cloud_adapter": adapter  # Pass adapter
    },
    outputs={"data": "raw_customers"}
)
```

#### Write to Azure ADLS

```python
# Write Delta to ADLS
Step(
    layer="store",
    name="save_azure_delta",
    type="config_op",
    engine="spark",
    value="abfss://container@storageaccount.dfs.core.windows.net/data/delta/customers",
    params={
        "format": "delta",
        "mode": "overwrite",
        "cloud_adapter": adapter
    },
    inputs={"data": "processed_customers"}
)
```

#### CloudAdapter Methods

```python
# Check if file exists
exists = adapter.exists("abfss://container@account.dfs.core.windows.net/data/file.csv")

# List files in directory
files = adapter.list("abfss://container@account.dfs.core.windows.net/data/")
for file in files:
    print(file)

# Delete file
adapter.delete("abfss://container@account.dfs.core.windows.net/data/old_file.csv")

# Read file directly
df = adapter.read("abfss://container@account.dfs.core.windows.net/data/customers.parquet")

# Write file directly
adapter.write(df, "abfss://container@account.dfs.core.windows.net/data/output.parquet")
```

### S3 (Stub - Simulation Only)

```python
# S3 adapter is a stub (not fully implemented)
# Simulates operations without actual AWS calls

adapter = CloudAdapter.create(
    provider="s3",
    bucket="my-bucket",
    region="us-west-2",
    access_key_id="...",
    secret_access_key="..."
)

# Operations return simulated results
# Useful for testing without AWS credentials
```

---

## 4. Secrets Management

### Why Secrets Matter

**NEVER hardcode secrets in your code!**

```python
# ❌ BAD - Secret exposed in code
Step(
    value="SELECT * FROM ...",
    params={
        "connection_string": "postgresql://user:MyPassword123@localhost/db"
    }
)

# ✅ GOOD - Secret retrieved securely
Step(
    value="SELECT * FROM ...",
    params={
        "connection_string": context.get_secret("db_connection_string")
    }
)
```

### Secrets in Context

```python
from odibi_core.engine_context import PandasEngineContext

# Local Development: Pass secrets dict
context = PandasEngineContext(
    secrets={
        "db_password": "MyPassword123",
        "api_key": "abc123xyz",
        "azure_key": "..."
    }
)

# In pipeline step
password = context.get_secret("db_password")
connection_string = f"postgresql://user:{password}@localhost/db"
```

### Databricks Secrets

```python
from odibi_core.engine_context import SparkEngineContext

# Databricks: Use dbutils.secrets
context = SparkEngineContext(
    secrets=lambda key: dbutils.secrets.get("my_scope", key)
)

# In pipeline step
password = context.get_secret("db_password")
# Internally calls: dbutils.secrets.get("my_scope", "db_password")
```

### Azure Key Vault

```python
from odibi_core.cloud_adapter import CloudAdapter

# Create Azure adapter
adapter = CloudAdapter.create(
    provider="azure",
    account_name="mystorageaccount",
    account_key="..."
)

# Get secret from Key Vault
api_key = adapter.get_secret(
    vault_name="my-keyvault",
    secret_name="api-key"
)

print(f"API Key: {api_key}")
```

### Using Secrets in Steps

```python
# Setup context with secrets
context = PandasEngineContext(
    secrets={
        "postgres_password": "secret123",
        "api_token": "token456"
    }
)

# Read from database using secret
Step(
    layer="ingest",
    name="read_postgres",
    type="config_op",
    engine="pandas",
    value="SELECT * FROM customers",
    params={
        "source_type": "sql",
        "connection_string": lambda ctx: f"postgresql://user:{ctx.get_secret('postgres_password')}@localhost/db"
    },
    outputs={"data": "raw_customers"}
)
```

---

## Format Recommendations

| Use Case | Recommended Format | Why |
|----------|-------------------|-----|
| **Development** | CSV or Parquet | CSV: human-readable; Parquet: fast |
| **Bronze Layer** | Match source or Parquet | Preserve raw data as-is or standardize |
| **Silver Layer** | Parquet or Delta | Parquet: fast; Delta: ACID |
| **Gold Layer** | Delta (Spark) or Parquet | Delta: ACID + time travel; Parquet: efficient |
| **Analytics** | Parquet | Columnar format, fast aggregations |
| **Machine Learning** | Parquet | Fast reads, works with all ML libraries |
| **Streaming** | JSON or AVRO | Flexible schema, append-friendly |
| **Small files (<100MB)** | CSV or JSON | Easy to work with |
| **Large files (>10GB)** | Parquet or Delta | Compression + columnar queries |

---

## Try It Yourself

### Exercise 1: Multi-Format Pipeline

Build a pipeline that:
1. Reads CSV
2. Saves as Parquet (Bronze)
3. Cleans data
4. Saves as Delta (Silver)

### Exercise 2: Database Integration

Connect to a local SQLite database:
1. Create SQLite DB with sample data
2. Read using odibi_core
3. Transform
4. Write back to different table

### Exercise 3: Cloud Simulation

Use Azure CloudAdapter (or S3 stub):
1. Create adapter
2. List files
3. Check exists
4. Simulate read/write

### Exercise 4: Secrets Management

Create a pipeline that uses secrets:
1. Setup PandasEngineContext with secrets dict
2. Use secret in connection string
3. Never print the secret

---

## Key Takeaways

| Concept | What You Learned |
|---------|-----------------|
| **Formats** | CSV (dev), Parquet (production), Delta (ACID), JSON (streaming) |
| **Databases** | SQLite, PostgreSQL (Pandas), JDBC (Spark) |
| **Cloud** | Azure ADLS (full), S3/HDFS/Kafka (stubs) |
| **Secrets** | Never hardcode, use context.get_secret(), Key Vault |
| **Format Selection** | Decision tree based on use case |

---

## What's Next?

**Level 7: Advanced Features** - Schedule pipelines with cron, build streaming systems, use distributed execution, and create custom functions.

[Continue to Level 7 →](ODIBI_CORE_LEVEL_7_ADVANCED.md)

---

## Summary

✅ You know which format to use for each use case  
✅ You can read/write CSV, Parquet, Delta, JSON  
✅ You can connect to databases (SQLite, PostgreSQL, JDBC)  
✅ You can integrate with cloud storage (Azure ADLS)  
✅ You understand secure secrets management
