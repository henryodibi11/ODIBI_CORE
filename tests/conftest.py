"""
Pytest configuration and shared fixtures.

Provides test data, mock contexts, and sample configurations for testing.
"""

import pytest
from typing import Dict, Any, List

# Check for required dependencies
try:
    import pandas as pd
except ImportError:
    pytest.skip("pandas not installed", allow_module_level=True)

# Optional dependencies
try:
    import duckdb

    HAS_DUCKDB = True
except ImportError:
    HAS_DUCKDB = False

try:
    import pyspark

    HAS_SPARK = True
except ImportError:
    HAS_SPARK = False


@pytest.fixture
def sample_step_config() -> Dict[str, Any]:
    """
    Sample step configuration for testing.

    Returns:
        Step configuration dict
    """
    return {
        "layer": "ingest",
        "name": "read_csv",
        "type": "config_op",
        "engine": "pandas",
        "value": "test_data.csv",
        "params": {"header": True},
        "inputs": {},
        "outputs": {"data": "raw_data"},
        "metadata": {"description": "Test ingestion"},
    }


@pytest.fixture
def sample_pipeline_config() -> List[Dict[str, Any]]:
    """
    Sample pipeline configuration for testing.

    Returns:
        List of step configurations
    """
    return [
        {
            "layer": "ingest",
            "name": "read_csv",
            "type": "config_op",
            "engine": "pandas",
            "value": "input.csv",
            "outputs": {"data": "raw_data"},
        },
        {
            "layer": "transform",
            "name": "filter",
            "type": "sql",
            "engine": "pandas",
            "value": "SELECT * FROM data WHERE value > 100",
            "inputs": {"data": "raw_data"},
            "outputs": {"data": "filtered_data"},
        },
        {
            "layer": "store",
            "name": "write_parquet",
            "type": "config_op",
            "engine": "pandas",
            "value": "output.parquet",
            "inputs": {"data": "filtered_data"},
        },
    ]


@pytest.fixture
def mock_pandas_dataframe():
    """
    Mock Pandas DataFrame for testing.

    Returns:
        Mock DataFrame object
    """
    # TODO Phase 1: Create mock DataFrame
    # - Use unittest.mock.MagicMock or actual pd.DataFrame
    pass


@pytest.fixture
def mock_spark_dataframe():
    """
    Mock Spark DataFrame for testing.

    Returns:
        Mock Spark DataFrame object
    """
    # TODO Phase 1: Create mock Spark DataFrame
    pass


@pytest.fixture
def pandas_context():
    """
    PandasEngineContext for testing.

    Returns:
        PandasEngineContext instance
    """
    from odibi_core.engine.pandas_context import PandasEngineContext

    return PandasEngineContext(secrets={"test_key": "test_value"})


@pytest.fixture
def spark_context():
    """
    SparkEngineContext for testing.

    Returns:
        SparkEngineContext instance
    """
    from odibi_core.engine.spark_context import SparkEngineContext

    return SparkEngineContext(secrets={"test_key": "test_value"})


@pytest.fixture
def tracker():
    """
    Tracker instance for testing.

    Returns:
        Tracker instance
    """
    from odibi_core.core.tracker import Tracker

    return Tracker()


@pytest.fixture
def events():
    """
    EventEmitter instance for testing.

    Returns:
        EventEmitter instance
    """
    from odibi_core.core.events import EventEmitter

    return EventEmitter()
