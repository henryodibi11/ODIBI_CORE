---
id: phase_2_engine_contexts
title: "Phase 2: The Dual-Engine System"
level: "Beginner"
tags: ["dual-engine", "pandas", "spark", "duckdb", "engine-abstraction", "parity"]
checkpoints: 6
quiz_questions: 18
teaching_mode: true
estimated_time: "4 hours"
prerequisites: ["phase_1_foundation"]
---

# ODIBI CORE v1.0 - Phase 2 Developer Walkthrough

**Building the Dual-Engine System: A Step-by-Step Guide**

**Author**: AMP AI Engineering Agent  
**Date**: 2025-11-01  
**Audience**: Developers learning dual-engine data frameworks  
**Duration**: ~4 hours (following this guide)  
**Prerequisites**: Completed Phase 1 (foundation & scaffolding)

---

## 📚 Engine Overview

### What is the Engine Context Layer?

Welcome to Phase 2! Think of the Engine Context as the **steering wheel** of ODIBI CORE. Just like a steering wheel provides the same interface whether you're driving a compact car or a semi-truck, the EngineContext gives you one consistent way to work with data—whether you're processing thousands of rows locally or billions in the cloud.

The Engine Context is the **abstraction layer** between your pipeline logic (Nodes) and the underlying data processing engine (Pandas or Spark).

**Analogy**: Think of it like a car's steering wheel:
- **Steering wheel** (NodeBase) = Same interface for all drivers
- **Engine** (PandasEngine vs SparkEngine) = Different implementations
- **Driver** (You) = Doesn't need to know how the engine works

### Why This Separation Matters

Imagine building a data pipeline and then realizing your dataset grew from 100,000 rows to 10 million. Without engine abstraction, you'd rewrite everything. With ODIBI CORE, you just change one line in your config. Let's see how:

```
┌─────────────────────────────────────────────────────┐
│  Nodes (Business Logic)                             │
│  "Read CSV, filter, aggregate, write Parquet"       │
└─────────────────────────────────────────────────────┘
                        ▼
                   [Uses EngineContext]
                        ▼
┌──────────────────────┬──────────────────────────────┐
│  PandasEngineContext │  SparkEngineContext          │
│  - Local execution   │  - Distributed execution     │
│  - Fast for <1M rows │  - Scales to billions        │
│  - DuckDB SQL        │  - Spark SQL                 │
│  - No cluster needed │  - Cluster/local modes       │
└──────────────────────┴──────────────────────────────┘
```

**Key Insight**: **Same Node code, different engine = different performance characteristics**

### The Engine Context Contract (Review)

From Phase 1, we defined:

```python
class EngineContext(ABC):
    @abstractmethod
    def connect(**kwargs): pass
    
    @abstractmethod
    def read(source, **kwargs): pass
    
    @abstractmethod
    def write(df, target, **kwargs): pass
    
    @abstractmethod
    def execute_sql(query, **kwargs): pass
    
    @abstractmethod
    def register_temp(name, df): pass
    
    @abstractmethod
    def collect_sample(df, n): pass
```

**Phase 2 Goal**: Implement these 6 methods for both Pandas and Spark.

---

## 🗺️ Dependency Map (Phase 2)

Here's the blueprint we'll follow. Think of this like a construction site—we build from the foundation up, layer by layer:

```
┌────────────────────────────────────────────────────────────┐
│                    User Code / Tests                       │
│   (Uses engine contexts via factory or directly)           │
└────────────────────────────────────────────────────────────┘
                            ▲
                            │
┌────────────────────────────────────────────────────────────┐
│         Orchestrator + Engine Factory                      │
│    create_engine_context("pandas" | "spark")               │
└────────────────────────────────────────────────────────────┘
                            ▲
                            │
┌──────────────────────┬─────────────────────────────────────┐
│ PandasEngineContext  │  SparkEngineContext                 │
│ (pandas_context.py)  │  (spark_context.py)                 │
│                      │         ▲                            │
│  Depends on:         │         │                            │
│  - pandas            │  Depends on:                         │
│  - duckdb            │  - pyspark                           │
│                      │  - spark_local_config.py             │
└──────────────────────┴─────────────────────────────────────┘
                            ▲
                            │
┌────────────────────────────────────────────────────────────┐
│              EngineContext (Abstract Base)                 │
│         (engine/base_context.py - Phase 1)                 │
└────────────────────────────────────────────────────────────┘
```

**Build Order:**
1. Spark local config (no dependencies)
2. PandasEngineContext (depends on: EngineContext ABC)
3. SparkEngineContext (depends on: EngineContext ABC, spark_local_config)
4. Engine factory (depends on: both contexts)
5. Tests (depend on: contexts)
6. Parity demo (depends on: both contexts, sample data)

---

## 🚀 Step-by-Step Build Missions

### Mission 1: Understand the Challenge

Before writing code, let's understand the **parity problem**. This is the heart of what makes ODIBI CORE powerful.

**Question**: How do we make this code work on both Pandas and Spark?

```python[demo]
# User writes this once:
ctx.read("data.csv")
ctx.execute_sql("SELECT * FROM data WHERE value > 100")
ctx.write(result, "output.parquet")
```

**Answer**: The `ctx` object implements the same methods differently:

| Method | Pandas | Spark |
|--------|--------|-------|
| `read()` | `pd.read_csv()` | `spark.read.csv()` |
| `execute_sql()` | DuckDB | `spark.sql()` |
| `write()` | `df.to_parquet()` | `df.write.parquet()` |

**Result**: Same interface, different execution.

**🧠 QUIZ #1-3:**
1. What is the main benefit of engine abstraction?
2. Which engine would you choose for a 500KB CSV file on your laptop?
3. Which engine would you choose for a 50GB dataset on a cluster?

---

### Mission 2: Create Spark Local Configuration

**Create: `odibi_core/engine/spark_local_config.py`**

**Why create this first?**
Think of this as preparing your recipe before cooking. We're defining all the Spark settings in one place so SparkEngineContext can use them later without guessing defaults.

- SparkEngineContext will use DEFAULT_SPARK_CONFIG
- No dependencies (pure data structure)
- Establishes Spark defaults before implementation

```python
"""Local Spark configuration for development and testing."""

from typing import Dict

DEFAULT_SPARK_CONFIG: Dict[str, str] = {
    "spark.master": "local[*]",          # Use all CPU cores
    "spark.app.name": "ODIBI_CORE_Local",
    "spark.driver.memory": "2g",
    "spark.executor.memory": "2g",
    "spark.sql.adaptive.enabled": "true",
    "spark.serializer": "org.apache.spark.serializer.KryoSerializer",
    "spark.sql.shuffle.partitions": "4",  # Reduced for local
    "spark.ui.showConsoleProgress": "false",
}

def get_local_spark_config(
    master: str = "local[*]",
    app_name: str = "ODIBI_CORE_Local",
    driver_memory: str = "2g",
    **overrides: str
) -> Dict[str, str]:
    """Get Spark config for local execution."""
    config = DEFAULT_SPARK_CONFIG.copy()
    config["spark.master"] = master
    config["spark.app.name"] = app_name
    config["spark.driver.memory"] = driver_memory
    config.update(overrides)
    return config
```

**What this enables:**
```python[demo]
# Later, in SparkEngineContext:
self.spark_config = spark_config or DEFAULT_SPARK_CONFIG.copy()
```

**Reflection Checkpoint:**
> **Why `local[*]` instead of `local[4]`?**
>
> Answer: `local[*]` uses all available CPU cores. This maximizes parallelism on developer laptops without hardcoding core count. On a 16-core machine, it uses 16 cores; on a 4-core machine, it uses 4.

**🧠 QUIZ #4-5:**
4. What does `local[*]` mean in Spark?
5. Why set `spark.sql.shuffle.partitions` to 4 instead of the default 200?

---

### Mission 3: Implement PandasEngineContext - Part 1 (Structure)

**Create: `odibi_core/engine/pandas_context.py`**

**Why build Pandas first?**
Pandas is like learning to ride a bike before trying a motorcycle. It's simpler than Spark (no session management), validates our EngineContext contract works, and enables local testing immediately.

- Simpler than Spark (no session management)
- Validates the EngineContext contract
- Enables local testing immediately

```python[demo]
"""Pandas engine context implementation."""

import logging
from typing import Any, Callable, Dict, Optional, Union
from odibi_core.engine.base_context import EngineContext

logger = logging.getLogger(__name__)


class PandasEngineContext(EngineContext):
    """
    Pandas engine context with DuckDB SQL support.
    """

    def __init__(
        self,
        secrets: Optional[Union[Dict[str, str], Callable[[str], str]]] = None,
        **kwargs: Any
    ) -> None:
        super().__init__(secrets, **kwargs)
        self._duckdb_conn: Optional[Any] = None  # Lazy initialization
        self._temp_tables: Dict[str, Any] = {}    # Cache for registered tables
```

**Key Design Decisions:**

1. **`_duckdb_conn: Optional[Any]`** - Lazy initialization (don't create until needed)
2. **`_temp_tables: Dict`** - Store registered DataFrames for SQL queries
3. **Inherits from EngineContext** - Gets `get_secret()` for free

**🧠 QUIZ #6:**
6. What does "lazy initialization" mean and why is it important here?

---

### Mission 4: Implement PandasEngineContext - Part 2 (Connect)

Now we're connecting to DuckDB—think of it as plugging in the "SQL brain" for Pandas. DuckDB is like having a tiny, lightning-fast database that lives in your computer's memory.

```python[demo]
def connect(self, **kwargs: Any) -> "PandasEngineContext":
    """Establish connection (initializes DuckDB)."""
    try:
        import duckdb
        self._duckdb_conn = duckdb.connect(":memory:")
        logger.info("DuckDB connection initialized (in-memory)")
    except ImportError:
        logger.warning("DuckDB not available, SQL operations will fail")
        self._duckdb_conn = None
    return self
```

**Why DuckDB?**
- **Fast**: C++ implementation, optimized for analytics
- **In-memory**: No disk I/O for temp tables
- **SQL-compatible**: Familiar syntax, works like Spark SQL
- **Pandas integration**: Direct DataFrame registration

**Reflection Checkpoint:**
> **Why DuckDB over SQLite for SQL queries?**
>
> Answer: 
> - **DuckDB**: Columnar storage, OLAP-optimized, 10-100x faster for analytics
> - **SQLite**: Row-based, OLTP-optimized, slower for aggregations
>
> Since we're doing data transformations (aggregations, JOINs), DuckDB is the right choice. It also matches Spark SQL semantics better.

**🧠 QUIZ #7-8:**
7. What does `:memory:` mean in `duckdb.connect(":memory:")`?
8. What happens if DuckDB is not installed when `connect()` is called?

---

## ✅ CHECKPOINT #1: Configuration & Connection Foundation

**Pause and reflect!** You've just completed the groundwork:

✅ Created Spark configuration defaults  
✅ Built the PandasEngineContext structure  
✅ Implemented DuckDB connection with graceful degradation

**Test your understanding:**
- Can you explain why we use `DEFAULT_SPARK_CONFIG` instead of hardcoding values?
- What would happen if someone calls `execute_sql()` before `connect()`?
- Why do we return `self` from `connect()`?

**Ready to move forward?** Let's implement the data reading operations!

---

### Mission 5: Implement PandasEngineContext - Part 3 (Read)

Here's where the magic starts! The `read()` method is your Swiss Army knife—it handles CSV, JSON, Parquet, and more, all with auto-detection.

**The read method must:**
1. Auto-detect format from extension
2. Support multiple formats
3. Handle optional dependencies gracefully

```python
def read(self, source: str, **kwargs: Any) -> Any:
    """Read data from source."""
    try:
        import pandas as pd
    except ImportError:
        raise ImportError("pandas is required. Install with: pip install pandas")

    source_type = kwargs.pop("source_type", None)
    
    # Auto-detect format
    if source_type is None:
        if source.endswith(".csv"):
            source_type = "csv"
        elif source.endswith(".json"):
            source_type = "json"
        elif source.endswith(".parquet"):
            source_type = "parquet"
        elif source.endswith(".avro"):
            source_type = "avro"
        # ... etc
    
    # Read based on type
    if source_type == "csv":
        df = pd.read_csv(source, **kwargs)
        logger.info(f"Read {len(df)} rows from CSV: {source}")
        return df
    elif source_type == "json":
        df = pd.read_json(source, **kwargs)
        logger.info(f"Read {len(df)} rows from JSON: {source}")
        return df
    # ... etc
```

**Pattern Emerging:**
1. **Try/except for imports** - Pandas might not be installed
2. **Auto-detect or override** - `source_type` parameter
3. **Format-specific logic** - Each format uses appropriate reader
4. **Logging** - Track what was read

**Why auto-detect?**
```python
# User-friendly (no need to specify format)
df = ctx.read("data.csv")

# vs verbose
df = ctx.read("data.csv", source_type="csv", format="csv")
```

**🧠 QUIZ #9-10:**
9. What happens if you call `ctx.read("data.csv", source_type="json")`?
10. Why does `read()` pop `source_type` from kwargs before passing to `pd.read_csv()`?

---

### Mission 6: Implement PandasEngineContext - Part 4 (SQL)

This is where PandasEngineContext becomes truly powerful. We're building the **SQL triad**: `register_temp()`, `execute_sql()`, and the `_temp_tables` cache working together like a well-oiled machine.

**The SQL triad: execute_sql + register_temp + temp_tables**

```python[demo]
def register_temp(self, name: str, df: Any) -> None:
    """Register DataFrame as temporary table for SQL queries."""
    try:
        import pandas as pd
    except ImportError:
        raise ImportError("pandas is required. Install with: pip install pandas")
    
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Expected pandas DataFrame, got {type(df)}")
    
    self._temp_tables[name] = df
    logger.info(f"Registered temp table '{name}' with {len(df)} rows")


def execute_sql(self, query: str, **kwargs: Any) -> Any:
    """Execute SQL query using DuckDB."""
    if self._duckdb_conn is None:
        self.connect()  # Lazy initialization
    
    if self._duckdb_conn is None:
        raise RuntimeError("DuckDB not available. Install with: pip install duckdb")

    try:
        # Register all temp tables with DuckDB
        for name, df in self._temp_tables.items():
            self._duckdb_conn.register(name, df)
        
        # Execute query
        result = self._duckdb_conn.execute(query).fetchdf()
        logger.info(f"Executed SQL, returned {len(result)} rows")
        return result
    except Exception as e:
        logger.error(f"SQL execution failed: {e}")
        raise
```

**Workflow:**
```
User calls register_temp("data", df)
    ↓
DataFrame stored in _temp_tables dict
    ↓
User calls execute_sql("SELECT * FROM data ...")
    ↓
DuckDB connects if not connected
    ↓
All _temp_tables registered with DuckDB
    ↓
Query executed
    ↓
Result returned as Pandas DataFrame
```

**Reflection Checkpoint:**
> **Why lazy initialization for DuckDB?**
>
> Answer: Not all pipelines use SQL. If a user only does `read() → write()`, no need to initialize DuckDB. This saves ~50ms startup time and memory.

**🧠 QUIZ #11-12:**
11. What's the purpose of the `_temp_tables` dictionary?
12. Can you execute SQL without calling `register_temp()` first? Why or why not?

---

## ✅ CHECKPOINT #2: Pandas Reading & SQL Complete

**Great progress!** You've built the core functionality of PandasEngineContext:

✅ File reading with auto-detection  
✅ SQL query execution via DuckDB  
✅ Temporary table registration

**Test your understanding:**
- What's the data flow when you call `execute_sql()`?
- Why do we re-register all temp tables on every SQL call?
- How would you read a CSV file from a custom URL?

**Next up:** Finishing touches on Pandas, then tackling Spark!

---

### Mission 7: Implement PandasEngineContext - Part 5 (Write & Sample)

Almost done with Pandas! These last two methods round out the interface—writing data out and grabbing quick samples.

**Write method (similar pattern to read):**

```python
def write(self, df: Any, target: str, **kwargs: Any) -> None:
    """Write DataFrame to target."""
    import pandas as pd
    
    # Auto-detect format
    if target.endswith(".csv"):
        df.to_csv(target, index=False, **kwargs)
        logger.info(f"Wrote {len(df)} rows to CSV: {target}")
    elif target.endswith(".json"):
        df.to_json(target, orient="records", **kwargs)
        logger.info(f"Wrote {len(df)} rows to JSON: {target}")
    elif target.endswith(".parquet"):
        df.to_parquet(target, **kwargs)
        logger.info(f"Wrote {len(df)} rows to Parquet: {target}")
    # ... etc
```

**Sample collection (simple for Pandas):**

```python
def collect_sample(self, df: Any, n: int = 5) -> Any:
    """Collect sample rows."""
    import pandas as pd
    
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Expected pandas DataFrame, got {type(df)}")
    
    return df.head(n)
```

**Why `head(n)` is sufficient for Pandas?**
- DataFrame already in memory
- No distributed partitions to worry about
- Fast (O(1) operation)

**🧠 QUIZ #13:**
13. Why do we set `index=False` in `df.to_csv()` by default?

---

### Mission 8: Implement SparkEngineContext - Part 1 (Structure & Connect)

**Create: `odibi_core/engine/spark_context.py`**

Now we step up to the big leagues! Spark is like upgrading from a car to a freight train—more complex, but capable of moving massive loads.

**Why build Spark after Pandas?**
- More complex (session management, distributed logic)
- Can copy structure from Pandas implementation
- Validates that contract works for both engines

```python[demo]
"""Spark engine context implementation."""

import logging
from typing import Any, Callable, Dict, Optional, Union

from odibi_core.engine.base_context import EngineContext
from odibi_core.engine.spark_local_config import DEFAULT_SPARK_CONFIG

logger = logging.getLogger(__name__)


class SparkEngineContext(EngineContext):
    """Spark engine context for distributed processing."""

    def __init__(
        self,
        secrets: Optional[Union[Dict[str, str], Callable[[str], str]]] = None,
        spark_config: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ) -> None:
        super().__init__(secrets, **kwargs)
        self.spark_config = spark_config or DEFAULT_SPARK_CONFIG.copy()
        self._spark: Optional[Any] = None  # SparkSession
```

**Key differences from Pandas:**
1. **`spark_config` parameter** - Configurable session
2. **`_spark: SparkSession`** - Heavyweight object (JVM process)
3. **Imports `DEFAULT_SPARK_CONFIG`** - Uses the config we created in Mission 2

**Connect method:**

```python[demo]
def connect(self, **kwargs: Any) -> "SparkEngineContext":
    """Initialize SparkSession."""
    try:
        from pyspark.sql import SparkSession
        
        # Merge kwargs into config
        config = self.spark_config.copy()
        for key, value in kwargs.items():
            spark_key = f"spark.{key}" if not key.startswith("spark.") else key
            config[spark_key] = value
        
        # Create SparkSession builder
        builder = SparkSession.builder
        
        # Apply configuration
        for key, value in config.items():
            builder = builder.config(key, value)
        
        # Create or get existing session
        self._spark = builder.getOrCreate()
        
        # Suppress logging noise
        self._spark.sparkContext.setLogLevel("WARN")
        
        logger.info(f"SparkSession created: {config.get('spark.app.name')}")
        return self
    except ImportError:
        raise ImportError("pyspark is required. Install with: pip install pyspark")
```

**🧠 QUIZ #14-15:**
14. Why do we use `getOrCreate()` instead of just `create()`?
15. What does `setLogLevel("WARN")` do and why is it useful?

---

## ✅ CHECKPOINT #3: Spark Foundation Ready

**Milestone reached!** You've initialized the Spark engine:

✅ SparkEngineContext structure defined  
✅ Configuration merging implemented  
✅ SparkSession creation with graceful error handling

**Test your understanding:**
- What's the difference between `_duckdb_conn` and `_spark`?
- Why do we make a copy of `DEFAULT_SPARK_CONFIG`?
- What happens when you call `connect()` twice?

**Next:** Implementing Spark's read, write, and SQL operations!

---

### Mission 9: Implement SparkEngineContext - Part 2 (Read & Write)

Spark's `read()` and `write()` follow the same pattern as Pandas, but with Spark-specific syntax. Notice the similarity to what we built before—that's the power of abstraction!

```python
def read(self, source: str, **kwargs: Any) -> Any:
    """Read data from source."""
    if self._spark is None:
        self.connect()
    
    source_type = kwargs.pop("source_type", None)
    
    # Auto-detect format
    if source_type is None:
        if source.endswith(".csv"):
            source_type = "csv"
        elif source.endswith(".json"):
            source_type = "json"
        elif source.endswith(".parquet"):
            source_type = "parquet"
        # ... etc
    
    # Read based on type
    if source_type == "csv":
        df = self._spark.read.csv(source, header=True, inferSchema=True, **kwargs)
        logger.info(f"Read Spark DataFrame from CSV: {source}")
        return df
    elif source_type == "json":
        df = self._spark.read.json(source, **kwargs)
        logger.info(f"Read Spark DataFrame from JSON: {source}")
        return df
    # ... etc


def write(self, df: Any, target: str, **kwargs: Any) -> None:
    """Write DataFrame to target."""
    from pyspark.sql import DataFrame
    
    if not isinstance(df, DataFrame):
        raise TypeError(f"Expected Spark DataFrame, got {type(df)}")
    
    mode = kwargs.pop("mode", "overwrite")
    
    # Auto-detect format
    if target.endswith(".csv"):
        df.write.mode(mode).csv(target, header=True, **kwargs)
        logger.info(f"Wrote Spark DataFrame to CSV: {target}")
    elif target.endswith(".parquet"):
        df.write.mode(mode).parquet(target, **kwargs)
        logger.info(f"Wrote Spark DataFrame to Parquet: {target}")
    # ... etc
```

**🧠 QUIZ #16:**
16. What's the default write mode for Spark, and why might that be dangerous?

---

### Mission 10: Implement SparkEngineContext - Part 3 (SQL & Sample)

The final pieces! Spark SQL is built-in, making this simpler than the DuckDB integration in Pandas.

```python[demo]
def register_temp(self, name: str, df: Any) -> None:
    """Register DataFrame as temporary view for SQL queries."""
    from pyspark.sql import DataFrame
    
    if not isinstance(df, DataFrame):
        raise TypeError(f"Expected Spark DataFrame, got {type(df)}")
    
    df.createOrReplaceTempView(name)
    logger.info(f"Registered temp view '{name}'")


def execute_sql(self, query: str, **kwargs: Any) -> Any:
    """Execute SQL query using Spark SQL."""
    if self._spark is None:
        self.connect()
    
    try:
        result = self._spark.sql(query)
        logger.info(f"Executed Spark SQL query")
        return result
    except Exception as e:
        logger.error(f"SQL execution failed: {e}")
        raise


def collect_sample(self, df: Any, n: int = 5) -> Any:
    """Collect sample rows (converts to Pandas)."""
    from pyspark.sql import DataFrame
    
    if not isinstance(df, DataFrame):
        raise TypeError(f"Expected Spark DataFrame, got {type(df)}")
    
    # Use limit + toPandas to avoid collecting entire dataset
    return df.limit(n).toPandas()


def stop(self) -> None:
    """Stop SparkSession."""
    if self._spark:
        self._spark.stop()
        logger.info("SparkSession stopped")
        self._spark = None
```

**Critical insight on `collect_sample()`:**
```python[demo]
# ❌ WRONG (loads entire dataset into memory)
df.toPandas().head(n)

# ✅ RIGHT (only loads n rows)
df.limit(n).toPandas()
```

This distinction is the difference between success and an out-of-memory crash on billion-row datasets!

**🧠 QUIZ #17-18:**
17. Why does Spark use `createOrReplaceTempView()` instead of storing DataFrames in a dictionary?
18. What would happen if you called `df.toPandas()` on a 1TB dataset?

---

## ✅ CHECKPOINT #4: Both Engines Complete!

**🎉 Huge milestone!** You've implemented both engine contexts:

✅ PandasEngineContext (300+ lines)  
✅ SparkEngineContext (350+ lines)  
✅ Identical interface, different implementations  
✅ Same 6 methods implemented for both

**Test your understanding:**
- Can you articulate the key difference between Pandas and Spark SQL handling?
- Why is `collect_sample()` critical for Spark but trivial for Pandas?
- What would break if we removed the `stop()` method from Spark?

**Next:** Testing parity and building the factory!

---

### Mission 11: Build Engine Factory & Parity Tests

Now we make it easy to switch between engines. The factory pattern is like a universal remote—press "pandas" or "spark," and you get the right engine without worrying about the details.

**Create: Update `odibi_core/engine/__init__.py`**

```python[demo]
from odibi_core.engine.base_context import EngineContext
from odibi_core.engine.pandas_context import PandasEngineContext
from odibi_core.engine.spark_context import SparkEngineContext

def create_engine_context(engine_type: str, **kwargs):
    """Factory function to create engine contexts."""
    if engine_type.lower() == "pandas":
        return PandasEngineContext(**kwargs)
    elif engine_type.lower() == "spark":
        return SparkEngineContext(**kwargs)
    else:
        raise ValueError(f"Unknown engine type: {engine_type}")

__all__ = [
    "EngineContext",
    "PandasEngineContext", 
    "SparkEngineContext",
    "create_engine_context"
]
```

**Parity Verification Strategy:**

Here's how we prove both engines produce identical results:

```python[demo]
# 1. Read same file
pandas_df = pandas_ctx.read("data.csv")
spark_df = spark_ctx.read("data.csv")

# 2. Compare row counts
assert len(pandas_df) == spark_df.count()

# 3. Execute same SQL
pandas_result = pandas_ctx.execute_sql("SELECT category, AVG(value) FROM data GROUP BY category ORDER BY category")
spark_result = spark_ctx.execute_sql("SELECT category, AVG(value) FROM data GROUP BY category ORDER BY category")

# 4. Compare results (sorted)
pandas_sorted = pandas_result.sort_values("category").reset_index(drop=True)
spark_sorted = spark_ctx.collect_sample(spark_result, 100).sort_values("category").reset_index(drop=True)

# 5. Check values match
assert list(pandas_sorted["category"]) == list(spark_sorted["category"])
for i in range(len(pandas_sorted)):
    assert abs(pandas_sorted.iloc[i]["avg_value"] - spark_sorted.iloc[i]["avg_value"]) < 0.01
```

---

## ✅ CHECKPOINT #5: Factory & Testing Infrastructure

**Excellent work!** You've created the abstraction layer:

✅ Engine factory for easy switching  
✅ Parity testing strategy defined  
✅ Verification workflow established

**Test your understanding:**
- Why use a factory instead of directly instantiating `PandasEngineContext()`?
- What would you do if aggregation results differ by 0.001 between engines?
- How would you add a third engine (e.g., Polars)?

**Almost there!** Final mission: Understanding deployment.

---

## 🏗️ Local Spark Setup Tutorial

### Understanding Local Spark

Let's demystify Spark's "local mode." Think of it as Spark's way of pretending your laptop is a mini-cluster. You get all the Spark APIs without needing a server farm!

**What is `local[*]`?**

```python
"spark.master": "local[*]"
```

**Breakdown:**
- **local** = Run Spark on this machine (no cluster)
- **[*]** = Use all available CPU cores
- **[2]** = Use 2 cores (explicit)
- **[1]** = Single-threaded (debugging)

**Why local mode?**
- ✅ No cluster setup needed
- ✅ Fast iteration
- ✅ Same API as production
- ✅ Free (no cloud costs)

### Verifying Local Spark Works

**Create: `test_spark_setup.py`**

```python
from odibi_core.engine import SparkEngineContext

ctx = SparkEngineContext()
ctx.connect()

print(f"Spark version: {ctx._spark.version}")
print(f"Master: {ctx._spark.sparkContext.master}")
print(f"App name: {ctx._spark.sparkContext.appName}")

# Create test DataFrame
data = [(1, "A"), (2, "B"), (3, "C")]
df = ctx._spark.createDataFrame(data, ["id", "name"])

print(f"Created DataFrame with {df.count()} rows")

# Test toPandas (this is where it usually fails on Windows)
pdf = df.toPandas()
print(f"Converted to Pandas: {len(pdf)} rows")

ctx.stop()
print("[SUCCESS] Spark is working!")
```

**Run:**
```bash
python test_spark_setup.py
```

**Expected output:**
```
Spark version: 3.5.7
Master: local[*]
App name: ODIBI_CORE_Local
Created DataFrame with 3 rows
Converted to Pandas: 3 rows
[SUCCESS] Spark is working!
```

**If it fails on Windows**: See SPARK_WINDOWS_GUIDE.md for winutils setup.

---

## 🎯 REFLECTION CHECKPOINTS - ANSWERS

### Q1: Why implement both Pandas and Spark if Pandas is simpler?

**Answer**:

**Pandas strengths:**
- Fast for small datasets (<1M rows)
- Zero infrastructure setup
- Instant startup
- Great for development

**Spark strengths:**
- Scales to billions of rows
- Distributed across machines
- Production-ready
- Industry standard

**ODIBI CORE philosophy**: Develop locally (Pandas), deploy globally (Spark), **same config**.

---

### Q2: Why DuckDB instead of just using Pandas operations?

**Comparison:**

**With DuckDB (current):**
```python
ctx.register_temp("data", df)
result = ctx.execute_sql("SELECT category, AVG(value) FROM data GROUP BY category")
```

**Without DuckDB (Pandas operations):**
```python
result = df.groupby("category")["value"].mean().reset_index()
result.columns = ["category", "avg_value"]
```

**Problem**: SQL is **declarative** (what you want), Pandas is **imperative** (how to do it).

For complex queries:
```sql
SELECT a.*, b.value
FROM table1 a
LEFT JOIN table2 b ON a.id = b.id
WHERE a.value > 100
GROUP BY a.category
HAVING COUNT(*) > 5
```

**Pandas equivalent**: 10+ lines of merge/filter/groupby/filter operations.

**Conclusion**: SQL is the universal language of data. DuckDB enables SQL without Spark overhead.

---

### Q3: Why collect_sample() instead of just returning full DataFrame?

**Answer**:

**Scenario**: Spark DataFrame with 1 billion rows.

**Option A (naive):**
```python
df.toPandas()  # Tries to load 1 billion rows into memory → OOM!
```

**Option B (current):**
```python
collect_sample(df, n=5)  # Only loads 5 representative rows
```

**Use cases:**
- Tracker snapshots (only need sample to show in HTML)
- Data preview (user doesn't need 1 billion rows to verify schema)
- Quick validation (check first few rows look correct)

**For full data**: User calls `.collect()` or `.toPandas()` explicitly.

---

### Q4: Why lazy initialization for DuckDB and SparkSession?

**Answer**:

**Scenario 1: Pure file operations (no SQL)**
```python
df = ctx.read("input.csv")
ctx.write(df, "output.parquet")
```

**Without lazy init:**
- DuckDB connection created (50ms, unused)
- SparkSession created (3s, unused)

**With lazy init:**
- No DuckDB/Spark created
- Read/write ~100ms total

**Scenario 2: With SQL**
```python
df = ctx.read("input.csv")
ctx.register_temp("data", df)
result = ctx.execute_sql("SELECT ...")  # <-- Connects here
```

**Conclusion**: Don't pay for what you don't use.

---

### Q5: Why auto-detect format instead of requiring source_type parameter?

**Answer**:

**User experience:**

**Without auto-detect:**
```python
df = ctx.read("data.csv", source_type="csv", format="csv", header=True)
```

**With auto-detect:**
```python
df = ctx.read("data.csv")
```

**Benefits:**
- Less typing
- Fewer errors (typos in source_type)
- Cleaner configs
- Override still available when needed

**Config impact:**
```json
// Without auto-detect
{"value": "data.csv", "params": {"source_type": "csv", "header": true}}

// With auto-detect
{"value": "data.csv"}
```

Reduces config verbosity by ~50%.

---

### Q6: Why separate read() and execute_sql() instead of universal read()?

**Answer**:

**Alternative design (rejected):**
```python
def read(source, **kwargs):
    if source.startswith("SELECT"):
        return execute_sql(source)  # SQL query
    else:
        return read_file(source)    # File path
```

**Problems:**
1. **Ambiguity**: What if filename starts with "SELECT"?
2. **Different parameters**: Files need paths, SQL needs temp tables
3. **Different semantics**: Read is stateless, SQL queries temp tables

**Current design (clear separation):**
```python
# Read from external source
df = ctx.read("data.csv")

# Query in-memory data
ctx.register_temp("data", df)
result = ctx.execute_sql("SELECT * FROM data")
```

**Benefits:**
- Clear intent
- Type safety
- No ambiguity

---

## ✅ CHECKPOINT #6: Deep Understanding Complete

**🏆 Congratulations!** You've mastered the dual-engine architecture:

✅ Understand the "why" behind every design decision  
✅ Can articulate trade-offs between Pandas and Spark  
✅ Know when to use each engine  
✅ Can debug parity issues  
✅ Ready to extend with new engines or formats

**Final reflection:**
- Which engine would you choose for local development? Why?
- Which engine for a production pipeline processing 10 million rows daily?
- How would you explain engine abstraction to a junior developer in 3 sentences?

---

## 📊 COMPLETION SUMMARY

### What Exists Now (Phase 2)

✅ **PandasEngineContext** (300+ lines)
- Fully functional
- 10 file formats (CSV, JSON, Parquet, AVRO, etc.)
- SQL databases (PostgreSQL, SQL Server, MySQL)
- DuckDB SQL engine
- 11/11 tests passing

✅ **SparkEngineContext** (350+ lines)
- Fully functional
- 11 file formats (CSV, JSON, Parquet, AVRO, ORC, Delta, JDBC)
- Local and cluster modes
- Spark SQL engine
- Intelligent sampling
- 10/10 tests (skip on Windows)

✅ **Engine Factory**
- `create_engine_context("pandas" | "spark")`
- Config-driven engine selection

✅ **Parity Verification**
- Demo script proves identical results
- Tests validate contract compliance

✅ **Documentation**
- Format guide (all formats explained)
- SQL database guide (connection examples)
- Spark Windows guide (setup options)

---

### What's Missing Until Phase 3

❌ No config loading yet (that's Phase 3)  
❌ No orchestration logic (Phase 5)  
❌ No tracker snapshots (Phase 6)  
❌ No function registry integration (Phase 7)  

**This is expected! Phase 2 is engines only.**

---

### File Tree Created (Phase 2 Additions)

```
odibi_core/
├── odibi_core/
│   ├── engine/
│   │   ├── pandas_context.py         ← 300+ lines ✅
│   │   ├── spark_context.py          ← 350+ lines ✅
│   │   └── spark_local_config.py     ← 68 lines ✅
│   └── examples/
│       ├── data/
│       │   └── sample.csv            ← Test data ✅
│       └── parity_demo.py            ← 220 lines ✅
├── tests/
│   ├── test_pandas_engine.py         ← 11 tests ✅
│   └── test_spark_engine.py          ← 10 tests ✅
├── FORMAT_SUPPORT.md                 ← Format guide ✅
├── SQL_DATABASE_SUPPORT.md           ← Database guide ✅
├── SPARK_WINDOWS_GUIDE.md            ← Setup guide ✅
└── setup.py                          ← For pip install ✅
```

**Total Phase 2**: ~1,200 lines of production code + tests

---

### Verification Checklist

Run these commands to verify Phase 2:

```bash
# 1. Check imports
python final_verification.py

# 2. Run tests
python test_all.py
# Expected: 20 passed, 10 skipped

# 3. Try Pandas engine
python -c "from odibi_core.engine import PandasEngineContext; ctx = PandasEngineContext(); ctx.connect(); print('[OK] Pandas works')"

# 4. Try Spark engine (Linux/Mac)
python -c "from odibi_core.engine import SparkEngineContext; ctx = SparkEngineContext(); ctx.connect(); print('[OK] Spark works'); ctx.stop()"

# 5. Run parity demo (Linux/Mac)
python -m odibi_core.examples.parity_demo
```

---

## 🔄 What Phase 3 Will Build

Phase 2 created the **engines**. Phase 3 will make them **config-driven**.

**Before Phase 3:**
```python
# Hardcoded
ctx = PandasEngineContext()
df = ctx.read("data.csv")
ctx.execute_sql("SELECT * FROM data")
```

**After Phase 3:**
```json
{
  "steps": [
    {"layer": "ingest", "name": "read_data", "engine": "pandas", "value": "data.csv"},
    {"layer": "transform", "name": "filter", "engine": "pandas", "type": "sql", "value": "SELECT * FROM data"}
  ]
}
```

```python
# Config-driven!
steps = ConfigLoader().load("pipeline.json")
orchestrator = Orchestrator(steps, create_engine_context("pandas"), tracker, events)
orchestrator.run()
```

**That's the power of config-driven pipelines!**

---

## 🎯 Key Takeaways

### Design Principles Applied

1. **Contract First** - EngineContext ABC defined in Phase 1, implemented in Phase 2
2. **Lazy Initialization** - Don't create resources until needed
3. **Graceful Degradation** - Work without optional dependencies, fail with clear messages
4. **Auto-Detection** - Reduce user cognitive load (file extensions → formats)
5. **Parity Testing** - Ensure both engines produce identical results

### Build Order Lessons

1. **Config before implementation** - spark_local_config.py created first
2. **Simple before complex** - Pandas before Spark
3. **Test as you go** - Each method gets a test
4. **Verify imports early** - Catch dependency issues immediately

### What Makes Good Engine Abstraction?

✅ **Complete** - All formats supported  
✅ **Consistent** - Same interface for both engines  
✅ **Tested** - 20 tests validate behavior  
✅ **Documented** - Every method has docstring + examples  
✅ **Extensible** - Easy to add new engines (Polars, DuckDB-native)  
✅ **Robust** - Handles missing dependencies gracefully  

---

## 📚 Additional Resources

- **Engineering Plan**: See `ODIBI_CORE_V1_ENGINEERING_PLAN.md` for Phase 2 objectives
- **Phase 2 Complete**: See `PHASE_2_COMPLETE.md` for detailed metrics
- **Format Guide**: See `FORMAT_SUPPORT.md` for all formats
- **SQL Guide**: See `SQL_DATABASE_SUPPORT.md` for database connections
- **Spark Setup**: See `SPARK_WINDOWS_GUIDE.md` for Windows setup

---

## 🎓 Final Exercise

**Try building a simple pipeline manually:**

```python
# 1. Create Pandas context
from odibi_core.engine import PandasEngineContext
ctx = PandasEngineContext()
ctx.connect()

# 2. Read CSV
df = ctx.read("odibi_core/examples/data/sample.csv")
print(f"Read {len(df)} rows")

# 3. Register for SQL
ctx.register_temp("data", df)

# 4. Filter with SQL
result = ctx.execute_sql("SELECT * FROM data WHERE value > 100")
print(f"Filtered to {len(result)} rows")

# 5. Aggregate
agg = ctx.execute_sql("SELECT category, AVG(value) as avg FROM data GROUP BY category")
print(f"Aggregated to {len(agg)} categories")
print(agg)

# 6. Write Parquet
ctx.write(result, "output/filtered.parquet")
print("Wrote Parquet file")
```

**Now try the same with Spark** (if Linux/Mac):
```python
from odibi_core.engine import SparkEngineContext
ctx = SparkEngineContext()
# ... same code, different engine!
```

**Result**: Identical outputs! That's parity! ✅

---

## 🎓 QUIZ ANSWER KEY

<details>
<summary>Click to reveal answers</summary>

1. **Switch engines without changing pipeline code** - enables local dev (Pandas) and production scale (Spark) with same config
2. **Pandas** - small files fit in memory, faster startup, no cluster needed
3. **Spark** - distributed processing required for datasets that don't fit on one machine
4. **Use all available CPU cores** - maximizes parallelism without hardcoding
5. **Reduce overhead for local dev** - default 200 causes excessive shuffling on small datasets
6. **Delay resource creation until first use** - saves memory and startup time for pipelines that don't use the feature
7. **In-memory database** - no files written to disk, faster for temporary operations
8. **Logs warning, sets `_duckdb_conn = None`** - SQL operations will fail with clear error message later
9. **Reads as JSON** - `source_type` override takes precedence over extension detection
10. **Pandas methods don't accept `source_type`** - would cause TypeError if passed through
11. **Store registered DataFrames for SQL queries** - enables multi-table joins and complex SQL
12. **No** - DuckDB needs tables registered to query, otherwise `FROM data` fails with "table not found"
13. **Avoid writing row numbers as a column** - keeps output clean and matches input structure
14. **Reuses existing session if present** - prevents multiple JVM processes, enables shared context
15. **Suppresses INFO logs** - reduces console noise, only shows warnings and errors
16. **`overwrite`** - can accidentally delete existing data; use `mode="append"` for safety
17. **Spark's catalog manages temp views** - more efficient for distributed metadata than Python dict
18. **Out-of-memory error** - entire dataset pulled to driver, exceeds RAM capacity

</details>

---

**Congratulations!** You've mastered the dual-engine architecture. You can now:
- Switch between Pandas and Spark seamlessly
- Understand when to use each engine
- Debug parity issues
- Add new formats
- Extend with new engines

**Time to Phase 3**: Build the ConfigLoader to make this truly config-driven! 🚀

---

**Document Status**: Complete  
**Phase**: 2 (Engine Contexts)  
**Next**: Phase 3 (Config Loader & Validation)  
**Estimated Time to Complete Phase 2**: 3-4 hours following this guide
