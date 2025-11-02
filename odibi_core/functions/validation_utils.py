"""
Validation Utilities - Data quality and schema validation functions.

Provides engine-agnostic functions for schema inference, type checking,
missing data analysis, duplication detection, and data quality reporting.
"""

from typing import Any, Dict, List, Optional, Union


def detect_engine(df: Any) -> str:
    """Detect DataFrame engine type."""
    module = type(df).__module__
    if "pandas" in module:
        return "pandas"
    elif "pyspark" in module:
        return "spark"
    else:
        raise TypeError(f"Unsupported DataFrame type: {type(df)}")


def get_schema(df: Any) -> Dict[str, str]:
    """
    Get DataFrame schema as a dictionary.

    Args:
        df: Input DataFrame

    Returns:
        dict: Dictionary mapping column names to data types

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"id": [1, 2], "name": ["Alice", "Bob"]})
        >>> schema = get_schema(df)
        >>> schema["id"]
        'int64'

    Cross-Engine Notes:
        - Pandas: Uses dtypes attribute
        - Spark: Uses schema.fields
    """
    engine = detect_engine(df)

    if engine == "pandas":
        return {col: str(dtype) for col, dtype in df.dtypes.items()}
    else:
        return {field.name: str(field.dataType) for field in df.schema.fields}


def check_missing_data(df: Any) -> Dict[str, Any]:
    """
    Analyze missing data across all columns.

    Args:
        df: Input DataFrame

    Returns:
        dict: Dictionary with column names as keys and missing data stats as values
              Each value contains: count, percentage

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"a": [1, None, 3], "b": [None, None, 6]})
        >>> missing = check_missing_data(df)
        >>> missing["a"]["count"]
        1
        >>> missing["b"]["percentage"]
        66.67

    Cross-Engine Notes:
        - Pandas: Uses isna().sum()
        - Spark: Uses count() with isNull() filter
    """
    engine = detect_engine(df)

    if engine == "pandas":
        return _check_missing_pandas(df)
    else:
        return _check_missing_spark(df)


def _check_missing_pandas(df):
    """Pandas implementation of check_missing_data."""
    total_rows = len(df)
    missing_stats = {}

    for col in df.columns:
        missing_count = df[col].isna().sum()
        missing_stats[col] = {
            "count": int(missing_count),
            "percentage": (
                round((missing_count / total_rows) * 100, 2) if total_rows > 0 else 0
            ),
        }

    return missing_stats


def _check_missing_spark(df):
    """Spark implementation of check_missing_data."""
    from pyspark.sql import functions as F

    total_rows = df.count()
    missing_stats = {}

    for col in df.columns:
        missing_count = df.filter(F.col(col).isNull()).count()
        missing_stats[col] = {
            "count": missing_count,
            "percentage": (
                round((missing_count / total_rows) * 100, 2) if total_rows > 0 else 0
            ),
        }

    return missing_stats


def find_duplicates(df: Any, subset: Optional[Union[str, List[str]]] = None) -> int:
    """
    Count duplicate rows in DataFrame.

    Args:
        df: Input DataFrame
        subset: Column name(s) to check for duplicates (None = all columns)

    Returns:
        int: Number of duplicate rows

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"id": [1, 1, 2, 3], "value": [10, 10, 20, 30]})
        >>> find_duplicates(df, subset="id")
        1

    Cross-Engine Notes:
        - Pandas: Uses duplicated().sum()
        - Spark: Uses count() difference before/after dropDuplicates()
    """
    engine = detect_engine(df)

    if engine == "pandas":
        if subset:
            return int(df.duplicated(subset=subset, keep="first").sum())
        else:
            return int(df.duplicated(keep="first").sum())
    else:
        total = df.count()
        if subset:
            subset_cols = [subset] if isinstance(subset, str) else subset
            unique = df.dropDuplicates(subset_cols).count()
        else:
            unique = df.dropDuplicates().count()
        return total - unique


def validate_not_null(df: Any, columns: Union[str, List[str]]) -> bool:
    """
    Validate that specified columns contain no null values.

    Args:
        df: Input DataFrame
        columns: Column name(s) to validate

    Returns:
        bool: True if all values are non-null, False otherwise

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"id": [1, 2, 3], "name": ["A", "B", "C"]})
        >>> validate_not_null(df, "id")
        True
        >>> df2 = pd.DataFrame({"id": [1, None, 3]})
        >>> validate_not_null(df2, "id")
        False

    Cross-Engine Notes:
        - Pandas: Uses isna().any()
        - Spark: Uses filter(isNull()).count()
    """
    engine = detect_engine(df)
    cols = [columns] if isinstance(columns, str) else columns

    if engine == "pandas":
        return not df[cols].isna().any().any()
    else:
        from pyspark.sql import functions as F

        for col in cols:
            if df.filter(F.col(col).isNull()).count() > 0:
                return False
        return True


def validate_unique(df: Any, columns: Union[str, List[str]]) -> bool:
    """
    Validate that specified columns contain unique values (no duplicates).

    Args:
        df: Input DataFrame
        columns: Column name(s) to validate

    Returns:
        bool: True if all values are unique, False otherwise

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"id": [1, 2, 3]})
        >>> validate_unique(df, "id")
        True
        >>> df2 = pd.DataFrame({"id": [1, 2, 2]})
        >>> validate_unique(df2, "id")
        False

    Cross-Engine Notes:
        - Pandas: Uses duplicated().any()
        - Spark: Compares count() with distinct().count()
    """
    engine = detect_engine(df)
    cols = [columns] if isinstance(columns, str) else columns

    if engine == "pandas":
        return not df.duplicated(subset=cols, keep=False).any()
    else:
        total = df.count()
        unique = df.select(cols).distinct().count()
        return total == unique


def validate_range(
    df: Any,
    column: str,
    min_val: Optional[float] = None,
    max_val: Optional[float] = None,
) -> bool:
    """
    Validate that numeric column values fall within a specified range.

    Args:
        df: Input DataFrame
        column: Column to validate
        min_val: Minimum allowed value (None = no lower bound)
        max_val: Maximum allowed value (None = no upper bound)

    Returns:
        bool: True if all values within range, False otherwise

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"score": [80, 90, 95]})
        >>> validate_range(df, "score", min_val=0, max_val=100)
        True
        >>> validate_range(df, "score", min_val=85, max_val=100)
        False

    Cross-Engine Notes:
        - Pandas: Uses boolean indexing
        - Spark: Uses filter() with conditions
    """
    engine = detect_engine(df)

    if engine == "pandas":
        if min_val is not None and (df[column] < min_val).any():
            return False
        if max_val is not None and (df[column] > max_val).any():
            return False
        return True
    else:
        from pyspark.sql import functions as F

        if min_val is not None:
            if df.filter(F.col(column) < min_val).count() > 0:
                return False
        if max_val is not None:
            if df.filter(F.col(column) > max_val).count() > 0:
                return False
        return True


def get_value_counts(df: Any, column: str, top_n: int = 10) -> Dict[Any, int]:
    """
    Get frequency counts for unique values in a column.

    Args:
        df: Input DataFrame
        column: Column to analyze
        top_n: Number of top values to return

    Returns:
        dict: Dictionary mapping values to their counts

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"category": ["A", "B", "A", "C", "A", "B"]})
        >>> counts = get_value_counts(df, "category", top_n=3)
        >>> counts["A"]
        3

    Cross-Engine Notes:
        - Pandas: Uses value_counts()
        - Spark: Uses groupBy().count() with orderBy()
    """
    engine = detect_engine(df)

    if engine == "pandas":
        return df[column].value_counts().head(top_n).to_dict()
    else:
        from pyspark.sql import functions as F

        counts_df = (
            df.groupBy(column).count().orderBy(F.desc("count")).limit(top_n).collect()
        )

        return {row[column]: row["count"] for row in counts_df}


def get_column_stats(df: Any, column: str) -> Dict[str, Any]:
    """
    Get statistical summary for a numeric column.

    Args:
        df: Input DataFrame
        column: Numeric column to analyze

    Returns:
        dict: Dictionary with stats - count, mean, std, min, max, median

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"value": [1, 2, 3, 4, 5]})
        >>> stats = get_column_stats(df, "value")
        >>> stats["mean"]
        3.0

    Cross-Engine Notes:
        - Pandas: Uses describe()
        - Spark: Uses summary() or multiple agg() functions
    """
    engine = detect_engine(df)

    if engine == "pandas":
        desc = df[column].describe()
        return {
            "count": int(desc["count"]),
            "mean": float(desc["mean"]),
            "std": float(desc["std"]),
            "min": float(desc["min"]),
            "max": float(desc["max"]),
            "median": float(df[column].median()),
        }
    else:
        from pyspark.sql import functions as F

        stats = df.agg(
            F.count(column).alias("count"),
            F.mean(column).alias("mean"),
            F.stddev(column).alias("std"),
            F.min(column).alias("min"),
            F.max(column).alias("max"),
        ).collect()[0]

        # Median requires approxQuantile
        median = df.approxQuantile(column, [0.5], 0.01)[0]

        return {
            "count": stats["count"],
            "mean": float(stats["mean"]) if stats["mean"] else None,
            "std": float(stats["std"]) if stats["std"] else None,
            "min": float(stats["min"]) if stats["min"] else None,
            "max": float(stats["max"]) if stats["max"] else None,
            "median": float(median),
        }


def generate_data_quality_report(df: Any) -> Dict[str, Any]:
    """
    Generate comprehensive data quality report.

    Args:
        df: Input DataFrame

    Returns:
        dict: Comprehensive report with schema, missing data, duplicates, and row count

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"id": [1, 2, None], "name": ["A", "B", "C"]})
        >>> report = generate_data_quality_report(df)
        >>> report["row_count"]
        3
        >>> report["missing_data"]["id"]["count"]
        1

    Cross-Engine Notes:
        - Combines multiple validation functions
        - Provides unified view of data quality
    """
    engine = detect_engine(df)

    row_count = len(df) if engine == "pandas" else df.count()

    return {
        "row_count": row_count,
        "column_count": len(df.columns),
        "schema": get_schema(df),
        "missing_data": check_missing_data(df),
        "duplicate_count": find_duplicates(df),
    }


def check_schema_match(
    df: Any, expected_schema: Dict[str, str], strict: bool = True
) -> Dict[str, Any]:
    """
    Validate DataFrame schema against expected schema.

    Args:
        df: Input DataFrame
        expected_schema: Dictionary mapping column names to expected types
        strict: If True, extra columns cause validation to fail

    Returns:
        dict: Validation result with is_valid flag and list of issues

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"id": [1, 2], "name": ["A", "B"]})
        >>> expected = {"id": "int64", "name": "object"}
        >>> result = check_schema_match(df, expected)
        >>> result["is_valid"]
        True

    Cross-Engine Notes:
        - Type string comparisons may need normalization
        - Spark types are more complex (e.g., IntegerType() vs "int64")
    """
    actual_schema = get_schema(df)
    issues = []

    # Check for missing columns
    for col, expected_type in expected_schema.items():
        if col not in actual_schema:
            issues.append(f"Missing column: {col}")
        elif str(actual_schema[col]) != str(expected_type):
            issues.append(
                f"Type mismatch for {col}: expected {expected_type}, got {actual_schema[col]}"
            )

    # Check for extra columns (if strict mode)
    if strict:
        for col in actual_schema:
            if col not in expected_schema:
                issues.append(f"Unexpected column: {col}")

    return {
        "is_valid": len(issues) == 0,
        "issues": issues,
        "actual_schema": actual_schema,
    }


__all__ = [
    "get_schema",
    "check_missing_data",
    "find_duplicates",
    "validate_not_null",
    "validate_unique",
    "validate_range",
    "get_value_counts",
    "get_column_stats",
    "generate_data_quality_report",
    "check_schema_match",
]
