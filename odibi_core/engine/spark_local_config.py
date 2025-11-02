"""
Local Spark configuration for development and testing.

Provides default configuration for running Spark locally without Databricks/cloud dependencies.
"""

from typing import Dict


# Default Spark configuration for local execution
DEFAULT_SPARK_CONFIG: Dict[str, str] = {
    # Master
    "spark.master": "local[*]",  # Use all available cores
    # Application
    "spark.app.name": "ODIBI_CORE_Local",
    # Memory
    "spark.driver.memory": "2g",
    "spark.executor.memory": "2g",
    # SQL
    "spark.sql.adaptive.enabled": "true",
    "spark.sql.adaptive.coalescePartitions.enabled": "true",
    # Serialization
    "spark.serializer": "org.apache.spark.serializer.KryoSerializer",
    # Shuffle
    "spark.sql.shuffle.partitions": "4",  # Reduced for local
    # UI
    "spark.ui.showConsoleProgress": "false",  # Reduce console noise
    # Warehouse
    "spark.sql.warehouse.dir": "spark-warehouse",
}


def get_local_spark_config(
    master: str = "local[*]",
    app_name: str = "ODIBI_CORE_Local",
    driver_memory: str = "2g",
    **overrides: str,
) -> Dict[str, str]:
    """
    Get Spark configuration for local execution.

    Args:
        master: Spark master URL (default: local[*])
        app_name: Application name
        driver_memory: Driver memory allocation
        **overrides: Additional config overrides

    Returns:
        Dictionary of Spark configuration settings

    Example:
        >>> config = get_local_spark_config(master="local[2]", driver_memory="4g")
        >>> ctx = SparkEngineContext(spark_config=config)
    """
    config = DEFAULT_SPARK_CONFIG.copy()

    # Apply parameters
    config["spark.master"] = master
    config["spark.app.name"] = app_name
    config["spark.driver.memory"] = driver_memory
    config["spark.executor.memory"] = driver_memory

    # Apply overrides
    config.update(overrides)

    return config
