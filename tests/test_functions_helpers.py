"""
Unit tests for helpers module.

Tests ODIBI-specific helper functions:
- resolve_column
- auto_rename
- compare_results
- get_metadata
- sample_data
- add_metadata_columns
- ensure_columns_exist
- collect_sample
"""

import pytest
import pandas as pd
from odibi_core.functions import helpers

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
        SparkSession.builder.master("local[1]").appName("test_helpers").getOrCreate()
    )
    yield spark
    spark.stop()


# ============================================================================
# resolve_column tests
# ============================================================================


def test_resolve_column_by_name():
    """Test resolving column by name."""
    df = pd.DataFrame({"a": [1], "b": [2], "c": [3]})

    result = helpers.resolve_column(df, "a")

    assert result == "a"


def test_resolve_column_by_index():
    """Test resolving column by index."""
    df = pd.DataFrame({"a": [1], "b": [2], "c": [3]})

    result = helpers.resolve_column(df, 1)

    assert result == "b"


def test_resolve_column_index_zero():
    """Test resolving first column by index 0."""
    df = pd.DataFrame({"a": [1], "b": [2]})

    result = helpers.resolve_column(df, 0)

    assert result == "a"


def test_resolve_column_invalid_name():
    """Test error when column name doesn't exist."""
    df = pd.DataFrame({"a": [1], "b": [2]})

    with pytest.raises(ValueError, match="not found"):
        helpers.resolve_column(df, "nonexistent")


def test_resolve_column_invalid_index():
    """Test error when index out of range."""
    df = pd.DataFrame({"a": [1], "b": [2]})

    with pytest.raises(IndexError, match="out of range"):
        helpers.resolve_column(df, 5)


def test_resolve_column_negative_index():
    """Test error with negative index."""
    df = pd.DataFrame({"a": [1], "b": [2]})

    with pytest.raises(IndexError):
        helpers.resolve_column(df, -1)


# ============================================================================
# auto_rename tests
# ============================================================================


def test_auto_rename_prefix():
    """Test automatic column renaming with prefix."""
    df = pd.DataFrame({"id": [1], "value": [10]})

    result = helpers.auto_rename(df, prefix="raw_")

    assert list(result.columns) == ["raw_id", "raw_value"]


def test_auto_rename_suffix():
    """Test automatic column renaming with suffix."""
    df = pd.DataFrame({"id": [1], "value": [10]})

    result = helpers.auto_rename(df, suffix="_old")

    assert list(result.columns) == ["id_old", "value_old"]


def test_auto_rename_prefix_and_suffix():
    """Test renaming with both prefix and suffix."""
    df = pd.DataFrame({"value": [10]})

    result = helpers.auto_rename(df, prefix="bronze_", suffix="_raw")

    assert list(result.columns) == ["bronze_value_raw"]


def test_auto_rename_exclude():
    """Test renaming with excluded columns."""
    df = pd.DataFrame({"id": [1], "value": [10]})

    result = helpers.auto_rename(df, prefix="raw_", exclude=["id"])

    assert list(result.columns) == ["id", "raw_value"]


def test_auto_rename_exclude_multiple():
    """Test renaming excluding multiple columns."""
    df = pd.DataFrame({"id": [1], "key": [2], "value": [10]})

    result = helpers.auto_rename(df, prefix="raw_", exclude=["id", "key"])

    assert list(result.columns) == ["id", "key", "raw_value"]


@pytest.mark.skipif(not HAS_SPARK, reason="Spark not installed")
def test_auto_rename_spark(spark_session):
    """Test auto renaming with Spark."""
    df = spark_session.createDataFrame([(1, 10)], ["id", "value"])

    result = helpers.auto_rename(df, prefix="raw_", exclude=["id"])

    assert "id" in result.columns
    assert "raw_value" in result.columns


# ============================================================================
# compare_results tests
# ============================================================================


def test_compare_results_identical():
    """Test comparison of identical DataFrames."""
    df_pd = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    df_pd2 = pd.DataFrame({"a": [1, 2], "b": [3, 4]})

    result = helpers.compare_results(df_pd, df_pd2)

    assert result["row_match"] is True
    assert result["col_match"] is True
    assert result["data_match"] is True


def test_compare_results_different_rows():
    """Test comparison with different row counts."""
    df1 = pd.DataFrame({"a": [1, 2]})
    df2 = pd.DataFrame({"a": [1, 2, 3]})

    result = helpers.compare_results(df1, df2)

    assert result["row_match"] is False


def test_compare_results_different_columns():
    """Test comparison with different columns."""
    df1 = pd.DataFrame({"a": [1, 2]})
    df2 = pd.DataFrame({"b": [1, 2]})

    result = helpers.compare_results(df1, df2)

    assert result["col_match"] is False


def test_compare_results_different_data():
    """Test comparison with different data values."""
    df1 = pd.DataFrame({"a": [1, 2]})
    df2 = pd.DataFrame({"a": [1, 3]})

    result = helpers.compare_results(df1, df2)

    assert result["row_match"] is True
    assert result["col_match"] is True
    assert result["data_match"] is False


@pytest.mark.skipif(not HAS_SPARK, reason="Spark not installed")
def test_compare_results_spark(spark_session):
    """Test comparing Pandas and Spark DataFrames."""
    df_pd = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    df_sp = spark_session.createDataFrame([(1, 3), (2, 4)], ["a", "b"])

    result = helpers.compare_results(df_pd, df_sp)

    assert result["row_match"] is True
    assert result["col_match"] is True


# ============================================================================
# get_metadata tests
# ============================================================================


def test_get_metadata_pandas():
    """Test metadata extraction from Pandas DataFrame."""
    df = pd.DataFrame({"id": [1, 2], "value": [10, 20]})

    meta = helpers.get_metadata(df)

    assert meta["row_count"] == 2
    assert meta["column_count"] == 2
    assert "id" in meta["columns"]
    assert "value" in meta["columns"]
    assert "schema" in meta
    assert "memory_usage_bytes" in meta


def test_get_metadata_schema():
    """Test metadata includes schema information."""
    df = pd.DataFrame({"int_col": [1, 2], "str_col": ["a", "b"]})

    meta = helpers.get_metadata(df)

    assert "int_col" in meta["schema"]
    assert "str_col" in meta["schema"]


def test_get_metadata_empty_df():
    """Test metadata for empty DataFrame."""
    df = pd.DataFrame({"a": [], "b": []})

    meta = helpers.get_metadata(df)

    assert meta["row_count"] == 0
    assert meta["column_count"] == 2


@pytest.mark.skipif(not HAS_SPARK, reason="Spark not installed")
def test_get_metadata_spark(spark_session):
    """Test metadata extraction from Spark DataFrame."""
    df = spark_session.createDataFrame([(1, 10), (2, 20)], ["id", "value"])

    meta = helpers.get_metadata(df)

    assert meta["row_count"] == 2
    assert meta["column_count"] == 2
    assert meta["memory_usage_bytes"] is None  # Not available in Spark


# ============================================================================
# sample_data tests
# ============================================================================


def test_sample_data_head():
    """Test sampling data from head."""
    df = pd.DataFrame({"value": range(100)})

    sample = helpers.sample_data(df, n=5, method="head")

    assert len(sample) == 5
    assert sample["value"].tolist() == [0, 1, 2, 3, 4]


def test_sample_data_tail():
    """Test sampling data from tail."""
    df = pd.DataFrame({"value": range(100)})

    sample = helpers.sample_data(df, n=5, method="tail")

    assert len(sample) == 5
    assert sample["value"].tolist() == [95, 96, 97, 98, 99]


def test_sample_data_random():
    """Test random sampling."""
    df = pd.DataFrame({"value": range(100)})

    sample = helpers.sample_data(df, n=5, method="random")

    assert len(sample) == 5


def test_sample_data_n_exceeds_length():
    """Test sampling when n exceeds DataFrame length."""
    df = pd.DataFrame({"value": [1, 2, 3]})

    sample = helpers.sample_data(df, n=10, method="random")

    assert len(sample) == 3


def test_sample_data_invalid_method():
    """Test error with invalid sampling method."""
    df = pd.DataFrame({"value": [1, 2, 3]})

    with pytest.raises(ValueError, match="Invalid method"):
        helpers.sample_data(df, n=2, method="invalid")


@pytest.mark.skipif(not HAS_SPARK, reason="Spark not installed")
def test_sample_data_spark(spark_session):
    """Test data sampling with Spark."""
    df = spark_session.createDataFrame([(i,) for i in range(100)], ["value"])

    sample = helpers.sample_data(df, n=5, method="head")

    assert sample.count() == 5


# ============================================================================
# add_metadata_columns tests
# ============================================================================


def test_add_metadata_columns_run_id():
    """Test adding run_id metadata column."""
    df = pd.DataFrame({"value": [1, 2, 3]})

    result = helpers.add_metadata_columns(df, run_id="run123", timestamp=False)

    assert "odibi_run_id" in result.columns
    assert all(result["odibi_run_id"] == "run123")


def test_add_metadata_columns_timestamp():
    """Test adding timestamp metadata column."""
    df = pd.DataFrame({"value": [1, 2, 3]})

    result = helpers.add_metadata_columns(df, timestamp=True, run_id=None)

    assert "odibi_timestamp" in result.columns
    assert pd.api.types.is_datetime64_any_dtype(result["odibi_timestamp"])


def test_add_metadata_columns_source():
    """Test adding source metadata column."""
    df = pd.DataFrame({"value": [1, 2, 3]})

    result = helpers.add_metadata_columns(
        df, source="bronze", timestamp=False, run_id=None
    )

    assert "odibi_source" in result.columns
    assert all(result["odibi_source"] == "bronze")


def test_add_metadata_columns_all():
    """Test adding all metadata columns."""
    df = pd.DataFrame({"value": [1, 2, 3]})

    result = helpers.add_metadata_columns(
        df, run_id="run123", timestamp=True, source="bronze"
    )

    assert "odibi_run_id" in result.columns
    assert "odibi_timestamp" in result.columns
    assert "odibi_source" in result.columns


@pytest.mark.skipif(not HAS_SPARK, reason="Spark not installed")
def test_add_metadata_columns_spark(spark_session):
    """Test adding metadata columns with Spark."""
    df = spark_session.createDataFrame([(1,), (2,), (3,)], ["value"])

    result = helpers.add_metadata_columns(
        df, run_id="run123", timestamp=True, source="bronze"
    )

    assert "odibi_run_id" in result.columns
    assert "odibi_timestamp" in result.columns
    assert "odibi_source" in result.columns


# ============================================================================
# ensure_columns_exist tests
# ============================================================================


def test_ensure_columns_exist_valid():
    """Test column existence validation passes."""
    df = pd.DataFrame({"a": [1], "b": [2], "c": [3]})

    result = helpers.ensure_columns_exist(df, ["a", "b"])

    assert result is True


def test_ensure_columns_exist_all_columns():
    """Test validating all columns exist."""
    df = pd.DataFrame({"a": [1], "b": [2]})

    result = helpers.ensure_columns_exist(df, ["a", "b"])

    assert result is True


def test_ensure_columns_exist_missing_raise():
    """Test validation raises error for missing columns."""
    df = pd.DataFrame({"a": [1], "b": [2]})

    with pytest.raises(ValueError, match="Missing required columns"):
        helpers.ensure_columns_exist(df, ["a", "c"], raise_error=True)


def test_ensure_columns_exist_missing_no_raise():
    """Test validation returns False for missing columns without raising."""
    df = pd.DataFrame({"a": [1], "b": [2]})

    result = helpers.ensure_columns_exist(df, ["a", "c"], raise_error=False)

    assert result is False


def test_ensure_columns_exist_empty_list():
    """Test validation with empty required columns list."""
    df = pd.DataFrame({"a": [1], "b": [2]})

    result = helpers.ensure_columns_exist(df, [])

    assert result is True


# ============================================================================
# collect_sample tests
# ============================================================================


def test_collect_sample_pandas():
    """Test collecting sample as Pandas DataFrame."""
    df = pd.DataFrame({"value": range(100)})

    sample = helpers.collect_sample(df, n=5)

    assert isinstance(sample, pd.DataFrame)
    assert len(sample) == 5


def test_collect_sample_small_df():
    """Test collecting sample from small DataFrame."""
    df = pd.DataFrame({"value": [1, 2, 3]})

    sample = helpers.collect_sample(df, n=10)

    assert len(sample) == 3


def test_collect_sample_returns_pandas():
    """Test that collect_sample always returns Pandas DataFrame."""
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})

    sample = helpers.collect_sample(df, n=2)

    assert type(sample).__name__ == "DataFrame"
    assert "pandas" in type(sample).__module__


@pytest.mark.skipif(not HAS_SPARK, reason="Spark not installed")
def test_collect_sample_spark(spark_session):
    """Test collecting sample from Spark as Pandas."""
    df = spark_session.createDataFrame([(i,) for i in range(100)], ["value"])

    sample = helpers.collect_sample(df, n=5)

    assert isinstance(sample, pd.DataFrame)
    assert len(sample) == 5


@pytest.mark.skipif(not HAS_SPARK, reason="Spark not installed")
def test_collect_sample_spark_always_pandas(spark_session):
    """Test Spark DataFrame is converted to Pandas."""
    df = spark_session.createDataFrame([(1, 2), (3, 4)], ["a", "b"])

    sample = helpers.collect_sample(df, n=2)

    # Verify it's a Pandas DataFrame, not Spark
    assert "pandas" in type(sample).__module__
    assert not hasattr(sample, "toPandas")  # Spark DataFrames have this method
