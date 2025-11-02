"""
Cheat Sheets - Quick reference guides for each phase
"""

CHEAT_SHEETS = {
    "phase1": """# Phase 1 Cheat Sheet: Core Architecture

## 🔧 The 5 Canonical Nodes

| Node | Purpose | Example |
|------|---------|---------|
| **ConnectNode** 🔌 | Establish connections | `conn = ConnectNode(source="db.csv")` |
| **IngestNode** 📥 | Read data | `df = IngestNode(conn).read()` |
| **TransformNode** ⚙️ | Transform data | `df = TransformNode(func).apply(df)` |
| **StoreNode** 💾 | Save data | `StoreNode(target="out.csv").write(df)` |
| **PublishNode** 📤 | Expose data | `PublishNode(endpoint).publish(df)` |

## 📊 Medallion Architecture

```
Bronze (Raw) → Silver (Clean) → Gold (Aggregate)
```

- **Bronze**: Ingest raw data, no transformations
- **Silver**: Validate, clean, standardize
- **Gold**: Aggregate, calculate KPIs, business-ready

## 💻 Basic Pipeline Pattern

```python
# 1. Connect
conn = ConnectNode(source="data.csv")

# 2. Ingest
df = IngestNode(conn).read()

# 3. Transform
df['new_col'] = df['old_col'] * 2

# 4. Store
StoreNode(target="output.csv").write(df)
```

## 🎯 Key Concepts

- **Composability**: Nodes can be mixed and matched
- **Reusability**: Same nodes work across pipelines
- **Observability**: Built-in logging and monitoring
- **Separation of Concerns**: Each node has one job

## ⚠️ Common Mistakes

❌ Putting transformation logic in IngestNode  
✅ Use separate TransformNode

❌ Hardcoding file paths  
✅ Use config files

❌ Not handling errors  
✅ Use try-except and log failures
    """,
    
    "phase2": """# Phase 2 Cheat Sheet: Dual-Engine Support

## ⚙️ Engine Detection

```python
from odibi_core.functions import detect_engine

engine = detect_engine(df)  # Returns "pandas" or "spark"
```

## 🔄 Engine-Agnostic Pattern

```python
def my_function(df):
    engine = detect_engine(df)
    
    if engine == "pandas":
        # Pandas implementation
        df['result'] = df['col1'] + df['col2']
    else:
        # Spark implementation
        df = df.withColumn('result', F.col('col1') + F.col('col2'))
    
    return df
```

## 📊 Common Operations - Both Engines

| Operation | Pandas | Spark |
|-----------|--------|-------|
| **Add Column** | `df['new'] = value` | `df.withColumn('new', value)` |
| **Filter** | `df[df['col'] > 5]` | `df.filter(F.col('col') > 5)` |
| **Group By** | `df.groupby('col').sum()` | `df.groupBy('col').sum()` |
| **Join** | `df1.merge(df2, on='id')` | `df1.join(df2, on='id')` |

## 🛡️ Safe Operations

```python
# Safe Division
from odibi_core.functions import safe_divide
df = safe_divide(df, 'numerator', 'denominator', 'result', fill_value=0)

# Safe Log
from odibi_core.functions import safe_log
df = safe_log(df, 'value', 'log_value', base=10, fill_value=0)
```

## ⚠️ Common Mistakes

❌ Using Pandas syntax on Spark DataFrame  
✅ Use detect_engine() first

❌ Not handling engine-specific imports  
✅ Import inside if/else blocks

❌ Assuming in-place modifications work on both  
✅ Always return the DataFrame
    """,
    
    "phase3": """# Phase 3 Cheat Sheet: Configuration System

## 📋 Config File Example

```json
{
  "pipeline_name": "sales_pipeline",
  "engine": "pandas",
  "bronze": {
    "sources": [
      {"name": "sales", "path": "raw/sales.csv", "type": "csv"}
    ],
    "target_dir": "data/bronze"
  },
  "silver": {
    "transformations": ["clean_nulls", "validate_types"],
    "target_dir": "data/silver"
  },
  "gold": {
    "aggregations": ["sum_by_customer", "avg_order_value"],
    "target_dir": "data/gold"
  }
}
```

## 🔧 Loading Config

```python
import json

with open("pipeline_config.json") as f:
    config = json.load(f)

# Access values
pipeline_name = config["pipeline_name"]
sources = config["bronze"]["sources"]
```

## 🗄️ Config in Database

```python
from odibi_core.config import ConfigManager

# Load from database
config_mgr = ConfigManager(db_path="configs.db")
config = config_mgr.get_config("sales_pipeline")
```

## ✅ Best Practices

✓ One config file per pipeline  
✓ Use relative paths  
✓ Validate config before execution  
✓ Version your config files  
✓ Document all config fields  

## ⚠️ Common Mistakes

❌ Hardcoding values in Python  
✅ Move everything to config

❌ Not validating config schema  
✅ Check required fields exist

❌ Mixing code and config  
✅ Keep them separate
    """,
    
    "functions": """# Functions Library Cheat Sheet

## 🧮 Math & Stats

```python
from odibi_core import functions as fn

# Safe operations
df = fn.safe_divide(df, 'a', 'b', 'result', fill_value=0)
df = fn.safe_log(df, 'value', 'log_value', base=10)

# Statistics
df = fn.calculate_z_score(df, 'sales', result_col='z_score')
df = fn.calculate_percentile(df, 'revenue', percentile=95)
```

## 🔄 Data Quality

```python
# Completeness
completeness = fn.calculate_completeness(df)  # Returns percentage

# Null handling
df = fn.fill_nulls_with_mean(df, 'column_name')
df = fn.remove_duplicates(df, subset=['id'])
```

## 🌡️ Engineering Functions

```python
# Temperature conversions
temp_f = fn.celsius_to_fahrenheit(25)  # 77.0
temp_c = fn.fahrenheit_to_celsius(77)  # 25.0

# Pressure conversions
pressure_psi = fn.convert_pressure(1.0, "bar", "psi")  # 14.5
```

## 📊 Common Patterns

| Task | Function |
|------|----------|
| Divide safely | `safe_divide()` |
| Find outliers | `calculate_z_score()` |
| Check data quality | `calculate_completeness()` |
| Convert units | `convert_*()` |
| Handle nulls | `fill_nulls_*()` |

## ⚠️ Remember

✓ All functions are dual-engine compatible  
✓ Always specify result_col for new columns  
✓ Use fill_value for safe operations  
✓ Functions work in-place or return new DataFrame
    """,
    
    "sdk": """# Phase 9 Cheat Sheet: SDK & CLI

## 🛠️ CLI Commands

```bash
# Run a pipeline
odibi run pipeline_config.json

# Validate config
odibi validate pipeline_config.json

# List pipelines
odibi list

# Show pipeline status
odibi status sales_pipeline

# View logs
odibi logs sales_pipeline --lines 50
```

## 💻 Python SDK

```python
from odibi_core.sdk import Pipeline

# Create pipeline
pipeline = Pipeline.from_config("pipeline_config.json")

# Execute
result = pipeline.run()

# Check status
print(pipeline.status)  # "success", "failed", "running"

# Get metrics
print(pipeline.metrics)  # Duration, rows processed, etc.
```

## 🔍 DAG Visualization

```python
from odibi_core.sdk import Pipeline

pipeline = Pipeline.from_config("config.json")
pipeline.visualize_dag(output="pipeline_dag.png")
```

## ⚠️ Common CLI Mistakes

❌ `python pipeline.py`  
✅ `odibi run pipeline_config.json`

❌ Forgetting to validate config first  
✅ `odibi validate config.json` before run

❌ Not checking logs when failures occur  
✅ `odibi logs <pipeline>` to debug
    """
}


def get_cheat_sheet(phase_key: str) -> str:
    """Get cheat sheet for a phase"""
    return CHEAT_SHEETS.get(phase_key, "# Cheat sheet not available yet")


def generate_downloadable_cheat_sheet(phase_key: str) -> str:
    """Generate downloadable markdown cheat sheet"""
    content = get_cheat_sheet(phase_key)
    header = f"""---
title: "ODIBI CORE - {phase_key.replace('_', ' ').title()} Cheat Sheet"
author: "LearnODIBI Studio"
date: "Generated by ODIBI CORE v1.0"
---

"""
    return header + content
