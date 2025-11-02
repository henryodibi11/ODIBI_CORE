# File Format Support - ODIBI CORE v1.0

## Supported Formats (Parity with v2)

ODIBI CORE supports the same formats as odibi_de_v2:

| Format | Pandas | Spark | Extension | Dependencies |
|--------|--------|-------|-----------|--------------|
| **CSV** | ✅ | ✅ | `.csv` | pandas, pyspark |
| **JSON** | ✅ | ✅ | `.json` | pandas, pyspark |
| **Parquet** | ✅ | ✅ | `.parquet` | pandas, pyspark |
| **AVRO** | ✅ | ✅ | `.avro` | pandavro (Pandas), pyspark (Spark) |
| **ORC** | ❌ | ✅ | `.orc` | pyspark only |
| **Delta** | ⚠️ | ✅ | `.delta` | pyspark (Pandas reads as Parquet) |
| **SQLite** | ✅ | ❌ | `.db`, `.sqlite` | pandas only |

---

## Format Details

### CSV (Comma-Separated Values)

**Pandas:**
```python
# Read
df = ctx.read("data.csv")
df = ctx.read("data.csv", header=True, sep=";")

# Write
ctx.write(df, "output.csv")
ctx.write(df, "output.csv", index=False)
```

**Spark:**
```python
# Read
df = ctx.read("data.csv")
df = ctx.read("data.csv", header=True, inferSchema=True)

# Write
ctx.write(df, "output.csv")
ctx.write(df, "output.csv", mode="append", header=True)
```

---

### JSON (JavaScript Object Notation)

**Pandas:**
```python
# Read
df = ctx.read("data.json")
df = ctx.read("data.json", orient="records")

# Write
ctx.write(df, "output.json")
ctx.write(df, "output.json", orient="records")
```

**Spark:**
```python
# Read
df = ctx.read("data.json")
df = ctx.read("data.json", multiLine=True)

# Write
ctx.write(df, "output.json")
ctx.write(df, "output.json", mode="overwrite")
```

---

### Parquet (Columnar Format)

**Pandas:**
```python
# Read
df = ctx.read("data.parquet")

# Write
ctx.write(df, "output.parquet")
ctx.write(df, "output.parquet", compression="snappy")
```

**Spark:**
```python
# Read
df = ctx.read("data.parquet")

# Write
ctx.write(df, "output.parquet")
ctx.write(df, "output.parquet", mode="append", partitionBy=["year", "month"])
```

---

### AVRO (Binary Format)

**Pandas:**
```python
# Requires: pip install pandavro

# Read
df = ctx.read("data.avro")

# Write  
ctx.write(df, "output.avro")
```

**Spark:**
```python
# Read
df = ctx.read("data.avro")

# Write
ctx.write(df, "output.avro")
ctx.write(df, "output.avro", mode="overwrite")
```

---

### ORC (Optimized Row Columnar)

**Pandas:**
```python
# Not supported natively
# Workaround: Use Spark to convert ORC → Parquet, then read with Pandas
```

**Spark:**
```python
# Read
df = ctx.read("data.orc")

# Write
ctx.write(df, "output.orc")
ctx.write(df, "output.orc", mode="append", compression="snappy")
```

---

### Delta Lake

**Pandas:**
```python
# Read Delta as Parquet (workaround)
df = ctx.read("delta_table/_delta_log", source_type="parquet")

# Write as Parquet (not true Delta)
ctx.write(df, "output.parquet")
```

**Spark:**
```python
# Read
df = ctx.read("delta_table", source_type="delta")
df = ctx.read("/path/to/delta_table.delta")

# Write
ctx.write(df, "delta_table", source_type="delta", mode="overwrite")
ctx.write(df, "delta_table", source_type="delta", mode="append")
```

---

### SQLite (Database)

**Pandas:**
```python
# Read
df = ctx.read("database.db", source_type="sqlite", table="my_table")

# Write (not implemented yet - Phase 8)
```

**Spark:**
```python
# Use JDBC instead
df = ctx.read("jdbc:sqlite:database.db", source_type="jdbc", table="my_table")
```

---

## Installation for Formats

### Minimal (CSV, JSON, Parquet)
```bash
pip install pandas
```

### With AVRO
```bash
pip install pandas pandavro
```

### With Spark (CSV, JSON, Parquet, AVRO, ORC, Delta)
```bash
pip install pyspark
```

### Full Support
```bash
pip install -e ".[all]"
```

---

## Format Comparison

### Best Practices

| Use Case | Recommended Format | Why |
|----------|-------------------|-----|
| **Small data (<1MB)** | CSV | Human-readable, universal |
| **Config/metadata** | JSON | Human-readable, structured |
| **Analytics (>10MB)** | Parquet | Columnar, compressed, fast |
| **Streaming** | AVRO | Schema evolution, compact |
| **Hive/Hadoop** | ORC | Optimized for analytics |
| **Data Lake** | Delta | ACID, time travel, versioning |

### Performance

| Format | Compression | Read Speed | Write Speed | Size |
|--------|-------------|------------|-------------|------|
| CSV | None | Slow | Slow | Large |
| JSON | None | Medium | Medium | Large |
| Parquet | High | Fast | Fast | Small |
| AVRO | Medium | Fast | Fast | Small |
| ORC | High | Fast | Fast | Small |
| Delta | High | Fast | Fast | Small |

---

## Parity with v2

ODIBI CORE v1 now supports **all formats from v2**:

| Format | v2 Support | v1 Support | Status |
|--------|-----------|------------|--------|
| CSV | ✅ | ✅ | ✅ Parity |
| JSON | ✅ | ✅ | ✅ Parity |
| Parquet | ✅ | ✅ | ✅ Parity |
| AVRO | ✅ | ✅ | ✅ Parity |
| Delta | ✅ (Spark) | ✅ (Spark) | ✅ Parity |
| ORC | ✅ (Spark) | ✅ (Spark) | ✅ Parity |
| SQL | ✅ | ✅ | ✅ Parity |
| API | ✅ | 🔜 Phase 4+ | ⏳ Planned |

---

## Examples

### Multi-Format Pipeline

```python
from odibi_core.engine import PandasEngineContext

ctx = PandasEngineContext()
ctx.connect()

# Read various formats
csv_df = ctx.read("input.csv")
json_df = ctx.read("config.json")
parquet_df = ctx.read("data.parquet")

# Combine and transform
ctx.register_temp("csv_data", csv_df)
ctx.register_temp("json_data", json_df)

result = ctx.execute_sql("""
    SELECT c.*, j.metadata
    FROM csv_data c
    LEFT JOIN json_data j ON c.id = j.id
""")

# Write to different formats
ctx.write(result, "output.parquet")  # For analytics
ctx.write(result, "output.json")     # For API consumption
ctx.write(result, "output.csv")      # For Excel users
```

### Spark with Delta Lake

```python
from odibi_core.engine import SparkEngineContext

ctx = SparkEngineContext()
ctx.connect()

# Read from various sources
csv_df = ctx.read("bronze/data.csv")
json_df = ctx.read("bronze/metadata.json")

# Transform
ctx.register_temp("data", csv_df)
silver_df = ctx.execute_sql("SELECT * FROM data WHERE quality_score > 0.8")

# Write to Delta (versioned, ACID)
ctx.write(silver_df, "delta_lake/silver/cleaned_data", source_type="delta", mode="overwrite")

# Also write Parquet for compatibility
ctx.write(silver_df, "silver/cleaned_data.parquet", mode="overwrite")

ctx.stop()
```

---

## Updated Dependencies

**requirements.txt:**
```
pandas>=1.5.0
duckdb>=0.9.0          # For Pandas SQL
pyspark>=3.3.0         # For Spark engine
pandavro>=1.7.0        # For AVRO with Pandas
```

**Install:**
```bash
# All formats
pip install -e ".[all]"

# Pandas with AVRO
pip install -e ".[formats]"
```

---

## Format Auto-Detection

ODIBI CORE auto-detects format from file extension:

```python
# Auto-detect (recommended)
df = ctx.read("data.csv")        # Detects CSV
df = ctx.read("data.json")       # Detects JSON
df = ctx.read("data.parquet")    # Detects Parquet
df = ctx.read("data.avro")       # Detects AVRO

# Override if needed
df = ctx.read("data.txt", source_type="csv")
df = ctx.read("delta_table", source_type="delta")
```

---

## Next Steps

**Phase 2 is now complete with v2 parity on formats!**

Ready to proceed to Phase 3 with full format support matching v2.
