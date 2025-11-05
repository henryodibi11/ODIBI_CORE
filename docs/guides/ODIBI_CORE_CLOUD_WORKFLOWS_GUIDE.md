# ODIBI CORE - Cloud Workflows Guide

**Complete guide to working with Azure, S3, and cloud storage using Pandas and Spark engines**

---

## 🎯 What You'll Learn

- Set up cloud storage authentication for both engines
- Read/write data from Azure ADLS Gen2 and Blob Storage
- Work with S3 (AWS) and other cloud providers
- Build complete cloud-based pipelines
- Handle secrets and credentials securely
- Best practices for cloud data workflows

---

## Table of Contents

1. [Cloud Architecture Overview](#cloud-architecture-overview)
2. [Authentication Methods](#authentication-methods)
3. [Azure Workflows](#azure-workflows)
4. [S3 Workflows](#s3-workflows)
5. [Complete Pipeline Examples](#complete-pipeline-examples)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

---

## Cloud Architecture Overview

### Two Approaches to Cloud Storage in ODIBI Core

```
┌────────────────────────────────────────────────────────────────┐
│                    APPROACH 1: EngineContext                   │
│                    (Recommended for Pipelines)                 │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  Orchestrator (with secrets)                                  │
│       │                                                        │
│       ├─▶ Creates EngineContext (Pandas or Spark)            │
│       │   with cloud credentials                              │
│       │                                                        │
│       └─▶ Steps use cloud paths directly:                     │
│           value="abfss://container@account.dfs.core..."       │
│           value="s3://bucket/path/data.parquet"               │
│                                                                │
│  ✅ Best for: End-to-end pipelines with Steps                 │
│  ✅ Secrets managed centrally via Orchestrator                │
│  ✅ Works with both Pandas and Spark engines                  │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│                    APPROACH 2: CloudAdapter                    │
│                    (Direct Cloud Operations)                   │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  CloudAdapter.create("azure", ...)                            │
│       │                                                        │
│       ├─▶ Direct operations:                                  │
│       │   df = azure.read("path/data.parquet")                │
│       │   azure.write(df, "output/result.parquet")            │
│       │   azure.list("path/", pattern="*.csv")                │
│       │                                                        │
│       └─▶ Use in custom code or scripts                       │
│                                                                │
│  ✅ Best for: Ad-hoc scripts, data exploration                │
│  ✅ Direct control over cloud operations                      │
│  ✅ Azure fully implemented, S3/HDFS/Kafka simulated          │
└────────────────────────────────────────────────────────────────┘
```

---

## Authentication Methods

### Secret Management Flow

```
┌──────────────────────────────────────────────────────────────┐
│ How Secrets Flow Through ODIBI Core                         │
└──────────────────────────────────────────────────────────────┘

1. YOU define secrets
   ├─ Option A: Dict (local/dev)
   │   secrets = {"azure_key": "...", "db_pass": "..."}
   │
   ├─ Option B: Callable (Databricks)
   │   secrets = lambda key: dbutils.secrets.get("scope", key)
   │
   └─ Option C: Environment Variables
       os.environ["AZURE_STORAGE_KEY"] = "..."

              ▼

2. Pass to Orchestrator
   orchestrator = Orchestrator(
       steps=steps,
       engine_type="spark",
       secrets=secrets  # ← Centralized secret management
   )

              ▼

3. Orchestrator creates EngineContext
   context = SparkEngineContext(secrets=secrets)
   context.connect()

              ▼

4. Nodes access secrets via context
   # ConnectNode
   password = context.get_secret("db_password")
   
   # IngestNode
   account_key = context.get_secret("azure_account_key")
```

### Supported Authentication Methods by Provider

| Provider | Method | Configuration | Status |
|----------|--------|--------------|--------|
| **Azure ADLS Gen2** | Account Key | `account_name`, `account_key` | ✅ Fully Supported |
| **Azure ADLS Gen2** | Service Principal | `tenant_id`, `client_id`, `client_secret` | ✅ Fully Supported |
| **Azure ADLS Gen2** | Managed Identity | Default credentials | ✅ Fully Supported |
| **Azure Key Vault** | Secrets retrieval | `vault_name`, `secret_name` | ✅ Fully Supported |
| **AWS S3** | Access Key/Secret | `access_key_id`, `secret_access_key` | ⚠️ Simulated |
| **HDFS** | Kerberos | `principal`, `keytab` | ⚠️ Simulated |
| **Kafka** | SASL/SSL | `username`, `password`, `ssl_cert` | ⚠️ Simulated |

---

## Azure Workflows

### Azure ADLS Gen2 Architecture

```
┌────────────────────────────────────────────────────────────┐
│ Azure Data Lake Storage Gen2 (ADLS)                       │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  Storage Account: mystorageaccount                        │
│      │                                                      │
│      ├─ Container: bronze                                  │
│      │   ├─ raw/customers/2024/01/data.parquet            │
│      │   └─ raw/orders/2024/01/data.parquet               │
│      │                                                      │
│      ├─ Container: silver                                  │
│      │   ├─ cleaned/customers/data.parquet                │
│      │   └─ cleaned/orders/data.parquet                   │
│      │                                                      │
│      └─ Container: gold                                    │
│          └─ aggregated/customer_summary.parquet            │
│                                                            │
│  Access Methods:                                           │
│  ├─ abfss://bronze@mystorageaccount.dfs.core.windows.net/ │
│  ├─ https://mystorageaccount.blob.core.windows.net/bronze/│
│  └─ wasbs://bronze@mystorageaccount.blob.core.windows.net/│
└────────────────────────────────────────────────────────────┘
```

### Method 1: Azure with Spark Engine (Recommended for Production)

#### Setup

```python
from odibi_core.orchestrator import Orchestrator
from odibi_core.step import Step

# Define secrets (use Azure Key Vault in production)
secrets = {
    "azure_storage_account": "mystorageaccount",
    "azure_storage_key": "your-account-key-here",
    # OR use environment variables
    # Orchestrator will read AZURE_STORAGE_ACCOUNT and AZURE_STORAGE_KEY
}

# Optional: Configure Spark for Azure
spark_config = {
    "spark.hadoop.fs.azure.account.auth.type.mystorageaccount.dfs.core.windows.net": "SharedKey",
    "spark.hadoop.fs.azure.account.key.mystorageaccount.dfs.core.windows.net": "${azure_storage_key}",
    # For OAuth (Service Principal)
    # "spark.hadoop.fs.azure.account.auth.type": "OAuth",
    # "spark.hadoop.fs.azure.account.oauth.provider.type": "org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider",
    # "spark.hadoop.fs.azure.account.oauth2.client.id": "${azure_client_id}",
    # "spark.hadoop.fs.azure.account.oauth2.client.secret": "${azure_client_secret}",
    # "spark.hadoop.fs.azure.account.oauth2.client.endpoint": "https://login.microsoftonline.com/${azure_tenant_id}/oauth2/token"
}
```

#### Pipeline: Read from Azure, Transform, Write back to Azure

```python
steps = [
    # Step 1: Read from Azure Bronze layer
    Step(
        layer="ingest",
        name="read_bronze_customers",
        type="config_op",
        engine="spark",
        value="abfss://bronze@mystorageaccount.dfs.core.windows.net/raw/customers/2024/01/data.parquet",
        params={
            "source_type": "parquet"
        },
        outputs={"data": "raw_customers"}
    ),
    
    # Step 2: Read orders from Azure
    Step(
        layer="ingest",
        name="read_bronze_orders",
        type="config_op",
        engine="spark",
        value="abfss://bronze@mystorageaccount.dfs.core.windows.net/raw/orders/2024/01/data.parquet",
        params={
            "source_type": "parquet"
        },
        outputs={"data": "raw_orders"}
    ),
    
    # Step 3: Clean customers (Silver layer logic)
    Step(
        layer="transform",
        name="clean_customers",
        type="sql",
        engine="spark",
        value="""
            SELECT 
                customer_id,
                TRIM(name) as name,
                LOWER(email) as email,
                age,
                status
            FROM bronze
            WHERE status IS NOT NULL
              AND email IS NOT NULL
              AND age >= 18
        """,
        inputs={"bronze": "raw_customers"},
        outputs={"data": "cleaned_customers"}
    ),
    
    # Step 4: Join customers with orders
    Step(
        layer="transform",
        name="join_customer_orders",
        type="sql",
        engine="spark",
        value="""
            SELECT 
                c.customer_id,
                c.name,
                c.email,
                o.order_id,
                o.amount,
                o.order_date
            FROM customers c
            JOIN orders o ON c.customer_id = o.customer_id
        """,
        inputs={
            "customers": "cleaned_customers",
            "orders": "raw_orders"
        },
        outputs={"data": "customer_orders"}
    ),
    
    # Step 5: Save to Silver layer
    Step(
        layer="store",
        name="save_silver_customer_orders",
        type="config_op",
        engine="spark",
        value="abfss://silver@mystorageaccount.dfs.core.windows.net/cleaned/customer_orders",
        params={
            "format": "parquet",
            "mode": "overwrite",
            "partitionBy": ["order_date"]  # Partition by date
        },
        inputs={"data": "customer_orders"}
    ),
    
    # Step 6: Aggregate for Gold layer
    Step(
        layer="transform",
        name="calculate_customer_summary",
        type="sql",
        engine="spark",
        value="""
            SELECT 
                customer_id,
                name,
                email,
                COUNT(order_id) as total_orders,
                SUM(amount) as total_spent,
                AVG(amount) as avg_order_value,
                MAX(order_date) as last_order_date
            FROM bronze
            GROUP BY customer_id, name, email
        """,
        inputs={"bronze": "customer_orders"},
        outputs={"data": "customer_summary"}
    ),
    
    # Step 7: Save to Gold layer
    Step(
        layer="store",
        name="save_gold_summary",
        type="config_op",
        engine="spark",
        value="abfss://gold@mystorageaccount.dfs.core.windows.net/aggregated/customer_summary",
        params={
            "format": "parquet",
            "mode": "overwrite"
        },
        inputs={"data": "customer_summary"}
    )
]

# Execute pipeline
orchestrator = Orchestrator(
    steps=steps,
    engine_type="spark",
    secrets=secrets,
    spark_config=spark_config,  # Pass Spark Azure configuration
    enable_tracker=True,
    enable_checkpoints=True,
    checkpoint_mode="LAYER"  # Checkpoint after Bronze/Silver/Gold
)

result = orchestrator.execute()

if result['success']:
    print(f"✅ Pipeline completed: {result['nodes_executed']} nodes")
else:
    print(f"❌ Pipeline failed: {result['failed_nodes']}")
```

### Method 2: Azure with Pandas Engine (Local/Small Data)

```python
from odibi_core.orchestrator import Orchestrator
from odibi_core.step import Step

# For Pandas, use CloudAdapter or local download approach

secrets = {
    "azure_account_name": "mystorageaccount",
    "azure_account_key": "your-key"
}

steps = [
    # Option 1: Use CloudAdapter in a custom function
    Step(
        layer="ingest",
        name="read_azure_data",
        type="function",
        engine="pandas",
        value="my_functions.read_from_azure",  # Custom function that uses CloudAdapter
        outputs={"data": "raw_data"}
    ),
    
    # Transform
    Step(
        layer="transform",
        name="filter_data",
        type="sql",
        engine="pandas",
        value="SELECT * FROM bronze WHERE amount > 100",
        inputs={"bronze": "raw_data"},
        outputs={"data": "filtered_data"}
    ),
    
    # Save locally or back to Azure
    Step(
        layer="store",
        name="save_local",
        type="config_op",
        engine="pandas",
        value="output/filtered_data.parquet",
        params={"format": "parquet"},
        inputs={"data": "filtered_data"}
    )
]
```

**Custom function for Pandas + Azure:**

```python
# my_functions.py
from odibi_core.cloud.cloud_adapter import CloudAdapter
import os

def read_from_azure(df=None):
    """Read data from Azure using CloudAdapter"""
    azure = CloudAdapter.create(
        "azure",
        account_name=os.environ["AZURE_STORAGE_ACCOUNT"],
        account_key=os.environ["AZURE_STORAGE_KEY"],
        container="bronze"
    )
    azure.connect()
    
    # Read data
    df = azure.read("raw/customers/data.parquet", format="parquet")
    return df

def write_to_azure(df):
    """Write data to Azure using CloudAdapter"""
    azure = CloudAdapter.create(
        "azure",
        account_name=os.environ["AZURE_STORAGE_ACCOUNT"],
        account_key=os.environ["AZURE_STORAGE_KEY"],
        container="silver"
    )
    azure.connect()
    
    # Write data
    azure.write(df, "cleaned/customers.parquet", format="parquet", mode="overwrite")
    return df
```

### Method 3: Direct CloudAdapter Usage (Ad-hoc Scripts)

```python
from odibi_core.cloud.cloud_adapter import CloudAdapter
import os

# Set up Azure adapter
azure = CloudAdapter.create(
    "azure",
    account_name="mystorageaccount",
    account_key=os.environ["AZURE_STORAGE_KEY"],  # From environment
    container="bronze"
)

# Connect
azure.connect()

# Read data
df = azure.read("raw/customers/2024/01/data.parquet", format="parquet")
print(f"Loaded {len(df)} rows")

# Transform (using Pandas)
filtered = df[df['amount'] > 100]

# Write back to Azure (different container)
azure_silver = CloudAdapter.create(
    "azure",
    account_name="mystorageaccount",
    account_key=os.environ["AZURE_STORAGE_KEY"],
    container="silver"
)
azure_silver.connect()
azure_silver.write(filtered, "cleaned/customers.parquet", format="parquet", mode="overwrite")

# List files
files = azure.list("raw/customers/", pattern="*.parquet")
print(f"Found {len(files)} parquet files")

# Check if file exists
if azure.exists("raw/customers/2024/01/data.parquet"):
    print("File exists!")

# Delete old file
azure.delete("raw/customers/2023/12/data.parquet")

# Get secret from Azure Key Vault
secret_value = azure.get_secret("my-keyvault", "database-password")
```

### Azure Authentication Options

#### 1. Account Key (Simple, Dev/Test)

```python
secrets = {
    "azure_account_name": "mystorageaccount",
    "azure_account_key": "your-64-char-base64-key"
}

# Or via environment variables
os.environ["AZURE_STORAGE_ACCOUNT"] = "mystorageaccount"
os.environ["AZURE_STORAGE_KEY"] = "your-key"
```

#### 2. Service Principal (Production, Recommended)

```python
secrets = {
    "azure_tenant_id": "your-tenant-id",
    "azure_client_id": "your-client-id",
    "azure_client_secret": "your-client-secret",
    "azure_account_name": "mystorageaccount"
}

# Or via environment variables
os.environ["AZURE_TENANT_ID"] = "..."
os.environ["AZURE_CLIENT_ID"] = "..."
os.environ["AZURE_CLIENT_SECRET"] = "..."
os.environ["AZURE_STORAGE_ACCOUNT"] = "..."

# CloudAdapter auto-detects service principal auth
azure = CloudAdapter.create(
    "azure",
    account_name=os.environ["AZURE_STORAGE_ACCOUNT"],
    tenant_id=os.environ["AZURE_TENANT_ID"],
    client_id=os.environ["AZURE_CLIENT_ID"],
    client_secret=os.environ["AZURE_CLIENT_SECRET"],
    container="bronze"
)
```

#### 3. Managed Identity (Azure VMs, Databricks)

```python
# No credentials needed - uses VM/service's managed identity
azure = CloudAdapter.create(
    "azure",
    account_name="mystorageaccount",
    container="bronze",
    use_managed_identity=True  # Auto-detects Azure managed identity
)
```

---

## S3 Workflows

### S3 with Spark Engine

#### Setup

```python
secrets = {
    "aws_access_key_id": "AKIAIOSFODNN7EXAMPLE",
    "aws_secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    "aws_region": "us-east-1"
}

spark_config = {
    "spark.hadoop.fs.s3a.access.key": "${aws_access_key_id}",
    "spark.hadoop.fs.s3a.secret.key": "${aws_secret_access_key}",
    "spark.hadoop.fs.s3a.endpoint": "s3.us-east-1.amazonaws.com",
    "spark.hadoop.fs.s3a.impl": "org.apache.hadoop.fs.s3a.S3AFileSystem"
}
```

#### Pipeline: Read from S3, Transform, Write back

```python
steps = [
    # Read from S3
    Step(
        layer="ingest",
        name="read_s3_data",
        type="config_op",
        engine="spark",
        value="s3a://my-bucket/raw/data.parquet",
        params={"source_type": "parquet"},
        outputs={"data": "raw_data"}
    ),
    
    # Transform
    Step(
        layer="transform",
        name="filter_data",
        type="sql",
        engine="spark",
        value="SELECT * FROM bronze WHERE amount > 100",
        inputs={"bronze": "raw_data"},
        outputs={"data": "filtered_data"}
    ),
    
    # Write back to S3
    Step(
        layer="store",
        name="save_to_s3",
        type="config_op",
        engine="spark",
        value="s3a://my-bucket/processed/data.parquet",
        params={
            "format": "parquet",
            "mode": "overwrite",
            "partitionBy": ["year", "month"]
        },
        inputs={"data": "filtered_data"}
    )
]

orchestrator = Orchestrator(
    steps=steps,
    engine_type="spark",
    secrets=secrets,
    spark_config=spark_config
)

result = orchestrator.execute()
```

### S3 with CloudAdapter (Simulated)

```python
from odibi_core.cloud.cloud_adapter import CloudAdapter

# Note: S3Adapter is currently simulated
s3 = CloudAdapter.create(
    "s3",
    bucket="my-bucket",
    region="us-east-1",
    access_key_id="AKIA...",
    secret_access_key="...",
    simulate=True  # Must be True in current version
)

s3.connect()

# Returns simulated DataFrame
df = s3.read("raw/data.parquet")

# Simulates write (no actual upload)
s3.write(df, "processed/data.parquet")

# Note: S3Adapter will be fully implemented in future releases
```

---

## Complete Pipeline Examples

### Example 1: Medallion Architecture on Azure (Bronze → Silver → Gold)

```python
from odibi_core.orchestrator import Orchestrator
from odibi_core.step import Step
from odibi_core.checkpoint_manager import CheckpointMode

# Secrets (use Azure Key Vault in production)
secrets = {
    "azure_account_name": "mystorageaccount",
    "azure_account_key": "your-key"
}

# Spark configuration for Azure
spark_config = {
    "spark.hadoop.fs.azure.account.auth.type.mystorageaccount.dfs.core.windows.net": "SharedKey",
    "spark.hadoop.fs.azure.account.key.mystorageaccount.dfs.core.windows.net": "${azure_account_key}"
}

steps = [
    # ═══════════════════════════════════════════════════════════
    # BRONZE LAYER: Ingest raw data from multiple sources
    # ═══════════════════════════════════════════════════════════
    
    Step(
        layer="bronze_ingest",
        name="read_raw_customers",
        type="config_op",
        engine="spark",
        value="abfss://landing@mystorageaccount.dfs.core.windows.net/raw/customers/2024/*.parquet",
        params={"source_type": "parquet"},
        outputs={"data": "raw_customers"}
    ),
    
    Step(
        layer="bronze_ingest",
        name="read_raw_orders",
        type="config_op",
        engine="spark",
        value="abfss://landing@mystorageaccount.dfs.core.windows.net/raw/orders/2024/*.parquet",
        params={"source_type": "parquet"},
        outputs={"data": "raw_orders"}
    ),
    
    Step(
        layer="bronze_ingest",
        name="read_raw_products",
        type="config_op",
        engine="spark",
        value="abfss://landing@mystorageaccount.dfs.core.windows.net/raw/products/*.parquet",
        params={"source_type": "parquet"},
        outputs={"data": "raw_products"}
    ),
    
    # Save raw data to Bronze
    Step(
        layer="bronze_store",
        name="save_bronze_customers",
        type="config_op",
        engine="spark",
        value="abfss://bronze@mystorageaccount.dfs.core.windows.net/customers",
        params={
            "format": "parquet",
            "mode": "overwrite"
        },
        inputs={"data": "raw_customers"}
    ),
    
    Step(
        layer="bronze_store",
        name="save_bronze_orders",
        type="config_op",
        engine="spark",
        value="abfss://bronze@mystorageaccount.dfs.core.windows.net/orders",
        params={
            "format": "parquet",
            "mode": "overwrite"
        },
        inputs={"data": "raw_orders"}
    ),
    
    Step(
        layer="bronze_store",
        name="save_bronze_products",
        type="config_op",
        engine="spark",
        value="abfss://bronze@mystorageaccount.dfs.core.windows.net/products",
        params={
            "format": "parquet",
            "mode": "overwrite"
        },
        inputs={"data": "raw_products"}
    ),
    
    # ═══════════════════════════════════════════════════════════
    # SILVER LAYER: Clean and validate data
    # ═══════════════════════════════════════════════════════════
    
    Step(
        layer="silver_transform",
        name="clean_customers",
        type="sql",
        engine="spark",
        value="""
            SELECT 
                customer_id,
                TRIM(UPPER(name)) as name,
                LOWER(TRIM(email)) as email,
                age,
                CASE 
                    WHEN status IS NULL THEN 'inactive'
                    ELSE status 
                END as status,
                country,
                CURRENT_TIMESTAMP() as processed_at
            FROM bronze
            WHERE customer_id IS NOT NULL
              AND email IS NOT NULL
              AND age >= 0
        """,
        inputs={"bronze": "raw_customers"},
        outputs={"data": "cleaned_customers"}
    ),
    
    Step(
        layer="silver_transform",
        name="clean_orders",
        type="sql",
        engine="spark",
        value="""
            SELECT 
                order_id,
                customer_id,
                product_id,
                CAST(amount AS DECIMAL(10,2)) as amount,
                CAST(quantity AS INT) as quantity,
                TO_DATE(order_date) as order_date,
                CURRENT_TIMESTAMP() as processed_at
            FROM bronze
            WHERE order_id IS NOT NULL
              AND customer_id IS NOT NULL
              AND amount > 0
              AND quantity > 0
        """,
        inputs={"bronze": "raw_orders"},
        outputs={"data": "cleaned_orders"}
    ),
    
    # Save to Silver layer
    Step(
        layer="silver_store",
        name="save_silver_customers",
        type="config_op",
        engine="spark",
        value="abfss://silver@mystorageaccount.dfs.core.windows.net/customers",
        params={
            "format": "delta",  # Use Delta for ACID transactions
            "mode": "overwrite"
        },
        inputs={"data": "cleaned_customers"}
    ),
    
    Step(
        layer="silver_store",
        name="save_silver_orders",
        type="config_op",
        engine="spark",
        value="abfss://silver@mystorageaccount.dfs.core.windows.net/orders",
        params={
            "format": "delta",
            "mode": "overwrite",
            "partitionBy": ["order_date"]  # Partition by date
        },
        inputs={"data": "cleaned_orders"}
    ),
    
    # ═══════════════════════════════════════════════════════════
    # GOLD LAYER: Business aggregations
    # ═══════════════════════════════════════════════════════════
    
    Step(
        layer="gold_transform",
        name="calculate_customer_metrics",
        type="sql",
        engine="spark",
        value="""
            SELECT 
                c.customer_id,
                c.name,
                c.email,
                c.country,
                COUNT(o.order_id) as total_orders,
                SUM(o.amount) as total_spent,
                AVG(o.amount) as avg_order_value,
                MIN(o.order_date) as first_order_date,
                MAX(o.order_date) as last_order_date,
                DATEDIFF(MAX(o.order_date), MIN(o.order_date)) as customer_lifetime_days
            FROM customers c
            LEFT JOIN orders o ON c.customer_id = o.customer_id
            GROUP BY c.customer_id, c.name, c.email, c.country
        """,
        inputs={
            "customers": "cleaned_customers",
            "orders": "cleaned_orders"
        },
        outputs={"data": "customer_metrics"}
    ),
    
    Step(
        layer="gold_transform",
        name="calculate_product_metrics",
        type="sql",
        engine="spark",
        value="""
            SELECT 
                p.product_id,
                p.product_name,
                p.category,
                COUNT(o.order_id) as times_ordered,
                SUM(o.quantity) as total_quantity_sold,
                SUM(o.amount) as total_revenue,
                AVG(o.amount / o.quantity) as avg_price_per_unit
            FROM products p
            LEFT JOIN orders o ON p.product_id = o.product_id
            GROUP BY p.product_id, p.product_name, p.category
            HAVING times_ordered > 0
            ORDER BY total_revenue DESC
        """,
        inputs={
            "products": "raw_products",
            "orders": "cleaned_orders"
        },
        outputs={"data": "product_metrics"}
    ),
    
    # Save to Gold layer
    Step(
        layer="gold_store",
        name="save_gold_customer_metrics",
        type="config_op",
        engine="spark",
        value="abfss://gold@mystorageaccount.dfs.core.windows.net/customer_metrics",
        params={
            "format": "delta",
            "mode": "overwrite"
        },
        inputs={"data": "customer_metrics"}
    ),
    
    Step(
        layer="gold_store",
        name="save_gold_product_metrics",
        type="config_op",
        engine="spark",
        value="abfss://gold@mystorageaccount.dfs.core.windows.net/product_metrics",
        params={
            "format": "delta",
            "mode": "overwrite"
        },
        inputs={"data": "product_metrics"}
    )
]

# Execute with full reliability features
orchestrator = Orchestrator(
    steps=steps,
    engine_type="spark",
    secrets=secrets,
    spark_config=spark_config,
    
    # Reliability features
    enable_checkpoints=True,
    checkpoint_mode=CheckpointMode.LAYER,  # Checkpoint after each layer
    checkpoint_dir="abfss://checkpoints@mystorageaccount.dfs.core.windows.net/",
    
    enable_cache=False,  # Disable cache for production
    
    max_retries=3,
    retry_delay=10,
    retry_backoff=True,
    
    enable_tracker=True,
    
    fail_fast=False  # Continue on errors to complete as much as possible
)

result = orchestrator.execute()

# Check results
if result['success']:
    print(f"✅ Medallion pipeline completed successfully!")
    print(f"   - Nodes executed: {result['nodes_executed']}")
    print(f"   - Duration: {result['duration_ms']}ms")
else:
    print(f"❌ Pipeline failed")
    print(f"   - Failed nodes: {result['failed_nodes']}")
    print(f"   - Successful nodes: {result['successful_nodes']}")
```

### Example 2: Hybrid Cloud Pipeline (S3 → Azure)

```python
# Read from S3, process, write to Azure
steps = [
    # Read from AWS S3
    Step(
        layer="ingest",
        name="read_from_s3",
        type="config_op",
        engine="spark",
        value="s3a://source-bucket/data/input.parquet",
        params={"source_type": "parquet"},
        outputs={"data": "s3_data"}
    ),
    
    # Transform
    Step(
        layer="transform",
        name="enrich_data",
        type="sql",
        engine="spark",
        value="""
            SELECT 
                *,
                YEAR(date_column) as year,
                MONTH(date_column) as month
            FROM bronze
        """,
        inputs={"bronze": "s3_data"},
        outputs={"data": "enriched_data"}
    ),
    
    # Write to Azure ADLS
    Step(
        layer="store",
        name="save_to_azure",
        type="config_op",
        engine="spark",
        value="abfss://processed@mystorageaccount.dfs.core.windows.net/output",
        params={
            "format": "parquet",
            "mode": "overwrite",
            "partitionBy": ["year", "month"]
        },
        inputs={"data": "enriched_data"}
    )
]

# Secrets for both clouds
secrets = {
    # AWS
    "aws_access_key_id": "AKIA...",
    "aws_secret_access_key": "...",
    # Azure
    "azure_account_name": "mystorageaccount",
    "azure_account_key": "..."
}

# Spark config for both
spark_config = {
    # S3
    "spark.hadoop.fs.s3a.access.key": "${aws_access_key_id}",
    "spark.hadoop.fs.s3a.secret.key": "${aws_secret_access_key}",
    # Azure
    "spark.hadoop.fs.azure.account.key.mystorageaccount.dfs.core.windows.net": "${azure_account_key}"
}

orchestrator = Orchestrator(
    steps=steps,
    engine_type="spark",
    secrets=secrets,
    spark_config=spark_config
)

result = orchestrator.execute()
```

---

## Best Practices

### 1. Secret Management

```
✅ DO:
├─ Use Azure Key Vault or AWS Secrets Manager in production
├─ Use environment variables for local development
├─ Use Databricks secrets (dbutils.secrets) on Databricks
├─ Rotate credentials regularly
└─ Use service principal/IAM roles instead of account keys

❌ DON'T:
├─ Hardcode credentials in code
├─ Commit secrets to git
├─ Share credentials via email/chat
└─ Use account keys in production (prefer OAuth/managed identity)
```

**Production Secret Setup:**

```python
# Use callable for secret retrieval (Databricks example)
def get_secret(key):
    # Retrieves from Databricks secret scope
    return dbutils.secrets.get(scope="production", key=key)

orchestrator = Orchestrator(
    steps=steps,
    engine_type="spark",
    secrets=get_secret  # Pass callable instead of dict
)
```

### 2. Path Conventions

```python
# Use consistent path structure
AZURE_PATHS = {
    "landing": "abfss://landing@{account}.dfs.core.windows.net/",
    "bronze": "abfss://bronze@{account}.dfs.core.windows.net/",
    "silver": "abfss://silver@{account}.dfs.core.windows.net/",
    "gold": "abfss://gold@{account}.dfs.core.windows.net/",
    "checkpoints": "abfss://checkpoints@{account}.dfs.core.windows.net/"
}

# Build paths programmatically
account = "mystorageaccount"
bronze_path = AZURE_PATHS["bronze"].format(account=account) + "customers"
```

### 3. Partitioning Strategy

```python
# Time-based partitioning (most common)
Step(
    layer="store",
    name="save_partitioned",
    type="config_op",
    engine="spark",
    value="abfss://silver@account.dfs.core.windows.net/orders",
    params={
        "format": "parquet",
        "mode": "append",
        "partitionBy": ["year", "month", "day"]  # Hierarchical partitioning
    },
    inputs={"data": "orders"}
)

# Results in structure:
# orders/
#   year=2024/
#     month=01/
#       day=15/
#         part-00000.parquet
#         part-00001.parquet
```

### 4. Format Selection

| Format | When to Use | Pros | Cons |
|--------|-------------|------|------|
| **Parquet** | Analytical queries, data lake | Columnar, compressed, fast queries | Not human-readable |
| **Delta** | ACID transactions, versioning | Time travel, ACID, schema evolution | Requires Delta library |
| **CSV** | Data exchange, simple datasets | Human-readable, universal | Slow, no schema enforcement |
| **JSON** | Semi-structured data, APIs | Flexible schema | Larger file size |
| **AVRO** | Streaming, schema evolution | Schema embedded, compact | Less query performance |

### 5. Error Handling for Cloud Operations

```python
from odibi_core.event_bus import EventBus, EventPriority

def cloud_error_handler(event_data):
    error = event_data.get('error_message', '')
    
    # Check for common cloud errors
    if 'AuthenticationFailed' in error or '403' in error:
        print("🚨 CRITICAL: Authentication failed - check credentials")
        # Send alert to ops team
    elif 'BlobNotFound' in error or '404' in error:
        print("⚠️ WARNING: File not found - check path")
    elif 'Throttled' in error or '429' in error:
        print("⏸️ THROTTLED: Rate limit hit - retry with backoff")
    else:
        print(f"❌ ERROR: {error}")

event_bus = EventBus()
event_bus.register_hook("node_error", cloud_error_handler, priority=EventPriority.CRITICAL)

orchestrator = Orchestrator(
    steps=steps,
    engine_type="spark",
    event_bus=event_bus,
    max_retries=5,  # More retries for cloud (transient failures common)
    retry_delay=10,
    retry_backoff=True
)
```

### 6. Performance Optimization

```python
# Optimize Spark for cloud storage
spark_config = {
    # Azure optimizations
    "spark.hadoop.fs.azure.io.read.request.size": "8388608",  # 8MB read buffer
    "spark.hadoop.fs.azure.io.write.request.size": "8388608",
    
    # S3 optimizations
    "spark.hadoop.fs.s3a.block.size": "134217728",  # 128MB blocks
    "spark.hadoop.fs.s3a.fast.upload": "true",
    "spark.hadoop.fs.s3a.fast.upload.buffer": "bytebuffer",
    
    # General Spark tuning
    "spark.sql.shuffle.partitions": "200",
    "spark.sql.adaptive.enabled": "true",
    "spark.sql.adaptive.coalescePartitions.enabled": "true"
}
```

---

## Troubleshooting

### Common Issues

#### 1. Authentication Failures

**Error:**
```
AuthenticationFailed: Server failed to authenticate the request
```

**Solutions:**
```python
# Check 1: Verify account name and key
print(f"Account: {os.environ.get('AZURE_STORAGE_ACCOUNT')}")
print(f"Key exists: {bool(os.environ.get('AZURE_STORAGE_KEY'))}")

# Check 2: Test CloudAdapter connection
azure = CloudAdapter.create("azure", account_name="...", account_key="...")
connected = azure.connect()
print(f"Connected: {connected}")

# Check 3: Verify Spark configuration
print(spark.conf.get("spark.hadoop.fs.azure.account.key.mystorageaccount.dfs.core.windows.net"))
```

#### 2. Path Not Found

**Error:**
```
FileNotFoundException: abfss://container@account.dfs.core.windows.net/path/file.parquet
```

**Solutions:**
```python
# Check 1: List files to verify path
azure = CloudAdapter.create("azure", account_name="...", container="bronze")
files = azure.list("", pattern="*.parquet")
print(f"Available files: {files}")

# Check 2: Check if file exists
exists = azure.exists("path/file.parquet")
print(f"File exists: {exists}")

# Check 3: Verify path format
# Correct: abfss://container@account.dfs.core.windows.net/path/file.parquet
# Wrong:   abfss://account@container.dfs.core.windows.net/path/file.parquet
```

#### 3. Permission Denied

**Error:**
```
This request is not authorized to perform this operation using this permission
```

**Solutions:**
- Verify Storage Blob Data Contributor role assigned to service principal
- Check container-level permissions
- Use account key instead of OAuth for testing

#### 4. Slow Cloud Reads

**Symptoms:**
- Long read times from cloud storage
- Timeouts

**Solutions:**
```python
# 1. Enable partitioning and predicate pushdown
df = spark.read.parquet("abfss://.../*.parquet") \
    .filter("date >= '2024-01-01'")  # Filter early

# 2. Increase parallelism
spark.conf.set("spark.sql.files.maxPartitionBytes", "134217728")  # 128MB

# 3. Use columnar formats (Parquet, Delta)
# Avoid CSV for large datasets

# 4. Enable caching for repeated reads
df = spark.read.parquet("abfss://.../data.parquet")
df.cache()
```

### Debugging Checklist

```
□ Credentials
  ├─ Environment variables set correctly
  ├─ Secrets accessible via context.get_secret()
  └─ Service principal has necessary roles

□ Paths
  ├─ Correct format (abfss://, s3a://)
  ├─ Container/bucket exists
  └─ File/directory exists at path

□ Spark Configuration
  ├─ Azure/S3 Hadoop configs set
  ├─ Credentials passed via spark_config
  └─ Required JARs available (Delta, AVRO, etc.)

□ Network
  ├─ Firewall allows outbound to cloud storage
  ├─ Proxy settings configured if needed
  └─ DNS resolves storage endpoints

□ Permissions
  ├─ Read permissions on source
  ├─ Write permissions on target
  └─ List permissions on containers
```

---

## Summary

| Topic | Key Points |
|-------|-----------|
| **Two Approaches** | 1) EngineContext (pipeline Steps), 2) CloudAdapter (direct ops) |
| **Authentication** | Account Key, Service Principal, Managed Identity, Key Vault |
| **Spark + Azure** | Use `abfss://` paths, configure Hadoop settings in `spark_config` |
| **Pandas + Azure** | Use CloudAdapter in custom functions or ad-hoc scripts |
| **S3 Support** | Spark: full support via `s3a://`, CloudAdapter: simulated |
| **Best Practices** | Use Key Vault, partition data, choose Delta for ACID, handle retries |
| **Medallion on Cloud** | Bronze (raw) → Silver (cleaned) → Gold (aggregated), all on Azure/S3 |

---

## Next Steps

1. **Set up Azure Storage Account**: Create containers for bronze/silver/gold
2. **Configure Secrets**: Use Azure Key Vault or environment variables
3. **Build First Cloud Pipeline**: Start with simple read → transform → write
4. **Add Reliability**: Enable checkpoints, retries, error hooks
5. **Scale Up**: Use Spark for large datasets, partitioning, Delta format

**Need more help?**
- See [ODIBI_CORE_CONTRACT_CHEATSHEET.md](ODIBI_CORE_CONTRACT_CHEATSHEET.md) for CloudAdapter API reference
- See [ODIBI_CORE_LEVEL_4_RELIABILITY.md](ODIBI_CORE_LEVEL_4_RELIABILITY.md) for checkpoint/retry strategies
- See [ODIBI_CORE_LEVEL_7_ADVANCED.md](ODIBI_CORE_LEVEL_7_ADVANCED.md) for scheduling cloud pipelines
