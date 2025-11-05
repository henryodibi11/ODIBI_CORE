# LEVEL 2: Building Pipelines

**Time**: 30-45 minutes  
**Goal**: Master the 5 node types, understand Step configuration, and build working pipelines

---

## 🎯 What You'll Learn

- The 5 node types and when to use each
- Step configuration structure (all fields explained)
- How data flows through data_map
- Build complete working pipelines with multiple transforms
- Inputs/outputs mapping

---

## The 5 Node Types - Decision Tree

```
What do you want to do?

├─ Establish database/system connection?
│  └─ ConnectNode
│     Example: Connect to PostgreSQL, MongoDB, Azure Storage
│
├─ Read data from a source?
│  └─ IngestNode
│     Example: Read CSV, Parquet, query database table
│
├─ Transform or filter data?
│  ├─ Using SQL queries?
│  │  └─ TransformNode (type="sql")
│  │     Example: SELECT *, amount * 1.1 as total FROM bronze WHERE status = 'active'
│  │
│  └─ Using Python function?
│     └─ TransformNode (type="function")
│        Example: def clean_data(df): return df.dropna()
│
├─ Save to Bronze/Silver/Gold layer?
│  └─ StoreNode
│     Example: Write to Parquet, Delta Lake, database table
│
└─ Export to external system?
   └─ PublishNode
      Example: Send to API, write to S3, publish to Kafka
```

---

## Node Type Deep Dive

### 1. ConnectNode

**Purpose**: Establish connections to databases or external systems

**When to use**:
- Before querying a database
- Before reading from cloud storage
- Setting up authentication

**Example**:

```python
Step(
    layer="connect",
    name="connect_postgres",
    type="config_op",
    engine="pandas",
    value="postgresql://user:pass@localhost:5432/mydb",
    params={"source_type": "sql"}
)
```

**What it does**:
- Creates connection object
- Stores in context for later use
- No data written to data_map

---

### 2. IngestNode

**Purpose**: Read data from sources into the pipeline

**When to use**:
- Reading files (CSV, Parquet, JSON, Delta)
- Querying database tables
- Loading data from cloud storage

**Examples**:

```python
# Read CSV file
Step(
    layer="ingest",
    name="read_customers",
    type="config_op",
    engine="pandas",
    value="data/customers.csv",
    params={"source_type": "csv", "header": True},
    outputs={"data": "raw_customers"}
)

# Query database table
Step(
    layer="ingest",
    name="read_orders",
    type="config_op",
    engine="pandas",
    value="SELECT * FROM orders WHERE date > '2024-01-01'",
    params={"source_type": "sql", "connection": "postgres_conn"},
    outputs={"data": "raw_orders"}
)

# Read Parquet
Step(
    layer="ingest",
    name="read_parquet",
    type="config_op",
    engine="pandas",
    value="data/products.parquet",
    params={"source_type": "parquet"},
    outputs={"data": "raw_products"}
)
```

**What it does**:
- Reads data using EngineContext.read()
- Writes DataFrame to data_map[output_key]

---

### 3. TransformNode

**Purpose**: Transform, filter, join, or enrich data

**When to use**:
- Filtering rows
- Adding/removing columns
- Joining datasets
- Aggregations
- Custom Python transformations

**Type A: SQL Transforms**

```python
Step(
    layer="transform",
    name="filter_active_customers",
    type="sql",
    engine="pandas",
    value="""
        SELECT 
            customer_id,
            name,
            email,
            age
        FROM bronze 
        WHERE status = 'active' AND age >= 18
    """,
    inputs={"bronze": "raw_customers"},
    outputs={"data": "active_customers"}
)
```

**Type B: Function Transforms**

```python
# Define custom function
def calculate_metrics(df):
    df['efficiency'] = df['output'] / df['input'] * 100
    df['profit'] = df['revenue'] - df['cost']
    return df

# Use in step
Step(
    layer="transform",
    name="calculate_metrics",
    type="function",
    engine="pandas",
    value="my_module.calculate_metrics",  # Dotted path to function
    inputs={"data": "raw_sales"},
    outputs={"data": "sales_with_metrics"}
)
```

**What it does**:
- Reads input DataFrames from data_map
- Executes SQL or function
- Writes result to data_map[output_key]

---

### 4. StoreNode

**Purpose**: Save data to Bronze/Silver/Gold layers

**When to use**:
- Saving to disk (Bronze layer: raw, Silver: cleaned, Gold: aggregated)
- Writing to data lake (Delta, Parquet)
- Persisting intermediate results

**Examples**:

```python
# Save to Bronze (Parquet)
Step(
    layer="store",
    name="save_bronze",
    type="config_op",
    engine="pandas",
    value="data/bronze/customers.parquet",
    params={"format": "parquet", "mode": "overwrite"},
    inputs={"data": "raw_customers"}
)

# Save to Silver (Delta)
Step(
    layer="store",
    name="save_silver",
    type="config_op",
    engine="spark",
    value="data/silver/customers_clean",
    params={"format": "delta", "mode": "overwrite"},
    inputs={"data": "cleaned_customers"}
)

# Save to Gold (Parquet partitioned)
Step(
    layer="store",
    name="save_gold",
    type="config_op",
    engine="spark",
    value="data/gold/customer_summary",
    params={
        "format": "parquet",
        "mode": "overwrite",
        "partitionBy": ["year", "month"]
    },
    inputs={"data": "customer_summary"}
)
```

**What it does**:
- Reads DataFrame from data_map
- Writes to disk using EngineContext.write()
- Does NOT modify data_map (side effect only)

---

### 5. PublishNode

**Purpose**: Export data to external systems

**When to use**:
- Sending to APIs
- Publishing to message queues (Kafka)
- Exporting to cloud storage
- Writing to external databases

**Examples**:

```python
# Publish to API
Step(
    layer="publish",
    name="publish_to_api",
    type="config_op",
    engine="pandas",
    value="https://api.example.com/data",
    params={
        "method": "POST",
        "headers": {"Authorization": "Bearer token"}
    },
    inputs={"data": "final_output"}
)

# Export to S3
Step(
    layer="publish",
    name="export_to_s3",
    type="config_op",
    engine="spark",
    value="s3://mybucket/output/data.parquet",
    params={"format": "parquet"},
    inputs={"data": "final_output"}
)
```

**What it does**:
- Reads DataFrame from data_map
- Sends to external system
- Does NOT modify data_map

---

## Step Configuration - Every Field Explained

| Field | Required | Type | Description | Example |
|-------|----------|------|-------------|---------|
| **layer** | ✅ Yes | str | Pipeline layer/stage | `"ingest"`, `"transform"`, `"store"` |
| **name** | ✅ Yes | str | Unique step identifier (must be unique in pipeline) | `"read_customers"`, `"filter_active"` |
| **type** | ✅ Yes | str | Step type | `"sql"`, `"function"`, `"config_op"` |
| **engine** | ✅ Yes | str | Execution engine | `"pandas"`, `"spark"` |
| **value** | ✅ Yes | str | Source path, SQL query, or function path | `"data/file.csv"`, `"SELECT * FROM..."`, `"module.func"` |
| **params** | ❌ No | dict | Additional parameters | `{"header": True, "mode": "overwrite"}` |
| **inputs** | ❌ No | dict | Logical name → data_map key mapping | `{"bronze": "raw_data", "silver": "cleaned"}` |
| **outputs** | ❌ No | dict | Logical name → data_map key mapping | `{"data": "output_key"}` |

### Understanding inputs and outputs

```python
# inputs: What the node needs FROM data_map
# outputs: What the node writes TO data_map

Step(
    layer="transform",
    name="join_data",
    type="sql",
    value="SELECT * FROM customers c JOIN orders o ON c.id = o.customer_id",
    inputs={
        "customers": "raw_customers",  # Read data_map["raw_customers"] as "customers" table
        "orders": "raw_orders"         # Read data_map["raw_orders"] as "orders" table
    },
    outputs={
        "data": "joined_data"           # Write result to data_map["joined_data"]
    }
)
```

---

## How data_map Works - Visual Flow

```
Pipeline Start: data_map = {}

┌─────────────────────────────────────────────────────────────┐
│ Step 1: IngestNode (read CSV)                              │
│ outputs = {"data": "raw_sales"}                            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
data_map = {
    "raw_sales": <DataFrame with 1000 rows>
}

┌─────────────────────────────────────────────────────────────┐
│ Step 2: TransformNode (SQL filter)                         │
│ inputs = {"bronze": "raw_sales"}                           │
│ outputs = {"data": "filtered_sales"}                       │
│                                                             │
│ Reads: data_map["raw_sales"] (available as "bronze" table) │
│ Executes: SELECT * FROM bronze WHERE amount > 100          │
│ Writes: data_map["filtered_sales"] = result                │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
data_map = {
    "raw_sales": <DataFrame with 1000 rows>,
    "filtered_sales": <DataFrame with 300 rows>
}

┌─────────────────────────────────────────────────────────────┐
│ Step 3: TransformNode (add tax column)                     │
│ inputs = {"bronze": "filtered_sales"}                      │
│ outputs = {"data": "sales_with_tax"}                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
data_map = {
    "raw_sales": <DataFrame with 1000 rows>,
    "filtered_sales": <DataFrame with 300 rows>,
    "sales_with_tax": <DataFrame with 300 rows, 1 extra column>
}

┌─────────────────────────────────────────────────────────────┐
│ Step 4: StoreNode (save to Parquet)                        │
│ inputs = {"data": "sales_with_tax"}                        │
│                                                             │
│ Reads: data_map["sales_with_tax"]                          │
│ Writes: File to disk (side effect)                         │
│ data_map: UNCHANGED                                         │
└─────────────────────────────────────────────────────────────┘

Final data_map = {
    "raw_sales": <DataFrame>,
    "filtered_sales": <DataFrame>,
    "sales_with_tax": <DataFrame>
}
```

**Key Insight**: data_map grows as the pipeline executes. Nodes leave data for downstream nodes.

---

## Complete Working Example

**Scenario**: Customer order processing pipeline

```python
from odibi_core.step import Step
from odibi_core.orchestrator import Orchestrator

# Define pipeline steps
steps = [
    # 1. Read customers CSV
    Step(
        layer="ingest",
        name="read_customers",
        type="config_op",
        engine="pandas",
        value="data/customers.csv",
        params={"source_type": "csv", "header": True},
        outputs={"data": "raw_customers"}
    ),
    
    # 2. Read orders CSV
    Step(
        layer="ingest",
        name="read_orders",
        type="config_op",
        engine="pandas",
        value="data/orders.csv",
        params={"source_type": "csv", "header": True},
        outputs={"data": "raw_orders"}
    ),
    
    # 3. Filter active customers
    Step(
        layer="transform",
        name="filter_active_customers",
        type="sql",
        engine="pandas",
        value="""
            SELECT 
                customer_id,
                name,
                email,
                status
            FROM bronze 
            WHERE status = 'active'
        """,
        inputs={"bronze": "raw_customers"},
        outputs={"data": "active_customers"}
    ),
    
    # 4. Join customers with orders
    Step(
        layer="transform",
        name="join_customer_orders",
        type="sql",
        engine="pandas",
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
            "customers": "active_customers",
            "orders": "raw_orders"
        },
        outputs={"data": "customer_orders"}
    ),
    
    # 5. Calculate customer summary
    Step(
        layer="transform",
        name="calculate_summary",
        type="sql",
        engine="pandas",
        value="""
            SELECT 
                customer_id,
                name,
                email,
                COUNT(order_id) as total_orders,
                SUM(amount) as total_spent,
                AVG(amount) as avg_order_value
            FROM bronze
            GROUP BY customer_id, name, email
        """,
        inputs={"bronze": "customer_orders"},
        outputs={"data": "customer_summary"}
    ),
    
    # 6. Save to Bronze layer
    Step(
        layer="store",
        name="save_bronze_orders",
        type="config_op",
        engine="pandas",
        value="output/bronze/customer_orders.parquet",
        params={"format": "parquet", "mode": "overwrite"},
        inputs={"data": "customer_orders"}
    ),
    
    # 7. Save to Gold layer
    Step(
        layer="store",
        name="save_gold_summary",
        type="config_op",
        engine="pandas",
        value="output/gold/customer_summary.parquet",
        params={"format": "parquet", "mode": "overwrite"},
        inputs={"data": "customer_summary"}
    )
]

# Execute pipeline
orchestrator = Orchestrator(
    steps=steps,
    engine_type="pandas",
    enable_tracker=True
)

result = orchestrator.execute()

print(f"Success: {result['success']}")
print(f"Nodes executed: {result['nodes_executed']}")
```

### Pipeline Flow Diagram

```
┌──────────────┐   ┌──────────────┐
│ customers.csv│   │ orders.csv   │
└──────┬───────┘   └──────┬───────┘
       │                  │
       ▼                  │
  IngestNode              │
  (raw_customers)         │
       │                  │
       ▼                  │
  TransformNode           │
  (filter active)         │
       │                  │
       ▼                  ▼
  (active_customers)  IngestNode
       │              (raw_orders)
       │                  │
       └────┬─────────────┘
            ▼
       TransformNode
       (JOIN)
            │
            ▼
       (customer_orders)
            │
            ├─────────────────┐
            │                 │
            ▼                 ▼
       TransformNode      StoreNode
       (aggregate)        (Bronze)
            │
            ▼
       (customer_summary)
            │
            ▼
       StoreNode
       (Gold)
```

---

## Try It Yourself

### Exercise 1: Add Another Transform

Add a step that filters the customer_summary to only customers who spent more than $1000:

```python
Step(
    layer="transform",
    name="filter_high_value",
    type="sql",
    engine="pandas",
    value="SELECT * FROM bronze WHERE total_spent > 1000",
    inputs={"bronze": "customer_summary"},
    outputs={"data": "high_value_customers"}
)
```

### Exercise 2: Add a Function Transform

Create a custom function and use it:

```python
def calculate_loyalty_score(df):
    df['loyalty_score'] = (df['total_orders'] * 10) + (df['total_spent'] / 100)
    return df

# Add to pipeline
Step(
    layer="transform",
    name="add_loyalty_score",
    type="function",
    engine="pandas",
    value="my_functions.calculate_loyalty_score",
    inputs={"data": "customer_summary"},
    outputs={"data": "customers_with_loyalty"}
)
```

### Exercise 3: Multi-Join Pipeline

Build a pipeline that:
1. Reads customers, orders, and products CSVs
2. Joins orders with products
3. Joins result with customers
4. Calculates total by customer
5. Saves to Gold

---

## Common Patterns

### Pattern 1: Read → Transform → Store

```
IngestNode → TransformNode → StoreNode
```

Simple ETL: Read data, clean it, save it.

### Pattern 2: Multiple Sources → Join → Aggregate

```
IngestNode (source A) ┐
                      ├─ TransformNode (JOIN) → TransformNode (AGG) → StoreNode
IngestNode (source B) ┘
```

Combine multiple sources, aggregate, save.

### Pattern 3: Medallion Architecture

```
IngestNode → StoreNode (Bronze) → TransformNode → StoreNode (Silver) → TransformNode → StoreNode (Gold)
```

Bronze (raw) → Silver (cleaned) → Gold (aggregated).

---

## Key Takeaways

| Concept | What You Learned |
|---------|-----------------|
| **5 Nodes** | Connect, Ingest, Transform, Store, Publish - each has specific purpose |
| **Step Config** | layer, name, type, engine, value, params, inputs, outputs |
| **data_map** | Shared dictionary - nodes write outputs, read inputs |
| **inputs/outputs** | Logical names map to data_map keys |
| **SQL Transforms** | Use type="sql" for SQL queries |
| **Function Transforms** | Use type="function" for Python functions |

---

## What's Next?

**Level 3: Understanding Execution** - Learn how DAGExecutor orchestrates nodes, how Tracker captures execution details, and the EventBus lifecycle.

[Continue to Level 3 →](ODIBI_CORE_LEVEL_3_EXECUTION.md)

---

## Summary

✅ You know when to use each of the 5 node types  
✅ You understand all Step configuration fields  
✅ You see how data flows through data_map  
✅ You can build multi-step pipelines with joins and aggregations  
✅ You know common pipeline patterns
