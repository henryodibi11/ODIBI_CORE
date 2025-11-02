"""
Unit tests for PandasEngineContext.

Tests:
- CSV/Parquet read/write
- SQL execution via DuckDB
- Temp table registration
- Sample collection
"""

import pytest
import pandas as pd
from pathlib import Path

# Check for DuckDB
try:
    import duckdb

    HAS_DUCKDB = True
except ImportError:
    HAS_DUCKDB = False

# Skip all tests in this module if pandas not available
pandas = pytest.importorskip("pandas")


@pytest.fixture
def pandas_context():
    """PandasEngineContext instance for testing."""
    from odibi_core.engine.pandas_context import PandasEngineContext

    ctx = PandasEngineContext()
    ctx.connect()
    return ctx


@pytest.fixture
def sample_dataframe():
    """Sample Pandas DataFrame for testing."""
    return pd.DataFrame(
        {
            "id": [1, 2, 3, 4, 5],
            "name": ["A", "B", "C", "D", "E"],
            "value": [100, 150, 75, 200, 50],
        }
    )


def test_pandas_context_instantiation():
    """Test PandasEngineContext can be instantiated."""
    from odibi_core.engine.pandas_context import PandasEngineContext

    ctx = PandasEngineContext()
    assert ctx is not None


def test_pandas_connect(pandas_context):
    """Test DuckDB connection initialization."""
    assert pandas_context._duckdb_conn is not None


def test_pandas_read_csv(pandas_context, tmp_path):
    """Test reading CSV file."""
    # Create test CSV
    csv_file = tmp_path / "test.csv"
    test_df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
    test_df.to_csv(csv_file, index=False)

    # Read with PandasContext
    df = pandas_context.read(str(csv_file))

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 3
    assert list(df.columns) == ["a", "b"]


def test_pandas_write_csv(pandas_context, sample_dataframe, tmp_path):
    """Test writing CSV file."""
    csv_file = tmp_path / "output.csv"

    pandas_context.write(sample_dataframe, str(csv_file))

    # Verify file exists and can be read
    assert csv_file.exists()
    df_read = pd.read_csv(csv_file)
    assert len(df_read) == len(sample_dataframe)


def test_pandas_write_read_parquet(pandas_context, sample_dataframe, tmp_path):
    """Test writing and reading Parquet file."""
    parquet_file = tmp_path / "output.parquet"

    # Write
    pandas_context.write(sample_dataframe, str(parquet_file))
    assert parquet_file.exists()

    # Read
    df_read = pandas_context.read(str(parquet_file))
    assert isinstance(df_read, pd.DataFrame)
    assert len(df_read) == len(sample_dataframe)
    pd.testing.assert_frame_equal(df_read, sample_dataframe)


def test_pandas_register_temp(pandas_context, sample_dataframe):
    """Test registering temp table."""
    pandas_context.register_temp("test_table", sample_dataframe)
    assert "test_table" in pandas_context._temp_tables


@pytest.mark.skipif(not HAS_DUCKDB, reason="DuckDB not installed")
def test_pandas_execute_sql(pandas_context, sample_dataframe):
    """Test SQL execution via DuckDB."""
    pandas_context.register_temp("data", sample_dataframe)

    result = pandas_context.execute_sql("SELECT * FROM data WHERE value > 100")

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 2  # 150 and 200
    assert all(result["value"] > 100)


@pytest.mark.skipif(not HAS_DUCKDB, reason="DuckDB not installed")
def test_pandas_execute_sql_aggregation(pandas_context, sample_dataframe):
    """Test SQL aggregation."""
    pandas_context.register_temp("data", sample_dataframe)

    result = pandas_context.execute_sql(
        "SELECT COUNT(*) as count, AVG(value) as avg_val FROM data"
    )

    assert isinstance(result, pd.DataFrame)
    assert result.iloc[0]["count"] == 5
    assert abs(result.iloc[0]["avg_val"] - 115.0) < 0.01  # (100+150+75+200+50)/5


def test_pandas_collect_sample(pandas_context, sample_dataframe):
    """Test sample collection."""
    sample = pandas_context.collect_sample(sample_dataframe, n=3)

    assert isinstance(sample, pd.DataFrame)
    assert len(sample) == 3
    pd.testing.assert_frame_equal(sample, sample_dataframe.head(3))


def test_pandas_collect_sample_more_than_available(pandas_context, sample_dataframe):
    """Test sample collection when requesting more rows than available."""
    sample = pandas_context.collect_sample(sample_dataframe, n=100)

    assert len(sample) == len(sample_dataframe)  # Should return all available


@pytest.mark.skipif(not HAS_DUCKDB, reason="DuckDB not installed")
def test_pandas_sql_multiple_tables(pandas_context):
    """Test SQL with multiple temp tables."""
    df1 = pd.DataFrame({"id": [1, 2], "val1": [10, 20]})
    df2 = pd.DataFrame({"id": [1, 2], "val2": [100, 200]})

    pandas_context.register_temp("table1", df1)
    pandas_context.register_temp("table2", df2)

    result = pandas_context.execute_sql(
        "SELECT t1.id, t1.val1, t2.val2 FROM table1 t1 JOIN table2 t2 ON t1.id = t2.id"
    )

    assert len(result) == 2
    assert list(result.columns) == ["id", "val1", "val2"]
