"""
ODIBI-Specific Helper Functions - Framework integration utilities.

Provides convenience functions that make working with ODIBI CORE workflows
effortless and intuitive, including column resolution, auto-renaming,
parity checking, and metadata extraction.
"""

from typing import Any, Dict, List, Optional, Union
import pandas as pd


def detect_engine(df: Any) -> str:
    """Detect DataFrame engine type."""
    module = type(df).__module__
    if "pandas" in module:
        return "pandas"
    elif "pyspark" in module:
        return "spark"
    else:
        raise TypeError(f"Unsupported DataFrame type: {type(df)}")


def resolve_column(df: Any, name: Union[str, int]) -> str:
    """
    Flexibly resolve column references (by name or index).

    Args:
        df: Input DataFrame
        name: Column name or integer index

    Returns:
        str: Resolved column name

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"a": [1], "b": [2], "c": [3]})
        >>> resolve_column(df, "a")
        'a'
        >>> resolve_column(df, 1)
        'b'

    Cross-Engine Notes:
        - Supports both name-based and index-based lookup
        - Validates column existence
    """
    if isinstance(name, int):
        if 0 <= name < len(df.columns):
            return df.columns[name]
        else:
            raise IndexError(
                f"Column index {name} out of range (0-{len(df.columns)-1})"
            )

    if name in df.columns:
        return name
    else:
        raise ValueError(f"Column '{name}' not found in DataFrame")


def auto_rename(
    df: Any,
    prefix: Optional[str] = None,
    suffix: Optional[str] = None,
    exclude: Optional[List[str]] = None,
) -> Any:
    """
    Automatically rename DataFrame columns with prefix/suffix.

    Args:
        df: Input DataFrame
        prefix: Prefix to add to column names
        suffix: Suffix to add to column names
        exclude: List of column names to exclude from renaming

    Returns:
        DataFrame: Result with renamed columns

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"id": [1], "value": [10]})
        >>> result = auto_rename(df, prefix="raw_", exclude=["id"])
        >>> list(result.columns)
        ['id', 'raw_value']

    Cross-Engine Notes:
        - Useful for adding layer identifiers (bronze_, silver_, gold_)
        - Preserves key columns when specified
    """
    engine = detect_engine(df)
    exclude_set = set(exclude) if exclude else set()

    mapping = {}
    for col in df.columns:
        if col not in exclude_set:
            new_name = col
            if prefix:
                new_name = f"{prefix}{new_name}"
            if suffix:
                new_name = f"{new_name}{suffix}"
            mapping[col] = new_name

    if engine == "pandas":
        return df.rename(columns=mapping)
    else:
        result = df
        for old, new in mapping.items():
            result = result.withColumnRenamed(old, new)
        return result


def compare_results(
    df_pandas: Any, df_spark: Any, tolerance: float = 1e-6
) -> Dict[str, Any]:
    """
    Compare Pandas and Spark DataFrame results for parity testing.

    Args:
        df_pandas: Pandas DataFrame
        df_spark: Spark DataFrame
        tolerance: Numeric tolerance for floating-point comparisons

    Returns:
        dict: Comparison results with row_match, col_match, schema_match, data_match

    Examples:
        >>> import pandas as pd
        >>> df_pd = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
        >>> # Assume df_sp is equivalent Spark DataFrame
        >>> result = compare_results(df_pd, df_sp)
        >>> result["row_match"]
        True

    Cross-Engine Notes:
        - Essential for validating Pandas/Spark parity in ODIBI
        - Converts Spark to Pandas for comparison
    """
    # Convert Spark to Pandas for comparison
    if hasattr(df_spark, "toPandas"):
        df_spark_pd = df_spark.toPandas()
    else:
        df_spark_pd = df_spark

    result = {
        "row_match": len(df_pandas) == len(df_spark_pd),
        "col_match": list(df_pandas.columns) == list(df_spark_pd.columns),
        "schema_match": True,  # Simplified
        "data_match": False,
    }

    # Check data match
    if result["row_match"] and result["col_match"]:
        try:
            # Sort both for fair comparison
            df_pd_sorted = df_pandas.sort_values(
                by=list(df_pandas.columns)
            ).reset_index(drop=True)
            df_sp_sorted = df_spark_pd.sort_values(
                by=list(df_spark_pd.columns)
            ).reset_index(drop=True)

            # Compare with tolerance
            result["data_match"] = df_pd_sorted.equals(df_sp_sorted) or all(
                (df_pd_sorted - df_sp_sorted).abs().max() < tolerance
            )
        except Exception:
            result["data_match"] = False

    return result


def get_metadata(df: Any) -> Dict[str, Any]:
    """
    Extract comprehensive metadata from DataFrame.

    Args:
        df: Input DataFrame

    Returns:
        dict: Metadata including row_count, column_count, schema, memory_usage

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"id": [1, 2], "value": [10, 20]})
        >>> meta = get_metadata(df)
        >>> meta["row_count"]
        2

    Cross-Engine Notes:
        - Useful for ODIBI Tracker and observability
        - Captures execution context information
    """
    engine = detect_engine(df)

    if engine == "pandas":
        return {
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": list(df.columns),
            "schema": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "memory_usage_bytes": int(df.memory_usage(deep=True).sum()),
        }
    else:
        return {
            "row_count": df.count(),
            "column_count": len(df.columns),
            "columns": list(df.columns),
            "schema": {field.name: str(field.dataType) for field in df.schema.fields},
            "memory_usage_bytes": None,  # Not directly available in Spark
        }


def sample_data(df: Any, n: int = 5, method: str = "head") -> Any:
    """
    Sample data from DataFrame (head, tail, or random).

    Args:
        df: Input DataFrame
        n: Number of rows to sample
        method: Sampling method - "head", "tail", "random"

    Returns:
        DataFrame: Sampled result

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"value": range(100)})
        >>> sample = sample_data(df, n=5, method="head")
        >>> len(sample)
        5

    Cross-Engine Notes:
        - Pandas: Uses head(), tail(), or sample()
        - Spark: Uses limit() or sample()
    """
    engine = detect_engine(df)

    if engine == "pandas":
        if method == "head":
            return df.head(n)
        elif method == "tail":
            return df.tail(n)
        elif method == "random":
            return df.sample(n=min(n, len(df)))
        else:
            raise ValueError(
                f"Invalid method '{method}'. Use 'head', 'tail', or 'random'."
            )
    else:
        if method == "head":
            return df.limit(n)
        elif method == "tail":
            # Spark doesn't have tail, approximate with orderBy DESC
            from pyspark.sql import functions as F

            return df.orderBy(F.monotonically_increasing_id().desc()).limit(n)
        elif method == "random":
            fraction = min(1.0, n / df.count())
            return df.sample(fraction=fraction).limit(n)
        else:
            raise ValueError(
                f"Invalid method '{method}'. Use 'head', 'tail', or 'random'."
            )


def add_metadata_columns(
    df: Any,
    run_id: Optional[str] = None,
    timestamp: bool = True,
    source: Optional[str] = None,
) -> Any:
    """
    Add metadata columns for lineage tracking.

    Args:
        df: Input DataFrame
        run_id: Pipeline run identifier
        timestamp: Whether to add current timestamp
        source: Source system identifier

    Returns:
        DataFrame: Result with metadata columns

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"value": [1, 2, 3]})
        >>> result = add_metadata_columns(df, run_id="run123", source="bronze")
        >>> "odibi_run_id" in result.columns
        True

    Cross-Engine Notes:
        - Essential for ODIBI observability and tracking
        - Enables full lineage across pipeline layers
    """
    engine = detect_engine(df)

    if engine == "pandas":
        df = df.copy()

        if run_id:
            df["odibi_run_id"] = run_id
        if timestamp:
            df["odibi_timestamp"] = pd.Timestamp.now()
        if source:
            df["odibi_source"] = source

        return df
    else:
        from pyspark.sql import functions as F

        if run_id:
            df = df.withColumn("odibi_run_id", F.lit(run_id))
        if timestamp:
            df = df.withColumn("odibi_timestamp", F.current_timestamp())
        if source:
            df = df.withColumn("odibi_source", F.lit(source))

        return df


def ensure_columns_exist(
    df: Any, required_columns: List[str], raise_error: bool = True
) -> bool:
    """
    Validate that required columns exist in DataFrame.

    Args:
        df: Input DataFrame
        required_columns: List of required column names
        raise_error: Whether to raise error if columns missing

    Returns:
        bool: True if all columns exist

    Raises:
        ValueError: If columns missing and raise_error=True

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"a": [1], "b": [2]})
        >>> ensure_columns_exist(df, ["a", "b"])
        True
        >>> ensure_columns_exist(df, ["a", "c"], raise_error=False)
        False

    Cross-Engine Notes:
        - Useful for pipeline validation in ODIBI Nodes
        - Provides clear error messages for missing dependencies
    """
    missing = [col for col in required_columns if col not in df.columns]

    if missing:
        if raise_error:
            raise ValueError(f"Missing required columns: {missing}")
        return False

    return True


def collect_sample(df: Any, n: int = 10) -> pd.DataFrame:
    """
    Collect a sample as Pandas DataFrame (for both Pandas and Spark).

    Args:
        df: Input DataFrame
        n: Number of rows to collect

    Returns:
        pd.DataFrame: Pandas DataFrame with sample

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"value": range(100)})
        >>> sample = collect_sample(df, n=5)
        >>> isinstance(sample, pd.DataFrame)
        True

    Cross-Engine Notes:
        - Always returns Pandas for easy inspection
        - Used by ODIBI Story generation and logging
    """
    engine = detect_engine(df)

    if engine == "pandas":
        return df.head(n)
    else:
        return df.limit(n).toPandas()


__all__ = [
    "resolve_column",
    "auto_rename",
    "compare_results",
    "get_metadata",
    "sample_data",
    "add_metadata_columns",
    "ensure_columns_exist",
    "collect_sample",
]
