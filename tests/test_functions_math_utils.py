"""
Unit tests for math_utils module.

Tests mathematical and statistical functions for both Pandas and Spark:
- safe_divide
- calculate_z_score
- normalize_min_max
- calculate_percentile
- round_numeric
- calculate_moving_average
- calculate_cumulative_sum
- calculate_percent_change
- clip_values
"""

import pytest
import pandas as pd
import numpy as np
from odibi_core.functions import math_utils

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
        SparkSession.builder.master("local[1]").appName("test_math_utils").getOrCreate()
    )
    yield spark
    spark.stop()


# ============================================================================
# safe_divide tests
# ============================================================================


def test_safe_divide_pandas_normal():
    """Test safe_divide with normal division in Pandas."""
    df = pd.DataFrame({"a": [10, 20, 30], "b": [2, 5, 10]})

    result = math_utils.safe_divide(df, "a", "b", "ratio")

    assert "ratio" in result.columns
    assert result["ratio"].tolist() == [5.0, 4.0, 3.0]


def test_safe_divide_pandas_zero_denominator():
    """Test safe_divide with zero denominator."""
    df = pd.DataFrame({"a": [10, 20, 30], "b": [2, 0, 5]})

    result = math_utils.safe_divide(df, "a", "b", "ratio", fill_value=0)

    assert result["ratio"].tolist() == [5.0, 0.0, 6.0]


def test_safe_divide_custom_fill_value():
    """Test safe_divide with custom fill value."""
    df = pd.DataFrame({"a": [10, 20], "b": [0, 5]})

    result = math_utils.safe_divide(df, "a", "b", "ratio", fill_value=-1)

    assert result["ratio"].tolist() == [-1.0, 4.0]


def test_safe_divide_all_zeros():
    """Test safe_divide when all denominators are zero."""
    df = pd.DataFrame({"a": [10, 20, 30], "b": [0, 0, 0]})

    result = math_utils.safe_divide(df, "a", "b", "ratio", fill_value=999)

    assert all(result["ratio"] == 999)


@pytest.mark.skipif(not HAS_SPARK, reason="Spark not installed")
def test_safe_divide_spark(spark_session):
    """Test safe_divide with Spark engine."""
    df = spark_session.createDataFrame([(10, 2), (20, 0), (30, 5)], ["a", "b"])

    result = math_utils.safe_divide(df, "a", "b", "ratio", fill_value=0)

    rows = result.collect()
    assert rows[0]["ratio"] == 5.0
    assert rows[1]["ratio"] == 0.0


# ============================================================================
# calculate_z_score tests
# ============================================================================


def test_calculate_z_score_pandas():
    """Test z-score calculation with Pandas."""
    df = pd.DataFrame({"value": [10, 20, 30, 40, 50]})

    result = math_utils.calculate_z_score(df, "value")

    assert "value_zscore" in result.columns
    # Mean is 30, std is ~15.81
    assert abs(result["value_zscore"].mean()) < 0.01


def test_calculate_z_score_custom_column():
    """Test z-score with custom result column name."""
    df = pd.DataFrame({"value": [1, 2, 3, 4, 5]})

    result = math_utils.calculate_z_score(df, "value", result_col="z")

    assert "z" in result.columns


def test_calculate_z_score_zero_std():
    """Test z-score when standard deviation is zero."""
    df = pd.DataFrame({"value": [5, 5, 5, 5]})

    result = math_utils.calculate_z_score(df, "value")

    assert all(result["value_zscore"] == 0.0)


def test_calculate_z_score_single_value():
    """Test z-score with single value."""
    df = pd.DataFrame({"value": [42]})

    result = math_utils.calculate_z_score(df, "value")

    assert result["value_zscore"].isna()[0] or result["value_zscore"][0] == 0.0


@pytest.mark.skipif(not HAS_SPARK, reason="Spark not installed")
def test_calculate_z_score_spark(spark_session):
    """Test z-score calculation with Spark."""
    df = spark_session.createDataFrame([(10,), (20,), (30,), (40,), (50,)], ["value"])

    result = math_utils.calculate_z_score(df, "value")

    assert "value_zscore" in result.columns


# ============================================================================
# normalize_min_max tests
# ============================================================================


def test_normalize_min_max_pandas_default():
    """Test min-max normalization to [0, 1] range."""
    df = pd.DataFrame({"value": [0, 50, 100]})

    result = math_utils.normalize_min_max(df, "value")

    assert "value_norm" in result.columns
    assert result["value_norm"].tolist() == [0.0, 0.5, 1.0]


def test_normalize_min_max_custom_range():
    """Test min-max normalization to custom range."""
    df = pd.DataFrame({"value": [0, 50, 100]})

    result = math_utils.normalize_min_max(df, "value", min_val=-1, max_val=1)

    assert result["value_norm"].tolist() == [-1.0, 0.0, 1.0]


def test_normalize_min_max_same_values():
    """Test normalization when all values are the same."""
    df = pd.DataFrame({"value": [42, 42, 42]})

    result = math_utils.normalize_min_max(df, "value", min_val=0, max_val=1)

    assert all(result["value_norm"] == 0.0)


def test_normalize_min_max_negative_values():
    """Test normalization with negative values."""
    df = pd.DataFrame({"value": [-10, 0, 10]})

    result = math_utils.normalize_min_max(df, "value")

    assert result["value_norm"].tolist() == [0.0, 0.5, 1.0]


@pytest.mark.skipif(not HAS_SPARK, reason="Spark not installed")
def test_normalize_min_max_spark(spark_session):
    """Test min-max normalization with Spark."""
    df = spark_session.createDataFrame([(0,), (50,), (100,)], ["value"])

    result = math_utils.normalize_min_max(df, "value")

    rows = result.collect()
    assert abs(rows[0]["value_norm"] - 0.0) < 0.01
    assert abs(rows[2]["value_norm"] - 1.0) < 0.01


# ============================================================================
# calculate_percentile tests
# ============================================================================


def test_calculate_percentile_pandas_median():
    """Test percentile calculation for median (50th percentile)."""
    df = pd.DataFrame({"value": [1, 2, 3, 4, 5]})

    result = math_utils.calculate_percentile(df, "value", 0.5)

    assert result == 3.0


def test_calculate_percentile_quartiles():
    """Test percentile calculation for quartiles."""
    df = pd.DataFrame({"value": list(range(1, 101))})

    q25 = math_utils.calculate_percentile(df, "value", 0.25)
    q75 = math_utils.calculate_percentile(df, "value", 0.75)

    assert 24 <= q25 <= 26
    assert 74 <= q75 <= 76


def test_calculate_percentile_extremes():
    """Test percentile at extremes (0th and 100th)."""
    df = pd.DataFrame({"value": [10, 20, 30, 40, 50]})

    p0 = math_utils.calculate_percentile(df, "value", 0.0)
    p100 = math_utils.calculate_percentile(df, "value", 1.0)

    assert p0 == 10.0
    assert p100 == 50.0


@pytest.mark.skipif(not HAS_SPARK, reason="Spark not installed")
def test_calculate_percentile_spark(spark_session):
    """Test percentile calculation with Spark."""
    df = spark_session.createDataFrame([(i,) for i in range(1, 101)], ["value"])

    result = math_utils.calculate_percentile(df, "value", 0.5)

    assert 45 <= result <= 55


# ============================================================================
# round_numeric tests
# ============================================================================


def test_round_numeric_pandas_default():
    """Test rounding to integer (0 decimals)."""
    df = pd.DataFrame({"value": [1.234, 5.678, 9.999]})

    result = math_utils.round_numeric(df, "value", decimals=0)

    assert result["value"].tolist() == [1.0, 6.0, 10.0]


def test_round_numeric_two_decimals():
    """Test rounding to 2 decimal places."""
    df = pd.DataFrame({"value": [1.234, 5.678, 9.999]})

    result = math_utils.round_numeric(df, "value", decimals=2)

    assert result["value"].tolist() == [1.23, 5.68, 10.0]


def test_round_numeric_custom_column():
    """Test rounding to new column."""
    df = pd.DataFrame({"value": [1.234, 5.678]})

    result = math_utils.round_numeric(df, "value", decimals=1, result_col="rounded")

    assert "value" in result.columns
    assert "rounded" in result.columns
    assert result["rounded"].tolist() == [1.2, 5.7]


@pytest.mark.skipif(not HAS_SPARK, reason="Spark not installed")
def test_round_numeric_spark(spark_session):
    """Test rounding with Spark."""
    df = spark_session.createDataFrame([(1.234,), (5.678,), (9.999,)], ["value"])

    result = math_utils.round_numeric(df, "value", decimals=2)

    rows = result.collect()
    assert abs(rows[0]["value"] - 1.23) < 0.01


# ============================================================================
# calculate_moving_average tests
# ============================================================================


def test_calculate_moving_average_pandas():
    """Test moving average calculation with Pandas."""
    df = pd.DataFrame({"value": [10, 20, 30, 40, 50]})

    result = math_utils.calculate_moving_average(df, "value", window=3)

    assert "value_ma3" in result.columns
    assert len(result) == 5


def test_calculate_moving_average_window_2():
    """Test moving average with window size 2."""
    df = pd.DataFrame({"value": [10, 20, 30, 40]})

    result = math_utils.calculate_moving_average(df, "value", window=2)

    # First value is 10, then 15, 25, 35
    assert result["value_ma2"].tolist()[1] == 15.0


def test_calculate_moving_average_custom_column():
    """Test moving average with custom result column."""
    df = pd.DataFrame({"value": [1, 2, 3, 4, 5]})

    result = math_utils.calculate_moving_average(df, "value", window=2, result_col="ma")

    assert "ma" in result.columns


@pytest.mark.skipif(not HAS_SPARK, reason="Spark not installed")
def test_calculate_moving_average_spark(spark_session):
    """Test moving average with Spark (requires order_by)."""
    df = spark_session.createDataFrame(
        [(1, 10), (2, 20), (3, 30), (4, 40), (5, 50)], ["id", "value"]
    )

    result = math_utils.calculate_moving_average(df, "value", window=3, order_by="id")

    assert "value_ma3" in result.columns


# ============================================================================
# calculate_cumulative_sum tests
# ============================================================================


def test_calculate_cumulative_sum_pandas():
    """Test cumulative sum with Pandas."""
    df = pd.DataFrame({"value": [1, 2, 3, 4, 5]})

    result = math_utils.calculate_cumulative_sum(df, "value")

    assert result["value_cumsum"].tolist() == [1, 3, 6, 10, 15]


def test_calculate_cumulative_sum_custom_column():
    """Test cumulative sum with custom result column."""
    df = pd.DataFrame({"value": [10, 20, 30]})

    result = math_utils.calculate_cumulative_sum(df, "value", result_col="cum")

    assert "cum" in result.columns
    assert result["cum"].tolist() == [10, 30, 60]


def test_calculate_cumulative_sum_negative_values():
    """Test cumulative sum with negative values."""
    df = pd.DataFrame({"value": [10, -5, 3, -2]})

    result = math_utils.calculate_cumulative_sum(df, "value")

    assert result["value_cumsum"].tolist() == [10, 5, 8, 6]


@pytest.mark.skipif(not HAS_SPARK, reason="Spark not installed")
def test_calculate_cumulative_sum_spark(spark_session):
    """Test cumulative sum with Spark (requires order_by)."""
    df = spark_session.createDataFrame(
        [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], ["id", "value"]
    )

    result = math_utils.calculate_cumulative_sum(df, "value", order_by="id")

    rows = result.collect()
    assert rows[-1]["value_cumsum"] == 15


# ============================================================================
# calculate_percent_change tests
# ============================================================================


def test_calculate_percent_change_pandas():
    """Test percent change calculation with Pandas."""
    df = pd.DataFrame({"value": [100, 110, 121, 133.1]})

    result = math_utils.calculate_percent_change(df, "value")

    assert "value_pct_change" in result.columns
    # First value should be NaN
    assert pd.isna(result["value_pct_change"].iloc[0])
    # Second value should be ~0.1 (10%)
    assert abs(result["value_pct_change"].iloc[1] - 0.1) < 0.01


def test_calculate_percent_change_periods():
    """Test percent change with different periods."""
    df = pd.DataFrame({"value": [100, 110, 120, 130, 140]})

    result = math_utils.calculate_percent_change(df, "value", periods=2)

    # First two values should be NaN
    assert pd.isna(result["value_pct_change"].iloc[0])
    assert pd.isna(result["value_pct_change"].iloc[1])


def test_calculate_percent_change_zero_base():
    """Test percent change when base value is zero."""
    df = pd.DataFrame({"value": [0, 10, 20]})

    result = math_utils.calculate_percent_change(df, "value")

    # First value is NaN, second should be inf
    assert pd.isna(result["value_pct_change"].iloc[0])


@pytest.mark.skipif(not HAS_SPARK, reason="Spark not installed")
def test_calculate_percent_change_spark(spark_session):
    """Test percent change with Spark (requires order_by)."""
    df = spark_session.createDataFrame([(1, 100), (2, 110), (3, 121)], ["id", "value"])

    result = math_utils.calculate_percent_change(df, "value", order_by="id")

    assert "value_pct_change" in result.columns


# ============================================================================
# clip_values tests
# ============================================================================


def test_clip_values_pandas_both_bounds():
    """Test clipping with both lower and upper bounds."""
    df = pd.DataFrame({"value": [1, 5, 10, 15, 20]})

    result = math_utils.clip_values(df, "value", lower=5, upper=15)

    assert result["value"].tolist() == [5, 5, 10, 15, 15]


def test_clip_values_lower_only():
    """Test clipping with lower bound only."""
    df = pd.DataFrame({"value": [1, 5, 10]})

    result = math_utils.clip_values(df, "value", lower=5)

    assert result["value"].tolist() == [5, 5, 10]


def test_clip_values_upper_only():
    """Test clipping with upper bound only."""
    df = pd.DataFrame({"value": [5, 10, 15]})

    result = math_utils.clip_values(df, "value", upper=10)

    assert result["value"].tolist() == [5, 10, 10]


def test_clip_values_no_clipping_needed():
    """Test clipping when all values are within bounds."""
    df = pd.DataFrame({"value": [5, 7, 9]})

    result = math_utils.clip_values(df, "value", lower=0, upper=10)

    assert result["value"].tolist() == [5, 7, 9]


def test_clip_values_custom_column():
    """Test clipping to new column."""
    df = pd.DataFrame({"value": [1, 10, 20]})

    result = math_utils.clip_values(
        df, "value", lower=5, upper=15, result_col="clipped"
    )

    assert "value" in result.columns
    assert "clipped" in result.columns
    assert result["clipped"].tolist() == [5, 10, 15]


@pytest.mark.skipif(not HAS_SPARK, reason="Spark not installed")
def test_clip_values_spark(spark_session):
    """Test clipping with Spark."""
    df = spark_session.createDataFrame([(1,), (5,), (10,), (15,), (20,)], ["value"])

    result = math_utils.clip_values(df, "value", lower=5, upper=15)

    rows = result.collect()
    assert rows[0]["value"] == 5
    assert rows[-1]["value"] == 15


# ============================================================================
# safe_log tests
# ============================================================================


def test_safe_log_pandas_positive_values():
    """Test safe_log with positive values."""
    df = pd.DataFrame({"value": [1, 10, 100, 1000]})

    result = math_utils.safe_log(df, "value", base=10.0)

    assert "value_log" in result.columns
    assert result["value_log"].tolist() == [0.0, 1.0, 2.0, 3.0]


def test_safe_log_with_zero():
    """Test safe_log handles zero values."""
    df = pd.DataFrame({"value": [1, 10, 0, 100]})

    result = math_utils.safe_log(df, "value", base=10.0, fill_value=-999.0)

    assert result["value_log"].tolist() == [0.0, 1.0, -999.0, 2.0]


def test_safe_log_with_negative():
    """Test safe_log handles negative values."""
    df = pd.DataFrame({"value": [10, -5, 100]})

    result = math_utils.safe_log(df, "value", base=10.0, fill_value=0.0)

    assert result["value_log"].tolist() == [1.0, 0.0, 2.0]


def test_safe_log_base_e():
    """Test safe_log with natural logarithm (base e)."""
    df = pd.DataFrame({"value": [1, np.e, np.e**2]})

    result = math_utils.safe_log(df, "value", base=np.e, fill_value=0.0)

    assert abs(result["value_log"].tolist()[0] - 0.0) < 0.01
    assert abs(result["value_log"].tolist()[1] - 1.0) < 0.01
    assert abs(result["value_log"].tolist()[2] - 2.0) < 0.01


def test_safe_log_base_2():
    """Test safe_log with base 2."""
    df = pd.DataFrame({"value": [2, 4, 8, 16]})

    result = math_utils.safe_log(df, "value", base=2.0)

    assert result["value_log"].tolist() == [1.0, 2.0, 3.0, 4.0]


def test_safe_log_custom_column():
    """Test safe_log with custom result column name."""
    df = pd.DataFrame({"value": [1, 10, 100]})

    result = math_utils.safe_log(df, "value", result_col="log10", base=10.0)

    assert "log10" in result.columns
    assert result["log10"].tolist() == [0.0, 1.0, 2.0]


@pytest.mark.skipif(not HAS_SPARK, reason="Spark not installed")
def test_safe_log_spark(spark_session):
    """Test safe_log with Spark."""
    df = spark_session.createDataFrame([(1,), (10,), (0,), (100,)], ["value"])

    result = math_utils.safe_log(df, "value", base=10.0, fill_value=0.0)

    rows = result.collect()
    assert abs(rows[0]["value_log"] - 0.0) < 0.01
    assert abs(rows[1]["value_log"] - 1.0) < 0.01
    assert abs(rows[2]["value_log"] - 0.0) < 0.01


# ============================================================================
# safe_sqrt tests
# ============================================================================


def test_safe_sqrt_pandas_positive():
    """Test safe_sqrt with positive values."""
    df = pd.DataFrame({"value": [4, 9, 16, 25]})

    result = math_utils.safe_sqrt(df, "value")

    assert "value_sqrt" in result.columns
    assert result["value_sqrt"].tolist() == [2.0, 3.0, 4.0, 5.0]


def test_safe_sqrt_with_negative():
    """Test safe_sqrt handles negative values."""
    df = pd.DataFrame({"value": [4, -1, 16, -9]})

    result = math_utils.safe_sqrt(df, "value", fill_value=-999.0)

    assert result["value_sqrt"].tolist() == [2.0, -999.0, 4.0, -999.0]


def test_safe_sqrt_with_zero():
    """Test safe_sqrt with zero value."""
    df = pd.DataFrame({"value": [0, 4, 9]})

    result = math_utils.safe_sqrt(df, "value")

    assert result["value_sqrt"].tolist() == [0.0, 2.0, 3.0]


def test_safe_sqrt_custom_fill_value():
    """Test safe_sqrt with custom fill value."""
    df = pd.DataFrame({"value": [16, -5, 25]})

    result = math_utils.safe_sqrt(df, "value", fill_value=0.0)

    assert result["value_sqrt"].tolist() == [4.0, 0.0, 5.0]


def test_safe_sqrt_custom_column():
    """Test safe_sqrt with custom result column name."""
    df = pd.DataFrame({"value": [4, 9, 16]})

    result = math_utils.safe_sqrt(df, "value", result_col="square_root")

    assert "square_root" in result.columns
    assert result["square_root"].tolist() == [2.0, 3.0, 4.0]


@pytest.mark.skipif(not HAS_SPARK, reason="Spark not installed")
def test_safe_sqrt_spark(spark_session):
    """Test safe_sqrt with Spark."""
    df = spark_session.createDataFrame([(4,), (-1,), (16,)], ["value"])

    result = math_utils.safe_sqrt(df, "value", fill_value=0.0)

    rows = result.collect()
    assert abs(rows[0]["value_sqrt"] - 2.0) < 0.01
    assert abs(rows[1]["value_sqrt"] - 0.0) < 0.01
    assert abs(rows[2]["value_sqrt"] - 4.0) < 0.01


# ============================================================================
# outlier_detection_iqr tests
# ============================================================================


def test_outlier_detection_iqr_pandas():
    """Test IQR outlier detection with Pandas."""
    df = pd.DataFrame({"value": [1, 2, 3, 4, 5, 100]})

    result = math_utils.outlier_detection_iqr(df, "value")

    assert "value_is_outlier" in result.columns
    # 100 should be detected as an outlier
    assert result["value_is_outlier"].tolist()[-1] is True


def test_outlier_detection_iqr_no_outliers():
    """Test IQR outlier detection with no outliers."""
    df = pd.DataFrame({"value": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]})

    result = math_utils.outlier_detection_iqr(df, "value", multiplier=1.5)

    # No extreme outliers in this dataset
    assert result["value_is_outlier"].sum() == 0


def test_outlier_detection_iqr_custom_multiplier():
    """Test IQR outlier detection with custom multiplier."""
    df = pd.DataFrame({"value": [1, 2, 3, 4, 5, 10]})

    # More lenient outlier detection (higher multiplier)
    result = math_utils.outlier_detection_iqr(df, "value", multiplier=3.0)

    # With higher multiplier, fewer values flagged as outliers
    assert result["value_is_outlier"].sum() <= 1


def test_outlier_detection_iqr_symmetric_outliers():
    """Test IQR outlier detection with outliers on both sides."""
    df = pd.DataFrame({"value": [-100, 1, 2, 3, 4, 5, 100]})

    result = math_utils.outlier_detection_iqr(df, "value")

    # Both -100 and 100 should be outliers
    assert result["value_is_outlier"].iloc[0] is True
    assert result["value_is_outlier"].iloc[-1] is True


def test_outlier_detection_iqr_custom_column():
    """Test IQR outlier detection with custom result column."""
    df = pd.DataFrame({"value": [1, 2, 3, 4, 5, 100]})

    result = math_utils.outlier_detection_iqr(df, "value", result_col="is_anomaly")

    assert "is_anomaly" in result.columns


@pytest.mark.skipif(not HAS_SPARK, reason="Spark not installed")
def test_outlier_detection_iqr_spark(spark_session):
    """Test IQR outlier detection with Spark."""
    df = spark_session.createDataFrame(
        [(1,), (2,), (3,), (4,), (5,), (100,)], ["value"]
    )

    result = math_utils.outlier_detection_iqr(df, "value")

    assert "value_is_outlier" in result.columns


# ============================================================================
# rolling_zscore tests
# ============================================================================


def test_rolling_zscore_pandas():
    """Test rolling z-score calculation with Pandas."""
    df = pd.DataFrame({"value": [10, 12, 11, 10, 25, 12, 11]})

    result = math_utils.rolling_zscore(df, "value", window=5)

    assert "value_rolling_z" in result.columns
    assert len(result) == len(df)


def test_rolling_zscore_window_size():
    """Test rolling z-score with different window sizes."""
    df = pd.DataFrame({"value": [10, 20, 30, 40, 50, 60]})

    result = math_utils.rolling_zscore(df, "value", window=3)

    assert "value_rolling_z" in result.columns
    # Check that values are calculated (not all zero or NaN)
    assert not all(result["value_rolling_z"] == 0.0)


def test_rolling_zscore_spike_detection():
    """Test rolling z-score detects sudden spikes."""
    df = pd.DataFrame({"value": [10, 10, 10, 10, 100, 10, 10]})

    result = math_utils.rolling_zscore(df, "value", window=5)

    # The spike (100) should have a high rolling z-score
    spike_idx = df["value"].idxmax()
    assert abs(result["value_rolling_z"].iloc[spike_idx]) > 1.0


def test_rolling_zscore_custom_column():
    """Test rolling z-score with custom result column."""
    df = pd.DataFrame({"value": [1, 2, 3, 4, 5, 6, 7]})

    result = math_utils.rolling_zscore(df, "value", window=3, result_col="rolling_z")

    assert "rolling_z" in result.columns


def test_rolling_zscore_constant_values():
    """Test rolling z-score with constant values (zero std)."""
    df = pd.DataFrame({"value": [5, 5, 5, 5, 5]})

    result = math_utils.rolling_zscore(df, "value", window=3)

    # All z-scores should be 0 (filled due to zero std)
    assert all(result["value_rolling_z"] == 0.0)


@pytest.mark.skipif(not HAS_SPARK, reason="Spark not installed")
def test_rolling_zscore_spark(spark_session):
    """Test rolling z-score with Spark."""
    df = spark_session.createDataFrame(
        [(1, 10), (2, 12), (3, 11), (4, 10), (5, 25), (6, 12), (7, 11)],
        ["id", "value"]
    )

    result = math_utils.rolling_zscore(df, "value", window=5, order_by="id")

    assert "value_rolling_z" in result.columns


@pytest.mark.skipif(not HAS_SPARK, reason="Spark not installed")
def test_rolling_zscore_spark_missing_order_by(spark_session):
    """Test rolling z-score raises ValueError without order_by for Spark."""
    df = spark_session.createDataFrame([(1, 10), (2, 20)], ["id", "value"])

    with pytest.raises(ValueError, match="order_by parameter required"):
        math_utils.rolling_zscore(df, "value", window=3)
