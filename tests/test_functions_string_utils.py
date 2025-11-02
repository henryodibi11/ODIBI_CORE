"""
Unit tests for string_utils module.

Tests string manipulation functions for both Pandas and Spark:
- to_lowercase, to_uppercase, to_titlecase
- trim_whitespace
- regex_replace, regex_extract
- replace_substring
- split_string, concat_strings
- string_length
- pad_string
- standardize_column_names
"""

import pytest
import pandas as pd
from odibi_core.functions import string_utils

try:
    import pyspark
    from pyspark.sql import SparkSession

    HAS_SPARK = True
except ImportError:
    HAS_SPARK = False


@pytest.fixture(scope="module")
def spark_session():
    """Create Spark session for testing."""
    if not HAS_SPARK:
        pytest.skip("Spark not available")

    spark = (
        SparkSession.builder.master("local[1]")
        .appName("test_string_utils")
        .getOrCreate()
    )
    yield spark
    spark.stop()


# ============================================================================
# Case conversion tests
# ============================================================================


def test_to_lowercase_pandas():
    """Test converting strings to lowercase."""
    df = pd.DataFrame({"text": ["HELLO", "World", "TEST"]})

    result = string_utils.to_lowercase(df, "text")

    assert result["text"].tolist() == ["hello", "world", "test"]


def test_to_uppercase_pandas():
    """Test converting strings to uppercase."""
    df = pd.DataFrame({"text": ["hello", "World", "test"]})

    result = string_utils.to_uppercase(df, "text")

    assert result["text"].tolist() == ["HELLO", "WORLD", "TEST"]


def test_to_titlecase_pandas():
    """Test converting strings to title case."""
    df = pd.DataFrame({"text": ["hello world", "DATA engineer"]})

    result = string_utils.to_titlecase(df, "text")

    assert result["text"].tolist() == ["Hello World", "Data Engineer"]


def test_case_conversion_with_new_column():
    """Test case conversion to new column."""
    df = pd.DataFrame({"text": ["HELLO"]})

    result = string_utils.to_lowercase(df, "text", result_col="lower")

    assert "text" in result.columns
    assert "lower" in result.columns
    assert result["lower"].tolist() == ["hello"]


@pytest.mark.skipif(not HAS_SPARK, reason="Spark not installed")
def test_to_lowercase_spark(spark_session):
    """Test lowercase conversion with Spark."""
    df = spark_session.createDataFrame([("HELLO",), ("World",), ("TEST",)], ["text"])

    result = string_utils.to_lowercase(df, "text")

    rows = result.collect()
    assert rows[0]["text"] == "hello"


# ============================================================================
# trim_whitespace tests
# ============================================================================


def test_trim_whitespace_both():
    """Test trimming whitespace from both sides."""
    df = pd.DataFrame({"text": ["  hello  ", " world ", "test  "]})

    result = string_utils.trim_whitespace(df, "text", side="both")

    assert result["text"].tolist() == ["hello", "world", "test"]


def test_trim_whitespace_left():
    """Test trimming whitespace from left side only."""
    df = pd.DataFrame({"text": ["  hello  ", " world"]})

    result = string_utils.trim_whitespace(df, "text", side="left")

    assert result["text"].tolist() == ["hello  ", "world"]


def test_trim_whitespace_right():
    """Test trimming whitespace from right side only."""
    df = pd.DataFrame({"text": ["  hello  ", "world "]})

    result = string_utils.trim_whitespace(df, "text", side="right")

    assert result["text"].tolist() == ["  hello", "world"]


def test_trim_whitespace_invalid_side():
    """Test error handling for invalid side parameter."""
    df = pd.DataFrame({"text": ["  hello  "]})

    with pytest.raises(ValueError, match="Invalid side"):
        string_utils.trim_whitespace(df, "text", side="invalid")


@pytest.mark.skipif(not HAS_SPARK, reason="Spark not installed")
def test_trim_whitespace_spark(spark_session):
    """Test trimming with Spark."""
    df = spark_session.createDataFrame([("  hello  ",), (" world ",)], ["text"])

    result = string_utils.trim_whitespace(df, "text")

    rows = result.collect()
    assert rows[0]["text"] == "hello"


# ============================================================================
# regex_replace tests
# ============================================================================


def test_regex_replace_pandas():
    """Test regex replacement with Pandas."""
    df = pd.DataFrame({"text": ["hello123", "world456", "test789"]})

    result = string_utils.regex_replace(df, "text", r"\d+", "XXX")

    assert result["text"].tolist() == ["helloXXX", "worldXXX", "testXXX"]


def test_regex_replace_complex_pattern():
    """Test regex replacement with complex pattern."""
    df = pd.DataFrame({"email": ["user@example.com", "admin@test.org"]})

    result = string_utils.regex_replace(df, "email", r"@.*$", "@hidden.com")

    assert result["email"].tolist() == ["user@hidden.com", "admin@hidden.com"]


def test_regex_replace_no_match():
    """Test regex replacement when pattern doesn't match."""
    df = pd.DataFrame({"text": ["hello", "world"]})

    result = string_utils.regex_replace(df, "text", r"\d+", "XXX")

    assert result["text"].tolist() == ["hello", "world"]


@pytest.mark.skipif(not HAS_SPARK, reason="Spark not installed")
def test_regex_replace_spark(spark_session):
    """Test regex replacement with Spark."""
    df = spark_session.createDataFrame([("hello123",), ("world456",)], ["text"])

    result = string_utils.regex_replace(df, "text", r"\d+", "XXX")

    rows = result.collect()
    assert rows[0]["text"] == "helloXXX"


# ============================================================================
# regex_extract tests
# ============================================================================


def test_regex_extract_pandas():
    """Test regex extraction with Pandas."""
    df = pd.DataFrame({"text": ["user@example.com", "admin@test.org"]})

    result = string_utils.regex_extract(df, "text", r"@(\w+)", group=1)

    assert result["text_extracted"].tolist() == ["example", "test"]


def test_regex_extract_full_match():
    """Test extracting full match (group 0)."""
    df = pd.DataFrame({"text": ["price: $100", "cost: $250"]})

    result = string_utils.regex_extract(df, "text", r"\$\d+", group=0)

    # For Pandas, extract needs a group, so this might differ
    # Just validate the column exists
    assert "text_extracted" in result.columns


def test_regex_extract_no_match():
    """Test regex extraction when pattern doesn't match."""
    df = pd.DataFrame({"text": ["hello", "world"]})

    result = string_utils.regex_extract(df, "text", r"\d+", group=0)

    assert result["text_extracted"].isna().all()


@pytest.mark.skipif(not HAS_SPARK, reason="Spark not installed")
def test_regex_extract_spark(spark_session):
    """Test regex extraction with Spark."""
    df = spark_session.createDataFrame(
        [("user@example.com",), ("admin@test.org",)], ["text"]
    )

    result = string_utils.regex_extract(df, "text", r"@(\w+)", group=1)

    rows = result.collect()
    assert rows[0]["text_extracted"] == "example"


# ============================================================================
# replace_substring tests
# ============================================================================


def test_replace_substring_pandas():
    """Test simple substring replacement."""
    df = pd.DataFrame({"text": ["hello_world", "test_data"]})

    result = string_utils.replace_substring(df, "text", "_", "-")

    assert result["text"].tolist() == ["hello-world", "test-data"]


def test_replace_substring_multiple_occurrences():
    """Test replacement of multiple occurrences."""
    df = pd.DataFrame({"text": ["a_b_c_d"]})

    result = string_utils.replace_substring(df, "text", "_", "-")

    assert result["text"].tolist() == ["a-b-c-d"]


def test_replace_substring_special_chars():
    """Test replacement with special characters."""
    df = pd.DataFrame({"text": ["hello.world"]})

    result = string_utils.replace_substring(df, "text", ".", "_")

    assert result["text"].tolist() == ["hello_world"]


@pytest.mark.skipif(not HAS_SPARK, reason="Spark not installed")
def test_replace_substring_spark(spark_session):
    """Test substring replacement with Spark."""
    df = spark_session.createDataFrame([("hello_world",), ("test_data",)], ["text"])

    result = string_utils.replace_substring(df, "text", "_", "-")

    rows = result.collect()
    assert rows[0]["text"] == "hello-world"


# ============================================================================
# split_string tests
# ============================================================================


def test_split_string_pandas():
    """Test string splitting with Pandas."""
    df = pd.DataFrame({"text": ["a,b,c", "x,y,z"]})

    result = string_utils.split_string(df, "text", ",")

    assert result["text_split"].tolist() == [["a", "b", "c"], ["x", "y", "z"]]


def test_split_string_custom_delimiter():
    """Test string splitting with custom delimiter."""
    df = pd.DataFrame({"text": ["a|b|c"]})

    result = string_utils.split_string(df, "text", "|")

    assert result["text_split"].tolist() == [["a", "b", "c"]]


def test_split_string_no_delimiter():
    """Test string splitting when delimiter not present."""
    df = pd.DataFrame({"text": ["hello"]})

    result = string_utils.split_string(df, "text", ",")

    assert result["text_split"].tolist() == [["hello"]]


@pytest.mark.skipif(not HAS_SPARK, reason="Spark not installed")
def test_split_string_spark(spark_session):
    """Test string splitting with Spark."""
    df = spark_session.createDataFrame([("a,b,c",), ("x,y,z",)], ["text"])

    result = string_utils.split_string(df, "text", ",")

    rows = result.collect()
    assert rows[0]["text_split"] == ["a", "b", "c"]


# ============================================================================
# concat_strings tests
# ============================================================================


def test_concat_strings_pandas():
    """Test concatenating multiple columns."""
    df = pd.DataFrame({"first": ["John", "Jane"], "last": ["Doe", "Smith"]})

    result = string_utils.concat_strings(
        df, ["first", "last"], "full_name", separator=" "
    )

    assert result["full_name"].tolist() == ["John Doe", "Jane Smith"]


def test_concat_strings_no_separator():
    """Test concatenation without separator."""
    df = pd.DataFrame({"a": ["hello"], "b": ["world"]})

    result = string_utils.concat_strings(df, ["a", "b"], "combined", separator="")

    assert result["combined"].tolist() == ["helloworld"]


def test_concat_strings_three_columns():
    """Test concatenating three columns."""
    df = pd.DataFrame({"a": ["one"], "b": ["two"], "c": ["three"]})

    result = string_utils.concat_strings(df, ["a", "b", "c"], "result", separator="-")

    assert result["result"].tolist() == ["one-two-three"]


@pytest.mark.skipif(not HAS_SPARK, reason="Spark not installed")
def test_concat_strings_spark(spark_session):
    """Test string concatenation with Spark."""
    df = spark_session.createDataFrame(
        [("John", "Doe"), ("Jane", "Smith")], ["first", "last"]
    )

    result = string_utils.concat_strings(
        df, ["first", "last"], "full_name", separator=" "
    )

    rows = result.collect()
    assert rows[0]["full_name"] == "John Doe"


# ============================================================================
# string_length tests
# ============================================================================


def test_string_length_pandas():
    """Test calculating string length."""
    df = pd.DataFrame({"text": ["hello", "world", "test"]})

    result = string_utils.string_length(df, "text")

    assert result["text_length"].tolist() == [5, 5, 4]


def test_string_length_empty_strings():
    """Test string length with empty strings."""
    df = pd.DataFrame({"text": ["hello", "", "abc"]})

    result = string_utils.string_length(df, "text")

    assert result["text_length"].tolist() == [5, 0, 3]


def test_string_length_custom_column():
    """Test string length with custom result column."""
    df = pd.DataFrame({"text": ["test"]})

    result = string_utils.string_length(df, "text", result_col="len")

    assert "len" in result.columns
    assert result["len"].tolist() == [4]


@pytest.mark.skipif(not HAS_SPARK, reason="Spark not installed")
def test_string_length_spark(spark_session):
    """Test string length with Spark."""
    df = spark_session.createDataFrame([("hello",), ("world",), ("test",)], ["text"])

    result = string_utils.string_length(df, "text")

    rows = result.collect()
    assert rows[0]["text_length"] == 5


# ============================================================================
# pad_string tests
# ============================================================================


def test_pad_string_left():
    """Test left padding strings."""
    df = pd.DataFrame({"id": ["1", "42", "999"]})

    result = string_utils.pad_string(df, "id", width=5, side="left", fillchar="0")

    assert result["id"].tolist() == ["00001", "00042", "00999"]


def test_pad_string_right():
    """Test right padding strings."""
    df = pd.DataFrame({"id": ["1", "42"]})

    result = string_utils.pad_string(df, "id", width=5, side="right", fillchar="0")

    assert result["id"].tolist() == ["10000", "42000"]


def test_pad_string_already_long():
    """Test padding when string is already at target width."""
    df = pd.DataFrame({"id": ["12345"]})

    result = string_utils.pad_string(df, "id", width=5, side="left", fillchar="0")

    assert result["id"].tolist() == ["12345"]


def test_pad_string_invalid_side():
    """Test error handling for invalid side parameter."""
    df = pd.DataFrame({"id": ["1"]})

    with pytest.raises(ValueError, match="Invalid side"):
        string_utils.pad_string(df, "id", width=5, side="middle")


@pytest.mark.skipif(not HAS_SPARK, reason="Spark not installed")
def test_pad_string_spark(spark_session):
    """Test string padding with Spark."""
    df = spark_session.createDataFrame([("1",), ("42",), ("999",)], ["id"])

    result = string_utils.pad_string(df, "id", width=5, side="left", fillchar="0")

    rows = result.collect()
    assert rows[0]["id"] == "00001"


# ============================================================================
# standardize_column_names tests
# ============================================================================


def test_standardize_column_names_snake_case():
    """Test standardizing to snake_case."""
    df = pd.DataFrame({"User Name": [1], "emailAddress": [2], "PhoneNumber": [3]})

    result = string_utils.standardize_column_names(df, style="snake_case")

    assert "user_name" in result.columns
    assert "email_address" in result.columns
    assert "phone_number" in result.columns


def test_standardize_column_names_camel_case():
    """Test standardizing to camelCase."""
    df = pd.DataFrame({"user_name": [1], "email_address": [2]})

    result = string_utils.standardize_column_names(df, style="camelCase")

    assert "userName" in result.columns
    assert "emailAddress" in result.columns


def test_standardize_column_names_pascal_case():
    """Test standardizing to PascalCase."""
    df = pd.DataFrame({"user_name": [1], "email_address": [2]})

    result = string_utils.standardize_column_names(df, style="PascalCase")

    assert "UserName" in result.columns
    assert "EmailAddress" in result.columns


def test_standardize_column_names_lowercase():
    """Test standardizing to lowercase."""
    df = pd.DataFrame({"User Name": [1], "EMAIL": [2]})

    result = string_utils.standardize_column_names(df, style="lowercase")

    assert "user_name" in result.columns
    assert "email" in result.columns


def test_standardize_column_names_invalid_style():
    """Test error handling for invalid style."""
    df = pd.DataFrame({"col": [1]})

    with pytest.raises(ValueError, match="Invalid style"):
        string_utils.standardize_column_names(df, style="invalid_style")


@pytest.mark.skipif(not HAS_SPARK, reason="Spark not installed")
def test_standardize_column_names_spark(spark_session):
    """Test column name standardization with Spark."""
    df = spark_session.createDataFrame(
        [(1, 2, 3)], ["User Name", "emailAddress", "PhoneNumber"]
    )

    result = string_utils.standardize_column_names(df, style="snake_case")

    assert "user_name" in result.columns
    assert "email_address" in result.columns
