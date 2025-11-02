"""
Unit tests for conversion_utils module.

Tests type conversion and data transformation functions:
- cast_column
- to_boolean
- parse_json
- map_values
- fill_null
- one_hot_encode
- normalize_nulls
- extract_numbers
- to_numeric
"""

import pytest
import pandas as pd
import numpy as np
from odibi_core.functions import conversion_utils

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
        .appName("test_conversion_utils")
        .getOrCreate()
    )
    yield spark
    spark.stop()


# ============================================================================
# cast_column tests
# ============================================================================


def test_cast_column_to_int():
    """Test casting string column to integer."""
    df = pd.DataFrame({"value": ["1", "2", "3"]})

    result = conversion_utils.cast_column(df, "value", "int")

    assert result["value"].dtype == np.int64


def test_cast_column_to_float():
    """Test casting to float."""
    df = pd.DataFrame({"value": ["1.5", "2.5", "3.5"]})

    result = conversion_utils.cast_column(df, "value", "float")

    assert result["value"].dtype == np.float64


def test_cast_column_to_string():
    """Test casting to string."""
    df = pd.DataFrame({"value": [1, 2, 3]})

    result = conversion_utils.cast_column(df, "value", "string")

    assert result["value"].dtype == object


def test_cast_column_new_column():
    """Test casting to new column."""
    df = pd.DataFrame({"value": ["1", "2"]})

    result = conversion_utils.cast_column(df, "value", "int", result_col="value_int")

    assert "value" in result.columns
    assert "value_int" in result.columns
    assert result["value_int"].dtype == np.int64


@pytest.mark.skipif(not HAS_SPARK, reason="Spark not installed")
def test_cast_column_spark(spark_session):
    """Test column casting with Spark."""
    df = spark_session.createDataFrame([("1",), ("2",), ("3",)], ["value"])

    result = conversion_utils.cast_column(df, "value", "int")

    assert "value" in result.columns


# ============================================================================
# to_boolean tests
# ============================================================================


def test_to_boolean_pandas_default_values():
    """Test boolean conversion with default true/false values."""
    df = pd.DataFrame({"status": ["yes", "no", "yes", "no"]})

    result = conversion_utils.to_boolean(df, "status")

    assert result["status"].tolist() == [True, False, True, False]


def test_to_boolean_numeric_values():
    """Test boolean conversion with numeric values."""
    df = pd.DataFrame({"flag": [1, 0, 1, 0]})

    result = conversion_utils.to_boolean(df, "flag")

    assert result["flag"].tolist() == [True, False, True, False]


def test_to_boolean_string_values():
    """Test boolean conversion with string representations."""
    df = pd.DataFrame({"flag": ["true", "false", "True", "False"]})

    result = conversion_utils.to_boolean(df, "flag")

    assert result["flag"].tolist() == [True, False, True, False]


def test_to_boolean_custom_values():
    """Test boolean conversion with custom true/false values."""
    df = pd.DataFrame({"status": ["active", "inactive", "active"]})

    result = conversion_utils.to_boolean(
        df, "status", true_values=["active"], false_values=["inactive"]
    )

    assert result["status"].tolist() == [True, False, True]


def test_to_boolean_unmapped_values():
    """Test boolean conversion with unmapped values becomes None."""
    df = pd.DataFrame({"status": ["yes", "maybe", "no"]})

    result = conversion_utils.to_boolean(df, "status")

    assert result["status"].tolist()[0] is True
    assert result["status"].tolist()[1] is None
    assert result["status"].tolist()[2] is False


@pytest.mark.skipif(not HAS_SPARK, reason="Spark not installed")
def test_to_boolean_spark(spark_session):
    """Test boolean conversion with Spark."""
    df = spark_session.createDataFrame([("yes",), ("no",), ("yes",)], ["status"])

    result = conversion_utils.to_boolean(df, "status")

    rows = result.collect()
    assert rows[0]["status"] is True
    assert rows[1]["status"] is False


# ============================================================================
# parse_json tests
# ============================================================================


def test_parse_json_pandas():
    """Test JSON parsing with Pandas."""
    df = pd.DataFrame({"json_str": ['{"a": 1}', '{"a": 2}']})

    result = conversion_utils.parse_json(df, "json_str")

    assert "json_str_parsed" in result.columns
    assert result["json_str_parsed"].tolist()[0] == {"a": 1}


def test_parse_json_complex():
    """Test parsing complex JSON."""
    df = pd.DataFrame({"json_str": ['{"name": "Alice", "age": 30}']})

    result = conversion_utils.parse_json(df, "json_str")

    assert result["json_str_parsed"].tolist()[0]["name"] == "Alice"


def test_parse_json_null():
    """Test parsing null JSON values."""
    df = pd.DataFrame({"json_str": ['{"a": 1}', None]})

    result = conversion_utils.parse_json(df, "json_str")

    assert result["json_str_parsed"].tolist()[0] == {"a": 1}
    assert result["json_str_parsed"].tolist()[1] is None


@pytest.mark.skipif(not HAS_SPARK, reason="Spark not installed")
def test_parse_json_spark(spark_session):
    """Test JSON parsing with Spark."""
    df = spark_session.createDataFrame([('{"a": "1"}',), ('{"a": "2"}',)], ["json_str"])

    result = conversion_utils.parse_json(df, "json_str")

    assert "json_str_parsed" in result.columns


# ============================================================================
# map_values tests
# ============================================================================


def test_map_values_pandas():
    """Test value mapping with dictionary."""
    df = pd.DataFrame({"status": ["active", "inactive", "pending"]})
    mapping = {"active": 1, "inactive": 0, "pending": 2}

    result = conversion_utils.map_values(df, "status", mapping)

    assert result["status"].tolist() == [1, 0, 2]


def test_map_values_with_default():
    """Test value mapping with default for unmapped values."""
    df = pd.DataFrame({"status": ["active", "unknown", "inactive"]})
    mapping = {"active": 1, "inactive": 0}

    result = conversion_utils.map_values(df, "status", mapping, default=-1)

    assert result["status"].tolist() == [1, -1, 0]


def test_map_values_numeric():
    """Test mapping numeric values."""
    df = pd.DataFrame({"code": [1, 2, 3]})
    mapping = {1: "A", 2: "B", 3: "C"}

    result = conversion_utils.map_values(df, "code", mapping)

    assert result["code"].tolist() == ["A", "B", "C"]


def test_map_values_new_column():
    """Test mapping to new column."""
    df = pd.DataFrame({"status": ["active", "inactive"]})
    mapping = {"active": 1, "inactive": 0}

    result = conversion_utils.map_values(
        df, "status", mapping, result_col="status_code"
    )

    assert "status" in result.columns
    assert "status_code" in result.columns


@pytest.mark.skipif(not HAS_SPARK, reason="Spark not installed")
def test_map_values_spark(spark_session):
    """Test value mapping with Spark."""
    df = spark_session.createDataFrame(
        [("active",), ("inactive",), ("pending",)], ["status"]
    )

    mapping = {"active": 1, "inactive": 0, "pending": 2}
    result = conversion_utils.map_values(df, "status", mapping)

    assert "status" in result.columns


# ============================================================================
# fill_null tests
# ============================================================================


def test_fill_null_pandas():
    """Test filling null values."""
    df = pd.DataFrame({"value": [1, None, 3]})

    result = conversion_utils.fill_null(df, "value", fill_value=0)

    assert result["value"].tolist() == [1.0, 0.0, 3.0]


def test_fill_null_string():
    """Test filling null strings."""
    df = pd.DataFrame({"text": ["hello", None, "world"]})

    result = conversion_utils.fill_null(df, "text", fill_value="MISSING")

    assert result["text"].tolist() == ["hello", "MISSING", "world"]


def test_fill_null_new_column():
    """Test filling nulls to new column."""
    df = pd.DataFrame({"value": [1, None, 3]})

    result = conversion_utils.fill_null(df, "value", fill_value=0, result_col="filled")

    assert "value" in result.columns
    assert "filled" in result.columns
    assert result["filled"].tolist() == [1.0, 0.0, 3.0]


@pytest.mark.skipif(not HAS_SPARK, reason="Spark not installed")
def test_fill_null_spark(spark_session):
    """Test filling nulls with Spark."""
    df = spark_session.createDataFrame([(1,), (None,), (3,)], ["value"])

    result = conversion_utils.fill_null(df, "value", fill_value=0)

    rows = result.collect()
    assert rows[1]["value"] == 0


# ============================================================================
# one_hot_encode tests
# ============================================================================


def test_one_hot_encode_pandas():
    """Test one-hot encoding with Pandas."""
    df = pd.DataFrame({"category": ["A", "B", "A", "C"]})

    result = conversion_utils.one_hot_encode(df, "category")

    assert "category_A" in result.columns
    assert "category_B" in result.columns
    assert "category_C" in result.columns


def test_one_hot_encode_custom_prefix():
    """Test one-hot encoding with custom prefix."""
    df = pd.DataFrame({"type": ["X", "Y", "X"]})

    result = conversion_utils.one_hot_encode(df, "type", prefix="t")

    assert "t_X" in result.columns
    assert "t_Y" in result.columns


def test_one_hot_encode_values():
    """Test one-hot encoding values are correct."""
    df = pd.DataFrame({"category": ["A", "B", "A"]})

    result = conversion_utils.one_hot_encode(df, "category")

    assert result["category_A"].tolist() == [1, 0, 1]
    assert result["category_B"].tolist() == [0, 1, 0]


@pytest.mark.skipif(not HAS_SPARK, reason="Spark not installed")
def test_one_hot_encode_spark(spark_session):
    """Test one-hot encoding with Spark."""
    df = spark_session.createDataFrame([("A",), ("B",), ("A",), ("C",)], ["category"])

    result = conversion_utils.one_hot_encode(df, "category")

    # Just verify new columns exist
    assert "category_A" in result.columns


# ============================================================================
# normalize_nulls tests
# ============================================================================


def test_normalize_nulls_pandas():
    """Test normalizing null representations."""
    df = pd.DataFrame({"value": ["valid", "N/A", "null", "data"]})

    result = conversion_utils.normalize_nulls(df, "value")

    assert result["value"].tolist()[0] == "valid"
    assert pd.isna(result["value"].tolist()[1])
    assert pd.isna(result["value"].tolist()[2])
    assert result["value"].tolist()[3] == "data"


def test_normalize_nulls_custom_representations():
    """Test normalizing with custom null representations."""
    df = pd.DataFrame({"value": ["valid", "MISSING", "empty"]})

    result = conversion_utils.normalize_nulls(
        df, "value", null_representations=["MISSING", "empty"]
    )

    assert result["value"].tolist()[0] == "valid"
    assert pd.isna(result["value"].tolist()[1])
    assert pd.isna(result["value"].tolist()[2])


def test_normalize_nulls_empty_string():
    """Test normalizing empty strings."""
    df = pd.DataFrame({"value": ["valid", "", "data"]})

    result = conversion_utils.normalize_nulls(df, "value")

    assert result["value"].tolist()[0] == "valid"
    assert pd.isna(result["value"].tolist()[1])


@pytest.mark.skipif(not HAS_SPARK, reason="Spark not installed")
def test_normalize_nulls_spark(spark_session):
    """Test normalizing nulls with Spark."""
    df = spark_session.createDataFrame(
        [("valid",), ("N/A",), ("null",), ("data",)], ["value"]
    )

    result = conversion_utils.normalize_nulls(df, "value")

    rows = result.collect()
    assert rows[0]["value"] == "valid"
    assert rows[1]["value"] is None


# ============================================================================
# extract_numbers tests
# ============================================================================


def test_extract_numbers_pandas():
    """Test extracting numbers from strings."""
    df = pd.DataFrame({"text": ["price: $100", "cost: $250"]})

    result = conversion_utils.extract_numbers(df, "text")

    assert result["text_numeric"].tolist() == ["100", "250"]


def test_extract_numbers_with_decimals():
    """Test extracting decimal numbers."""
    df = pd.DataFrame({"text": ["value: 3.14", "amount: 2.5"]})

    result = conversion_utils.extract_numbers(df, "text")

    assert result["text_numeric"].tolist() == ["3.14", "2.5"]


def test_extract_numbers_no_numbers():
    """Test extracting when no numbers present."""
    df = pd.DataFrame({"text": ["hello", "world"]})

    result = conversion_utils.extract_numbers(df, "text")

    assert all(pd.isna(result["text_numeric"]))


def test_extract_numbers_multiple():
    """Test extracting first number when multiple present."""
    df = pd.DataFrame({"text": ["values: 10 and 20"]})

    result = conversion_utils.extract_numbers(df, "text")

    # Extracts first match
    assert result["text_numeric"].tolist()[0] == "10"


@pytest.mark.skipif(not HAS_SPARK, reason="Spark not installed")
def test_extract_numbers_spark(spark_session):
    """Test extracting numbers with Spark."""
    df = spark_session.createDataFrame([("price: $100",), ("cost: $250",)], ["text"])

    result = conversion_utils.extract_numbers(df, "text")

    rows = result.collect()
    assert rows[0]["text_numeric"] == "100"


# ============================================================================
# to_numeric tests
# ============================================================================


def test_to_numeric_pandas_valid():
    """Test converting valid strings to numeric."""
    df = pd.DataFrame({"value": ["1", "2", "3"]})

    result = conversion_utils.to_numeric(df, "value")

    assert result["value"].tolist() == [1.0, 2.0, 3.0]


def test_to_numeric_coerce_errors():
    """Test converting with error coercion (invalid -> NaN)."""
    df = pd.DataFrame({"value": ["1", "2", "invalid", "4"]})

    result = conversion_utils.to_numeric(df, "value", errors="coerce")

    assert result["value"].tolist()[0] == 1.0
    assert result["value"].tolist()[1] == 2.0
    assert pd.isna(result["value"].tolist()[2])
    assert result["value"].tolist()[3] == 4.0


def test_to_numeric_with_decimals():
    """Test converting decimal strings."""
    df = pd.DataFrame({"value": ["1.5", "2.3", "3.7"]})

    result = conversion_utils.to_numeric(df, "value")

    assert result["value"].tolist() == [1.5, 2.3, 3.7]


def test_to_numeric_new_column():
    """Test converting to new column."""
    df = pd.DataFrame({"value": ["1", "2"]})

    result = conversion_utils.to_numeric(df, "value", result_col="numeric")

    assert "value" in result.columns
    assert "numeric" in result.columns
    assert result["numeric"].dtype == np.float64


@pytest.mark.skipif(not HAS_SPARK, reason="Spark not installed")
def test_to_numeric_spark(spark_session):
    """Test numeric conversion with Spark."""
    df = spark_session.createDataFrame([("1",), ("2",), ("3",)], ["value"])

    result = conversion_utils.to_numeric(df, "value", errors="coerce")

    rows = result.collect()
    assert rows[0]["value"] == 1.0
