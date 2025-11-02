"""
Unit tests for SparkEngineContext.

Tests:
- Local Spark initialization
- CSV/Parquet read/write
- SQL execution
- Temp view registration
- Sample collection

Note: Spark tests may fail on Windows due to Hadoop winutils.exe requirement.
This is a known Spark on Windows issue and does not affect production usage
(Databricks/EMR). For Windows development, use PandasEngineContext.
"""

import pytest
import sys
from pathlib import Path

# Skip all tests in this module if pyspark not available
pytest.importorskip("pyspark")

# Mark all Spark tests as potentially slow/flaky on Windows
pytestmark = pytest.mark.skipif(
    sys.platform == "win32",
    reason="Spark on Windows requires Hadoop winutils.exe - use Pandas for local dev",
)


@pytest.fixture(scope="module")
def spark_context():
    """SparkEngineContext instance for testing (module-scoped for performance)."""
    from odibi_core.engine.spark_context import SparkEngineContext

    ctx = SparkEngineContext()
    ctx.connect()
    yield ctx
    ctx.stop()


@pytest.fixture
def sample_data_dict():
    """Sample data as dict for creating DataFrames."""
    return {
        "id": [1, 2, 3, 4, 5],
        "name": ["A", "B", "C", "D", "E"],
        "value": [100, 150, 75, 200, 50],
    }


def test_spark_context_instantiation():
    """Test SparkEngineContext can be instantiated."""
    from odibi_core.engine.spark_context import SparkEngineContext

    ctx = SparkEngineContext()
    assert ctx is not None


def test_spark_connect(spark_context):
    """Test SparkSession initialization."""
    assert spark_context._spark is not None
    assert spark_context._spark.sparkContext.appName == "ODIBI_CORE_Local"


def test_spark_read_csv(spark_context, tmp_path):
    """Test reading CSV file with Spark."""
    import pandas as pd

    # Create test CSV
    csv_file = tmp_path / "test.csv"
    test_df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
    test_df.to_csv(csv_file, index=False)

    # Read with SparkContext
    df = spark_context.read(str(csv_file))

    assert df is not None
    assert df.count() == 3
    assert df.columns == ["a", "b"]


def test_spark_write_csv(spark_context, sample_data_dict, tmp_path):
    """Test writing CSV file with Spark."""
    from pyspark.sql import SparkSession

    # Create Spark DataFrame
    spark = spark_context._spark
    df = spark.createDataFrame(
        [
            (row["id"], row["name"], row["value"])
            for row in [
                dict(zip(sample_data_dict.keys(), vals))
                for vals in zip(*sample_data_dict.values())
            ]
        ],
        ["id", "name", "value"],
    )

    csv_dir = tmp_path / "output_csv"
    spark_context.write(df, str(csv_dir))

    # Verify directory exists (Spark writes to directory)
    assert csv_dir.exists()


def test_spark_write_read_parquet(spark_context, sample_data_dict, tmp_path):
    """Test writing and reading Parquet with Spark."""
    import pandas as pd

    # Create Spark DataFrame
    spark = spark_context._spark
    data = [
        (
            sample_data_dict["id"][i],
            sample_data_dict["name"][i],
            sample_data_dict["value"][i],
        )
        for i in range(len(sample_data_dict["id"]))
    ]
    df = spark.createDataFrame(data, ["id", "name", "value"])

    parquet_dir = tmp_path / "output.parquet"

    # Write
    spark_context.write(df, str(parquet_dir))
    assert parquet_dir.exists()

    # Read
    df_read = spark_context.read(str(parquet_dir))
    assert df_read.count() == len(sample_data_dict["id"])


def test_spark_register_temp(spark_context, sample_data_dict):
    """Test registering temp view."""
    spark = spark_context._spark
    data = [
        (
            sample_data_dict["id"][i],
            sample_data_dict["name"][i],
            sample_data_dict["value"][i],
        )
        for i in range(len(sample_data_dict["id"]))
    ]
    df = spark.createDataFrame(data, ["id", "name", "value"])

    spark_context.register_temp("test_view", df)

    # Verify view exists by querying it
    result = spark_context.execute_sql("SELECT COUNT(*) as cnt FROM test_view")
    assert result.collect()[0]["cnt"] == 5


def test_spark_execute_sql(spark_context, sample_data_dict):
    """Test SQL execution."""
    spark = spark_context._spark
    data = [
        (
            sample_data_dict["id"][i],
            sample_data_dict["name"][i],
            sample_data_dict["value"][i],
        )
        for i in range(len(sample_data_dict["id"]))
    ]
    df = spark.createDataFrame(data, ["id", "name", "value"])

    spark_context.register_temp("data", df)

    result = spark_context.execute_sql("SELECT * FROM data WHERE value > 100")

    assert result.count() == 2  # 150 and 200


def test_spark_execute_sql_aggregation(spark_context, sample_data_dict):
    """Test SQL aggregation."""
    spark = spark_context._spark
    data = [
        (
            sample_data_dict["id"][i],
            sample_data_dict["name"][i],
            sample_data_dict["value"][i],
        )
        for i in range(len(sample_data_dict["id"]))
    ]
    df = spark.createDataFrame(data, ["id", "name", "value"])

    spark_context.register_temp("data", df)

    result = spark_context.execute_sql(
        "SELECT COUNT(*) as count, AVG(value) as avg_val FROM data"
    )

    row = result.collect()[0]
    assert row["count"] == 5
    assert abs(row["avg_val"] - 115.0) < 0.01  # (100+150+75+200+50)/5


def test_spark_collect_sample(spark_context, sample_data_dict):
    """Test sample collection."""
    import pandas as pd

    spark = spark_context._spark
    data = [
        (
            sample_data_dict["id"][i],
            sample_data_dict["name"][i],
            sample_data_dict["value"][i],
        )
        for i in range(len(sample_data_dict["id"]))
    ]
    df = spark.createDataFrame(data, ["id", "name", "value"])

    sample = spark_context.collect_sample(df, n=3)

    assert isinstance(sample, pd.DataFrame)
    assert len(sample) == 3


def test_spark_cache_checkpoint(spark_context, sample_data_dict):
    """Test DataFrame caching."""
    spark = spark_context._spark
    data = [
        (
            sample_data_dict["id"][i],
            sample_data_dict["name"][i],
            sample_data_dict["value"][i],
        )
        for i in range(len(sample_data_dict["id"]))
    ]
    df = spark.createDataFrame(data, ["id", "name", "value"])

    df_cached = spark_context.cache_checkpoint(df, "test_cache")

    assert df_cached is not None
    # Verify cache by checking storage level
    assert df_cached.is_cached
