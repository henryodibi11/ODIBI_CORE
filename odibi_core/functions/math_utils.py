"""
Mathematical Utilities - Statistical and numerical operations for DataFrames.

Provides engine-agnostic functions for aggregations, z-scores, normalization,
safe division, rounding, and other mathematical transformations.
"""

from typing import Any, List, Optional, Union


def detect_engine(df: Any) -> str:
    """Detect DataFrame engine type."""
    module = type(df).__module__
    if "pandas" in module:
        return "pandas"
    elif "pyspark" in module:
        return "spark"
    else:
        raise TypeError(f"Unsupported DataFrame type: {type(df)}")


def safe_divide(
    df: Any, numerator: str, denominator: str, result_col: str, fill_value: float = 0.0
) -> Any:
    """
    Safely divide two columns, handling division by zero.

    Args:
        df: Input DataFrame
        numerator: Name of numerator column
        denominator: Name of denominator column
        result_col: Name for the result column
        fill_value: Value to use when denominator is zero

    Returns:
        DataFrame: Result with new division column

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"a": [10, 20, 30], "b": [2, 0, 5]})
        >>> result = safe_divide(df, "a", "b", "ratio", fill_value=0)
        >>> result["ratio"].tolist()
        [5.0, 0.0, 6.0]

    Cross-Engine Notes:
        - Pandas: Uses np.where() for conditional logic
        - Spark: Uses F.when().otherwise() expressions
    """
    engine = detect_engine(df)

    if engine == "pandas":
        return _safe_divide_pandas(df, numerator, denominator, result_col, fill_value)
    else:
        return _safe_divide_spark(df, numerator, denominator, result_col, fill_value)


def _safe_divide_pandas(df, numerator, denominator, result_col, fill_value):
    """Pandas implementation of safe_divide."""
    import numpy as np

    df = df.copy()
    df[result_col] = np.where(
        df[denominator] != 0, df[numerator] / df[denominator], fill_value
    )
    return df


def _safe_divide_spark(df, numerator, denominator, result_col, fill_value):
    """Spark implementation of safe_divide."""
    from pyspark.sql import functions as F

    return df.withColumn(
        result_col,
        F.when(
            F.col(denominator) != 0, F.col(numerator) / F.col(denominator)
        ).otherwise(fill_value),
    )


def calculate_z_score(df: Any, column: str, result_col: Optional[str] = None) -> Any:
    """
    Calculate z-scores (standard scores) for a column.

    Z-score = (value - mean) / std_dev

    Args:
        df: Input DataFrame
        column: Column to calculate z-scores for
        result_col: Name for result column (default: "{column}_zscore")

    Returns:
        DataFrame: Result with z-score column

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"value": [10, 20, 30, 40, 50]})
        >>> result = calculate_z_score(df, "value")
        >>> "value_zscore" in result.columns
        True

    Cross-Engine Notes:
        - Pandas: Uses mean() and std() methods
        - Spark: Uses avg() and stddev() aggregations with broadcast
    """
    engine = detect_engine(df)
    result_col = result_col or f"{column}_zscore"

    if engine == "pandas":
        return _zscore_pandas(df, column, result_col)
    else:
        return _zscore_spark(df, column, result_col)


def _zscore_pandas(df, column, result_col):
    """Pandas implementation of calculate_z_score."""
    df = df.copy()
    mean = df[column].mean()
    std = df[column].std()

    if std == 0:
        df[result_col] = 0.0
    else:
        df[result_col] = (df[column] - mean) / std

    return df


def _zscore_spark(df, column, result_col):
    """Spark implementation of calculate_z_score."""
    from pyspark.sql import functions as F

    # Calculate mean and std
    stats = df.agg(
        F.mean(column).alias("mean"), F.stddev(column).alias("std")
    ).collect()[0]

    mean = stats["mean"]
    std = stats["std"]

    if std is None or std == 0:
        return df.withColumn(result_col, F.lit(0.0))

    return df.withColumn(result_col, (F.col(column) - mean) / std)


def normalize_min_max(
    df: Any,
    column: str,
    result_col: Optional[str] = None,
    min_val: float = 0.0,
    max_val: float = 1.0,
) -> Any:
    """
    Normalize a column using min-max scaling.

    Normalized = (value - min) / (max - min) * (max_val - min_val) + min_val

    Args:
        df: Input DataFrame
        column: Column to normalize
        result_col: Name for result column (default: "{column}_norm")
        min_val: Minimum value for normalized range
        max_val: Maximum value for normalized range

    Returns:
        DataFrame: Result with normalized column

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"value": [0, 50, 100]})
        >>> result = normalize_min_max(df, "value")
        >>> result["value_norm"].tolist()
        [0.0, 0.5, 1.0]

    Cross-Engine Notes:
        - Pandas: Direct vectorized operations
        - Spark: Uses column expressions with broadcast values
    """
    engine = detect_engine(df)
    result_col = result_col or f"{column}_norm"

    if engine == "pandas":
        return _normalize_pandas(df, column, result_col, min_val, max_val)
    else:
        return _normalize_spark(df, column, result_col, min_val, max_val)


def _normalize_pandas(df, column, result_col, min_val, max_val):
    """Pandas implementation of normalize_min_max."""
    df = df.copy()
    col_min = df[column].min()
    col_max = df[column].max()

    if col_max == col_min:
        df[result_col] = min_val
    else:
        df[result_col] = (df[column] - col_min) / (col_max - col_min) * (
            max_val - min_val
        ) + min_val

    return df


def _normalize_spark(df, column, result_col, min_val, max_val):
    """Spark implementation of normalize_min_max."""
    from pyspark.sql import functions as F

    # Calculate min and max
    stats = df.agg(F.min(column).alias("min"), F.max(column).alias("max")).collect()[0]

    col_min = stats["min"]
    col_max = stats["max"]

    if col_max == col_min:
        return df.withColumn(result_col, F.lit(min_val))

    return df.withColumn(
        result_col,
        (F.col(column) - col_min) / (col_max - col_min) * (max_val - min_val) + min_val,
    )


def calculate_percentile(
    df: Any,
    column: str,
    percentile: float,
) -> float:
    """
    Calculate a specific percentile value for a column.

    Args:
        df: Input DataFrame
        column: Column to calculate percentile for
        percentile: Percentile to calculate (0.0 to 1.0)

    Returns:
        float: Percentile value

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"value": [1, 2, 3, 4, 5]})
        >>> p50 = calculate_percentile(df, "value", 0.5)
        >>> p50
        3.0

    Cross-Engine Notes:
        - Pandas: Uses quantile() method
        - Spark: Uses approxQuantile() for efficiency
    """
    engine = detect_engine(df)

    if engine == "pandas":
        return df[column].quantile(percentile)
    else:
        return df.approxQuantile(column, [percentile], 0.01)[0]


def round_numeric(
    df: Any, column: str, decimals: int = 0, result_col: Optional[str] = None
) -> Any:
    """
    Round numeric column to specified decimal places.

    Args:
        df: Input DataFrame
        column: Column to round
        decimals: Number of decimal places
        result_col: Name for result column (default: overwrites original)

    Returns:
        DataFrame: Result with rounded column

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"value": [1.234, 5.678, 9.999]})
        >>> result = round_numeric(df, "value", decimals=2)
        >>> result["value"].tolist()
        [1.23, 5.68, 10.0]

    Cross-Engine Notes:
        - Pandas: Uses round() method
        - Spark: Uses F.round() function
    """
    engine = detect_engine(df)
    target_col = result_col or column

    if engine == "pandas":
        df = df.copy()
        df[target_col] = df[column].round(decimals)
        return df
    else:
        from pyspark.sql import functions as F

        return df.withColumn(target_col, F.round(F.col(column), decimals))


def calculate_moving_average(
    df: Any,
    column: str,
    window: int,
    result_col: Optional[str] = None,
    order_by: Optional[str] = None,
) -> Any:
    """
    Calculate moving average over a window.

    Args:
        df: Input DataFrame
        column: Column to calculate moving average for
        window: Number of rows in the window
        result_col: Name for result column (default: "{column}_ma{window}")
        order_by: Column to order by (required for Spark)

    Returns:
        DataFrame: Result with moving average column

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"value": [10, 20, 30, 40, 50]})
        >>> result = calculate_moving_average(df, "value", window=3)
        >>> "value_ma3" in result.columns
        True

    Cross-Engine Notes:
        - Pandas: Uses rolling() method
        - Spark: Uses Window.rowsBetween() with avg()
    """
    engine = detect_engine(df)
    result_col = result_col or f"{column}_ma{window}"

    if engine == "pandas":
        return _moving_avg_pandas(df, column, window, result_col)
    else:
        if order_by is None:
            raise ValueError("order_by parameter required for Spark moving average")
        return _moving_avg_spark(df, column, window, result_col, order_by)


def _moving_avg_pandas(df, column, window, result_col):
    """Pandas implementation of calculate_moving_average."""
    df = df.copy()
    df[result_col] = df[column].rolling(window=window, min_periods=1).mean()
    return df


def _moving_avg_spark(df, column, window, result_col, order_by):
    """Spark implementation of calculate_moving_average."""
    from pyspark.sql import functions as F
    from pyspark.sql.window import Window

    window_spec = Window.orderBy(order_by).rowsBetween(-(window - 1), 0)
    return df.withColumn(result_col, F.avg(column).over(window_spec))


def calculate_cumulative_sum(
    df: Any,
    column: str,
    result_col: Optional[str] = None,
    order_by: Optional[str] = None,
) -> Any:
    """
    Calculate cumulative sum of a column.

    Args:
        df: Input DataFrame
        column: Column to calculate cumulative sum for
        result_col: Name for result column (default: "{column}_cumsum")
        order_by: Column to order by (required for Spark)

    Returns:
        DataFrame: Result with cumulative sum column

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"value": [1, 2, 3, 4, 5]})
        >>> result = calculate_cumulative_sum(df, "value")
        >>> result["value_cumsum"].tolist()
        [1, 3, 6, 10, 15]

    Cross-Engine Notes:
        - Pandas: Uses cumsum() method
        - Spark: Uses Window.unboundedPreceding with sum()
    """
    engine = detect_engine(df)
    result_col = result_col or f"{column}_cumsum"

    if engine == "pandas":
        df = df.copy()
        df[result_col] = df[column].cumsum()
        return df
    else:
        if order_by is None:
            raise ValueError("order_by parameter required for Spark cumulative sum")

        from pyspark.sql import functions as F
        from pyspark.sql.window import Window

        window_spec = Window.orderBy(order_by).rowsBetween(Window.unboundedPreceding, 0)
        return df.withColumn(result_col, F.sum(column).over(window_spec))


def calculate_percent_change(
    df: Any,
    column: str,
    result_col: Optional[str] = None,
    periods: int = 1,
    order_by: Optional[str] = None,
) -> Any:
    """
    Calculate percentage change between current and prior value.

    Args:
        df: Input DataFrame
        column: Column to calculate percent change for
        result_col: Name for result column (default: "{column}_pct_change")
        periods: Number of periods to shift (default: 1)
        order_by: Column to order by (required for Spark)

    Returns:
        DataFrame: Result with percent change column

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"value": [100, 110, 121, 133.1]})
        >>> result = calculate_percent_change(df, "value")
        >>> # First value is NaN, then 10%, 10%, 10%

    Cross-Engine Notes:
        - Pandas: Uses pct_change() method
        - Spark: Uses lag() window function with manual calculation
    """
    engine = detect_engine(df)
    result_col = result_col or f"{column}_pct_change"

    if engine == "pandas":
        df = df.copy()
        df[result_col] = df[column].pct_change(periods=periods)
        return df
    else:
        if order_by is None:
            raise ValueError("order_by parameter required for Spark percent change")

        from pyspark.sql import functions as F
        from pyspark.sql.window import Window

        window_spec = Window.orderBy(order_by)
        lag_col = F.lag(column, periods).over(window_spec)

        return df.withColumn(
            result_col,
            F.when(lag_col.isNotNull(), (F.col(column) - lag_col) / lag_col).otherwise(
                None
            ),
        )


def clip_values(
    df: Any,
    column: str,
    lower: Optional[float] = None,
    upper: Optional[float] = None,
    result_col: Optional[str] = None,
) -> Any:
    """
    Clip (limit) values in a column to a specified range.

    Args:
        df: Input DataFrame
        column: Column to clip
        lower: Minimum value (None = no lower bound)
        upper: Maximum value (None = no upper bound)
        result_col: Name for result column (default: overwrites original)

    Returns:
        DataFrame: Result with clipped values

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"value": [1, 5, 10, 15, 20]})
        >>> result = clip_values(df, "value", lower=5, upper=15)
        >>> result["value"].tolist()
        [5, 5, 10, 15, 15]

    Cross-Engine Notes:
        - Pandas: Uses clip() method
        - Spark: Uses F.when() chaining or F.least/greatest
    """
    engine = detect_engine(df)
    target_col = result_col or column

    if engine == "pandas":
        df = df.copy()
        df[target_col] = df[column].clip(lower=lower, upper=upper)
        return df
    else:
        from pyspark.sql import functions as F

        expr = F.col(column)
        if lower is not None:
            expr = F.greatest(expr, F.lit(lower))
        if upper is not None:
            expr = F.least(expr, F.lit(upper))

        return df.withColumn(target_col, expr)


def safe_log(
    df: Any,
    column: str,
    result_col: Optional[str] = None,
    base: float = 10.0,
    fill_value: float = 0.0
) -> Any:
    """
    Safely calculate logarithm, handling zero and negative values.

    Args:
        df: Input DataFrame
        column: Column to calculate log for
        result_col: Name for result column (default: "{column}_log")
        base: Logarithm base (default: 10 for log10)
        fill_value: Value to use for zero/negative numbers

    Returns:
        DataFrame: Result with log column

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"value": [1, 10, 100, 0, -5]})
        >>> result = safe_log(df, "value", base=10.0, fill_value=0.0)
        >>> result["value_log"].tolist()
        [0.0, 1.0, 2.0, 0.0, 0.0]

    Cross-Engine Notes:
        - Pandas: Uses np.where() with np.log()
        - Spark: Uses F.when() with F.log()
    """
    engine = detect_engine(df)
    result_col = result_col or f"{column}_log"

    if engine == "pandas":
        return _safe_log_pandas(df, column, result_col, base, fill_value)
    else:
        return _safe_log_spark(df, column, result_col, base, fill_value)


def _safe_log_pandas(df, column, result_col, base, fill_value):
    """Pandas implementation of safe_log."""
    import numpy as np

    df = df.copy()
    df[result_col] = np.where(
        df[column] > 0,
        np.log(df[column]) / np.log(base),
        fill_value
    )
    return df


def _safe_log_spark(df, column, result_col, base, fill_value):
    """Spark implementation of safe_log."""
    from pyspark.sql import functions as F
    import math

    log_base = math.log(base)
    return df.withColumn(
        result_col,
        F.when(
            F.col(column) > 0,
            F.log(column) / log_base
        ).otherwise(fill_value)
    )


def safe_sqrt(
    df: Any,
    column: str,
    result_col: Optional[str] = None,
    fill_value: float = 0.0
) -> Any:
    """
    Safely calculate square root, handling negative values.

    Args:
        df: Input DataFrame
        column: Column to calculate sqrt for
        result_col: Name for result column (default: "{column}_sqrt")
        fill_value: Value to use for negative numbers

    Returns:
        DataFrame: Result with sqrt column

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"value": [4, 9, 16, 0, -5]})
        >>> result = safe_sqrt(df, "value", fill_value=0.0)
        >>> result["value_sqrt"].tolist()
        [2.0, 3.0, 4.0, 0.0, 0.0]

    Cross-Engine Notes:
        - Pandas: Uses np.where() with np.sqrt()
        - Spark: Uses F.when() with F.sqrt()
    """
    engine = detect_engine(df)
    result_col = result_col or f"{column}_sqrt"

    if engine == "pandas":
        return _safe_sqrt_pandas(df, column, result_col, fill_value)
    else:
        return _safe_sqrt_spark(df, column, result_col, fill_value)


def _safe_sqrt_pandas(df, column, result_col, fill_value):
    """Pandas implementation of safe_sqrt."""
    import numpy as np

    df = df.copy()
    df[result_col] = np.where(
        df[column] >= 0,
        np.sqrt(df[column]),
        fill_value
    )
    return df


def _safe_sqrt_spark(df, column, result_col, fill_value):
    """Spark implementation of safe_sqrt."""
    from pyspark.sql import functions as F

    return df.withColumn(
        result_col,
        F.when(
            F.col(column) >= 0,
            F.sqrt(column)
        ).otherwise(fill_value)
    )


def outlier_detection_iqr(
    df: Any,
    column: str,
    multiplier: float = 1.5,
    result_col: Optional[str] = None
) -> Any:
    """
    Detect outliers using Interquartile Range (IQR) method.

    Outliers are values outside [Q1 - multiplier*IQR, Q3 + multiplier*IQR]

    Args:
        df: Input DataFrame
        column: Column to check for outliers
        multiplier: IQR multiplier (default: 1.5 for standard outliers)
        result_col: Name for outlier flag column (default: "{column}_is_outlier")

    Returns:
        DataFrame: Result with boolean outlier flag column

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"value": [1, 2, 3, 4, 5, 100]})
        >>> result = outlier_detection_iqr(df, "value")
        >>> result["value_is_outlier"].tolist()
        [False, False, False, False, False, True]

    Cross-Engine Notes:
        - Pandas: Uses quantile() method
        - Spark: Uses approxQuantile() for efficiency
    """
    engine = detect_engine(df)
    result_col = result_col or f"{column}_is_outlier"

    if engine == "pandas":
        return _iqr_pandas(df, column, multiplier, result_col)
    else:
        return _iqr_spark(df, column, multiplier, result_col)


def _iqr_pandas(df, column, multiplier, result_col):
    """Pandas implementation of outlier_detection_iqr."""
    df = df.copy()
    
    q1 = df[column].quantile(0.25)
    q3 = df[column].quantile(0.75)
    iqr = q3 - q1
    
    lower_bound = q1 - multiplier * iqr
    upper_bound = q3 + multiplier * iqr
    
    df[result_col] = (df[column] < lower_bound) | (df[column] > upper_bound)
    
    return df


def _iqr_spark(df, column, multiplier, result_col):
    """Spark implementation of outlier_detection_iqr."""
    from pyspark.sql import functions as F
    
    quantiles = df.approxQuantile(column, [0.25, 0.75], 0.01)
    q1 = quantiles[0]
    q3 = quantiles[1]
    iqr = q3 - q1
    
    lower_bound = q1 - multiplier * iqr
    upper_bound = q3 + multiplier * iqr
    
    return df.withColumn(
        result_col,
        (F.col(column) < lower_bound) | (F.col(column) > upper_bound)
    )


def rolling_zscore(
    df: Any,
    column: str,
    window: int,
    result_col: Optional[str] = None,
    order_by: Optional[str] = None
) -> Any:
    """
    Calculate rolling z-score over a window.

    Args:
        df: Input DataFrame
        column: Column to calculate rolling z-score for
        window: Number of rows in the window
        result_col: Name for result column (default: "{column}_rolling_z")
        order_by: Column to order by (required for Spark)

    Returns:
        DataFrame: Result with rolling z-score column

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"value": [10, 12, 11, 10, 25, 12, 11]})
        >>> result = rolling_zscore(df, "value", window=5)
        >>> "value_rolling_z" in result.columns
        True

    Cross-Engine Notes:
        - Pandas: Uses rolling() with mean() and std()
        - Spark: Uses Window.rowsBetween() with avg() and stddev()
    """
    engine = detect_engine(df)
    result_col = result_col or f"{column}_rolling_z"

    if engine == "pandas":
        return _rolling_zscore_pandas(df, column, window, result_col)
    else:
        if order_by is None:
            raise ValueError("order_by parameter required for Spark rolling z-score")
        return _rolling_zscore_spark(df, column, window, result_col, order_by)


def _rolling_zscore_pandas(df, column, window, result_col):
    """Pandas implementation of rolling_zscore."""
    df = df.copy()
    
    rolling_mean = df[column].rolling(window=window, min_periods=1).mean()
    rolling_std = df[column].rolling(window=window, min_periods=1).std()
    
    # Avoid division by zero
    df[result_col] = ((df[column] - rolling_mean) / rolling_std).fillna(0.0)
    
    return df


def _rolling_zscore_spark(df, column, window, result_col, order_by):
    """Spark implementation of rolling_zscore."""
    from pyspark.sql import functions as F
    from pyspark.sql.window import Window

    window_spec = Window.orderBy(order_by).rowsBetween(-(window - 1), 0)
    
    rolling_mean = F.avg(column).over(window_spec)
    rolling_std = F.stddev(column).over(window_spec)
    
    return df.withColumn(
        result_col,
        F.when(
            (rolling_std.isNotNull()) & (rolling_std != 0),
            (F.col(column) - rolling_mean) / rolling_std
        ).otherwise(0.0)
    )


__all__ = [
    "safe_divide",
    "calculate_z_score",
    "normalize_min_max",
    "calculate_percentile",
    "round_numeric",
    "calculate_moving_average",
    "calculate_cumulative_sum",
    "calculate_percent_change",
    "clip_values",
    "safe_log",
    "safe_sqrt",
    "outlier_detection_iqr",
    "rolling_zscore",
]
