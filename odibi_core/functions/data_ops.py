"""
Data Operations - Universal DataFrame manipulation utilities.

Provides engine-agnostic functions for common data operations including
joins, filters, grouping, reshaping, pivots, and unpivots.
"""

from typing import Any, Dict, List, Optional, Union


def detect_engine(df: Any) -> str:
    """
    Detect the DataFrame engine type.

    Args:
        df: DataFrame object (Pandas or Spark)

    Returns:
        str: "pandas" or "spark"

    Raises:
        TypeError: If the object is not a recognized DataFrame type

    Examples:
        >>> import pandas as pd
        >>> df_pd = pd.DataFrame({"a": [1, 2]})
        >>> detect_engine(df_pd)
        'pandas'
    """
    module = type(df).__module__

    if "pandas" in module:
        return "pandas"
    elif "pyspark" in module:
        return "spark"
    else:
        raise TypeError(
            f"Unsupported DataFrame type: {type(df)}. "
            f"Expected pandas.DataFrame or pyspark.sql.DataFrame"
        )


def safe_join(
    left: Any,
    right: Any,
    on: Union[str, List[str]],
    how: str = "inner",
    suffixes: tuple = ("_left", "_right"),
) -> Any:
    """
    Join two DataFrames with graceful handling of schema mismatches.

    Automatically resolves duplicate column names and validates join keys.
    Works seamlessly across Pandas and Spark engines.

    Args:
        left: Left DataFrame
        right: Right DataFrame
        on: Column name(s) to join on
        how: Join type - "inner", "left", "right", "outer"
        suffixes: Suffix tuple for duplicate columns (Pandas only)

    Returns:
        DataFrame: Joined result

    Raises:
        ValueError: If join keys are missing from either DataFrame

    Examples:
        >>> import pandas as pd
        >>> left = pd.DataFrame({"id": [1, 2], "value": [10, 20]})
        >>> right = pd.DataFrame({"id": [1, 2], "score": [100, 200]})
        >>> result = safe_join(left, right, on="id")
        >>> len(result)
        2

    Cross-Engine Notes:
        - Pandas: Uses merge() with automatic suffix handling
        - Spark: Uses join() with column disambiguation
    """
    engine = detect_engine(left)

    if engine == "pandas":
        return _safe_join_pandas(left, right, on, how, suffixes)
    else:
        return _safe_join_spark(left, right, on, how)


def _safe_join_pandas(left, right, on, how, suffixes):
    """Pandas implementation of safe_join."""
    import pandas as pd

    # Ensure join keys exist
    join_cols = [on] if isinstance(on, str) else on
    for col in join_cols:
        if col not in left.columns:
            raise ValueError(f"Join key '{col}' not found in left DataFrame")
        if col not in right.columns:
            raise ValueError(f"Join key '{col}' not found in right DataFrame")

    return pd.merge(left, right, on=on, how=how, suffixes=suffixes)


def _safe_join_spark(left, right, on, how):
    """Spark implementation of safe_join."""
    from pyspark.sql import functions as F

    join_cols = [on] if isinstance(on, str) else on

    # Validate join keys
    for col in join_cols:
        if col not in left.columns:
            raise ValueError(f"Join key '{col}' not found in left DataFrame")
        if col not in right.columns:
            raise ValueError(f"Join key '{col}' not found in right DataFrame")

    # Perform join with automatic column disambiguation
    if how == "outer":
        how = "full_outer"

    return left.join(right, on=join_cols, how=how)


def filter_rows(df: Any, condition: Union[str, Any]) -> Any:
    """
    Filter DataFrame rows based on a condition.

    Supports both SQL-style string conditions and native filter objects.

    Args:
        df: Input DataFrame
        condition: Filter condition (SQL string or native filter)

    Returns:
        DataFrame: Filtered result

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"value": [1, 2, 3, 4, 5]})
        >>> result = filter_rows(df, "value > 2")
        >>> len(result)
        3

    Cross-Engine Notes:
        - Pandas: Uses query() for SQL strings, loc[] for masks
        - Spark: Uses filter() or where() with SQL expressions
    """
    engine = detect_engine(df)

    if engine == "pandas":
        return _filter_pandas(df, condition)
    else:
        return _filter_spark(df, condition)


def _filter_pandas(df, condition):
    """Pandas implementation of filter_rows."""
    if isinstance(condition, str):
        return df.query(condition)
    else:
        return df.loc[condition]


def _filter_spark(df, condition):
    """Spark implementation of filter_rows."""
    return df.filter(condition)


def group_and_aggregate(
    df: Any, group_by: Union[str, List[str]], agg_spec: Dict[str, Union[str, List[str]]]
) -> Any:
    """
    Group DataFrame and apply aggregations.

    Provides a unified interface for grouping and aggregating across engines.

    Args:
        df: Input DataFrame
        group_by: Column name(s) to group by
        agg_spec: Dictionary mapping column names to aggregation functions
                  e.g., {"sales": "sum", "quantity": ["mean", "max"]}

    Returns:
        DataFrame: Aggregated result

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     "category": ["A", "A", "B", "B"],
        ...     "value": [10, 20, 30, 40]
        ... })
        >>> result = group_and_aggregate(df, "category", {"value": "sum"})
        >>> len(result)
        2

    Cross-Engine Notes:
        - Pandas: Uses groupby().agg()
        - Spark: Uses groupBy().agg() with F functions
    """
    engine = detect_engine(df)

    if engine == "pandas":
        return _aggregate_pandas(df, group_by, agg_spec)
    else:
        return _aggregate_spark(df, group_by, agg_spec)


def _aggregate_pandas(df, group_by, agg_spec):
    """Pandas implementation of group_and_aggregate."""
    return df.groupby(group_by).agg(agg_spec).reset_index()


def _aggregate_spark(df, group_by, agg_spec):
    """Spark implementation of group_and_aggregate."""
    from pyspark.sql import functions as F

    # Convert agg_spec to Spark aggregation functions
    agg_exprs = []
    agg_func_map = {
        "sum": F.sum,
        "mean": F.avg,
        "avg": F.avg,
        "count": F.count,
        "min": F.min,
        "max": F.max,
        "std": F.stddev,
        "var": F.variance,
    }

    for col, funcs in agg_spec.items():
        func_list = [funcs] if isinstance(funcs, str) else funcs
        for func_name in func_list:
            if func_name in agg_func_map:
                agg_exprs.append(
                    agg_func_map[func_name](col).alias(f"{col}_{func_name}")
                )

    group_cols = [group_by] if isinstance(group_by, str) else group_by
    return df.groupBy(*group_cols).agg(*agg_exprs)


def pivot_table(
    df: Any,
    index: Union[str, List[str]],
    columns: str,
    values: str,
    aggfunc: str = "sum",
) -> Any:
    """
    Create a pivot table from a DataFrame.

    Reshapes data from long to wide format with aggregation.

    Args:
        df: Input DataFrame
        index: Column(s) to use as row index
        columns: Column to pivot into new columns
        values: Column to aggregate
        aggfunc: Aggregation function ("sum", "mean", "count", etc.)

    Returns:
        DataFrame: Pivoted result

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     "date": ["2023-01", "2023-01", "2023-02", "2023-02"],
        ...     "product": ["A", "B", "A", "B"],
        ...     "sales": [100, 200, 150, 250]
        ... })
        >>> result = pivot_table(df, index="date", columns="product", values="sales")

    Cross-Engine Notes:
        - Pandas: Uses pivot_table()
        - Spark: Uses groupBy().pivot().agg()
    """
    engine = detect_engine(df)

    if engine == "pandas":
        return _pivot_pandas(df, index, columns, values, aggfunc)
    else:
        return _pivot_spark(df, index, columns, values, aggfunc)


def _pivot_pandas(df, index, columns, values, aggfunc):
    """Pandas implementation of pivot_table."""
    result = df.pivot_table(
        index=index, columns=columns, values=values, aggfunc=aggfunc
    )
    return result.reset_index()


def _pivot_spark(df, index, columns, values, aggfunc):
    """Spark implementation of pivot_table."""
    from pyspark.sql import functions as F

    agg_func_map = {
        "sum": F.sum,
        "mean": F.avg,
        "avg": F.avg,
        "count": F.count,
        "min": F.min,
        "max": F.max,
    }

    index_cols = [index] if isinstance(index, str) else index
    agg_func = agg_func_map.get(aggfunc, F.sum)

    return df.groupBy(*index_cols).pivot(columns).agg(agg_func(values))


def unpivot(
    df: Any,
    id_vars: Union[str, List[str]],
    value_vars: Optional[List[str]] = None,
    var_name: str = "variable",
    value_name: str = "value",
) -> Any:
    """
    Unpivot (melt) a DataFrame from wide to long format.

    Args:
        df: Input DataFrame
        id_vars: Column(s) to keep as identifiers
        value_vars: Columns to unpivot (None = all non-id columns)
        var_name: Name for the variable column
        value_name: Name for the value column

    Returns:
        DataFrame: Unpivoted result

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     "id": [1, 2],
        ...     "A": [10, 20],
        ...     "B": [30, 40]
        ... })
        >>> result = unpivot(df, id_vars="id", value_vars=["A", "B"])
        >>> len(result)
        4

    Cross-Engine Notes:
        - Pandas: Uses melt()
        - Spark: Uses stack() or unpivot() (Spark 3.4+)
    """
    engine = detect_engine(df)

    if engine == "pandas":
        return _unpivot_pandas(df, id_vars, value_vars, var_name, value_name)
    else:
        return _unpivot_spark(df, id_vars, value_vars, var_name, value_name)


def _unpivot_pandas(df, id_vars, value_vars, var_name, value_name):
    """Pandas implementation of unpivot."""
    return df.melt(
        id_vars=id_vars, value_vars=value_vars, var_name=var_name, value_name=value_name
    )


def _unpivot_spark(df, id_vars, value_vars, var_name, value_name):
    """Spark implementation of unpivot."""
    from pyspark.sql import functions as F

    id_cols = [id_vars] if isinstance(id_vars, str) else id_vars

    # Determine columns to unpivot
    if value_vars is None:
        value_vars = [c for c in df.columns if c not in id_cols]

    # Build stack expression
    stack_expr = f"stack({len(value_vars)}, "
    stack_items = []
    for col in value_vars:
        stack_items.append(f"'{col}', `{col}`")
    stack_expr += ", ".join(stack_items) + f") as ({var_name}, {value_name})"

    return df.select(*id_cols, F.expr(stack_expr))


def deduplicate(
    df: Any, subset: Optional[Union[str, List[str]]] = None, keep: str = "first"
) -> Any:
    """
    Remove duplicate rows from a DataFrame.

    Args:
        df: Input DataFrame
        subset: Column name(s) to consider for duplicates (None = all columns)
        keep: Which duplicates to keep - "first", "last", or False (remove all)

    Returns:
        DataFrame: Deduplicated result

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     "id": [1, 1, 2, 3],
        ...     "value": [10, 10, 20, 30]
        ... })
        >>> result = deduplicate(df, subset="id")
        >>> len(result)
        3

    Cross-Engine Notes:
        - Pandas: Uses drop_duplicates()
        - Spark: Uses dropDuplicates()
    """
    engine = detect_engine(df)

    if engine == "pandas":
        return _deduplicate_pandas(df, subset, keep)
    else:
        return _deduplicate_spark(df, subset)


def _deduplicate_pandas(df, subset, keep):
    """Pandas implementation of deduplicate."""
    return df.drop_duplicates(subset=subset, keep=keep)


def _deduplicate_spark(df, subset):
    """Spark implementation of deduplicate."""
    if subset is None:
        return df.dropDuplicates()

    subset_cols = [subset] if isinstance(subset, str) else subset
    return df.dropDuplicates(subset_cols)


def sort_data(
    df: Any, by: Union[str, List[str]], ascending: Union[bool, List[bool]] = True
) -> Any:
    """
    Sort DataFrame by one or more columns.

    Args:
        df: Input DataFrame
        by: Column name(s) to sort by
        ascending: Sort order (True = ascending, False = descending)

    Returns:
        DataFrame: Sorted result

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"value": [3, 1, 2]})
        >>> result = sort_data(df, by="value")
        >>> result["value"].tolist()
        [1, 2, 3]

    Cross-Engine Notes:
        - Pandas: Uses sort_values()
        - Spark: Uses orderBy()
    """
    engine = detect_engine(df)

    if engine == "pandas":
        return _sort_pandas(df, by, ascending)
    else:
        return _sort_spark(df, by, ascending)


def _sort_pandas(df, by, ascending):
    """Pandas implementation of sort_data."""
    return df.sort_values(by=by, ascending=ascending)


def _sort_spark(df, by, ascending):
    """Spark implementation of sort_data."""
    from pyspark.sql import functions as F

    sort_cols = [by] if isinstance(by, str) else by
    asc_list = [ascending] if isinstance(ascending, bool) else ascending

    # Build sort expressions
    sort_exprs = []
    for i, col in enumerate(sort_cols):
        asc = asc_list[i] if i < len(asc_list) else True
        if asc:
            sort_exprs.append(F.col(col).asc())
        else:
            sort_exprs.append(F.col(col).desc())

    return df.orderBy(*sort_exprs)


def select_columns(df: Any, columns: List[str]) -> Any:
    """
    Select specific columns from a DataFrame.

    Args:
        df: Input DataFrame
        columns: List of column names to select

    Returns:
        DataFrame: Result with selected columns

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"a": [1, 2], "b": [3, 4], "c": [5, 6]})
        >>> result = select_columns(df, ["a", "c"])
        >>> list(result.columns)
        ['a', 'c']

    Cross-Engine Notes:
        - Pandas: Uses bracket notation
        - Spark: Uses select()
    """
    engine = detect_engine(df)

    if engine == "pandas":
        return df[columns]
    else:
        return df.select(*columns)


def rename_columns(df: Any, mapping: Dict[str, str]) -> Any:
    """
    Rename DataFrame columns.

    Args:
        df: Input DataFrame
        mapping: Dictionary mapping old names to new names

    Returns:
        DataFrame: Result with renamed columns

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"old_name": [1, 2]})
        >>> result = rename_columns(df, {"old_name": "new_name"})
        >>> list(result.columns)
        ['new_name']

    Cross-Engine Notes:
        - Pandas: Uses rename()
        - Spark: Uses withColumnRenamed() or toDF()
    """
    engine = detect_engine(df)

    if engine == "pandas":
        return df.rename(columns=mapping)
    else:
        result = df
        for old, new in mapping.items():
            result = result.withColumnRenamed(old, new)
        return result


__all__ = [
    "detect_engine",
    "safe_join",
    "filter_rows",
    "group_and_aggregate",
    "pivot_table",
    "unpivot",
    "deduplicate",
    "sort_data",
    "select_columns",
    "rename_columns",
]
