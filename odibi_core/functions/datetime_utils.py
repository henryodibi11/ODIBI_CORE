"""
DateTime Utilities - Date and time manipulation functions for DataFrames.

Provides engine-agnostic functions for date/time parsing, extraction,
arithmetic, truncation, and window calculations.
"""

from typing import Any, Optional, Union


def detect_engine(df: Any) -> str:
    """Detect DataFrame engine type."""
    module = type(df).__module__
    if "pandas" in module:
        return "pandas"
    elif "pyspark" in module:
        return "spark"
    else:
        raise TypeError(f"Unsupported DataFrame type: {type(df)}")


def to_datetime(
    df: Any, column: str, format: Optional[str] = None, result_col: Optional[str] = None
) -> Any:
    """
    Convert string column to datetime.

    Args:
        df: Input DataFrame
        column: Column to convert
        format: Date format string (None = auto-detect)
        result_col: Name for result column (default: overwrites original)

    Returns:
        DataFrame: Result with datetime column

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"date_str": ["2023-01-15", "2023-02-20"]})
        >>> result = to_datetime(df, "date_str")
        >>> result["date_str"].dtype
        datetime64[ns]

    Cross-Engine Notes:
        - Pandas: Uses pd.to_datetime()
        - Spark: Uses F.to_timestamp() or F.to_date()
    """
    engine = detect_engine(df)
    target_col = result_col or column

    if engine == "pandas":
        import pandas as pd

        df = df.copy()
        df[target_col] = pd.to_datetime(df[column], format=format)
        return df
    else:
        from pyspark.sql import functions as F

        if format:
            return df.withColumn(target_col, F.to_timestamp(F.col(column), format))
        else:
            return df.withColumn(target_col, F.to_timestamp(F.col(column)))


def extract_date_parts(
    df: Any, column: str, parts: list = ["year", "month", "day"]
) -> Any:
    """
    Extract year, month, day, hour, etc. from datetime column.

    Args:
        df: Input DataFrame
        column: Datetime column to extract from
        parts: List of parts to extract - "year", "month", "day", "hour", "minute", "second", "dayofweek"

    Returns:
        DataFrame: Result with extracted date part columns

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"date": pd.to_datetime(["2023-01-15", "2023-02-20"])})
        >>> result = extract_date_parts(df, "date", parts=["year", "month"])
        >>> list(result.columns)
        ['date', 'year', 'month']

    Cross-Engine Notes:
        - Pandas: Uses .dt accessor (year, month, day, etc.)
        - Spark: Uses F.year(), F.month(), F.dayofmonth(), etc.
    """
    engine = detect_engine(df)

    if engine == "pandas":
        return _extract_pandas(df, column, parts)
    else:
        return _extract_spark(df, column, parts)


def _extract_pandas(df, column, parts):
    """Pandas implementation of extract_date_parts."""
    df = df.copy()

    for part in parts:
        if part == "year":
            df["year"] = df[column].dt.year
        elif part == "month":
            df["month"] = df[column].dt.month
        elif part == "day":
            df["day"] = df[column].dt.day
        elif part == "hour":
            df["hour"] = df[column].dt.hour
        elif part == "minute":
            df["minute"] = df[column].dt.minute
        elif part == "second":
            df["second"] = df[column].dt.second
        elif part == "dayofweek":
            df["dayofweek"] = df[column].dt.dayofweek
        elif part == "quarter":
            df["quarter"] = df[column].dt.quarter
        elif part == "dayofyear":
            df["dayofyear"] = df[column].dt.dayofyear
        elif part == "weekofyear":
            df["weekofyear"] = df[column].dt.isocalendar().week

    return df


def _extract_spark(df, column, parts):
    """Spark implementation of extract_date_parts."""
    from pyspark.sql import functions as F

    for part in parts:
        if part == "year":
            df = df.withColumn("year", F.year(F.col(column)))
        elif part == "month":
            df = df.withColumn("month", F.month(F.col(column)))
        elif part == "day":
            df = df.withColumn("day", F.dayofmonth(F.col(column)))
        elif part == "hour":
            df = df.withColumn("hour", F.hour(F.col(column)))
        elif part == "minute":
            df = df.withColumn("minute", F.minute(F.col(column)))
        elif part == "second":
            df = df.withColumn("second", F.second(F.col(column)))
        elif part == "dayofweek":
            df = df.withColumn("dayofweek", F.dayofweek(F.col(column)))
        elif part == "quarter":
            df = df.withColumn("quarter", F.quarter(F.col(column)))
        elif part == "dayofyear":
            df = df.withColumn("dayofyear", F.dayofyear(F.col(column)))
        elif part == "weekofyear":
            df = df.withColumn("weekofyear", F.weekofyear(F.col(column)))

    return df


def add_time_delta(
    df: Any,
    column: str,
    days: int = 0,
    hours: int = 0,
    minutes: int = 0,
    seconds: int = 0,
    result_col: Optional[str] = None,
) -> Any:
    """
    Add a time delta to a datetime column.

    Args:
        df: Input DataFrame
        column: Datetime column
        days: Number of days to add
        hours: Number of hours to add
        minutes: Number of minutes to add
        seconds: Number of seconds to add
        result_col: Name for result column (default: overwrites original)

    Returns:
        DataFrame: Result with adjusted datetime

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"date": pd.to_datetime(["2023-01-15"])})
        >>> result = add_time_delta(df, "date", days=7, result_col="new_date")
        >>> # new_date will be 2023-01-22

    Cross-Engine Notes:
        - Pandas: Uses pd.Timedelta
        - Spark: Uses F.expr() with INTERVAL syntax
    """
    engine = detect_engine(df)
    target_col = result_col or column

    if engine == "pandas":
        import pandas as pd

        df = df.copy()
        delta = pd.Timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
        df[target_col] = df[column] + delta
        return df
    else:
        from pyspark.sql import functions as F

        # Build interval expression
        interval_parts = []
        if days != 0:
            interval_parts.append(f"{days} days")
        if hours != 0:
            interval_parts.append(f"{hours} hours")
        if minutes != 0:
            interval_parts.append(f"{minutes} minutes")
        if seconds != 0:
            interval_parts.append(f"{seconds} seconds")

        if not interval_parts:
            return df.withColumn(target_col, F.col(column))

        interval_str = " + ".join([f"INTERVAL '{p}'" for p in interval_parts])
        return df.withColumn(target_col, F.expr(f"{column} + {interval_str}"))


def date_diff(
    df: Any,
    start_col: str,
    end_col: str,
    unit: str = "days",
    result_col: str = "date_diff",
) -> Any:
    """
    Calculate difference between two datetime columns.

    Args:
        df: Input DataFrame
        start_col: Start datetime column
        end_col: End datetime column
        unit: Unit for difference - "days", "hours", "minutes", "seconds"
        result_col: Name for result column

    Returns:
        DataFrame: Result with difference column

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     "start": pd.to_datetime(["2023-01-01"]),
        ...     "end": pd.to_datetime(["2023-01-10"])
        ... })
        >>> result = date_diff(df, "start", "end", unit="days")
        >>> result["date_diff"].tolist()
        [9]

    Cross-Engine Notes:
        - Pandas: Uses timedelta arithmetic
        - Spark: Uses datediff() or unix_timestamp() calculations
    """
    engine = detect_engine(df)

    if engine == "pandas":
        df = df.copy()
        diff = df[end_col] - df[start_col]

        if unit == "days":
            df[result_col] = diff.dt.days
        elif unit == "hours":
            df[result_col] = diff.dt.total_seconds() / 3600
        elif unit == "minutes":
            df[result_col] = diff.dt.total_seconds() / 60
        elif unit == "seconds":
            df[result_col] = diff.dt.total_seconds()
        else:
            raise ValueError(
                f"Invalid unit '{unit}'. Use 'days', 'hours', 'minutes', or 'seconds'."
            )

        return df
    else:
        from pyspark.sql import functions as F

        if unit == "days":
            return df.withColumn(
                result_col, F.datediff(F.col(end_col), F.col(start_col))
            )
        elif unit == "hours":
            return df.withColumn(
                result_col,
                (F.unix_timestamp(end_col) - F.unix_timestamp(start_col)) / 3600,
            )
        elif unit == "minutes":
            return df.withColumn(
                result_col,
                (F.unix_timestamp(end_col) - F.unix_timestamp(start_col)) / 60,
            )
        elif unit == "seconds":
            return df.withColumn(
                result_col, F.unix_timestamp(end_col) - F.unix_timestamp(start_col)
            )
        else:
            raise ValueError(
                f"Invalid unit '{unit}'. Use 'days', 'hours', 'minutes', or 'seconds'."
            )


def truncate_datetime(
    df: Any, column: str, unit: str = "day", result_col: Optional[str] = None
) -> Any:
    """
    Truncate datetime to specified unit (floor operation).

    Args:
        df: Input DataFrame
        column: Datetime column to truncate
        unit: Unit to truncate to - "year", "month", "day", "hour", "minute", "second"
        result_col: Name for result column (default: overwrites original)

    Returns:
        DataFrame: Result with truncated datetime

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"timestamp": pd.to_datetime(["2023-01-15 14:30:45"])})
        >>> result = truncate_datetime(df, "timestamp", unit="day")
        >>> # Result: 2023-01-15 00:00:00

    Cross-Engine Notes:
        - Pandas: Uses dt.floor()
        - Spark: Uses date_trunc() or trunc()
    """
    engine = detect_engine(df)
    target_col = result_col or column

    if engine == "pandas":
        df = df.copy()

        unit_map = {
            "year": "Y",
            "month": "M",
            "day": "D",
            "hour": "H",
            "minute": "T",
            "second": "S",
        }

        freq = unit_map.get(unit)
        if not freq:
            raise ValueError(
                f"Invalid unit '{unit}'. Use 'year', 'month', 'day', 'hour', 'minute', or 'second'."
            )

        df[target_col] = df[column].dt.floor(freq)
        return df
    else:
        from pyspark.sql import functions as F

        if unit in ["year", "month", "day"]:
            return df.withColumn(target_col, F.trunc(F.col(column), unit))
        else:
            return df.withColumn(target_col, F.date_trunc(unit, F.col(column)))


def format_datetime(
    df: Any, column: str, format: str, result_col: Optional[str] = None
) -> Any:
    """
    Format datetime column as string.

    Args:
        df: Input DataFrame
        column: Datetime column to format
        format: Format string (e.g., "%Y-%m-%d", "yyyy-MM-dd")
        result_col: Name for result column (default: "{column}_formatted")

    Returns:
        DataFrame: Result with formatted string column

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"date": pd.to_datetime(["2023-01-15"])})
        >>> result = format_datetime(df, "date", "%Y/%m/%d")
        >>> result["date_formatted"].tolist()
        ['2023/01/15']

    Cross-Engine Notes:
        - Pandas: Uses strftime()
        - Spark: Uses date_format() with different format syntax
    """
    engine = detect_engine(df)
    target_col = result_col or f"{column}_formatted"

    if engine == "pandas":
        df = df.copy()
        df[target_col] = df[column].dt.strftime(format)
        return df
    else:
        from pyspark.sql import functions as F

        # Convert Python strftime format to Spark format if needed
        spark_format = (
            format.replace("%Y", "yyyy").replace("%m", "MM").replace("%d", "dd")
        )
        spark_format = (
            spark_format.replace("%H", "HH").replace("%M", "mm").replace("%S", "ss")
        )

        return df.withColumn(target_col, F.date_format(F.col(column), spark_format))


def get_current_timestamp(df: Any, result_col: str = "current_timestamp") -> Any:
    """
    Add a column with the current timestamp.

    Args:
        df: Input DataFrame
        result_col: Name for result column

    Returns:
        DataFrame: Result with current timestamp column

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"id": [1, 2, 3]})
        >>> result = get_current_timestamp(df)
        >>> "current_timestamp" in result.columns
        True

    Cross-Engine Notes:
        - Pandas: Uses pd.Timestamp.now()
        - Spark: Uses F.current_timestamp()
    """
    engine = detect_engine(df)

    if engine == "pandas":
        import pandas as pd

        df = df.copy()
        df[result_col] = pd.Timestamp.now()
        return df
    else:
        from pyspark.sql import functions as F

        return df.withColumn(result_col, F.current_timestamp())


def is_weekend(df: Any, column: str, result_col: str = "is_weekend") -> Any:
    """
    Check if date falls on a weekend (Saturday or Sunday).

    Args:
        df: Input DataFrame
        column: Date column to check
        result_col: Name for result column

    Returns:
        DataFrame: Result with boolean weekend indicator

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"date": pd.to_datetime(["2023-01-14", "2023-01-15"])})
        >>> result = is_weekend(df, "date")
        >>> result["is_weekend"].tolist()
        [True, True]  # Both are Saturday and Sunday

    Cross-Engine Notes:
        - Pandas: Uses dt.dayofweek
        - Spark: Uses dayofweek() function
    """
    engine = detect_engine(df)

    if engine == "pandas":
        df = df.copy()
        # In Pandas, Monday=0, Sunday=6
        df[result_col] = df[column].dt.dayofweek.isin([5, 6])
        return df
    else:
        from pyspark.sql import functions as F

        # In Spark, Sunday=1, Saturday=7
        return df.withColumn(result_col, F.dayofweek(F.col(column)).isin([1, 7]))


def calculate_age(
    df: Any,
    birth_date_col: str,
    reference_date_col: Optional[str] = None,
    result_col: str = "age",
) -> Any:
    """
    Calculate age in years from birth date.

    Args:
        df: Input DataFrame
        birth_date_col: Birth date column
        reference_date_col: Reference date column (None = current date)
        result_col: Name for result column

    Returns:
        DataFrame: Result with age column

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     "birth_date": pd.to_datetime(["2000-01-15"])
        ... })
        >>> result = calculate_age(df, "birth_date")
        >>> # age will be calculated from today

    Cross-Engine Notes:
        - Pandas: Uses timedelta arithmetic
        - Spark: Uses datediff() divided by 365.25
    """
    engine = detect_engine(df)

    if engine == "pandas":
        import pandas as pd

        df = df.copy()

        if reference_date_col:
            ref_date = df[reference_date_col]
        else:
            ref_date = pd.Timestamp.now()

        df[result_col] = ((ref_date - df[birth_date_col]).dt.days / 365.25).astype(int)
        return df
    else:
        from pyspark.sql import functions as F

        if reference_date_col:
            ref_expr = F.col(reference_date_col)
        else:
            ref_expr = F.current_date()

        return df.withColumn(
            result_col,
            (F.datediff(ref_expr, F.col(birth_date_col)) / 365.25).cast("int"),
        )


__all__ = [
    "to_datetime",
    "extract_date_parts",
    "add_time_delta",
    "date_diff",
    "truncate_datetime",
    "format_datetime",
    "get_current_timestamp",
    "is_weekend",
    "calculate_age",
]
