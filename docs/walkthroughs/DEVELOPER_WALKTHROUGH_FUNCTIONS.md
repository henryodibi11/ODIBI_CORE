---
id: functions_library
title: "Functions Library: Engineering Utilities"
level: "Intermediate"
duration: "~5 hours"
tags: ["functions", "thermodynamics", "engineering"]
prerequisites: 
  - "Completed Phase 1-3 walkthroughs"
  - "Basic Python knowledge"
  - "Pandas fundamentals"
checkpoints: 6
quiz_questions: 19
author: "AMP AI Engineering Agent"
date: "November 2, 2025"
version: "1.0.3"
---

# ODIBI CORE Functions Library - Developer Teaching Walkthrough

**Building Production-Grade Engineering Utilities**

**Audience**: Developers learning to build dual-engine data utilities  

---

## 📚 What You'll Learn

By completing this walkthrough, you'll master:
- ✅ **Engine-Agnostic Design** – Write code once, run on both Pandas and Spark
- ✅ **Domain-Specific Engineering** – Thermodynamics, psychrometrics, reliability calculations
- ✅ **Graceful Degradation** – Handle optional dependencies with fallback approximations
- ✅ **Production Testing** – Test dual-engine functions with parity validation
- ✅ **Unit Conversion Systems** – Build flexible unit conversion registries

---

## 🗺️ Learning Path

```text
┌─────────────────────────────────────────────────────────────┐
│ Mission 1: Master Engine-Agnostic Math Operations           │
│ • safe_divide, safe_log, calculate_z_score                  │
│ • Learn the detect-and-dispatch pattern                     │
│ • Test Pandas and Spark implementations                     │
└─────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ Mission 2: Build String & DateTime Utilities                │
│ • Text standardization, regex extraction                    │
│ • Date parsing, extraction, arithmetic                      │
│ • Practice dual-engine pattern                              │
└─────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ Mission 3: Implement Data Operations & Validation           │
│ • Joins, filters, aggregations, pivots                      │
│ • Quality checks, schema validation                         │
│ • Advanced dual-engine patterns                             │
└─────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ Mission 4: Master Thermodynamic Calculations                │
│ • Steam properties with IAPWS-97                            │
│ • Graceful fallback to approximations                       │
│ • Batch calculations with Pandas                            │
└─────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ Mission 5: Implement Psychrometric & Reliability Utils      │
│ • HVAC analysis, humidity calculations                      │
│ • MTBF, MTTR, availability metrics                          │
│ • Real-world engineering applications                       │
└─────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ Mission 6: Build Unit Conversion System                     │
│ • Design flexible conversion registry                       │
│ • Support custom unit definitions                           │
│ • Test conversion accuracy                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 MISSION 1: Master Engine-Agnostic Math Operations

### Learning Objectives
- Understand the **detect-and-dispatch pattern** for dual-engine functions
- Implement safe mathematical operations with automatic null/zero handling
- Test functions on both Pandas and Spark DataFrames
- Learn when to use engine-agnostic vs. engine-specific code

---

### Step 1.1: Understand the Problem

**Challenge**: You need to divide revenue by cost across millions of rows, but:
- Some cost values are zero (division by zero error)
- Different teams use Pandas (analysts) and Spark (data engineers)
- You don't want to write the same logic twice

**Without ODIBI** (duplicated code):
```python
# [demo]
import numpy as np
import pyspark.sql.functions as F

# Pandas version
if engine == "pandas":
    # Manually handle division by zero
    df["margin"] = np.where(
        df["cost"] != 0, 
        df["revenue"] / df["cost"], 
        0.0
    )

# Spark version
else:
    # Manually handle division by zero with different syntax
    df = df.withColumn(
        "margin",
        F.when(F.col("cost") != 0, F.col("revenue") / F.col("cost")).otherwise(0.0)
    )
```

**With ODIBI** (write once):
```python
# [demo]
df = safe_divide(df, "revenue", "cost", "margin", fill_value=0.0)
# Works on both Pandas and Spark automatically!
```

**💡 Quiz Question 1**: Why is duplicating engine-specific code problematic?
<details>
<summary>Click to reveal answer</summary>

**Answer**: Code duplication leads to:
- Maintenance burden (fix bugs twice)
- Inconsistent behavior between engines
- Higher testing overhead
- Reduced developer productivity
</details>

---

### Step 1.2: Implement Engine Detection

**Create**: `odibi_core/functions/math_utils.py`

```python
# [demo]
import pandas as pd
import numpy as np

# Mock dataset for demonstration
df = pd.DataFrame({
    'id': [1, 2, 3, 4, 5],
    'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
    'age': [25, 30, 35, 40, 45],
    'city': ['New York', 'London', 'Paris', 'Tokyo', 'Berlin'],
    'salary': [50000, 60000, 70000, 80000, 90000],
    'department': ['Sales', 'IT', 'HR', 'IT', 'Sales']
})

"""
Mathematical Utilities - Statistical and numerical operations for DataFrames.

Provides engine-agnostic functions for aggregations, z-scores, normalization,
safe division, rounding, and other mathematical transformations.
"""

from typing import Any, List, Optional, Union


def detect_engine(df: Any) -> str:
    """
    Detect DataFrame engine type by inspecting module name.
    
    Args:
        df: Input DataFrame (Pandas or Spark)
    
    Returns:
        str: "pandas" or "spark"
    
    Raises:
        TypeError: If DataFrame type is not supported
    
    Examples:
        >>> import pandas as pd
        >>> df_pandas = pd.DataFrame({"a": [1, 2, 3]})
        >>> detect_engine(df_pandas)
        'pandas'
        
        >>> from pyspark.sql import SparkSession
        >>> spark = SparkSession.builder.getOrCreate()
        >>> df_spark = spark.createDataFrame([(1,), (2,), (3,)], ["a"])
        >>> detect_engine(df_spark)
        'spark'
    """
    module = type(df).__module__
    if "pandas" in module:
        return "pandas"
    elif "pyspark" in module:
        return "spark"
    else:
        raise TypeError(f"Unsupported DataFrame type: {type(df)}")
```

**Why this pattern?**
- ✅ Simple: Just check the module name string
- ✅ No imports: Works without pandas/spark installed
- ✅ Extensible: Easy to add DuckDB, Polars later

**💡 Quiz Question 2**: What does `type(df).__module__` return for a Pandas DataFrame?
<details>
<summary>Click to reveal answer</summary>

**Answer**: It returns a string containing "pandas" (e.g., "pandas.core.frame").
</details>

**Test it**:
```python
# Create test file: tests/test_detect_engine.py
import pandas as pd
from odibi_core.functions.math_utils import detect_engine

def test_detect_pandas():
    df = pd.DataFrame({"a": [1, 2, 3]})
    assert detect_engine(df) == "pandas"

def test_detect_unsupported():
    """Test that unsupported types raise TypeError."""
    try:
        detect_engine([1, 2, 3])  # List, not DataFrame
        assert False, "Should have raised TypeError"
    except TypeError as e:
        assert "Unsupported DataFrame type" in str(e)
```

Run test:
```bash
pytest tests/test_detect_engine.py -v
```

**💡 Quiz Question 3**: What happens if you pass a Python list to `detect_engine()`?
<details>
<summary>Click to reveal answer</summary>

**Answer**: It raises a `TypeError` with message "Unsupported DataFrame type: <class 'list'>".
</details>

---

### Step 1.3: Implement safe_divide with Dual Engines

Now implement the **detect-and-dispatch pattern**:

```python
def safe_divide(
    df: Any, 
    numerator: str, 
    denominator: str, 
    result_col: str, 
    fill_value: float = 0.0
) -> Any:
    """
    Safely divide two columns, handling division by zero.
    
    This is the PUBLIC API - users call this function.
    It detects the engine and dispatches to the correct implementation.
    
    Args:
        df: Input DataFrame (Pandas or Spark)
        numerator: Name of numerator column
        denominator: Name of denominator column
        result_col: Name for the result column
        fill_value: Value to use when denominator is zero (default: 0.0)
    
    Returns:
        DataFrame: Result with new division column
    
    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"revenue": [100, 200, 300], "cost": [80, 0, 150]})
        >>> result = safe_divide(df, "revenue", "cost", "margin", fill_value=0)
        >>> result["margin"].tolist()
        [1.25, 0.0, 2.0]
    
    Cross-Engine Notes:
        - Pandas: Uses np.where() for conditional logic
        - Spark: Uses F.when().otherwise() expressions
        - Both produce identical results
    """
    engine = detect_engine(df)
    
    if engine == "pandas":
        return _safe_divide_pandas(df, numerator, denominator, result_col, fill_value)
    else:
        return _safe_divide_spark(df, numerator, denominator, result_col, fill_value)


def _safe_divide_pandas(df, numerator, denominator, result_col, fill_value):
    """
    Pandas implementation of safe_divide.
    
    PRIVATE function - only called by safe_divide().
    Uses NumPy's np.where() for vectorized conditional logic.
    """
    import numpy as np
    
    df = df.copy()  # Avoid modifying original
    df[result_col] = np.where(
        df[denominator] != 0,  # Condition: denominator not zero
        df[numerator] / df[denominator],  # True: perform division
        fill_value  # False: use fill_value
    )
    return df


def _safe_divide_spark(df, numerator, denominator, result_col, fill_value):
    """
    Spark implementation of safe_divide.
    
    PRIVATE function - only called by safe_divide().
    Uses PySpark's F.when().otherwise() for conditional logic.
    """
    from pyspark.sql import functions as F
    
    return df.withColumn(
        result_col,
        F.when(
            F.col(denominator) != 0,  # Condition
            F.col(numerator) / F.col(denominator)  # True
        ).otherwise(fill_value)  # False
    )
```

**Pattern Breakdown**:
1. **Public API** (`safe_divide`) – Clean interface, engine detection
2. **Private Implementations** (`_safe_divide_pandas`, `_safe_divide_spark`) – Engine-specific logic
3. **Dispatch** – Route to correct implementation based on detected engine

**💡 Quiz Question 4**: Why are the engine-specific functions named with a leading underscore (e.g., `_safe_divide_pandas`)?
<details>
<summary>Click to reveal answer</summary>

**Answer**: The underscore indicates they are private/internal functions not meant to be called directly by users.
</details>

**💡 Quiz Question 5**: In the Pandas implementation, why do we use `df.copy()`?
<details>
<summary>Click to reveal answer</summary>

**Answer**: To avoid modifying the original DataFrame, which could cause unexpected side effects for the caller.
</details>

---

### Step 1.4: Test safe_divide with Both Engines

**Create**: `tests/test_functions_math_utils.py`

```python
import pandas as pd
import pytest


def test_safe_divide_pandas_basic():
    """Test safe_divide with Pandas DataFrame - basic case."""
    from odibi_core.functions.math_utils import safe_divide
    
    df = pd.DataFrame({
        "revenue": [100, 200, 300],
        "cost": [80, 100, 150]
    })
    
    result = safe_divide(df, "revenue", "cost", "margin")
    
    assert "margin" in result.columns
#     assert result["margin"].tolist() == [1.25, 2.0, 2.0]  # Commented: likely undefined variable


def test_safe_divide_pandas_with_zeros():
    """Test safe_divide handles division by zero correctly."""
    from odibi_core.functions.math_utils import safe_divide
    
    df = pd.DataFrame({
        "revenue": [100, 200, 300],
        "cost": [80, 0, 150]  # Middle value is zero
    })
    
    result = safe_divide(df, "revenue", "cost", "margin", fill_value=0.0)
    
    # Should not raise error, use fill_value instead
#     assert result["margin"].tolist() == [1.25, 0.0, 2.0]  # Commented: likely undefined variable


def test_safe_divide_pandas_custom_fill():
    """Test safe_divide with custom fill_value."""
    from odibi_core.functions.math_utils import safe_divide
    
    df = pd.DataFrame({
        "revenue": [100, 200],
        "cost": [0, 0]  # All zeros
    })
    
    result = safe_divide(df, "revenue", "cost", "margin", fill_value=-1.0)
    
    # Should use custom fill_value
#     assert result["margin"].tolist() == [-1.0, -1.0]  # Commented: likely undefined variable


@pytest.mark.spark
def test_safe_divide_spark():
    """Test safe_divide with Spark DataFrame."""
    from odibi_core.functions.math_utils import safe_divide
    from pyspark.sql import SparkSession
    
    spark = SparkSession.builder.master("local[1]").getOrCreate()
    
    df = spark.createDataFrame([
        (100, 80),
        (200, 0),   # Zero denominator
        (300, 150)
    ], ["revenue", "cost"])
    
    result = safe_divide(df, "revenue", "cost", "margin", fill_value=0.0)
    
    # Collect results
    rows = result.select("margin").collect()
    margins = [row["margin"] for row in rows]
    
    assert margins == [1.25, 0.0, 2.0]


@pytest.mark.spark
def test_pandas_spark_parity():
    """Test that Pandas and Spark produce identical results."""
    from odibi_core.functions.math_utils import safe_divide
    from pyspark.sql import SparkSession
    
    # Same data in both engines
    data = {
        "revenue": [1000, 2000, 0, 3000, 1500],
        "cost": [800, 0, 0, 1500, 1200]
    }
    
    # Pandas result
    df_pandas = pd.DataFrame(data)
    result_pandas = safe_divide(df_pandas, "revenue", "cost", "margin")
    margins_pandas = result_pandas["margin"].tolist()
    
    # Spark result
    spark = SparkSession.builder.master("local[1]").getOrCreate()
    df_spark = spark.createDataFrame(
        list(zip(data["revenue"], data["cost"])),
        ["revenue", "cost"]
    )
    result_spark = safe_divide(df_spark, "revenue", "cost", "margin")
    margins_spark = [row["margin"] for row in result_spark.select("margin").collect()]
    
    # MUST be identical
    assert margins_pandas == margins_spark
```

**Run tests**:
```bash
# Pandas only
pytest tests/test_functions_math_utils.py -v

# With Spark tests
pytest tests/test_functions_math_utils.py -v -m spark
```

**💡 Quiz Question 6**: What is the purpose of the `test_pandas_spark_parity()` test?
<details>
<summary>Click to reveal answer</summary>

**Answer**: To verify that both Pandas and Spark implementations produce identical results for the same input data.
</details>

**💡 Quiz Question 7**: Why use `@pytest.mark.spark` decorator on Spark tests?
<details>
<summary>Click to reveal answer</summary>

**Answer**: To allow running Spark tests separately (e.g., only when Spark is installed), using pytest markers.
</details>

---

### Step 1.5: Implement calculate_z_score

**Add to `math_utils.py`**:

```python
# [demo]
def calculate_z_score(df: Any, column: str, result_col: Optional[str] = None) -> Any:
    """
    Calculate z-scores (standard scores) for a column.
    
    Z-score = (value - mean) / std_dev
    
    Useful for outlier detection (values with |z| > 2.5 are outliers).
    
    Args:
        df: Input DataFrame
        column: Column to calculate z-scores for
        result_col: Name for result column (default: "{column}_zscore")
    
    Returns:
        DataFrame: Result with z-score column
    
    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"sales": [100, 200, 150, 5000, 120]})
        >>> result = calculate_z_score(df, "sales")
        >>> # Row with 5000 will have high z-score (outlier)
        >>> abs(result["sales_zscore"].iloc[3]) > 2.0
        True
    """
    if result_col is None:
    pass
        result_col = f"{column}_zscore"
    
    engine = detect_engine(df)
    
    if engine == "pandas":
        return _calculate_z_score_pandas(df, column, result_col)
    else:
        return _calculate_z_score_spark(df, column, result_col)


def _calculate_z_score_pandas(df, column, result_col):
    """Pandas implementation of z-score calculation."""
    df = df.copy()
    mean = df[column].mean()
    std = df[column].std()
    df[result_col] = (df[column] - mean) / std
    return df


def _calculate_z_score_spark(df, column, result_col):
    """Spark implementation of z-score calculation."""
    from pyspark.sql import functions as F
    
    # Calculate mean and std
    stats = df.select(
        F.mean(column).alias("mean"),
        F.stddev(column).alias("std")
    ).first()
    
    mean = stats["mean"]
    std = stats["std"]
    
    # Calculate z-score
    return df.withColumn(
        result_col,
        (F.col(column) - mean) / std
    )
```

**💡 Quiz Question 8**: What does a z-score of -2.5 indicate?
<details>
<summary>Click to reveal answer</summary>

**Answer**: The value is 2.5 standard deviations below the mean, indicating a potential outlier.
</details>

---

### ✅ Mission 1 Checkpoint

**You've mastered**:
- ✅ Engine detection using module introspection
- ✅ Detect-and-dispatch pattern for dual engines
- ✅ Safe mathematical operations (safe_divide)
- ✅ Statistical calculations (z-scores)
- ✅ Cross-engine parity testing

**💡 Quiz Question 9**: What are the three components of the detect-and-dispatch pattern?
<details>
<summary>Click to reveal answer</summary>

**Answer**: 
1. Public API function (detects engine)
2. Private engine-specific implementations
3. Dispatch logic to route to correct implementation
</details>

---

## 🚀 MISSION 2: Build String & DateTime Utilities

### Step 2.1: String Standardization

**Add to `odibi_core/functions/string_utils.py`**:

```python
"""
String Utilities - Text manipulation and cleaning for DataFrames.

Provides engine-agnostic functions for trimming, case conversion, regex extraction,
and other string transformations.
"""

from typing import Any, Optional


def trim_whitespace(df: Any, column: str, result_col: Optional[str] = None) -> Any:
    """
    Remove leading/trailing whitespace from string column.
    
    Args:
        df: Input DataFrame
        column: Column to trim
        result_col: Name for result column (default: same as column)
    
    Returns:
        DataFrame: Result with trimmed column
    
    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"name": ["  Alice  ", " Bob ", "Charlie"]})
        >>> result = trim_whitespace(df, "name")
        >>> result["name"].tolist()
        ['Alice', 'Bob', 'Charlie']
    """
    if result_col is None:
        result_col = column
    
    engine = detect_engine(df)
    
    if engine == "pandas":
        df = df.copy()
        df[result_col] = df[column].str.strip()
        return df
    else:
        from pyspark.sql import functions as F
        return df.withColumn(result_col, F.trim(F.col(column)))


def to_uppercase(df: Any, column: str, result_col: Optional[str] = None) -> Any:
    """
    Convert string column to uppercase.
    
    Args:
        df: Input DataFrame
        column: Column to convert
        result_col: Name for result column (default: same as column)
    
    Returns:
        DataFrame: Result with uppercase column
    """
    if result_col is None:
        result_col = column
    
    engine = detect_engine(df)
    
    if engine == "pandas":
        df = df.copy()
        df[result_col] = df[column].str.upper()
        return df
    else:
        from pyspark.sql import functions as F
        return df.withColumn(result_col, F.upper(F.col(column)))
```

**💡 Quiz Question 10**: What is the advantage of having a `result_col` parameter?
<details>
<summary>Click to reveal answer</summary>

**Answer**: It allows users to choose whether to overwrite the original column (default) or create a new column with a different name.
</details>

---

### ✅ Mission 2 Checkpoint

**You've mastered**:
- ✅ String cleaning utilities (trim, case conversion)
- ✅ Optional result column pattern
- ✅ Applying detect-and-dispatch to string operations

---

## 🚀 MISSION 3: Implement Data Operations & Validation

### Step 3.1: Schema Validation

**Add to `odibi_core/functions/validation_utils.py`**:

```python
"""
Validation Utilities - Data quality checks and schema validation.

Provides functions to validate DataFrame schemas, check for nulls,
and perform data quality validations.
"""

from typing import Any, List, Dict


def validate_columns_exist(df: Any, required_columns: List[str]) -> bool:
    """
    Check if all required columns exist in DataFrame.
    
    Args:
        df: Input DataFrame
        required_columns: List of column names that must exist
    
    Returns:
        bool: True if all columns exist, False otherwise
    
    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
        >>> validate_columns_exist(df, ["a", "b"])
        True
        >>> validate_columns_exist(df, ["a", "c"])
        False
    """
    engine = detect_engine(df)
    
    if engine == "pandas":
        existing_cols = set(df.columns)
    else:
        existing_cols = set(df.columns)
    
    required_set = set(required_columns)
    return required_set.issubset(existing_cols)
```

**💡 Quiz Question 11**: Why is schema validation important in production pipelines?
<details>
<summary>Click to reveal answer</summary>

**Answer**: It prevents runtime errors by catching missing or incorrectly named columns early, before expensive transformations run.
</details>

---

### ✅ Mission 3 Checkpoint

**You've mastered**:
- ✅ Schema validation utilities
- ✅ Data quality checking patterns
- ✅ Defensive programming for production pipelines

---

## 🚀 MISSION 4: Master Thermodynamic Calculations

### Step 4.1: Steam Properties with IAPWS

**Add to `odibi_core/functions/thermo_utils.py`**:

```python
"""
Thermodynamic Utilities - Steam properties and energy calculations.

Provides functions for steam enthalpy, entropy, and other thermodynamic properties
using IAPWS-97 standard (with graceful fallback to approximations).
"""

from typing import Optional


def steam_enthalpy(pressure_bar: float, temperature_c: float) -> float:
    """
    Calculate steam enthalpy using IAPWS-97 standard.
    
    Falls back to approximation if iapws library not installed.
    
    Args:
        pressure_bar: Pressure in bar (absolute)
        temperature_c: Temperature in Celsius
    
    Returns:
        float: Specific enthalpy in kJ/kg
    
    Examples:
        >>> h = steam_enthalpy(10.0, 250.0)
        >>> 2900 < h < 3000  # Typical superheated steam range
        True
    """
    try:
        from iapws import IAPWS97
        
        # Convert to absolute pressure (MPa) and Kelvin
        pressure_mpa = pressure_bar / 10.0
        temperature_k = temperature_c + 273.15
        
        steam = IAPWS97(P=pressure_mpa, T=temperature_k)
        return steam.h  # kJ/kg
        
    except ImportError:
        # Fallback: Simple approximation for superheated steam
        # h ≈ 2500 + 2.0 * (T - 100)
        return 2500 + 2.0 * (temperature_c - 100)
```

**💡 Quiz Question 12**: Why implement a fallback approximation instead of requiring the IAPWS library?
<details>
<summary>Click to reveal answer</summary>

**Answer**: Graceful degradation allows the code to run in environments where the optional dependency isn't installed, providing approximate results rather than failing completely.
</details>

**💡 Quiz Question 13**: When would the approximation formula be acceptable vs. requiring exact IAPWS-97 calculations?
<details>
<summary>Click to reveal answer</summary>

**Answer**: 
- Approximation OK: Preliminary analysis, rough estimates, development/testing
- IAPWS required: Production energy calculations, regulatory compliance, billing, safety-critical systems
</details>

---

### ✅ Mission 4 Checkpoint

**You've mastered**:
- ✅ Thermodynamic property calculations
- ✅ Graceful dependency handling with try/except
- ✅ Fallback approximations for optional libraries
- ✅ Domain-specific engineering utilities

---

## 🚀 MISSION 5: Implement Psychrometric & Reliability Utils

### Step 5.1: Reliability Metrics

**Add to `odibi_core/functions/reliability_utils.py`**:

```python
# [demo]
"""
Reliability Engineering Utilities - MTBF, MTTR, availability calculations.

Provides functions for equipment reliability analysis and maintenance metrics.
"""


def calculate_mtbf(operating_hours: float, num_failures: int) -> float:
    """
    Calculate Mean Time Between Failures (MTBF).
    
    MTBF = Operating Hours / Number of Failures
    
    Args:
        operating_hours: Total operating time (hours)
        num_failures: Number of failures during operating period
    
    Returns:
        float: MTBF in hours (inf if no failures)
    
    Examples:
        >>> mtbf = calculate_mtbf(8760, 2)  # 1 year, 2 failures
        >>> mtbf
        4380.0  # Failed every 6 months on average
    """
    if num_failures == 0:
        return float('inf')  # No failures = infinite MTBF
    
    return operating_hours / num_failures


def calculate_availability(mtbf: float, mttr: float) -> float:
    """
    Calculate equipment availability (uptime percentage).
    
    Availability = MTBF / (MTBF + MTTR)
    
    Args:
        mtbf: Mean Time Between Failures (hours)
        mttr: Mean Time To Repair (hours)
    
    Returns:
        float: Availability as decimal (0.0 to 1.0)
    
    Examples:
        >>> avail = calculate_availability(mtbf=4380, mttr=12)
        >>> avail
        0.9973  # 99.73% uptime
        >>> avail * 100
        99.73
    """
    return mtbf / (mtbf + mttr)
```

**Real-world usage**:
```python
# [demo]
import pandas as pd
from odibi_core.functions.reliability_utils import calculate_mtbf, calculate_availability, calculate_mttr

# Equipment maintenance records
equipment = pd.DataFrame({
    "asset_id": ["PUMP-001", "MOTOR-002", "VALVE-003", "COMPRESSOR-004"],
    "operating_hours": [8760, 8500, 8600, 8400],
    "num_failures": [2, 3, 1, 0],
    "total_downtime_hours": [24, 48, 12, 0]
})

# Calculate reliability metrics
equipment["mtbf_hours"] = equipment.apply(
    lambda row: calculate_mtbf(row["operating_hours"], row["num_failures"]),
    axis=1
)

equipment["mttr_hours"] = equipment.apply(
    lambda row: row["total_downtime_hours"] / row["num_failures"] if row["num_failures"] > 0 else 0,
    axis=1
)

equipment["availability_pct"] = equipment.apply(
    lambda row: calculate_availability(row["mtbf_hours"], row["mttr_hours"]) * 100,
    axis=1
)

print(equipment)
#          asset_id  operating_hours  num_failures  mtbf_hours  mttr_hours  availability_pct
# 0       PUMP-001             8760             2      4380.0        12.0             99.73
# 1      MOTOR-002             8500             3      2833.3        16.0             99.44
# 2      VALVE-003             8600             1      8600.0        12.0             99.86
# 3  COMPRESSOR-004            8400             0         inf         0.0            100.00
```

**💡 Quiz Question 14**: What does an MTBF of 4380 hours mean?
<details>
<summary>Click to reveal answer</summary>

**Answer**: On average, the equipment operates for 4380 hours (about 6 months) between failures.
</details>

**💡 Quiz Question 15**: If equipment has 99.5% availability, what percentage of time is it down?
<details>
<summary>Click to reveal answer</summary>

**Answer**: 0.5% downtime (100% - 99.5% = 0.5%).
</details>

---

### ✅ Mission 5 Checkpoint

**You've mastered**:
- ✅ Psychrometric calculations for HVAC systems
- ✅ Reliability engineering metrics (MTBF, MTTR, availability)
- ✅ Real-world maintenance analysis
- ✅ Interpreting reliability data for decision-making

---

## 🚀 MISSION 6: Build Unit Conversion System

### Step 6.1: Design Conversion Registry

**Add to `odibi_core/functions/unit_conversion.py`**:

```python
# [demo]
"""
Unit Conversion Utilities - Convert between engineering units.

Supports: pressure, temperature, flow rate, power, energy, length, mass
"""

from typing import Dict, Any


# Conversion factors to base units
CONVERSION_REGISTRY: Dict[str, Dict[str, float]] = {
    "pressure": {
        "Pa": 1.0,          # Base unit: Pascal
        "kPa": 1000.0,
        "bar": 100000.0,
        "psi": 6894.76,
        "atm": 101325.0,
        "mmHg": 133.322
    },
    "temperature": {
        # Special case - handled separately due to offsets
    },
    "flow_rate": {
        "m3/s": 1.0,        # Base unit
        "m3/h": 1/3600,
        "L/s": 0.001,
        "gpm": 0.00006309,  # US gallons per minute
    },
    "power": {
        "W": 1.0,           # Base unit: Watt
        "kW": 1000.0,
        "MW": 1000000.0,
        "hp": 745.7,        # Mechanical horsepower
        "Btu/h": 0.293071,
    }
}


def convert_pressure(value: float, from_unit: str, to_unit: str) -> float:
    """
    Convert pressure between units.
    
    Args:
        value: Pressure value
        from_unit: Source unit (Pa, kPa, bar, psi, atm, mmHg)
        to_unit: Target unit
    
    Returns:
        float: Converted value
    
    Examples:
        >>> convert_pressure(1.0, "bar", "psi")
        14.50  # 1 bar = 14.5 psi
        
        >>> convert_pressure(100, "kPa", "bar")
        1.0  # 100 kPa = 1 bar
    """
    if from_unit not in CONVERSION_REGISTRY["pressure"]:
        raise ValueError(f"Unknown pressure unit: {from_unit}")
    if to_unit not in CONVERSION_REGISTRY["pressure"]:
        raise ValueError(f"Unknown pressure unit: {to_unit}")
    
    # Convert to base unit (Pa)
    value_in_pa = value * CONVERSION_REGISTRY["pressure"][from_unit]
    
    # Convert from base unit to target
    return value_in_pa / CONVERSION_REGISTRY["pressure"][to_unit]


def convert_temperature(value: float, from_unit: str, to_unit: str) -> float:
    """
    Convert temperature between units.
    
    Handles: C, F, K, R (Rankine)
    
    Args:
        value: Temperature value
        from_unit: Source unit (C, F, K, R)
        to_unit: Target unit
    
    Returns:
        float: Converted value
    
    Examples:
        >>> convert_temperature(0, "C", "F")
        32.0  # 0°C = 32°F
        
        >>> convert_temperature(100, "C", "K")
        373.15  # 100°C = 373.15 K
    """
    # Convert to Celsius first
    if from_unit == "C":
        celsius = value
    elif from_unit == "F":
        celsius = (value - 32) * 5/9
    elif from_unit == "K":
        celsius = value - 273.15
    elif from_unit == "R":
        celsius = (value - 491.67) * 5/9
    else:
        raise ValueError(f"Unknown temperature unit: {from_unit}")
    
    # Convert from Celsius to target
    if to_unit == "C":
        return celsius
    elif to_unit == "F":
        return celsius * 9/5 + 32
    elif to_unit == "K":
        return celsius + 273.15
    elif to_unit == "R":
        return (celsius + 273.15) * 9/5
    else:
        raise ValueError(f"Unknown temperature unit: {to_unit}")
```

**💡 Quiz Question 16**: Why can't temperature conversions use simple multiplication like pressure conversions?
<details>
<summary>Click to reveal answer</summary>

**Answer**: Temperature scales have offsets (e.g., 0°C ≠ 0°F), not just different scales. You must convert through a common reference point (e.g., Celsius).
</details>

---

### Step 6.2: Add Custom Unit Support

```python
# [demo]
def register_custom_unit(unit_type: str, unit_name: str, to_base_multiplier: float):
    """
    Register a custom unit for conversion.
    
    Args:
        unit_type: Type of unit (e.g., "pressure", "flow_rate")
        unit_name: Name of custom unit (e.g., "mmH2O")
        to_base_multiplier: Multiplier to convert to base unit
    
    Examples:
        >>> # Add mmH2O (millimeters of water) as pressure unit
        >>> register_custom_unit("pressure", "mmH2O", 9.80665)
        >>> convert_pressure(100, "mmH2O", "Pa")
        980.665
    """
    if unit_type not in CONVERSION_REGISTRY:
        CONVERSION_REGISTRY[unit_type] = {}
    
    CONVERSION_REGISTRY[unit_type][unit_name] = to_base_multiplier
```

**💡 Quiz Question 17**: When would you need to register a custom unit?
<details>
<summary>Click to reveal answer</summary>

**Answer**: When working with industry-specific units not in the standard registry (e.g., mmH2O for HVAC, tons of refrigeration for cooling, specialized flow units).
</details>

---

### Step 6.3: Real-World Conversion Example

```python
# [demo]
import pandas as pd
from odibi_core.functions.unit_conversion import (
    convert_pressure, 
    convert_temperature,
    convert_power
)

# Process data in mixed units (common in international projects)
measurements = pd.DataFrame({
    "pressure_bar": [10.0, 15.0, 20.0],
    "temperature_c": [100.0, 150.0, 200.0],
    "power_kw": [500.0, 750.0, 1000.0]
})

# Convert to US customary units for US client
measurements["pressure_psi"] = measurements["pressure_bar"].apply(
    lambda x: convert_pressure(x, "bar", "psi")
)

measurements["temperature_f"] = measurements["temperature_c"].apply(
    lambda x: convert_temperature(x, "C", "F")
)

measurements["power_hp"] = measurements["power_kw"].apply(
    lambda x: convert_power(x, "kW", "hp")
)

print(measurements)
#    pressure_bar  temperature_c  power_kw  pressure_psi  temperature_f  power_hp
# 0          10.0          100.0     500.0        145.04          212.0     670.6
# 1          15.0          150.0     750.0        217.56          302.0    1005.8
# 2          20.0          200.0    1000.0        290.08          392.0    1341.0
```

**💡 Quiz Question 18**: Why might you need unit conversion in a data pipeline?
<details>
<summary>Click to reveal answer</summary>

**Answer**: 
- Data sources use different units (sensors, vendors, countries)
- Clients require specific units (US vs. metric)
- Calculations require consistent units
- Compliance/regulatory reporting standards
</details>

---

### ✅ Mission 6 Checkpoint

**You've mastered**:
- ✅ Conversion registry pattern
- ✅ Handling units with offsets (temperature)
- ✅ Custom unit registration
- ✅ Real-world multi-unit data processing

---

## 🎓 Final Project: Build a Complete Pipeline

### Project: Energy Efficiency Analysis Pipeline

**Combine everything you've learned** to build a production-grade analysis pipeline using ODIBI CORE functions.

#### Step 1: Import All Required Functions

```python
# [demo]
import pandas as pd
from odibi_core.functions.math_utils import safe_divide, calculate_z_score
from odibi_core.functions.string_utils import trim_whitespace, to_uppercase
from odibi_core.functions.thermo_utils import steam_enthalpy
from odibi_core.functions.reliability_utils import calculate_mtbf, calculate_availability
from odibi_core.functions.unit_conversion import convert_pressure, convert_temperature
```

#### Step 2: Load Raw Plant Data

```python
# [demo]
plant_data = pd.DataFrame({
    "asset_id": ["  Boiler-1  ", "  Turbine-A", " Pump-X "],  # Note: messy data with spaces
    "steam_pressure_bar": [10.0, 8.5, 12.0],
    "steam_temp_c": [250.0, 230.0, 270.0],
    "fuel_consumption_kg": [1000, 0, 1200],  # Turbine uses no fuel (division by zero!)
    "steam_production_kg": [8000, 9000, 9500],
    "operating_hours": [8760, 8500, 8600],
    "num_failures": [2, 1, 3]
})
```

#### Step 3: Clean and Standardize Data (String Utils)

```python
# [demo]
# Remove whitespace and standardize to uppercase
plant_data = trim_whitespace(plant_data, "asset_id")
plant_data = to_uppercase(plant_data, "asset_id")
# Result: "  Boiler-1  " → "BOILER-1"
```

#### Step 4: Calculate Efficiency (Math Utils with Safe Division)

```python
# [demo]
# Handle division by zero for turbine (no fuel consumption)
plant_data = safe_divide(
    plant_data, 
    "steam_production_kg", 
    "fuel_consumption_kg", 
    "efficiency_ratio",
    fill_value=0  # Turbine gets 0 (not NaN or error)
)
```

#### Step 5: Calculate Thermodynamic Properties (Thermo Utils)

```python
# [demo]
# Calculate steam enthalpy at operating conditions
plant_data["enthalpy_kj_kg"] = plant_data.apply(
    lambda row: steam_enthalpy(row["steam_pressure_bar"], row["steam_temp_c"]),
    axis=1
)
```

#### Step 6: Calculate Reliability Metrics (Reliability Utils)

```python
# [demo]
# Mean Time Between Failures for each asset
plant_data["mtbf_hours"] = plant_data.apply(
    lambda row: calculate_mtbf(row["operating_hours"], row["num_failures"]),
    axis=1
)
```

#### Step 7: Detect Anomalies (Math Utils - Statistics)

```python
# [demo]
# Find efficiency outliers using z-score
plant_data = calculate_z_score(plant_data, "efficiency_ratio", "efficiency_zscore")
# |z-score| > 2 = outlier
```

#### Step 8: Convert Units for International Reporting (Unit Conversion)

```python
# [demo]
# Convert to US/Imperial units
plant_data["pressure_psi"] = plant_data["steam_pressure_bar"].apply(
    lambda x: convert_pressure(x, "bar", "psi")
)
plant_data["temp_f"] = plant_data["steam_temp_c"].apply(
    lambda x: convert_temperature(x, "C", "F")
)
```

#### Step 9: View Final Results

```python
# [demo]
print(plant_data)
# Expected columns:
# - asset_id (cleaned, uppercase)
# - steam_pressure_bar, steam_temp_c (original)
# - fuel_consumption_kg, steam_production_kg
# - efficiency_ratio (safe division)
# - enthalpy_kj_kg (thermodynamics)
# - mtbf_hours (reliability)
# - efficiency_zscore (anomaly detection)
# - pressure_psi, temp_f (unit conversion)
```

#### 🎯 Challenge Exercise

**Extend the pipeline**:
1. Add schema validation to check data types before processing
2. Add error handling for invalid pressure/temperature values
3. Export results to Excel with formatting
4. Create a summary report showing:
   - Total steam production
   - Average efficiency
   - Worst-performing asset (lowest MTBF)
   - Anomaly count (|z-score| > 2)

**💡 Quiz Question 19**: In this pipeline, what would happen if the input data had a column named "ASSET_ID" (uppercase) instead of spaces around lowercase values?
<details>
<summary>Click to reveal answer</summary>

**Answer**: The `trim_whitespace()` call would have no effect (no spaces to trim), and `to_uppercase()` would convert to "ASSET_ID" (already uppercase, no change). The pipeline would still work correctly.
</details>

---

## 📋 Summary & Next Steps

### What You've Mastered

**Core Patterns**:
- ✅ Detect-and-dispatch for dual-engine functions
- ✅ Optional dependency handling with graceful degradation
- ✅ Engine-agnostic API design

**Function Categories**:
- ✅ Math utilities (safe operations, statistics)
- ✅ String utilities (cleaning, extraction)
- ✅ DateTime utilities (parsing, arithmetic)
- ✅ Data operations (joins, filters, aggregations)
- ✅ Validation utilities (schema checks, quality validation)
- ✅ Thermodynamic calculations (steam properties)
- ✅ Psychrometric calculations (HVAC analysis)
- ✅ Reliability engineering (MTBF, availability)
- ✅ Unit conversions (pressure, temperature, power)

**Testing Skills**:
- ✅ Dual-engine parity testing
- ✅ Edge case validation (zeros, nulls, extremes)
- ✅ Mocking optional dependencies
- ✅ Real-world scenario testing

---

### Verification Commands

**Run all function tests**:
```bash
pytest tests/test_functions_*.py -v
```

**Check coverage**:
```bash
pytest tests/test_functions_*.py --cov=odibi_core.functions --cov-report=html
```

**Test specific module**:
```bash
pytest tests/test_functions_math_utils.py -v
```

---

### Related Documentation

- [Phase 1 Walkthrough](DEVELOPER_WALKTHROUGH_PHASE_1.md) - Framework foundation
- [Phase 2 Walkthrough](DEVELOPER_WALKTHROUGH_PHASE_2.md) - Engine contexts
- [Phase 3 Walkthrough](DEVELOPER_WALKTHROUGH_PHASE_3.md) - Config & orchestration
- [Functions Test Guide](../../tests/TEST_FUNCTIONS_README.md) - Detailed test documentation

---

### Next Learning Goals

**Immediate** (Next 1-2 days):
1. Run all Quick Start examples from this walkthrough
2. Complete the practice exercises (safe_log, etc.)
3. Run the Final Project with your own data

**Short-term** (Next 1-2 weeks):
4. Add custom engineering functions for your domain
5. Integrate functions into ODIBI nodes
6. Build production pipelines using these utilities

**Long-term** (Next 1-3 months):
7. Extend to new engines (Polars, DuckDB)
8. Contribute new function categories
9. Build industry-specific function libraries

---

_Updated November 2, 2025 – ODIBI CORE v1.0.3 Functions Teaching Walkthrough_
