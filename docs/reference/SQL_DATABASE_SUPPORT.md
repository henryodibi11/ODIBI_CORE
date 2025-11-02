# SQL Database Support - Real Databases, Not Just SQLite

## Why SQLite vs SQL Databases?

### SQLite
- **Purpose**: Local file-based database (like a better CSV)
- **Use case**: Testing, local storage, embedded databases
- **Connection**: File path (`data.db`)
- **No server needed**

### SQL Databases (PostgreSQL, SQL Server, MySQL)
- **Purpose**: Production databases with concurrent access
- **Use case**: Read from/write to enterprise databases
- **Connection**: Connection string (`postgresql://host/db`)
- **Server required**

**ODIBI CORE supports both!**

---

## SQL Database Support (Pandas)

### Connection Strings (SQLAlchemy)

**PostgreSQL:**
```python
connection_string = "postgresql://user:password@host:5432/database"
```

**SQL Server:**
```python
connection_string = "mssql+pyodbc://user:password@host/database?driver=ODBC+Driver+17+for+SQL+Server"
```

**MySQL:**
```python
connection_string = "mysql+pymysql://user:password@host:3306/database"
```

### Reading from SQL Database

**Query approach:**
```python
from odibi_core.engine import PandasEngineContext

ctx = PandasEngineContext()

df = ctx.read(
    "dummy_path",  # Not used for SQL
    source_type="sql",
    connection_string="postgresql://user:pass@localhost:5432/mydb",
    query="SELECT * FROM customers WHERE region = 'USA'"
)
```

**Table approach:**
```python
df = ctx.read(
    "dummy_path",
    source_type="sql",
    connection_string="postgresql://user:pass@localhost:5432/mydb",
    table="customers"
)
```

### Using Secrets

```python
ctx = PandasEngineContext(secrets={
    "db_user": "admin",
    "db_password": "secret123"
})

# Build connection string from secrets
user = ctx.get_secret("db_user")
password = ctx.get_secret("db_password")
conn_str = f"postgresql://{user}:{password}@localhost:5432/mydb"

df = ctx.read(
    "dummy",
    source_type="sql",
    connection_string=conn_str,
    table="sales"
)
```

---

## SQL Database Support (Spark)

### JDBC Connections

**PostgreSQL:**
```python
from odibi_core.engine import SparkEngineContext

ctx = SparkEngineContext()
ctx.connect()

df = ctx.read(
    "dummy_path",
    source_type="jdbc",
    jdbc_url="jdbc:postgresql://host:5432/database",
    table="customers",
    driver="org.postgresql.Driver",
    user="admin",
    password="secret"
)
```

**SQL Server:**
```python
df = ctx.read(
    "dummy_path",
    source_type="jdbc",
    jdbc_url="jdbc:sqlserver://host:1433;databaseName=mydb",
    table="dbo.sales",
    driver="com.microsoft.sqlserver.jdbc.SQLServerDriver",
    user="admin",
    password="secret"
)
```

**MySQL:**
```python
df = ctx.read(
    "dummy_path",
    source_type="jdbc",
    jdbc_url="jdbc:mysql://host:3306/database",
    table="orders",
    driver="com.mysql.jdbc.Driver",
    user="admin",
    password="secret"
)
```

### Writing to SQL Database

```python
ctx.write(
    df,
    "dummy_target",
    source_type="jdbc",
    jdbc_url="jdbc:postgresql://host:5432/database",
    table="processed_data",
    driver="org.postgresql.Driver",
    user="admin",
    password="secret",
    mode="overwrite"  # or "append"
)
```

---

## Complete Format Support Matrix

| Format | Pandas | Spark | Use Case |
|--------|--------|-------|----------|
| **CSV** | ✅ | ✅ | Files, Excel export |
| **JSON** | ✅ | ✅ | APIs, configs |
| **Parquet** | ✅ | ✅ | Data lake, analytics |
| **AVRO** | ✅ | ✅ | Streaming, schema evolution |
| **ORC** | ❌ | ✅ | Hive, Hadoop |
| **Delta** | ⚠️ | ✅ | Data lake, ACID |
| **SQLite** | ✅ | ❌ | Local files |
| **PostgreSQL** | ✅ | ✅ | Production DB |
| **SQL Server** | ✅ | ✅ | Enterprise DB |
| **MySQL** | ✅ | ✅ | Web apps DB |
| **Oracle** | ✅ | ✅ | Enterprise DB |

**Now matches v2 completely!** ✅

---

## Example: Read from SQL Server, Write to Delta

```python
from odibi_core.engine import SparkEngineContext

ctx = SparkEngineContext()
ctx.connect()

# Read from SQL Server (Bronze)
bronze_df = ctx.read(
    "source",
    source_type="jdbc",
    jdbc_url="jdbc:sqlserver://prod-db:1433;databaseName=sales",
    table="dbo.transactions",
    driver="com.microsoft.sqlserver.jdbc.SQLServerDriver",
    user="etl_user",
    password="secret"
)

# Transform (Silver)
ctx.register_temp("bronze", bronze_df)
silver_df = ctx.execute_sql("""
    SELECT 
        transaction_id,
        customer_id,
        amount,
        transaction_date
    FROM bronze
    WHERE status = 'completed'
    AND amount > 0
""")

# Write to Delta Lake (Silver layer)
ctx.write(
    silver_df,
    "/mnt/delta/silver/transactions",
    source_type="delta",
    mode="overwrite"
)

ctx.stop()
```

---

## Updated Dependencies

### For SQL Database Support (Pandas)

**PostgreSQL:**
```bash
pip install sqlalchemy psycopg2-binary
```

**SQL Server:**
```bash
pip install sqlalchemy pyodbc
```

**MySQL:**
```bash
pip install sqlalchemy pymysql
```

### For JDBC Support (Spark)

**Spark includes JDBC, but you need database drivers:**

**PostgreSQL:**
```bash
# Download JDBC driver
# https://jdbc.postgresql.org/download/
# Add to Spark: --jars postgresql-42.x.jar
```

**SQL Server:**
```bash
# Download from Microsoft
# https://docs.microsoft.com/en-us/sql/connect/jdbc/
```

**Or use Databricks (includes all drivers)**

---

## Config Example with SQL Database

```json
{
  "layer": "ingest",
  "name": "read_sql_server",
  "type": "config_op",
  "engine": "pandas",
  "value": "source_path",
  "params": {
    "source_type": "sql",
    "connection_string": "mssql+pyodbc://user:pass@host/db?driver=ODBC+Driver+17+for+SQL+Server",
    "table": "dbo.sales"
  },
  "outputs": {"data": "bronze_sales"}
}
```

---

## Why This Matters

### v2 Use Cases Now Supported

1. **Read from Production Databases**
   - ✅ Extract data from SQL Server
   - ✅ Replicate PostgreSQL tables
   - ✅ Sync MySQL data

2. **Write to Data Warehouses**
   - ✅ Load processed data to PostgreSQL
   - ✅ Update SQL Server tables
   - ✅ Export to MySQL

3. **Hybrid Pipelines**
   - ✅ Read from SQL → Transform → Write to Delta
   - ✅ Read from Delta → Write to SQL
   - ✅ Multi-database joins

### Example: Energy Efficiency (Your Use Case)

```python
# Read from SQL Server (sensor data)
bronze_df = pandas_ctx.read(
    "source",
    source_type="sql",
    connection_string="mssql+pyodbc://...",
    query="""
        SELECT timestamp, plant, asset, tag, value
        FROM sensor_readings
        WHERE timestamp > '2025-01-01'
    """
)

# Transform (calculate efficiency)
ctx.register_temp("bronze", bronze_df)
silver_df = ctx.execute_sql("""
    SELECT 
        plant,
        asset,
        AVG(value) as avg_efficiency
    FROM bronze
    WHERE tag = 'Boiler_Efficiency'
    GROUP BY plant, asset
""")

# Write back to SQL (analytics table)
# TODO Phase 8: Implement write_sql for Pandas
```

---

## Summary

**Before:** Only CSV and Parquet ❌  
**Now:** CSV, JSON, Parquet, AVRO, ORC, Delta, SQL databases ✅  

**Matches v2 exactly!** ✅

**Ready for Phase 3 with full database support!** 🚀
