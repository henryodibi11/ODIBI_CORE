"""
Unit tests for data_ops module.

Tests data manipulation functions for both Pandas and Spark engines:
- detect_engine
- safe_join
- filter_rows
- group_and_aggregate
- pivot_table
- unpivot
- deduplicate
- sort_data
- select_columns
- rename_columns
"""

import pytest
import pandas as pd
import numpy as np
from odibi_core.functions import data_ops

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
        SparkSession.builder.master("local[1]").appName("test_data_ops").getOrCreate()
    )
    yield spark
    spark.stop()


@pytest.fixture
def sample_pandas_df():
    """Sample Pandas DataFrame for testing."""
    return pd.DataFrame(
        {
            "id": [1, 2, 3, 4, 5],
            "category": ["A", "B", "A", "B", "C"],
            "value": [10, 20, 30, 40, 50],
        }
    )


@pytest.fixture
def sample_spark_df(spark_session, sample_pandas_df):
    """Sample Spark DataFrame for testing."""
    if not HAS_SPARK:
        pytest.skip("Spark not available")
    return spark_session.createDataFrame(sample_pandas_df)


# ============================================================================
# detect_engine tests
# ============================================================================


def test_detect_engine_pandas(sample_pandas_df):
    """Test engine detection for Pandas DataFrame."""
    result = data_ops.detect_engine(sample_pandas_df)
    assert result == "pandas"


@pytest.mark.skipif(not HAS_SPARK, reason="Spark not installed")
def test_detect_engine_spark(sample_spark_df):
    """Test engine detection for Spark DataFrame."""
    result = data_ops.detect_engine(sample_spark_df)
    assert result == "spark"


def test_detect_engine_invalid():
    """Test engine detection with invalid DataFrame type."""
    with pytest.raises(TypeError):
        data_ops.detect_engine([1, 2, 3])


# ============================================================================
# safe_join tests
# ============================================================================


def test_safe_join_pandas_inner():
    """Test safe_join with Pandas engine using inner join."""
    left = pd.DataFrame({"id": [1, 2, 3], "value": [10, 20, 30]})
    right = pd.DataFrame({"id": [1, 2, 4], "score": [100, 200, 400]})

    result = data_ops.safe_join(left, right, on="id", how="inner")

    assert len(result) == 2
    assert "value" in result.columns
    assert "score" in result.columns
    assert list(result["id"]) == [1, 2]


def test_safe_join_pandas_left():
    """Test safe_join with Pandas engine using left join."""
    left = pd.DataFrame({"id": [1, 2, 3], "value": [10, 20, 30]})
    right = pd.DataFrame({"id": [1, 2], "score": [100, 200]})

    result = data_ops.safe_join(left, right, on="id", how="left")

    assert len(result) == 3
    assert result["score"].isna().sum() == 1


def test_safe_join_pandas_multiple_keys():
    """Test safe_join with multiple join keys."""
    left = pd.DataFrame(
        {"id": [1, 2, 3], "type": ["A", "B", "A"], "value": [10, 20, 30]}
    )
    right = pd.DataFrame(
        {"id": [1, 2, 3], "type": ["A", "B", "C"], "score": [100, 200, 300]}
    )

    result = data_ops.safe_join(left, right, on=["id", "type"], how="inner")
    assert len(result) == 2


def test_safe_join_pandas_missing_key():
    """Test safe_join raises error for missing join key."""
    left = pd.DataFrame({"id": [1, 2], "value": [10, 20]})
    right = pd.DataFrame({"key": [1, 2], "score": [100, 200]})

    with pytest.raises(ValueError, match="Join key.*not found"):
        data_ops.safe_join(left, right, on="id")


@pytest.mark.skipif(not HAS_SPARK, reason="Spark not installed")
def test_safe_join_spark(spark_session):
    """Test safe_join with Spark engine."""
    left = spark_session.createDataFrame([(1, 10), (2, 20), (3, 30)], ["id", "value"])
    right = spark_session.createDataFrame(
        [(1, 100), (2, 200), (4, 400)], ["id", "score"]
    )

    result = data_ops.safe_join(left, right, on="id", how="inner")

    assert result.count() == 2
    assert "value" in result.columns
    assert "score" in result.columns


# ============================================================================
# filter_rows tests
# ============================================================================


def test_filter_rows_pandas_string_condition():
    """Test filter_rows with string SQL condition in Pandas."""
    df = pd.DataFrame({"value": [1, 2, 3, 4, 5]})

    result = data_ops.filter_rows(df, "value > 2")

    assert len(result) == 3
    assert result["value"].tolist() == [3, 4, 5]


def test_filter_rows_pandas_complex_condition():
    """Test filter_rows with complex condition."""
    df = pd.DataFrame({"value": [1, 2, 3, 4, 5], "category": ["A", "B", "A", "B", "A"]})

    result = data_ops.filter_rows(df, "value > 2 and category == 'A'")

    assert len(result) == 2
    assert result["value"].tolist() == [3, 5]


def test_filter_rows_pandas_boolean_mask():
    """Test filter_rows with boolean mask."""
    df = pd.DataFrame({"value": [1, 2, 3, 4, 5]})
    mask = df["value"] > 3

    result = data_ops.filter_rows(df, mask)

    assert len(result) == 2
    assert result["value"].tolist() == [4, 5]


def test_filter_rows_empty_result():
    """Test filter_rows with condition that matches no rows."""
    df = pd.DataFrame({"value": [1, 2, 3]})

    result = data_ops.filter_rows(df, "value > 10")

    assert len(result) == 0


@pytest.mark.skipif(not HAS_SPARK, reason="Spark not installed")
def test_filter_rows_spark(spark_session):
    """Test filter_rows with Spark engine."""
    df = spark_session.createDataFrame([(1,), (2,), (3,), (4,), (5,)], ["value"])

    result = data_ops.filter_rows(df, "value > 2")

    assert result.count() == 3


# ============================================================================
# group_and_aggregate tests
# ============================================================================


def test_group_and_aggregate_pandas_single_function():
    """Test group_and_aggregate with single aggregation function."""
    df = pd.DataFrame({"category": ["A", "A", "B", "B"], "value": [10, 20, 30, 40]})

    result = data_ops.group_and_aggregate(df, "category", {"value": "sum"})

    assert len(result) == 2
    assert "category" in result.columns
    assert result[result["category"] == "A"]["value"].values[0] == 30


def test_group_and_aggregate_pandas_multiple_functions():
    """Test group_and_aggregate with multiple aggregation functions."""
    df = pd.DataFrame({"category": ["A", "A", "B", "B"], "value": [10, 20, 30, 40]})

    result = data_ops.group_and_aggregate(
        df, "category", {"value": ["sum", "mean", "max"]}
    )

    assert len(result) == 2


def test_group_and_aggregate_multiple_columns():
    """Test group_and_aggregate with multiple groupby columns."""
    df = pd.DataFrame(
        {
            "cat1": ["A", "A", "B", "B"],
            "cat2": ["X", "Y", "X", "Y"],
            "value": [10, 20, 30, 40],
        }
    )

    result = data_ops.group_and_aggregate(df, ["cat1", "cat2"], {"value": "sum"})

    assert len(result) == 4


def test_group_and_aggregate_empty_df():
    """Test group_and_aggregate with empty DataFrame."""
    df = pd.DataFrame({"category": [], "value": []})

    result = data_ops.group_and_aggregate(df, "category", {"value": "sum"})

    assert len(result) == 0


@pytest.mark.skipif(not HAS_SPARK, reason="Spark not installed")
def test_group_and_aggregate_spark(spark_session):
    """Test group_and_aggregate with Spark engine."""
    df = spark_session.createDataFrame(
        [("A", 10), ("A", 20), ("B", 30), ("B", 40)], ["category", "value"]
    )

    result = data_ops.group_and_aggregate(df, "category", {"value": "sum"})

    assert result.count() == 2


# ============================================================================
# pivot_table tests
# ============================================================================


def test_pivot_table_pandas():
    """Test pivot_table with Pandas engine."""
    df = pd.DataFrame(
        {
            "date": ["2023-01", "2023-01", "2023-02", "2023-02"],
            "product": ["A", "B", "A", "B"],
            "sales": [100, 200, 150, 250],
        }
    )

    result = data_ops.pivot_table(df, index="date", columns="product", values="sales")

    assert "A" in result.columns
    assert "B" in result.columns
    assert len(result) == 2


def test_pivot_table_with_aggregation():
    """Test pivot_table with different aggregation functions."""
    df = pd.DataFrame(
        {
            "date": ["2023-01", "2023-01", "2023-01"],
            "product": ["A", "A", "B"],
            "sales": [100, 150, 200],
        }
    )

    result = data_ops.pivot_table(
        df, index="date", columns="product", values="sales", aggfunc="mean"
    )

    assert result.loc["2023-01", "A"] == 125


@pytest.mark.skipif(not HAS_SPARK, reason="Spark not installed")
def test_pivot_table_spark(spark_session):
    """Test pivot_table with Spark engine."""
    df = spark_session.createDataFrame(
        [
            ("2023-01", "A", 100),
            ("2023-01", "B", 200),
            ("2023-02", "A", 150),
            ("2023-02", "B", 250),
        ],
        ["date", "product", "sales"],
    )

    result = data_ops.pivot_table(df, index="date", columns="product", values="sales")

    assert result.count() == 2


# ============================================================================
# unpivot tests
# ============================================================================


def test_unpivot_pandas():
    """Test unpivot (melt) with Pandas engine."""
    df = pd.DataFrame({"id": [1, 2], "A": [10, 20], "B": [30, 40]})

    result = data_ops.unpivot(df, id_vars="id", value_vars=["A", "B"])

    assert len(result) == 4
    assert "variable" in result.columns
    assert "value" in result.columns


def test_unpivot_custom_names():
    """Test unpivot with custom column names."""
    df = pd.DataFrame({"id": [1, 2], "A": [10, 20], "B": [30, 40]})

    result = data_ops.unpivot(
        df, id_vars="id", value_vars=["A", "B"], var_name="metric", value_name="amount"
    )

    assert "metric" in result.columns
    assert "amount" in result.columns


def test_unpivot_auto_value_vars():
    """Test unpivot with automatic value_vars detection."""
    df = pd.DataFrame({"id": [1, 2], "A": [10, 20], "B": [30, 40]})

    result = data_ops.unpivot(df, id_vars="id")

    assert len(result) == 4


@pytest.mark.skipif(not HAS_SPARK, reason="Spark not installed")
def test_unpivot_spark(spark_session):
    """Test unpivot with Spark engine."""
    df = spark_session.createDataFrame([(1, 10, 30), (2, 20, 40)], ["id", "A", "B"])

    result = data_ops.unpivot(df, id_vars="id", value_vars=["A", "B"])

    assert result.count() == 4


# ============================================================================
# deduplicate tests
# ============================================================================


def test_deduplicate_pandas_all_columns():
    """Test deduplicate considering all columns."""
    df = pd.DataFrame({"id": [1, 1, 2, 3], "value": [10, 10, 20, 30]})

    result = data_ops.deduplicate(df)

    assert len(result) == 3


def test_deduplicate_pandas_subset():
    """Test deduplicate with specific column subset."""
    df = pd.DataFrame({"id": [1, 1, 2, 3], "value": [10, 20, 30, 40]})

    result = data_ops.deduplicate(df, subset="id")

    assert len(result) == 3
    assert 1 in result["id"].values


def test_deduplicate_keep_last():
    """Test deduplicate keeping last occurrence."""
    df = pd.DataFrame({"id": [1, 1, 2], "value": [10, 20, 30]})

    result = data_ops.deduplicate(df, subset="id", keep="last")

    assert len(result) == 2
    assert result[result["id"] == 1]["value"].values[0] == 20


def test_deduplicate_no_duplicates():
    """Test deduplicate on DataFrame with no duplicates."""
    df = pd.DataFrame({"id": [1, 2, 3], "value": [10, 20, 30]})

    result = data_ops.deduplicate(df)

    assert len(result) == 3


@pytest.mark.skipif(not HAS_SPARK, reason="Spark not installed")
def test_deduplicate_spark(spark_session):
    """Test deduplicate with Spark engine."""
    df = spark_session.createDataFrame(
        [(1, 10), (1, 10), (2, 20), (3, 30)], ["id", "value"]
    )

    result = data_ops.deduplicate(df, subset="id")

    assert result.count() == 3


# ============================================================================
# sort_data tests
# ============================================================================


def test_sort_data_pandas_ascending():
    """Test sort_data with ascending order."""
    df = pd.DataFrame({"value": [3, 1, 2]})

    result = data_ops.sort_data(df, by="value", ascending=True)

    assert result["value"].tolist() == [1, 2, 3]


def test_sort_data_pandas_descending():
    """Test sort_data with descending order."""
    df = pd.DataFrame({"value": [3, 1, 2]})

    result = data_ops.sort_data(df, by="value", ascending=False)

    assert result["value"].tolist() == [3, 2, 1]


def test_sort_data_multiple_columns():
    """Test sort_data with multiple columns."""
    df = pd.DataFrame({"cat": ["A", "A", "B", "B"], "value": [2, 1, 4, 3]})

    result = data_ops.sort_data(df, by=["cat", "value"], ascending=True)

    assert result["value"].tolist() == [1, 2, 3, 4]


def test_sort_data_mixed_order():
    """Test sort_data with mixed ascending/descending."""
    df = pd.DataFrame({"cat": ["A", "B", "A", "B"], "value": [1, 3, 2, 4]})

    result = data_ops.sort_data(df, by=["cat", "value"], ascending=[True, False])

    assert result.iloc[0]["value"] == 2
    assert result.iloc[1]["value"] == 1


@pytest.mark.skipif(not HAS_SPARK, reason="Spark not installed")
def test_sort_data_spark(spark_session):
    """Test sort_data with Spark engine."""
    df = spark_session.createDataFrame([(3,), (1,), (2,)], ["value"])

    result = data_ops.sort_data(df, by="value", ascending=True)

    rows = result.collect()
    assert rows[0]["value"] == 1


# ============================================================================
# select_columns tests
# ============================================================================


def test_select_columns_pandas():
    """Test select_columns with Pandas engine."""
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4], "c": [5, 6]})

    result = data_ops.select_columns(df, ["a", "c"])

    assert list(result.columns) == ["a", "c"]
    assert len(result) == 2


def test_select_columns_single():
    """Test select_columns with single column."""
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})

    result = data_ops.select_columns(df, ["a"])

    assert list(result.columns) == ["a"]


@pytest.mark.skipif(not HAS_SPARK, reason="Spark not installed")
def test_select_columns_spark(spark_session):
    """Test select_columns with Spark engine."""
    df = spark_session.createDataFrame([(1, 3, 5), (2, 4, 6)], ["a", "b", "c"])

    result = data_ops.select_columns(df, ["a", "c"])

    assert result.columns == ["a", "c"]


# ============================================================================
# rename_columns tests
# ============================================================================


def test_rename_columns_pandas():
    """Test rename_columns with Pandas engine."""
    df = pd.DataFrame({"old_name": [1, 2]})

    result = data_ops.rename_columns(df, {"old_name": "new_name"})

    assert list(result.columns) == ["new_name"]


def test_rename_columns_multiple():
    """Test rename_columns with multiple columns."""
    df = pd.DataFrame({"a": [1], "b": [2], "c": [3]})

    result = data_ops.rename_columns(df, {"a": "x", "b": "y"})

    assert list(result.columns) == ["x", "y", "c"]


def test_rename_columns_preserve_original():
    """Test that rename_columns doesn't modify original DataFrame."""
    df = pd.DataFrame({"old": [1, 2]})

    result = data_ops.rename_columns(df, {"old": "new"})

    assert "old" in df.columns
    assert "new" in result.columns


@pytest.mark.skipif(not HAS_SPARK, reason="Spark not installed")
def test_rename_columns_spark(spark_session):
    """Test rename_columns with Spark engine."""
    df = spark_session.createDataFrame([(1,), (2,)], ["old_name"])

    result = data_ops.rename_columns(df, {"old_name": "new_name"})

    assert "new_name" in result.columns
