"""
Conversion Utilities - Type casting and data transformation functions.

Provides engine-agnostic functions for flexible type casting, enum parsing,
boolean coercion, unit conversions, and safe type transformations.
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


def cast_column(
    df: Any, column: str, target_type: str, result_col: Optional[str] = None
) -> Any:
    """
    Cast column to a different data type.

    Args:
        df: Input DataFrame
        column: Column to cast
        target_type: Target type - "int", "float", "string", "boolean", "datetime"
        result_col: Name for result column (default: overwrites original)

    Returns:
        DataFrame: Result with casted column

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"value": ["1", "2", "3"]})
        >>> result = cast_column(df, "value", "int")
        >>> result["value"].dtype
        dtype('int64')

    Cross-Engine Notes:
        - Pandas: Uses astype()
        - Spark: Uses cast() function
    """
    engine = detect_engine(df)
    target_col = result_col or column

    if engine == "pandas":
        return _cast_pandas(df, column, target_type, target_col)
    else:
        return _cast_spark(df, column, target_type, target_col)


def _cast_pandas(df, column, target_type, target_col):
    """Pandas implementation of cast_column."""
    import pandas as pd
    import numpy as np

    df = df.copy()

    type_map = {
        "int": "int64",
        "float": "float64",
        "string": "object",
        "str": "object",
        "boolean": "bool",
        "bool": "bool",
        "datetime": "datetime64[ns]",
    }

    pandas_type = type_map.get(target_type, target_type)

    if target_type in ["datetime", "datetime64[ns]"]:
        df[target_col] = pd.to_datetime(df[column])
    else:
        df[target_col] = df[column].astype(pandas_type)

    return df


def _cast_spark(df, column, target_type, target_col):
    """Spark implementation of cast_column."""
    from pyspark.sql import functions as F

    type_map = {
        "int": "integer",
        "float": "double",
        "string": "string",
        "str": "string",
        "boolean": "boolean",
        "bool": "boolean",
        "datetime": "timestamp",
    }

    spark_type = type_map.get(target_type, target_type)

    return df.withColumn(target_col, F.col(column).cast(spark_type))


def to_boolean(
    df: Any,
    column: str,
    true_values: Optional[List[Any]] = None,
    false_values: Optional[List[Any]] = None,
    result_col: Optional[str] = None,
) -> Any:
    """
    Convert column to boolean with flexible value mapping.

    Args:
        df: Input DataFrame
        column: Column to convert
        true_values: Values to map to True (default: [1, "1", "true", "True", "yes", "Yes"])
        false_values: Values to map to False (default: [0, "0", "false", "False", "no", "No"])
        result_col: Name for result column (default: overwrites original)

    Returns:
        DataFrame: Result with boolean column

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"status": ["yes", "no", "yes"]})
        >>> result = to_boolean(df, "status")
        >>> result["status"].tolist()
        [True, False, True]

    Cross-Engine Notes:
        - Pandas: Uses isin() and np.where()
        - Spark: Uses F.when() chaining
    """
    engine = detect_engine(df)
    target_col = result_col or column

    if true_values is None:
        true_values = [1, "1", "true", "True", "yes", "Yes", "Y", "y"]
    if false_values is None:
        false_values = [0, "0", "false", "False", "no", "No", "N", "n"]

    if engine == "pandas":
        import numpy as np

        df = df.copy()

        df[target_col] = np.where(
            df[column].isin(true_values),
            True,
            np.where(df[column].isin(false_values), False, None),
        )
        return df
    else:
        from pyspark.sql import functions as F

        expr = (
            F.when(F.col(column).isin(true_values), True)
            .when(F.col(column).isin(false_values), False)
            .otherwise(None)
        )

        return df.withColumn(target_col, expr)


def parse_json(df: Any, column: str, result_col: Optional[str] = None) -> Any:
    """
    Parse JSON string column into structured data.

    Args:
        df: Input DataFrame
        column: Column containing JSON strings
        result_col: Name for result column (default: "{column}_parsed")

    Returns:
        DataFrame: Result with parsed JSON column

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"json_str": ['{"a": 1}', '{"a": 2}']})
        >>> result = parse_json(df, "json_str")
        >>> # Creates a column with parsed dict/struct

    Cross-Engine Notes:
        - Pandas: Uses json.loads() with apply()
        - Spark: Uses from_json() with inferred or provided schema
    """
    engine = detect_engine(df)
    target_col = result_col or f"{column}_parsed"

    if engine == "pandas":
        import json

        df = df.copy()
        df[target_col] = df[column].apply(lambda x: json.loads(x) if x else None)
        return df
    else:
        from pyspark.sql import functions as F

        # For Spark, we need to infer schema from first non-null value
        # This is a simplified version - production use would need explicit schema
        return df.withColumn(
            target_col, F.from_json(F.col(column), "map<string,string>")
        )


def map_values(
    df: Any,
    column: str,
    mapping: Dict[Any, Any],
    default: Any = None,
    result_col: Optional[str] = None,
) -> Any:
    """
    Map column values using a dictionary.

    Args:
        df: Input DataFrame
        column: Column to map
        mapping: Dictionary mapping old values to new values
        default: Default value for unmapped entries
        result_col: Name for result column (default: overwrites original)

    Returns:
        DataFrame: Result with mapped values

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"status": ["active", "inactive", "pending"]})
        >>> mapping = {"active": 1, "inactive": 0, "pending": 2}
        >>> result = map_values(df, "status", mapping)
        >>> result["status"].tolist()
        [1, 0, 2]

    Cross-Engine Notes:
        - Pandas: Uses map() or replace()
        - Spark: Uses F.create_map() or multiple F.when()
    """
    engine = detect_engine(df)
    target_col = result_col or column

    if engine == "pandas":
        df = df.copy()
        df[target_col] = (
            df[column]
            .map(mapping)
            .fillna(default if default is not None else df[column])
        )
        return df
    else:
        from pyspark.sql import functions as F
        from itertools import chain

        # Build when() chain for Spark
        mapping_expr = F.create_map([F.lit(x) for x in chain(*mapping.items())])

        if default is not None:
            expr = F.coalesce(mapping_expr[F.col(column)], F.lit(default))
        else:
            expr = F.coalesce(mapping_expr[F.col(column)], F.col(column))

        return df.withColumn(target_col, expr)


def fill_null(
    df: Any, column: str, fill_value: Any, result_col: Optional[str] = None
) -> Any:
    """
    Fill null values in a column with a specified value.

    Args:
        df: Input DataFrame
        column: Column to fill
        fill_value: Value to use for nulls
        result_col: Name for result column (default: overwrites original)

    Returns:
        DataFrame: Result with nulls filled

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"value": [1, None, 3]})
        >>> result = fill_null(df, "value", fill_value=0)
        >>> result["value"].tolist()
        [1.0, 0.0, 3.0]

    Cross-Engine Notes:
        - Pandas: Uses fillna()
        - Spark: Uses fillna() or coalesce()
    """
    engine = detect_engine(df)
    target_col = result_col or column

    if engine == "pandas":
        df = df.copy()
        df[target_col] = df[column].fillna(fill_value)
        return df
    else:
        from pyspark.sql import functions as F

        return df.withColumn(target_col, F.coalesce(F.col(column), F.lit(fill_value)))


def one_hot_encode(df: Any, column: str, prefix: Optional[str] = None) -> Any:
    """
    One-hot encode a categorical column.

    Args:
        df: Input DataFrame
        column: Categorical column to encode
        prefix: Prefix for new column names (default: column name)

    Returns:
        DataFrame: Result with one-hot encoded columns

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"category": ["A", "B", "A", "C"]})
        >>> result = one_hot_encode(df, "category")
        >>> # Creates category_A, category_B, category_C columns

    Cross-Engine Notes:
        - Pandas: Uses pd.get_dummies()
        - Spark: Uses pivot or StringIndexer + OneHotEncoder
    """
    engine = detect_engine(df)
    col_prefix = prefix or column

    if engine == "pandas":
        import pandas as pd

        dummies = pd.get_dummies(df[column], prefix=col_prefix)
        return pd.concat([df, dummies], axis=1)
    else:
        # Spark one-hot encoding is more complex, simplified version:
        from pyspark.sql import functions as F

        # Get unique values
        unique_vals = [row[column] for row in df.select(column).distinct().collect()]

        # Create binary columns
        for val in unique_vals:
            col_name = f"{col_prefix}_{val}"
            df = df.withColumn(col_name, F.when(F.col(column) == val, 1).otherwise(0))

        return df


def normalize_nulls(
    df: Any,
    column: str,
    null_representations: Optional[List[Any]] = None,
    result_col: Optional[str] = None,
) -> Any:
    """
    Convert various null representations to actual null values.

    Args:
        df: Input DataFrame
        column: Column to normalize
        null_representations: Values to treat as null (default: ["", "null", "NULL", "None", "N/A"])
        result_col: Name for result column (default: overwrites original)

    Returns:
        DataFrame: Result with normalized nulls

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"value": ["valid", "N/A", "null", "data"]})
        >>> result = normalize_nulls(df, "value")
        >>> result["value"].tolist()
        ['valid', None, None, 'data']

    Cross-Engine Notes:
        - Pandas: Uses replace() with np.nan
        - Spark: Uses F.when() with null literal
    """
    engine = detect_engine(df)
    target_col = result_col or column

    if null_representations is None:
        null_representations = ["", "null", "NULL", "None", "N/A", "NA", "#N/A"]

    if engine == "pandas":
        import numpy as np

        df = df.copy()
        df[target_col] = df[column].replace(null_representations, np.nan)
        return df
    else:
        from pyspark.sql import functions as F

        expr = F.when(F.col(column).isin(null_representations), None).otherwise(
            F.col(column)
        )
        return df.withColumn(target_col, expr)


def extract_numbers(df: Any, column: str, result_col: Optional[str] = None) -> Any:
    """
    Extract numeric values from string column.

    Args:
        df: Input DataFrame
        column: String column containing numbers
        result_col: Name for result column (default: "{column}_numeric")

    Returns:
        DataFrame: Result with extracted numeric values

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"text": ["price: $100", "cost: $250"]})
        >>> result = extract_numbers(df, "text")
        >>> result["text_numeric"].tolist()
        ['100', '250']

    Cross-Engine Notes:
        - Pandas: Uses str.extract() with regex
        - Spark: Uses F.regexp_extract()
    """
    engine = detect_engine(df)
    target_col = result_col or f"{column}_numeric"

    pattern = r"(\d+\.?\d*)"

    if engine == "pandas":
        df = df.copy()
        df[target_col] = df[column].str.extract(pattern, expand=False)
        return df
    else:
        from pyspark.sql import functions as F

        return df.withColumn(target_col, F.regexp_extract(F.col(column), pattern, 1))


def to_numeric(
    df: Any, column: str, errors: str = "coerce", result_col: Optional[str] = None
) -> Any:
    """
    Convert column to numeric, handling non-numeric values.

    Args:
        df: Input DataFrame
        column: Column to convert
        errors: How to handle errors - "coerce" (nulls), "raise", "ignore"
        result_col: Name for result column (default: overwrites original)

    Returns:
        DataFrame: Result with numeric column

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"value": ["1", "2", "invalid", "4"]})
        >>> result = to_numeric(df, "value", errors="coerce")
        >>> result["value"].tolist()
        [1.0, 2.0, nan, 4.0]

    Cross-Engine Notes:
        - Pandas: Uses pd.to_numeric()
        - Spark: Uses cast() with null handling
    """
    engine = detect_engine(df)
    target_col = result_col or column

    if engine == "pandas":
        import pandas as pd

        df = df.copy()
        df[target_col] = pd.to_numeric(df[column], errors=errors)
        return df
    else:
        from pyspark.sql import functions as F

        if errors == "coerce":
            return df.withColumn(target_col, F.col(column).cast("double"))
        elif errors == "raise":
            # Spark will raise on invalid casts
            return df.withColumn(target_col, F.col(column).cast("double"))
        else:  # ignore
            return df


__all__ = [
    "cast_column",
    "to_boolean",
    "parse_json",
    "map_values",
    "fill_null",
    "one_hot_encode",
    "normalize_nulls",
    "extract_numbers",
    "to_numeric",
]
