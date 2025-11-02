"""
Unit tests for datetime_utils module.

Tests date and time manipulation functions for both Pandas and Spark:
- to_datetime
- extract_date_parts
- add_time_delta
- date_diff
- truncate_datetime
- format_datetime
- get_current_timestamp
- is_weekend
- calculate_age
"""

import pytest
import pandas as pd
from datetime import datetime, timedelta
from odibi_core.functions import datetime_utils

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
        .appName("test_datetime_utils")
        .getOrCreate()
    )
    yield spark
    spark.stop()


# ============================================================================
# to_datetime tests
# ============================================================================


def test_to_datetime_pandas():
    """Test converting string to datetime with Pandas."""
    df = pd.DataFrame({"date_str": ["2023-01-15", "2023-02-20"]})

    result = datetime_utils.to_datetime(df, "date_str")

    assert pd.api.types.is_datetime64_any_dtype(result["date_str"])


def test_to_datetime_with_format():
    """Test datetime conversion with explicit format."""
    df = pd.DataFrame({"date_str": ["15/01/2023", "20/02/2023"]})

    result = datetime_utils.to_datetime(df, "date_str", format="%d/%m/%Y")

    assert pd.api.types.is_datetime64_any_dtype(result["date_str"])


def test_to_datetime_new_column():
    """Test datetime conversion to new column."""
    df = pd.DataFrame({"date_str": ["2023-01-15"]})

    result = datetime_utils.to_datetime(df, "date_str", result_col="date")

    assert "date_str" in result.columns
    assert "date" in result.columns


@pytest.mark.skipif(not HAS_SPARK, reason="Spark not installed")
def test_to_datetime_spark(spark_session):
    """Test datetime conversion with Spark."""
    df = spark_session.createDataFrame([("2023-01-15",), ("2023-02-20",)], ["date_str"])

    result = datetime_utils.to_datetime(df, "date_str")

    assert "date_str" in result.columns


# ============================================================================
# extract_date_parts tests
# ============================================================================


def test_extract_date_parts_pandas_basic():
    """Test extracting year, month, day from datetime."""
    df = pd.DataFrame({"date": pd.to_datetime(["2023-01-15", "2023-02-20"])})

    result = datetime_utils.extract_date_parts(
        df, "date", parts=["year", "month", "day"]
    )

    assert "year" in result.columns
    assert "month" in result.columns
    assert "day" in result.columns
    assert result["year"].tolist() == [2023, 2023]
    assert result["month"].tolist() == [1, 2]
    assert result["day"].tolist() == [15, 20]


def test_extract_date_parts_time_components():
    """Test extracting hour, minute, second."""
    df = pd.DataFrame({"timestamp": pd.to_datetime(["2023-01-15 14:30:45"])})

    result = datetime_utils.extract_date_parts(
        df, "timestamp", parts=["hour", "minute", "second"]
    )

    assert result["hour"].tolist() == [14]
    assert result["minute"].tolist() == [30]
    assert result["second"].tolist() == [45]


def test_extract_date_parts_dayofweek():
    """Test extracting day of week."""
    df = pd.DataFrame({"date": pd.to_datetime(["2023-01-15"])})  # Sunday

    result = datetime_utils.extract_date_parts(df, "date", parts=["dayofweek"])

    assert "dayofweek" in result.columns


def test_extract_date_parts_quarter():
    """Test extracting quarter."""
    df = pd.DataFrame(
        {
            "date": pd.to_datetime(
                ["2023-01-15", "2023-04-15", "2023-07-15", "2023-10-15"]
            )
        }
    )

    result = datetime_utils.extract_date_parts(df, "date", parts=["quarter"])

    assert result["quarter"].tolist() == [1, 2, 3, 4]


@pytest.mark.skipif(not HAS_SPARK, reason="Spark not installed")
def test_extract_date_parts_spark(spark_session):
    """Test extracting date parts with Spark."""
    df = spark_session.createDataFrame([("2023-01-15",), ("2023-02-20",)], ["date_str"])

    df = datetime_utils.to_datetime(df, "date_str")
    result = datetime_utils.extract_date_parts(df, "date_str", parts=["year", "month"])

    assert "year" in result.columns
    assert "month" in result.columns


# ============================================================================
# add_time_delta tests
# ============================================================================


def test_add_time_delta_days():
    """Test adding days to datetime."""
    df = pd.DataFrame({"date": pd.to_datetime(["2023-01-15"])})

    result = datetime_utils.add_time_delta(df, "date", days=7, result_col="new_date")

    assert result["new_date"][0] == pd.Timestamp("2023-01-22")


def test_add_time_delta_hours():
    """Test adding hours to datetime."""
    df = pd.DataFrame({"date": pd.to_datetime(["2023-01-15 12:00:00"])})

    result = datetime_utils.add_time_delta(df, "date", hours=5, result_col="new_date")

    assert result["new_date"][0] == pd.Timestamp("2023-01-15 17:00:00")


def test_add_time_delta_combined():
    """Test adding combined time components."""
    df = pd.DataFrame({"date": pd.to_datetime(["2023-01-15 12:00:00"])})

    result = datetime_utils.add_time_delta(
        df, "date", days=1, hours=2, minutes=30, result_col="new_date"
    )

    assert result["new_date"][0] == pd.Timestamp("2023-01-16 14:30:00")


def test_add_time_delta_negative():
    """Test subtracting time (negative delta)."""
    df = pd.DataFrame({"date": pd.to_datetime(["2023-01-15"])})

    result = datetime_utils.add_time_delta(df, "date", days=-7)

    assert result["date"][0] == pd.Timestamp("2023-01-08")


@pytest.mark.skipif(not HAS_SPARK, reason="Spark not installed")
def test_add_time_delta_spark(spark_session):
    """Test adding time delta with Spark."""
    df = spark_session.createDataFrame([("2023-01-15",)], ["date_str"])

    df = datetime_utils.to_datetime(df, "date_str")
    result = datetime_utils.add_time_delta(df, "date_str", days=7)

    rows = result.collect()
    # Just verify column exists
    assert "date_str" in result.columns


# ============================================================================
# date_diff tests
# ============================================================================


def test_date_diff_days():
    """Test calculating date difference in days."""
    df = pd.DataFrame(
        {"start": pd.to_datetime(["2023-01-01"]), "end": pd.to_datetime(["2023-01-10"])}
    )

    result = datetime_utils.date_diff(df, "start", "end", unit="days")

    assert result["date_diff"].tolist() == [9]


def test_date_diff_hours():
    """Test calculating date difference in hours."""
    df = pd.DataFrame(
        {
            "start": pd.to_datetime(["2023-01-01 00:00:00"]),
            "end": pd.to_datetime(["2023-01-01 12:00:00"]),
        }
    )

    result = datetime_utils.date_diff(df, "start", "end", unit="hours")

    assert result["date_diff"].tolist() == [12.0]


def test_date_diff_minutes():
    """Test calculating date difference in minutes."""
    df = pd.DataFrame(
        {
            "start": pd.to_datetime(["2023-01-01 00:00:00"]),
            "end": pd.to_datetime(["2023-01-01 02:00:00"]),
        }
    )

    result = datetime_utils.date_diff(df, "start", "end", unit="minutes")

    assert result["date_diff"].tolist() == [120.0]


def test_date_diff_negative():
    """Test date difference when end is before start."""
    df = pd.DataFrame(
        {"start": pd.to_datetime(["2023-01-10"]), "end": pd.to_datetime(["2023-01-01"])}
    )

    result = datetime_utils.date_diff(df, "start", "end", unit="days")

    assert result["date_diff"].tolist() == [-9]


def test_date_diff_invalid_unit():
    """Test error handling for invalid unit."""
    df = pd.DataFrame(
        {"start": pd.to_datetime(["2023-01-01"]), "end": pd.to_datetime(["2023-01-10"])}
    )

    with pytest.raises(ValueError, match="Invalid unit"):
        datetime_utils.date_diff(df, "start", "end", unit="years")


@pytest.mark.skipif(not HAS_SPARK, reason="Spark not installed")
def test_date_diff_spark(spark_session):
    """Test date difference with Spark."""
    df = spark_session.createDataFrame(
        [("2023-01-01", "2023-01-10")], ["start_str", "end_str"]
    )

    df = datetime_utils.to_datetime(df, "start_str")
    df = datetime_utils.to_datetime(df, "end_str")
    result = datetime_utils.date_diff(df, "start_str", "end_str", unit="days")

    rows = result.collect()
    assert rows[0]["date_diff"] == 9


# ============================================================================
# truncate_datetime tests
# ============================================================================


def test_truncate_datetime_day():
    """Test truncating datetime to day."""
    df = pd.DataFrame({"timestamp": pd.to_datetime(["2023-01-15 14:30:45"])})

    result = datetime_utils.truncate_datetime(df, "timestamp", unit="day")

    assert result["timestamp"][0] == pd.Timestamp("2023-01-15 00:00:00")


def test_truncate_datetime_month():
    """Test truncating datetime to month."""
    df = pd.DataFrame({"timestamp": pd.to_datetime(["2023-01-15 14:30:45"])})

    result = datetime_utils.truncate_datetime(df, "timestamp", unit="month")

    assert result["timestamp"][0] == pd.Timestamp("2023-01-01 00:00:00")


def test_truncate_datetime_hour():
    """Test truncating datetime to hour."""
    df = pd.DataFrame({"timestamp": pd.to_datetime(["2023-01-15 14:30:45"])})

    result = datetime_utils.truncate_datetime(df, "timestamp", unit="hour")

    assert result["timestamp"][0] == pd.Timestamp("2023-01-15 14:00:00")


def test_truncate_datetime_invalid_unit():
    """Test error handling for invalid truncation unit."""
    df = pd.DataFrame({"timestamp": pd.to_datetime(["2023-01-15 14:30:45"])})

    with pytest.raises(ValueError, match="Invalid unit"):
        datetime_utils.truncate_datetime(df, "timestamp", unit="invalid")


@pytest.mark.skipif(not HAS_SPARK, reason="Spark not installed")
def test_truncate_datetime_spark(spark_session):
    """Test datetime truncation with Spark."""
    df = spark_session.createDataFrame([("2023-01-15 14:30:45",)], ["timestamp_str"])

    df = datetime_utils.to_datetime(df, "timestamp_str")
    result = datetime_utils.truncate_datetime(df, "timestamp_str", unit="day")

    assert "timestamp_str" in result.columns


# ============================================================================
# format_datetime tests
# ============================================================================


def test_format_datetime_pandas():
    """Test formatting datetime as string."""
    df = pd.DataFrame({"date": pd.to_datetime(["2023-01-15"])})

    result = datetime_utils.format_datetime(df, "date", "%Y/%m/%d")

    assert result["date_formatted"].tolist() == ["2023/01/15"]


def test_format_datetime_custom_format():
    """Test formatting with custom format string."""
    df = pd.DataFrame({"date": pd.to_datetime(["2023-01-15 14:30:45"])})

    result = datetime_utils.format_datetime(df, "date", "%d-%b-%Y %H:%M")

    assert "15-Jan-2023 14:30" in result["date_formatted"].tolist()[0]


def test_format_datetime_new_column():
    """Test formatting to new column."""
    df = pd.DataFrame({"date": pd.to_datetime(["2023-01-15"])})

    result = datetime_utils.format_datetime(
        df, "date", "%Y-%m-%d", result_col="formatted"
    )

    assert "date" in result.columns
    assert "formatted" in result.columns


@pytest.mark.skipif(not HAS_SPARK, reason="Spark not installed")
def test_format_datetime_spark(spark_session):
    """Test datetime formatting with Spark."""
    df = spark_session.createDataFrame([("2023-01-15",)], ["date_str"])

    df = datetime_utils.to_datetime(df, "date_str")
    result = datetime_utils.format_datetime(df, "date_str", "%Y/%m/%d")

    assert "date_str_formatted" in result.columns


# ============================================================================
# get_current_timestamp tests
# ============================================================================


def test_get_current_timestamp_pandas():
    """Test adding current timestamp column."""
    df = pd.DataFrame({"id": [1, 2, 3]})

    result = datetime_utils.get_current_timestamp(df)

    assert "current_timestamp" in result.columns
    assert pd.api.types.is_datetime64_any_dtype(result["current_timestamp"])


def test_get_current_timestamp_custom_column():
    """Test current timestamp with custom column name."""
    df = pd.DataFrame({"id": [1, 2]})

    result = datetime_utils.get_current_timestamp(df, result_col="now")

    assert "now" in result.columns


@pytest.mark.skipif(not HAS_SPARK, reason="Spark not installed")
def test_get_current_timestamp_spark(spark_session):
    """Test current timestamp with Spark."""
    df = spark_session.createDataFrame([(1,), (2,), (3,)], ["id"])

    result = datetime_utils.get_current_timestamp(df)

    assert "current_timestamp" in result.columns


# ============================================================================
# is_weekend tests
# ============================================================================


def test_is_weekend_pandas():
    """Test weekend detection with Pandas."""
    df = pd.DataFrame(
        {"date": pd.to_datetime(["2023-01-14", "2023-01-15", "2023-01-16"])}
    )

    result = datetime_utils.is_weekend(df, "date")

    # 2023-01-14 is Saturday, 2023-01-15 is Sunday, 2023-01-16 is Monday
    assert result["is_weekend"].tolist() == [True, True, False]


def test_is_weekend_all_weekdays():
    """Test weekend detection with all weekdays."""
    df = pd.DataFrame(
        {"date": pd.to_datetime(["2023-01-16", "2023-01-17", "2023-01-18"])}
    )

    result = datetime_utils.is_weekend(df, "date")

    assert result["is_weekend"].tolist() == [False, False, False]


def test_is_weekend_custom_column():
    """Test weekend detection with custom result column."""
    df = pd.DataFrame({"date": pd.to_datetime(["2023-01-14"])})

    result = datetime_utils.is_weekend(df, "date", result_col="weekend_flag")

    assert "weekend_flag" in result.columns


@pytest.mark.skipif(not HAS_SPARK, reason="Spark not installed")
def test_is_weekend_spark(spark_session):
    """Test weekend detection with Spark."""
    df = spark_session.createDataFrame(
        [("2023-01-14",), ("2023-01-15",), ("2023-01-16",)], ["date_str"]
    )

    df = datetime_utils.to_datetime(df, "date_str")
    result = datetime_utils.is_weekend(df, "date_str")

    assert "is_weekend" in result.columns


# ============================================================================
# calculate_age tests
# ============================================================================


def test_calculate_age_pandas():
    """Test age calculation from birth date."""
    # Use a fixed reference date to avoid test instability
    df = pd.DataFrame(
        {
            "birth_date": pd.to_datetime(["2000-01-15"]),
            "ref_date": pd.to_datetime(["2023-01-15"]),
        }
    )

    result = datetime_utils.calculate_age(
        df, "birth_date", reference_date_col="ref_date"
    )

    assert result["age"].tolist() == [23]


def test_calculate_age_different_ages():
    """Test age calculation with different birth dates."""
    df = pd.DataFrame(
        {
            "birth_date": pd.to_datetime(["2000-01-01", "1990-06-15", "2010-12-31"]),
            "ref_date": pd.to_datetime(["2023-01-01", "2023-01-01", "2023-01-01"]),
        }
    )

    result = datetime_utils.calculate_age(
        df, "birth_date", reference_date_col="ref_date"
    )

    assert result["age"].tolist() == [23, 32, 12]


def test_calculate_age_custom_column():
    """Test age calculation with custom result column."""
    df = pd.DataFrame(
        {
            "birth_date": pd.to_datetime(["2000-01-15"]),
            "ref_date": pd.to_datetime(["2023-01-15"]),
        }
    )

    result = datetime_utils.calculate_age(
        df, "birth_date", "ref_date", result_col="years_old"
    )

    assert "years_old" in result.columns


@pytest.mark.skipif(not HAS_SPARK, reason="Spark not installed")
def test_calculate_age_spark(spark_session):
    """Test age calculation with Spark."""
    df = spark_session.createDataFrame(
        [("2000-01-15", "2023-01-15")], ["birth_str", "ref_str"]
    )

    df = datetime_utils.to_datetime(df, "birth_str")
    df = datetime_utils.to_datetime(df, "ref_str")
    result = datetime_utils.calculate_age(df, "birth_str", "ref_str")

    rows = result.collect()
    assert rows[0]["age"] == 23
