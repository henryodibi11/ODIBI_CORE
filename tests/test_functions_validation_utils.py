"""
Unit tests for validation_utils module.

Tests data validation and quality checking functions:
- get_schema
- check_missing_data
- find_duplicates
- validate_not_null
- validate_unique
- validate_range
- get_value_counts
- get_column_stats
- generate_data_quality_report
- check_schema_match
"""

import pytest
import pandas as pd
import numpy as np
from odibi_core.functions import validation_utils

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
        .appName("test_validation_utils")
        .getOrCreate()
    )
    yield spark
    spark.stop()


# ============================================================================
# get_schema tests
# ============================================================================


def test_get_schema_pandas():
    """Test schema extraction from Pandas DataFrame."""
    df = pd.DataFrame({"id": [1, 2], "name": ["Alice", "Bob"]})

    schema = validation_utils.get_schema(df)

    assert "id" in schema
    assert "name" in schema
    assert "int" in schema["id"]
    assert "object" in schema["name"]


def test_get_schema_various_types():
    """Test schema with various data types."""
    df = pd.DataFrame(
        {
            "int_col": [1, 2],
            "float_col": [1.5, 2.5],
            "str_col": ["a", "b"],
            "bool_col": [True, False],
        }
    )

    schema = validation_utils.get_schema(df)

    assert len(schema) == 4
    assert "float" in schema["float_col"]


@pytest.mark.skipif(not HAS_SPARK, reason="Spark not installed")
def test_get_schema_spark(spark_session):
    """Test schema extraction from Spark DataFrame."""
    df = spark_session.createDataFrame([(1, "Alice"), (2, "Bob")], ["id", "name"])

    schema = validation_utils.get_schema(df)

    assert "id" in schema
    assert "name" in schema


# ============================================================================
# check_missing_data tests
# ============================================================================


def test_check_missing_data_pandas():
    """Test missing data analysis with Pandas."""
    df = pd.DataFrame({"a": [1, None, 3], "b": [None, None, 6]})

    missing = validation_utils.check_missing_data(df)

    assert missing["a"]["count"] == 1
    assert abs(missing["a"]["percentage"] - 33.33) < 0.1
    assert missing["b"]["count"] == 2
    assert abs(missing["b"]["percentage"] - 66.67) < 0.1


def test_check_missing_data_no_nulls():
    """Test missing data check when no nulls present."""
    df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})

    missing = validation_utils.check_missing_data(df)

    assert missing["a"]["count"] == 0
    assert missing["a"]["percentage"] == 0
    assert missing["b"]["count"] == 0


def test_check_missing_data_all_nulls():
    """Test missing data when all values are null."""
    df = pd.DataFrame({"a": [None, None, None]})

    missing = validation_utils.check_missing_data(df)

    assert missing["a"]["count"] == 3
    assert missing["a"]["percentage"] == 100.0


def test_check_missing_data_empty_df():
    """Test missing data on empty DataFrame."""
    df = pd.DataFrame({"a": [], "b": []})

    missing = validation_utils.check_missing_data(df)

    assert missing["a"]["percentage"] == 0


@pytest.mark.skipif(not HAS_SPARK, reason="Spark not installed")
def test_check_missing_data_spark(spark_session):
    """Test missing data analysis with Spark."""
    df = spark_session.createDataFrame([(1, None), (None, None), (3, 6)], ["a", "b"])

    missing = validation_utils.check_missing_data(df)

    assert missing["a"]["count"] == 1
    assert missing["b"]["count"] == 2


# ============================================================================
# find_duplicates tests
# ============================================================================


def test_find_duplicates_pandas_all_columns():
    """Test duplicate detection considering all columns."""
    df = pd.DataFrame({"id": [1, 1, 2, 3], "value": [10, 10, 20, 30]})

    dup_count = validation_utils.find_duplicates(df)

    assert dup_count == 1


def test_find_duplicates_pandas_subset():
    """Test duplicate detection on specific columns."""
    df = pd.DataFrame({"id": [1, 1, 2, 3], "value": [10, 20, 20, 30]})

    dup_count = validation_utils.find_duplicates(df, subset="id")

    assert dup_count == 1


def test_find_duplicates_no_duplicates():
    """Test duplicate detection when no duplicates exist."""
    df = pd.DataFrame({"id": [1, 2, 3], "value": [10, 20, 30]})

    dup_count = validation_utils.find_duplicates(df)

    assert dup_count == 0


def test_find_duplicates_multiple_columns():
    """Test duplicate detection on multiple columns."""
    df = pd.DataFrame(
        {"a": [1, 1, 1, 2], "b": [10, 10, 20, 10], "c": [100, 100, 200, 300]}
    )

    dup_count = validation_utils.find_duplicates(df, subset=["a", "b"])

    assert dup_count == 1


@pytest.mark.skipif(not HAS_SPARK, reason="Spark not installed")
def test_find_duplicates_spark(spark_session):
    """Test duplicate detection with Spark."""
    df = spark_session.createDataFrame(
        [(1, 10), (1, 10), (2, 20), (3, 30)], ["id", "value"]
    )

    dup_count = validation_utils.find_duplicates(df, subset="id")

    assert dup_count == 1


# ============================================================================
# validate_not_null tests
# ============================================================================


def test_validate_not_null_pandas_valid():
    """Test validation passes when no nulls present."""
    df = pd.DataFrame({"id": [1, 2, 3], "name": ["A", "B", "C"]})

    result = validation_utils.validate_not_null(df, "id")

    assert result is True


def test_validate_not_null_pandas_invalid():
    """Test validation fails when nulls present."""
    df = pd.DataFrame({"id": [1, None, 3]})

    result = validation_utils.validate_not_null(df, "id")

    assert result is False


def test_validate_not_null_multiple_columns():
    """Test validation on multiple columns."""
    df = pd.DataFrame({"id": [1, 2, 3], "name": ["A", "B", "C"]})

    result = validation_utils.validate_not_null(df, ["id", "name"])

    assert result is True


def test_validate_not_null_one_column_has_nulls():
    """Test validation fails if any column has nulls."""
    df = pd.DataFrame({"id": [1, 2, 3], "name": ["A", None, "C"]})

    result = validation_utils.validate_not_null(df, ["id", "name"])

    assert result is False


@pytest.mark.skipif(not HAS_SPARK, reason="Spark not installed")
def test_validate_not_null_spark(spark_session):
    """Test null validation with Spark."""
    df = spark_session.createDataFrame([(1, "A"), (2, "B"), (3, "C")], ["id", "name"])

    result = validation_utils.validate_not_null(df, "id")

    assert result is True


# ============================================================================
# validate_unique tests
# ============================================================================


def test_validate_unique_pandas_valid():
    """Test uniqueness validation passes."""
    df = pd.DataFrame({"id": [1, 2, 3]})

    result = validation_utils.validate_unique(df, "id")

    assert result is True


def test_validate_unique_pandas_invalid():
    """Test uniqueness validation fails with duplicates."""
    df = pd.DataFrame({"id": [1, 2, 2]})

    result = validation_utils.validate_unique(df, "id")

    assert result is False


def test_validate_unique_multiple_columns():
    """Test uniqueness on composite key."""
    df = pd.DataFrame({"a": [1, 1, 2], "b": [10, 20, 10]})

    result = validation_utils.validate_unique(df, ["a", "b"])

    assert result is True


@pytest.mark.skipif(not HAS_SPARK, reason="Spark not installed")
def test_validate_unique_spark(spark_session):
    """Test uniqueness validation with Spark."""
    df = spark_session.createDataFrame([(1,), (2,), (3,)], ["id"])

    result = validation_utils.validate_unique(df, "id")

    assert result is True


# ============================================================================
# validate_range tests
# ============================================================================


def test_validate_range_pandas_valid():
    """Test range validation passes when all values in range."""
    df = pd.DataFrame({"score": [80, 90, 95]})

    result = validation_utils.validate_range(df, "score", min_val=0, max_val=100)

    assert result is True


def test_validate_range_pandas_invalid_min():
    """Test range validation fails when value below minimum."""
    df = pd.DataFrame({"score": [80, 90, 95]})

    result = validation_utils.validate_range(df, "score", min_val=85, max_val=100)

    assert result is False


def test_validate_range_pandas_invalid_max():
    """Test range validation fails when value above maximum."""
    df = pd.DataFrame({"score": [80, 90, 105]})

    result = validation_utils.validate_range(df, "score", min_val=0, max_val=100)

    assert result is False


def test_validate_range_only_min():
    """Test range validation with only minimum bound."""
    df = pd.DataFrame({"value": [5, 10, 15]})

    result = validation_utils.validate_range(df, "value", min_val=0)

    assert result is True


def test_validate_range_only_max():
    """Test range validation with only maximum bound."""
    df = pd.DataFrame({"value": [5, 10, 15]})

    result = validation_utils.validate_range(df, "value", max_val=20)

    assert result is True


@pytest.mark.skipif(not HAS_SPARK, reason="Spark not installed")
def test_validate_range_spark(spark_session):
    """Test range validation with Spark."""
    df = spark_session.createDataFrame([(80,), (90,), (95,)], ["score"])

    result = validation_utils.validate_range(df, "score", min_val=0, max_val=100)

    assert result is True


# ============================================================================
# get_value_counts tests
# ============================================================================


def test_get_value_counts_pandas():
    """Test value frequency counting."""
    df = pd.DataFrame({"category": ["A", "B", "A", "C", "A", "B"]})

    counts = validation_utils.get_value_counts(df, "category", top_n=3)

    assert counts["A"] == 3
    assert counts["B"] == 2
    assert counts["C"] == 1


def test_get_value_counts_limit():
    """Test value counts respects top_n limit."""
    df = pd.DataFrame({"category": ["A", "B", "C", "D", "E"]})

    counts = validation_utils.get_value_counts(df, "category", top_n=2)

    assert len(counts) <= 2


def test_get_value_counts_numeric():
    """Test value counts on numeric column."""
    df = pd.DataFrame({"value": [1, 2, 1, 3, 1, 2]})

    counts = validation_utils.get_value_counts(df, "value")

    assert counts[1] == 3
    assert counts[2] == 2


@pytest.mark.skipif(not HAS_SPARK, reason="Spark not installed")
def test_get_value_counts_spark(spark_session):
    """Test value counts with Spark."""
    df = spark_session.createDataFrame(
        [("A",), ("B",), ("A",), ("C",), ("A",), ("B",)], ["category"]
    )

    counts = validation_utils.get_value_counts(df, "category", top_n=3)

    assert counts["A"] == 3
    assert counts["B"] == 2


# ============================================================================
# get_column_stats tests
# ============================================================================


def test_get_column_stats_pandas():
    """Test statistical summary for numeric column."""
    df = pd.DataFrame({"value": [1, 2, 3, 4, 5]})

    stats = validation_utils.get_column_stats(df, "value")

    assert stats["count"] == 5
    assert stats["mean"] == 3.0
    assert stats["min"] == 1.0
    assert stats["max"] == 5.0
    assert stats["median"] == 3.0


def test_get_column_stats_with_nulls():
    """Test column stats with null values."""
    df = pd.DataFrame({"value": [1, 2, None, 4, 5]})

    stats = validation_utils.get_column_stats(df, "value")

    assert stats["count"] == 4  # Excludes null
    assert stats["mean"] == 3.0


def test_get_column_stats_single_value():
    """Test column stats with single value."""
    df = pd.DataFrame({"value": [42]})

    stats = validation_utils.get_column_stats(df, "value")

    assert stats["count"] == 1
    assert stats["mean"] == 42.0
    assert stats["median"] == 42.0


@pytest.mark.skipif(not HAS_SPARK, reason="Spark not installed")
def test_get_column_stats_spark(spark_session):
    """Test column stats with Spark."""
    df = spark_session.createDataFrame([(1,), (2,), (3,), (4,), (5,)], ["value"])

    stats = validation_utils.get_column_stats(df, "value")

    assert stats["count"] == 5
    assert stats["mean"] == 3.0


# ============================================================================
# generate_data_quality_report tests
# ============================================================================


def test_generate_data_quality_report_pandas():
    """Test comprehensive data quality report generation."""
    df = pd.DataFrame({"id": [1, 2, None], "name": ["A", "B", "C"]})

    report = validation_utils.generate_data_quality_report(df)

    assert report["row_count"] == 3
    assert report["column_count"] == 2
    assert "schema" in report
    assert "missing_data" in report
    assert "duplicate_count" in report
    assert report["missing_data"]["id"]["count"] == 1


def test_generate_data_quality_report_with_duplicates():
    """Test report includes duplicate count."""
    df = pd.DataFrame({"id": [1, 1, 2], "value": [10, 10, 20]})

    report = validation_utils.generate_data_quality_report(df)

    assert report["duplicate_count"] == 1


def test_generate_data_quality_report_clean_data():
    """Test report on clean data (no issues)."""
    df = pd.DataFrame({"id": [1, 2, 3], "value": [10, 20, 30]})

    report = validation_utils.generate_data_quality_report(df)

    assert report["row_count"] == 3
    assert report["duplicate_count"] == 0
    assert all(report["missing_data"][col]["count"] == 0 for col in ["id", "value"])


@pytest.mark.skipif(not HAS_SPARK, reason="Spark not installed")
def test_generate_data_quality_report_spark(spark_session):
    """Test data quality report with Spark."""
    df = spark_session.createDataFrame(
        [(1, "A"), (2, "B"), (None, "C")], ["id", "name"]
    )

    report = validation_utils.generate_data_quality_report(df)

    assert report["row_count"] == 3
    assert report["column_count"] == 2


# ============================================================================
# check_schema_match tests
# ============================================================================


def test_check_schema_match_valid():
    """Test schema validation passes when schemas match."""
    df = pd.DataFrame({"id": [1, 2], "name": ["A", "B"]})
    expected = {"id": "int64", "name": "object"}

    result = validation_utils.check_schema_match(df, expected)

    assert result["is_valid"] is True
    assert len(result["issues"]) == 0


def test_check_schema_match_missing_column():
    """Test schema validation fails with missing column."""
    df = pd.DataFrame({"id": [1, 2]})
    expected = {"id": "int64", "name": "object"}

    result = validation_utils.check_schema_match(df, expected)

    assert result["is_valid"] is False
    assert any("Missing column" in issue for issue in result["issues"])


def test_check_schema_match_type_mismatch():
    """Test schema validation fails with type mismatch."""
    df = pd.DataFrame({"id": ["1", "2"]})  # String instead of int
    expected = {"id": "int64"}

    result = validation_utils.check_schema_match(df, expected)

    assert result["is_valid"] is False
    assert any("Type mismatch" in issue for issue in result["issues"])


def test_check_schema_match_extra_column_strict():
    """Test schema validation fails with extra column in strict mode."""
    df = pd.DataFrame({"id": [1, 2], "extra": [3, 4]})
    expected = {"id": "int64"}

    result = validation_utils.check_schema_match(df, expected, strict=True)

    assert result["is_valid"] is False
    assert any("Unexpected column" in issue for issue in result["issues"])


def test_check_schema_match_extra_column_non_strict():
    """Test schema validation passes with extra column in non-strict mode."""
    df = pd.DataFrame({"id": [1, 2], "extra": [3, 4]})
    expected = {"id": "int64"}

    result = validation_utils.check_schema_match(df, expected, strict=False)

    assert result["is_valid"] is True


@pytest.mark.skipif(not HAS_SPARK, reason="Spark not installed")
def test_check_schema_match_spark(spark_session):
    """Test schema validation with Spark."""
    df = spark_session.createDataFrame([(1, "A"), (2, "B")], ["id", "name"])

    # Spark uses different type names
    expected = {"id": "LongType()", "name": "StringType()"}

    result = validation_utils.check_schema_match(df, expected, strict=False)

    # Just verify structure
    assert "is_valid" in result
    assert "issues" in result
