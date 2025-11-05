# ODIBI CORE - Contract Implementation Cheatsheet

A quick reference guide showing how different implementations follow the core contracts in ODIBI CORE.

---

## 📋 Table of Contents

1. [NodeBase Contract - Pipeline Operations](#nodebase-contract---pipeline-operations)
2. [EngineContext Contract - Execution Engines](#enginecontext-contract---execution-engines)
3. [Reader/Writer Contracts - I/O Operations](#readerwriter-contracts---io-operations)
4. [CloudAdapter Contract - Cloud Storage](#cloudadapter-contract---cloud-storage)

---

## NodeBase Contract - Pipeline Operations

**Contract:** `NodeBase` (Abstract Base Class)  
**Location:** `odibi_core/core/node.py`  
**Purpose:** All pipeline operations are modeled as Nodes

### Contract Requirements

```python
@abstractmethod
def run(data_map: Dict[str, Any]) -> Dict[str, Any]:
    """Execute node operation and return updated data_map"""
    pass
```

### Implementation Comparison

| Node Type | Purpose | Inputs | Outputs | Key Parameters |
|-----------|---------|--------|---------|----------------|
| **IngestNode** | Read data from sources | None (uses `step.value`) | Writes to `data_map` via `step.outputs` | `step.value` = source path/query<br>`step.params` = read options |
| **TransformNode** | Transform data via SQL or function | Reads from `data_map` via `step.inputs` | Writes to `data_map` via `step.outputs` | `step.type` = "sql" or "function"<br>`step.value` = SQL query or function path<br>`step.inputs` = logical name → dataset key mapping |
| **StoreNode** | Persist data to storage layers | Reads from `data_map` via `step.inputs` | No output (side effect: writes to disk) | `step.value` = target path<br>`step.params` = write options (mode, format) |
| **ConnectNode** | Establish database/storage connections | None | No output (side effect: connection state) | `step.value` = connection string<br>`step.params` = connection params (user, password_key) |
| **PublishNode** | Export to external systems | Reads from `data_map` via `step.inputs` | No output (side effect: writes to external system) | `step.value` = target endpoint<br>`step.params` = write options (mode, format) |

### Common Input/Output Pattern

All nodes follow this pattern:

```python
# INPUT: data_map structure
data_map = {
    "raw_data": pd.DataFrame(...),      # Dataset key → DataFrame
    "filtered_data": pd.DataFrame(...)
}

# Step configuration (inputs/outputs use logical names)
step = Step(
    inputs={"bronze": "raw_data"},      # Logical name → dataset key
    outputs={"data": "transformed_data"}
)

# OUTPUT: Updated data_map
updated_map = node.run(data_map)
# Returns: {"raw_data": ..., "filtered_data": ..., "transformed_data": ...}
```

### Quick Examples

#### IngestNode
```python
step = Step(
    layer="ingest", 
    name="read_csv", 
    type="config_op",
    engine="pandas",
    value="data/input.csv",  # Source path
    outputs={"data": "raw_data"}  # Write to data_map["raw_data"]
)
node = IngestNode(step, context, tracker, events)
data_map = node.run({})  # Empty input, produces output
```

#### TransformNode (SQL)
```python
step = Step(
    layer="transform",
    name="filter_high_efficiency",
    type="sql",
    engine="pandas",
    value="SELECT * FROM bronze WHERE efficiency > 80",  # SQL query
    inputs={"bronze": "raw_data"},  # Read from data_map["raw_data"]
    outputs={"data": "filtered_data"}  # Write to data_map["filtered_data"]
)
node = TransformNode(step, context, tracker, events)
data_map = node.run({"raw_data": bronze_df})
```

#### TransformNode (Function)
```python
step = Step(
    layer="transform",
    name="calc_enthalpy",
    type="function",
    engine="pandas",
    value="thermo.steam.calc_enthalpy",  # Function path
    inputs={"data": "raw_data"},
    outputs={"data": "enriched_data"}
)
```

#### StoreNode
```python
step = Step(
    layer="store",
    name="write_bronze",
    type="config_op",
    engine="pandas",
    value="output/bronze.parquet",  # Target path
    inputs={"data": "raw_data"},  # Read from data_map["raw_data"]
    params={"mode": "overwrite"}
)
```

#### ConnectNode
```python
step = Step(
    layer="connect",
    name="connect_postgres",
    type="config_op",
    engine="pandas",
    value="postgresql://host:port/db",
    params={"user": "admin", "password_key": "db_pass"}  # Resolves secrets
)
```

#### PublishNode
```python
step = Step(
    layer="publish",
    name="publish_to_delta",
    type="config_op",
    engine="spark",
    value="delta_table_name",
    inputs={"data": "gold_data"},
    params={"mode": "append"}
)
```

---

## EngineContext Contract - Execution Engines

**Contract:** `EngineContext` (Abstract Base Class)  
**Location:** `odibi_core/engine/base_context.py`  
**Purpose:** Execution environments for Pandas or Spark

### Contract Requirements

```python
@abstractmethod
def connect(**kwargs) -> EngineContext
def read(source: str, **kwargs) -> DataFrame
def write(df: DataFrame, target: str, **kwargs) -> None
def execute_sql(query: str, **kwargs) -> DataFrame
def register_temp(name: str, df: DataFrame) -> None
def collect_sample(df: DataFrame, n: int = 5) -> pd.DataFrame
def get_secret(key: str) -> str
```

### Implementation Comparison

| Feature | PandasEngineContext | SparkEngineContext |
|---------|---------------------|-------------------|
| **Engine** | Pandas + DuckDB for SQL | PySpark (local or cluster) |
| **DataFrame Type** | `pd.DataFrame` | `pyspark.sql.DataFrame` |
| **SQL Backend** | DuckDB (in-memory) | Spark SQL |
| **Initialization** | `PandasEngineContext(secrets={...})` | `SparkEngineContext(secrets={...}, spark_config={...})` |
| **Connection** | Initializes DuckDB in-memory | Creates/gets SparkSession |
| **Temp Table** | Stores in `_temp_tables` dict, registers with DuckDB | `df.createOrReplaceTempView(name)` |
| **Sample Collection** | `df.head(n)` | `df.limit(n).toPandas()` with smart sampling |

### Supported Formats

#### PandasEngineContext - Read/Write Formats

| Format | Read Method | Write Method | Auto-Detection | Notes |
|--------|-------------|--------------|----------------|-------|
| **CSV** | `pd.read_csv()` | `df.to_csv()` | `.csv` extension | Supports `header`, `delimiter` params |
| **JSON** | `pd.read_json()` | `df.to_json()` | `.json` extension | Supports `orient` param |
| **Parquet** | `pd.read_parquet()` | `df.to_parquet()` | `.parquet` extension | Recommended for large data |
| **AVRO** | `pdx.read_avro()` | `pdx.to_avro()` | `.avro` extension | Requires `pandavro` package |
| **SQLite** | `pd.read_sql()` | N/A | `.db`, `.sqlite` | Requires `table` param |
| **SQL Database** | `pd.read_sql()` | N/A | `source_type="sql"` | Requires SQLAlchemy, `connection_string` |

**Read Examples:**
```python
# CSV
df = pandas_ctx.read("data/input.csv", header=True)

# Parquet
df = pandas_ctx.read("data/input.parquet")

# SQLite
df = pandas_ctx.read("data.db", source_type="sqlite", table="my_table")

# SQL Database
df = pandas_ctx.read("connection.db", 
                     source_type="sql", 
                     connection_string="postgresql://user:pass@host/db",
                     query="SELECT * FROM table WHERE id > 100")
```

**Write Examples:**
```python
# CSV
pandas_ctx.write(df, "output.csv", index=False)

# Parquet
pandas_ctx.write(df, "output.parquet")

# JSON
pandas_ctx.write(df, "output.json", orient="records")
```

#### SparkEngineContext - Read/Write Formats

| Format | Read Method | Write Method | Auto-Detection | Notes |
|--------|-------------|--------------|----------------|-------|
| **CSV** | `spark.read.csv()` | `df.write.csv()` | `.csv` extension | Supports `header`, `inferSchema` |
| **JSON** | `spark.read.json()` | `df.write.json()` | `.json` extension | Line-delimited JSON |
| **Parquet** | `spark.read.parquet()` | `df.write.parquet()` | `.parquet` extension | Columnar format, efficient |
| **AVRO** | `spark.read.format("avro")` | `df.write.format("avro")` | `.avro` extension | Requires spark-avro package |
| **ORC** | `spark.read.orc()` | `df.write.orc()` | `.orc` extension | Optimized Row Columnar |
| **Delta** | `spark.read.format("delta")` | `df.write.format("delta")` | `.delta` or "delta" in path | ACID transactions, time travel |
| **JDBC** | `spark.read.format("jdbc")` | `df.write.format("jdbc")` | `source_type="jdbc"` | Requires JDBC driver, connection params |

**Read Examples:**
```python
# CSV
df = spark_ctx.read("data/input.csv", header=True)

# Parquet
df = spark_ctx.read("data/input.parquet")

# Delta
df = spark_ctx.read("delta/table_path", source_type="delta")

# JDBC
df = spark_ctx.read("table_name",
                    source_type="jdbc",
                    jdbc_url="jdbc:postgresql://host:5432/db",
                    table="users",
                    driver="org.postgresql.Driver",
                    user="admin",
                    password="secret")
```

**Write Examples:**
```python
# CSV
spark_ctx.write(df, "output.csv", mode="overwrite", header=True)

# Parquet
spark_ctx.write(df, "output.parquet", mode="append")

# Delta
spark_ctx.write(df, "delta/table", source_type="delta", mode="overwrite")

# JDBC
spark_ctx.write(df, "table_name",
                source_type="jdbc",
                jdbc_url="jdbc:postgresql://host:5432/db",
                table="users",
                driver="org.postgresql.Driver",
                mode="overwrite")
```

### SQL Operations

#### PandasEngineContext - DuckDB SQL

```python
# Register temp tables
pandas_ctx.register_temp("bronze", bronze_df)
pandas_ctx.register_temp("config", config_df)

# Execute SQL
result = pandas_ctx.execute_sql("""
    SELECT b.*, c.factor
    FROM bronze b
    LEFT JOIN config c ON b.type = c.type
    WHERE b.efficiency > 80
""")
```

#### SparkEngineContext - Spark SQL

```python
# Register temp views
spark_ctx.register_temp("bronze", bronze_df)
spark_ctx.register_temp("config", config_df)

# Execute SQL
result = spark_ctx.execute_sql("""
    SELECT b.*, c.factor
    FROM bronze b
    LEFT JOIN config c ON b.type = c.type
    WHERE b.efficiency > 80
""")
```

### Secret Management

Both engines support secrets via dict or callable:

```python
# Dict-based secrets (local development)
pandas_ctx = PandasEngineContext(secrets={
    "db_user": "admin",
    "db_pass": "secret123"
})
password = pandas_ctx.get_secret("db_pass")  # Returns "secret123"

# Callable-based secrets (Databricks)
spark_ctx = SparkEngineContext(
    secrets=lambda key: dbutils.secrets.get("scope", key)
)
api_key = spark_ctx.get_secret("api_key")  # Calls dbutils
```

---

## Reader/Writer Contracts - I/O Operations

**Contracts:** `BaseReader`, `BaseWriter` (Abstract Base Classes)  
**Location:** `odibi_core/io/readers.py`, `odibi_core/io/writers.py`  
**Purpose:** Abstracted I/O operations for various formats

### BaseReader Implementations

| Reader Class | Format | Supported Engines | Key Parameters |
|--------------|--------|-------------------|----------------|
| **CsvReader** | CSV files | Pandas, Spark | `source` = file path<br>`header`, `delimiter`, etc. |
| **ParquetReader** | Parquet files | Pandas, Spark | `source` = file path |
| **SqlReader** | SQL queries | Pandas, Spark | `query` = SQL string |
| **DeltaReader** | Delta Lake | Spark (Pandas reads as Parquet) | `source` = Delta table path |

**Usage Pattern:**
```python
# Initialize with context
reader = CsvReader(pandas_context)

# Read data
df = reader.read("data/input.csv", header=True)
```

### BaseWriter Implementations

| Writer Class | Format | Supported Engines | Key Parameters |
|--------------|--------|-------------------|----------------|
| **CsvWriter** | CSV files | Pandas, Spark | `target` = file path<br>`header`, `index`, etc. |
| **ParquetWriter** | Parquet files | Pandas, Spark | `target` = file path<br>`mode`, `compression` |
| **DeltaWriter** | Delta Lake | Spark (Pandas writes as Parquet) | `target` = Delta table path<br>`mode`, `partitionBy` |

**Usage Pattern:**
```python
# Initialize with context
writer = ParquetWriter(pandas_context)

# Write data
writer.write(df, "output/data.parquet", mode="overwrite")
```

### Note on Implementation Status

The Reader/Writer classes provide the contract abstraction, but in practice, the `EngineContext` implementations (`PandasEngineContext` and `SparkEngineContext`) provide the full I/O functionality via their `read()` and `write()` methods.

---

## CloudAdapter Contract - Cloud Storage

**Contract:** `CloudAdapterBase` (Abstract Base Class)  
**Location:** `odibi_core/cloud/cloud_adapter.py`  
**Purpose:** Unified API for cloud storage backends

### Contract Requirements

```python
@abstractmethod
def connect() -> bool
def read(path: str, **kwargs) -> Any
def write(data: Any, path: str, **kwargs) -> bool
def exists(path: str) -> bool
def list(path: str, pattern: Optional[str] = None) -> list
def delete(path: str) -> bool
```

### Implementation Comparison

| Adapter | Backend | Status | Authentication | Key Features |
|---------|---------|--------|----------------|--------------|
| **AzureAdapter** | Azure Blob/ADLS Gen2 | ✅ Fully Implemented | Account Key, Service Principal, Managed Identity | Blob storage, Key Vault secrets, Azure SQL |
| **S3Adapter** | AWS S3 | ⚠️ Simulation Stub | Access Key/Secret (planned) | Simulated S3 operations |
| **HDFSAdapter** | Hadoop HDFS | ⚠️ Simulation Stub | Kerberos (planned) | Simulated HDFS operations |
| **KafkaAdapter** | Kafka Streams | ⚠️ Simulation Stub | SASL/SSL (planned) | Simulated Kafka pub/sub |

### AzureAdapter - Full Implementation

**Initialization Options:**

| Parameter | Description | Environment Variable | Required |
|-----------|-------------|---------------------|----------|
| `account_name` | Storage account name | `AZURE_STORAGE_ACCOUNT` | ✅ Yes |
| `account_key` | Storage account key | `AZURE_STORAGE_KEY` | For account key auth |
| `container` | Default container name | - | No |
| `tenant_id` | Azure AD tenant ID | `AZURE_TENANT_ID` | For service principal |
| `client_id` | Service principal client ID | `AZURE_CLIENT_ID` | For service principal |
| `client_secret` | Service principal secret | `AZURE_CLIENT_SECRET` | For service principal |
| `simulate` | Simulation mode | - | No (default: False) |

**Usage Examples:**

```python
# Account key authentication
azure = CloudAdapter.create(
    "azure",
    account_name="mystorageaccount",
    account_key="...",
    simulate=False
)
azure.connect()

# Read from ADLS
df = azure.read("container/path/data.parquet")

# Write to ADLS
azure.write(df, "container/output/data.parquet", format="parquet")

# Check existence
exists = azure.exists("container/path/data.parquet")

# List files
files = azure.list("container/path/", pattern="*.parquet")

# Delete file
azure.delete("container/path/old_data.parquet")

# Get secret from Key Vault
secret = azure.get_secret("keyvault-name", "secret-name")

# Connect to Azure SQL
conn = azure.connect_sql("server", "database", "username", "password")
```

**Supported Read/Write Formats:**

| Format | Method Call | Notes |
|--------|-------------|-------|
| Parquet | `read(path, format="parquet")` | Default format, columnar |
| CSV | `read(path, format="csv")` | Supports header param |
| JSON | `read(path, format="json")` | Line-delimited JSON |

### S3Adapter - Simulation Stub

```python
# Simulation mode (no real AWS calls)
s3 = CloudAdapter.create(
    "s3",
    bucket="my-bucket",
    region="us-east-1",
    simulate=True  # Must be True in Phase 7
)
s3.connect()

# Returns simulated DataFrame
df = s3.read("path/to/data.parquet")

# Simulates write (no actual upload)
s3.write(df, "path/to/output.parquet")
```

**Note:** S3Adapter is a simulation stub. Set `simulate=True` for testing S3-based pipelines without AWS credentials.

### HDFSAdapter - Simulation Stub

```python
# Simulation mode
hdfs = CloudAdapter.create(
    "hdfs",
    namenode_host="localhost",
    namenode_port=9000,
    simulate=True
)
hdfs.connect()

# Returns simulated DataFrame
df = hdfs.read("/user/hadoop/data.parquet")
```

### KafkaAdapter - Simulation Stub

```python
# Simulation mode
kafka = CloudAdapter.create(
    "kafka",
    bootstrap_servers="localhost:9092",
    topic="my-topic",
    simulate=True
)
kafka.connect()

# Returns simulated DataFrame (stream data)
df = kafka.read("my-topic")
```

### Factory Pattern Usage

All cloud adapters are created via the `CloudAdapter` factory:

```python
# List available backends
backends = CloudAdapter.list_backends()
# Returns: ['azure', 's3', 'hdfs', 'kafka']

# Create adapter dynamically
adapter = CloudAdapter.create("azure", account_name="...", account_key="...")
```

---

## 🔑 Key Takeaways

### 1. **Everything is a Node**
All pipeline operations (connect, ingest, transform, store, publish) implement `NodeBase.run()` and work with the `data_map` dictionary.

### 2. **Engine-Agnostic Design**
`EngineContext` abstractions allow switching between Pandas (local) and Spark (distributed) without changing pipeline logic.

### 3. **Contract-Driven Architecture**
All implementations follow well-defined contracts (ABC classes), making the framework extensible and testable.

### 4. **Unified I/O**
Both `EngineContext` and `CloudAdapter` provide consistent `read()`/`write()` APIs across different backends and formats.

### 5. **Secret Management**
Built-in secret resolution supports both local development (dict) and production (callable/Key Vault).

### 6. **Simulation Support**
Cloud adapters support simulation mode for testing without cloud credentials.

---

## 📚 Quick Reference Cards

### Step Configuration Pattern

```python
Step(
    layer="ingest|transform|store|connect|publish",
    name="unique_step_name",
    type="sql|function|config_op|api",
    engine="pandas|spark",
    value="path|query|connection_string|function_path",
    params={"key": "value"},  # Optional parameters
    inputs={"logical_name": "dataset_key"},  # For transform/store
    outputs={"logical_name": "dataset_key"},  # For ingest/transform
    metadata={"description": "..."}  # Optional docs
)
```

### Common Workflow Pattern

```python
# 1. Initialize context
context = PandasEngineContext(secrets={"db_pass": "secret"})
context.connect()

# 2. Ingest data
ingest_step = Step(layer="ingest", name="read_csv", ...)
ingest_node = IngestNode(ingest_step, context, tracker, events)
data_map = ingest_node.run({})

# 3. Transform data
transform_step = Step(layer="transform", name="filter", type="sql", ...)
transform_node = TransformNode(transform_step, context, tracker, events)
data_map = transform_node.run(data_map)

# 4. Store data
store_step = Step(layer="store", name="write_parquet", ...)
store_node = StoreNode(store_step, context, tracker, events)
data_map = store_node.run(data_map)
```

### Format Auto-Detection

Both `EngineContext` and `CloudAdapter` auto-detect formats by file extension:

| Extension | Format | Both Engines |
|-----------|--------|--------------|
| `.csv` | CSV | ✅ |
| `.json` | JSON | ✅ |
| `.parquet` | Parquet | ✅ |
| `.avro` | AVRO | ✅ |
| `.orc` | ORC | ✅ Spark only |
| `.delta` | Delta Lake | ✅ Spark (Pandas reads as Parquet) |
| `.db`, `.sqlite` | SQLite | ✅ Pandas only |

---

**Version:** ODIBI CORE Phase 7  
**Last Updated:** 2024  
**For walkthrough support:** See `odibi_core/docs/walkthroughs/`
