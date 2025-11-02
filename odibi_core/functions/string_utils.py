"""
String Utilities - Text manipulation and cleaning functions for DataFrames.

Provides engine-agnostic functions for case conversion, regex operations,
tokenization, trimming, and column name standardization.
"""

from typing import Any, List, Optional, Pattern
import re


def detect_engine(df: Any) -> str:
    """Detect DataFrame engine type."""
    module = type(df).__module__
    if "pandas" in module:
        return "pandas"
    elif "pyspark" in module:
        return "spark"
    else:
        raise TypeError(f"Unsupported DataFrame type: {type(df)}")


def to_lowercase(df: Any, column: str, result_col: Optional[str] = None) -> Any:
    """
    Convert string column to lowercase.

    Args:
        df: Input DataFrame
        column: Column to convert
        result_col: Name for result column (default: overwrites original)

    Returns:
        DataFrame: Result with lowercase column

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"text": ["HELLO", "World", "TEST"]})
        >>> result = to_lowercase(df, "text")
        >>> result["text"].tolist()
        ['hello', 'world', 'test']

    Cross-Engine Notes:
        - Pandas: Uses str.lower() method
        - Spark: Uses F.lower() function
    """
    engine = detect_engine(df)
    target_col = result_col or column

    if engine == "pandas":
        df = df.copy()
        df[target_col] = df[column].str.lower()
        return df
    else:
        from pyspark.sql import functions as F

        return df.withColumn(target_col, F.lower(F.col(column)))


def to_uppercase(df: Any, column: str, result_col: Optional[str] = None) -> Any:
    """
    Convert string column to uppercase.

    Args:
        df: Input DataFrame
        column: Column to convert
        result_col: Name for result column (default: overwrites original)

    Returns:
        DataFrame: Result with uppercase column

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"text": ["hello", "World", "test"]})
        >>> result = to_uppercase(df, "text")
        >>> result["text"].tolist()
        ['HELLO', 'WORLD', 'TEST']

    Cross-Engine Notes:
        - Pandas: Uses str.upper() method
        - Spark: Uses F.upper() function
    """
    engine = detect_engine(df)
    target_col = result_col or column

    if engine == "pandas":
        df = df.copy()
        df[target_col] = df[column].str.upper()
        return df
    else:
        from pyspark.sql import functions as F

        return df.withColumn(target_col, F.upper(F.col(column)))


def to_titlecase(df: Any, column: str, result_col: Optional[str] = None) -> Any:
    """
    Convert string column to title case.

    Args:
        df: Input DataFrame
        column: Column to convert
        result_col: Name for result column (default: overwrites original)

    Returns:
        DataFrame: Result with title case column

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"text": ["hello world", "DATA engineer"]})
        >>> result = to_titlecase(df, "text")
        >>> result["text"].tolist()
        ['Hello World', 'Data Engineer']

    Cross-Engine Notes:
        - Pandas: Uses str.title() method
        - Spark: Uses F.initcap() function
    """
    engine = detect_engine(df)
    target_col = result_col or column

    if engine == "pandas":
        df = df.copy()
        df[target_col] = df[column].str.title()
        return df
    else:
        from pyspark.sql import functions as F

        return df.withColumn(target_col, F.initcap(F.col(column)))


def trim_whitespace(
    df: Any, column: str, result_col: Optional[str] = None, side: str = "both"
) -> Any:
    """
    Remove leading and/or trailing whitespace from string column.

    Args:
        df: Input DataFrame
        column: Column to trim
        result_col: Name for result column (default: overwrites original)
        side: Which side to trim - "both", "left", "right"

    Returns:
        DataFrame: Result with trimmed column

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"text": ["  hello  ", " world ", "test  "]})
        >>> result = trim_whitespace(df, "text")
        >>> result["text"].tolist()
        ['hello', 'world', 'test']

    Cross-Engine Notes:
        - Pandas: Uses str.strip(), str.lstrip(), str.rstrip()
        - Spark: Uses F.trim(), F.ltrim(), F.rtrim()
    """
    engine = detect_engine(df)
    target_col = result_col or column

    if engine == "pandas":
        df = df.copy()
        if side == "both":
            df[target_col] = df[column].str.strip()
        elif side == "left":
            df[target_col] = df[column].str.lstrip()
        elif side == "right":
            df[target_col] = df[column].str.rstrip()
        else:
            raise ValueError(f"Invalid side '{side}'. Use 'both', 'left', or 'right'.")
        return df
    else:
        from pyspark.sql import functions as F

        if side == "both":
            return df.withColumn(target_col, F.trim(F.col(column)))
        elif side == "left":
            return df.withColumn(target_col, F.ltrim(F.col(column)))
        elif side == "right":
            return df.withColumn(target_col, F.rtrim(F.col(column)))
        else:
            raise ValueError(f"Invalid side '{side}'. Use 'both', 'left', or 'right'.")


def regex_replace(
    df: Any,
    column: str,
    pattern: str,
    replacement: str,
    result_col: Optional[str] = None,
) -> Any:
    """
    Replace text matching a regex pattern with a replacement string.

    Args:
        df: Input DataFrame
        column: Column to apply regex to
        pattern: Regular expression pattern
        replacement: Replacement string
        result_col: Name for result column (default: overwrites original)

    Returns:
        DataFrame: Result with replaced text

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"text": ["hello123", "world456", "test789"]})
        >>> result = regex_replace(df, "text", r"\\d+", "XXX")
        >>> result["text"].tolist()
        ['helloXXX', 'worldXXX', 'testXXX']

    Cross-Engine Notes:
        - Pandas: Uses str.replace() with regex=True
        - Spark: Uses F.regexp_replace()
    """
    engine = detect_engine(df)
    target_col = result_col or column

    if engine == "pandas":
        df = df.copy()
        df[target_col] = df[column].str.replace(pattern, replacement, regex=True)
        return df
    else:
        from pyspark.sql import functions as F

        return df.withColumn(
            target_col, F.regexp_replace(F.col(column), pattern, replacement)
        )


def regex_extract(
    df: Any, column: str, pattern: str, group: int = 0, result_col: Optional[str] = None
) -> Any:
    """
    Extract text matching a regex pattern.

    Args:
        df: Input DataFrame
        column: Column to extract from
        pattern: Regular expression pattern with optional groups
        group: Capture group to extract (0 = entire match)
        result_col: Name for result column (default: "{column}_extracted")

    Returns:
        DataFrame: Result with extracted text

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"text": ["user@example.com", "admin@test.org"]})
        >>> result = regex_extract(df, "text", r"@(\\w+)", group=1)
        >>> result["text_extracted"].tolist()
        ['example', 'test']

    Cross-Engine Notes:
        - Pandas: Uses str.extract()
        - Spark: Uses F.regexp_extract()
    """
    engine = detect_engine(df)
    target_col = result_col or f"{column}_extracted"

    if engine == "pandas":
        df = df.copy()
        df[target_col] = df[column].str.extract(f"({pattern})", expand=False)
        return df
    else:
        from pyspark.sql import functions as F

        return df.withColumn(
            target_col, F.regexp_extract(F.col(column), pattern, group)
        )


def replace_substring(
    df: Any, column: str, old: str, new: str, result_col: Optional[str] = None
) -> Any:
    """
    Replace all occurrences of a substring.

    Args:
        df: Input DataFrame
        column: Column to apply replacement to
        old: Substring to replace
        new: Replacement substring
        result_col: Name for result column (default: overwrites original)

    Returns:
        DataFrame: Result with replaced substrings

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"text": ["hello_world", "test_data"]})
        >>> result = replace_substring(df, "text", "_", "-")
        >>> result["text"].tolist()
        ['hello-world', 'test-data']

    Cross-Engine Notes:
        - Pandas: Uses str.replace() with regex=False
        - Spark: Uses F.replace() or F.regexp_replace()
    """
    engine = detect_engine(df)
    target_col = result_col or column

    if engine == "pandas":
        df = df.copy()
        df[target_col] = df[column].str.replace(old, new, regex=False)
        return df
    else:
        from pyspark.sql import functions as F

        return df.withColumn(
            target_col, F.regexp_replace(F.col(column), re.escape(old), new)
        )


def split_string(
    df: Any, column: str, delimiter: str, result_col: Optional[str] = None
) -> Any:
    """
    Split string column into array/list.

    Args:
        df: Input DataFrame
        column: Column to split
        delimiter: Delimiter to split on
        result_col: Name for result column (default: "{column}_split")

    Returns:
        DataFrame: Result with array/list column

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"text": ["a,b,c", "x,y,z"]})
        >>> result = split_string(df, "text", ",")
        >>> result["text_split"].tolist()
        [['a', 'b', 'c'], ['x', 'y', 'z']]

    Cross-Engine Notes:
        - Pandas: Uses str.split() returning lists
        - Spark: Uses F.split() returning arrays
    """
    engine = detect_engine(df)
    target_col = result_col or f"{column}_split"

    if engine == "pandas":
        df = df.copy()
        df[target_col] = df[column].str.split(delimiter)
        return df
    else:
        from pyspark.sql import functions as F

        return df.withColumn(target_col, F.split(F.col(column), re.escape(delimiter)))


def concat_strings(
    df: Any, columns: List[str], result_col: str, separator: str = ""
) -> Any:
    """
    Concatenate multiple string columns.

    Args:
        df: Input DataFrame
        columns: List of column names to concatenate
        result_col: Name for result column
        separator: Separator to insert between columns

    Returns:
        DataFrame: Result with concatenated column

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"first": ["John", "Jane"], "last": ["Doe", "Smith"]})
        >>> result = concat_strings(df, ["first", "last"], "full_name", separator=" ")
        >>> result["full_name"].tolist()
        ['John Doe', 'Jane Smith']

    Cross-Engine Notes:
        - Pandas: Uses + operator or str.cat()
        - Spark: Uses F.concat_ws()
    """
    engine = detect_engine(df)

    if engine == "pandas":
        df = df.copy()
        if separator:
            df[result_col] = df[columns].apply(
                lambda row: separator.join(row.values.astype(str)), axis=1
            )
        else:
            df[result_col] = df[columns].apply(
                lambda row: "".join(row.values.astype(str)), axis=1
            )
        return df
    else:
        from pyspark.sql import functions as F

        return df.withColumn(
            result_col, F.concat_ws(separator, *[F.col(c) for c in columns])
        )


def string_length(df: Any, column: str, result_col: Optional[str] = None) -> Any:
    """
    Calculate length of strings in a column.

    Args:
        df: Input DataFrame
        column: Column to measure
        result_col: Name for result column (default: "{column}_length")

    Returns:
        DataFrame: Result with length column

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"text": ["hello", "world", "test"]})
        >>> result = string_length(df, "text")
        >>> result["text_length"].tolist()
        [5, 5, 4]

    Cross-Engine Notes:
        - Pandas: Uses str.len()
        - Spark: Uses F.length()
    """
    engine = detect_engine(df)
    target_col = result_col or f"{column}_length"

    if engine == "pandas":
        df = df.copy()
        df[target_col] = df[column].str.len()
        return df
    else:
        from pyspark.sql import functions as F

        return df.withColumn(target_col, F.length(F.col(column)))


def pad_string(
    df: Any,
    column: str,
    width: int,
    side: str = "left",
    fillchar: str = " ",
    result_col: Optional[str] = None,
) -> Any:
    """
    Pad string column to specified width.

    Args:
        df: Input DataFrame
        column: Column to pad
        width: Total width after padding
        side: Which side to pad - "left" or "right"
        fillchar: Character to use for padding
        result_col: Name for result column (default: overwrites original)

    Returns:
        DataFrame: Result with padded column

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"id": ["1", "42", "999"]})
        >>> result = pad_string(df, "id", width=5, side="left", fillchar="0")
        >>> result["id"].tolist()
        ['00001', '00042', '00999']

    Cross-Engine Notes:
        - Pandas: Uses str.pad() or str.zfill()
        - Spark: Uses F.lpad() or F.rpad()
    """
    engine = detect_engine(df)
    target_col = result_col or column

    if engine == "pandas":
        df = df.copy()
        if side == "left":
            df[target_col] = df[column].str.pad(width, side="left", fillchar=fillchar)
        elif side == "right":
            df[target_col] = df[column].str.pad(width, side="right", fillchar=fillchar)
        else:
            raise ValueError(f"Invalid side '{side}'. Use 'left' or 'right'.")
        return df
    else:
        from pyspark.sql import functions as F

        if side == "left":
            return df.withColumn(target_col, F.lpad(F.col(column), width, fillchar))
        elif side == "right":
            return df.withColumn(target_col, F.rpad(F.col(column), width, fillchar))
        else:
            raise ValueError(f"Invalid side '{side}'. Use 'left' or 'right'.")


def standardize_column_names(df: Any, style: str = "snake_case") -> Any:
    """
    Standardize DataFrame column names to a consistent format.

    Args:
        df: Input DataFrame
        style: Naming style - "snake_case", "camelCase", "PascalCase", "lowercase"

    Returns:
        DataFrame: Result with standardized column names

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"User Name": [1], "emailAddress": [2], "PhoneNumber": [3]})
        >>> result = standardize_column_names(df, style="snake_case")
        >>> list(result.columns)
        ['user_name', 'email_address', 'phone_number']

    Cross-Engine Notes:
        - Both engines use column renaming with Python transformations
    """

    def to_snake_case(name: str) -> str:
        name = re.sub(r"[\s\-]+", "_", name)
        name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
        return name.lower()

    def to_camel_case(name: str) -> str:
        parts = re.split(r"[\s_\-]+", name.lower())
        return parts[0] + "".join(p.capitalize() for p in parts[1:])

    def to_pascal_case(name: str) -> str:
        parts = re.split(r"[\s_\-]+", name.lower())
        return "".join(p.capitalize() for p in parts)

    engine = detect_engine(df)

    if style == "snake_case":
        transform = to_snake_case
    elif style == "camelCase":
        transform = to_camel_case
    elif style == "PascalCase":
        transform = to_pascal_case
    elif style == "lowercase":
        transform = lambda x: x.lower().replace(" ", "_").replace("-", "_")
    else:
        raise ValueError(
            f"Invalid style '{style}'. Use 'snake_case', 'camelCase', 'PascalCase', or 'lowercase'."
        )

    mapping = {col: transform(col) for col in df.columns}

    if engine == "pandas":
        return df.rename(columns=mapping)
    else:
        result = df
        for old, new in mapping.items():
            result = result.withColumnRenamed(old, new)
        return result


__all__ = [
    "to_lowercase",
    "to_uppercase",
    "to_titlecase",
    "trim_whitespace",
    "regex_replace",
    "regex_extract",
    "replace_substring",
    "split_string",
    "concat_strings",
    "string_length",
    "pad_string",
    "standardize_column_names",
]
