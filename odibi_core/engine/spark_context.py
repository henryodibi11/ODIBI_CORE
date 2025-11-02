"""
Spark engine context implementation.

Manages SparkSession and supports local execution for development/testing.
"""

import logging
from typing import Any, Callable, Dict, Optional, Union

from odibi_core.engine.base_context import EngineContext
from odibi_core.engine.spark_local_config import DEFAULT_SPARK_CONFIG

logger = logging.getLogger(__name__)


class SparkEngineContext(EngineContext):
    """
    Spark engine context for distributed processing.

    Supports:
    - Local Spark execution (master="local[*]")
    - Parquet, CSV I/O
    - Spark SQL queries
    - Temporary view registration

    Args:
        secrets: Secret store (dict or callable)
        spark_config: SparkSession configuration
        **kwargs: Additional Spark configuration

    Example:
        >>> # Local Spark
        >>> ctx = SparkEngineContext()
        >>> df = ctx.read("data/input.csv")
        >>> ctx.register_temp("data", df)
        >>> result = ctx.execute_sql("SELECT * FROM data WHERE value > 100")
        >>> ctx.write(result, "output/filtered.parquet")
    """

    def __init__(
        self,
        secrets: Optional[Union[Dict[str, str], Callable[[str], str]]] = None,
        spark_config: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize Spark context.

        Args:
            secrets: Secret store
            spark_config: SparkSession configuration (uses DEFAULT_SPARK_CONFIG if None)
            **kwargs: Additional options
        """
        super().__init__(secrets, **kwargs)
        self.spark_config = spark_config or DEFAULT_SPARK_CONFIG.copy()
        self._spark: Optional[Any] = None  # SparkSession

    def connect(self, **kwargs: Any) -> "SparkEngineContext":
        """
        Initialize SparkSession.

        Args:
            **kwargs: Connection parameters (merged into spark_config)

        Returns:
            Self for chaining

        Example:
            >>> ctx.connect()
            >>> ctx.connect(master="local[2]")
        """
        try:
            from pyspark.sql import SparkSession

            # Merge kwargs into config
            config = self.spark_config.copy()
            for key, value in kwargs.items():
                spark_key = f"spark.{key}" if not key.startswith("spark.") else key
                config[spark_key] = value

            # Create SparkSession builder
            builder = SparkSession.builder

            # Apply configuration
            for key, value in config.items():
                builder = builder.config(key, value)

            # Create or get existing session
            self._spark = builder.getOrCreate()

            # Suppress Spark logging noise
            self._spark.sparkContext.setLogLevel("WARN")

            logger.info(f"SparkSession initialized: {self._spark.sparkContext.appName}")
            logger.info(f"Spark version: {self._spark.version}")
            logger.info(f"Master: {self._spark.sparkContext.master}")

        except ImportError:
            logger.error("PySpark not available. Install with: pip install pyspark")
            raise RuntimeError("PySpark not installed")

        return self

    def read(self, source: str, **kwargs: Any) -> Any:
        """
        Read data from source.

        Supported formats:
        - CSV: Auto-detected by .csv extension
        - JSON: Auto-detected by .json extension
        - Parquet: Auto-detected by .parquet extension
        - AVRO: Auto-detected by .avro extension
        - ORC: Auto-detected by .orc extension
        - Delta: Auto-detected by .delta extension or source_type="delta"
        - JDBC: source_type="jdbc", requires jdbc_url, table, driver, user, password

        Args:
            source: File path
            **kwargs: Read parameters
                - header (bool): For CSV, default True
                - source_type (str): Override format detection

        Returns:
            Spark DataFrame

        Example:
            >>> df = ctx.read("data.csv")
            >>> df = ctx.read("data.json")
            >>> df = ctx.read("data.parquet")
            >>> df = ctx.read("delta_table", source_type="delta")
        """
        if self._spark is None:
            self.connect()

        source_type = kwargs.pop("source_type", None)

        # Auto-detect format
        if source_type is None:
            if source.endswith(".csv"):
                source_type = "csv"
            elif source.endswith(".json"):
                source_type = "json"
            elif source.endswith(".parquet"):
                source_type = "parquet"
            elif source.endswith(".avro"):
                source_type = "avro"
            elif source.endswith(".orc"):
                source_type = "orc"
            elif source.endswith(".delta") or "delta" in source.lower():
                source_type = "delta"
            else:
                raise ValueError(f"Cannot detect format for: {source}")

        # Read based on type
        if source_type == "csv":
            header = kwargs.get("header", True)
            df = self._spark.read.csv(
                source,
                header=header,
                inferSchema=kwargs.get("inferSchema", True),
                **{
                    k: v
                    for k, v in kwargs.items()
                    if k not in ["header", "inferSchema"]
                },
            )
            logger.info(f"Read {df.count()} rows from CSV: {source}")
            return df

        elif source_type == "json":
            df = self._spark.read.json(source, **kwargs)
            logger.info(f"Read {df.count()} rows from JSON: {source}")
            return df

        elif source_type == "parquet":
            df = self._spark.read.parquet(source)
            logger.info(f"Read {df.count()} rows from Parquet: {source}")
            return df

        elif source_type == "avro":
            df = self._spark.read.format("avro").load(source, **kwargs)
            logger.info(f"Read {df.count()} rows from AVRO: {source}")
            return df

        elif source_type == "orc":
            df = self._spark.read.orc(source, **kwargs)
            logger.info(f"Read {df.count()} rows from ORC: {source}")
            return df

        elif source_type == "delta":
            df = self._spark.read.format("delta").load(source, **kwargs)
            logger.info(f"Read {df.count()} rows from Delta: {source}")
            return df

        elif source_type == "jdbc":
            # JDBC database connection (PostgreSQL, SQL Server, MySQL, etc.)
            jdbc_url = kwargs.get("jdbc_url")
            table = kwargs.get("table")
            driver = kwargs.get("driver")
            user = kwargs.get("user")
            password = kwargs.get("password")

            if not all([jdbc_url, table, driver]):
                raise ValueError("JDBC read requires: jdbc_url, table, driver")

            jdbc_options = {
                "url": jdbc_url,
                "dbtable": table,
                "driver": driver,
            }

            if user:
                jdbc_options["user"] = user
            if password:
                jdbc_options["password"] = password

            # Add any additional properties
            for k, v in kwargs.items():
                if k not in ["jdbc_url", "table", "driver", "user", "password"]:
                    jdbc_options[k] = v

            df = self._spark.read.format("jdbc").options(**jdbc_options).load()
            logger.info(f"Read {df.count()} rows from JDBC: {table}")
            return df

        else:
            raise ValueError(f"Unsupported source type: {source_type}")

    def write(self, df: Any, target: str, **kwargs: Any) -> None:
        """
        Write DataFrame to target.

        Supported formats:
        - CSV: Auto-detected by .csv extension
        - JSON: Auto-detected by .json extension
        - Parquet: Auto-detected by .parquet extension
        - AVRO: Auto-detected by .avro extension
        - ORC: Auto-detected by .orc extension
        - Delta: Auto-detected by .delta extension or source_type="delta"
        - JDBC: source_type="jdbc", requires jdbc_url, table, driver

        Args:
            df: Spark DataFrame
            target: Output file path
            **kwargs: Write parameters
                - mode (str): Write mode (overwrite, append), default overwrite
                - header (bool): For CSV, default True

        Example:
            >>> ctx.write(df, "output.csv")
            >>> ctx.write(df, "output.json")
            >>> ctx.write(df, "output.parquet", mode="append")
            >>> ctx.write(df, "delta_table", source_type="delta", mode="overwrite")
        """
        mode = kwargs.pop("mode", "overwrite")
        source_type = kwargs.pop("source_type", None)

        # Auto-detect format
        if source_type is None:
            if target.endswith(".csv"):
                source_type = "csv"
            elif target.endswith(".json"):
                source_type = "json"
            elif target.endswith(".parquet"):
                source_type = "parquet"
            elif target.endswith(".avro"):
                source_type = "avro"
            elif target.endswith(".orc"):
                source_type = "orc"
            elif target.endswith(".delta") or "delta" in target.lower():
                source_type = "delta"
            else:
                raise ValueError(f"Cannot detect format for: {target}")

        # Write based on type
        if source_type == "csv":
            header = kwargs.get("header", True)
            df.write.mode(mode).csv(
                target,
                header=header,
                **{k: v for k, v in kwargs.items() if k != "header"},
            )
            logger.info(f"Wrote DataFrame to CSV: {target}")

        elif source_type == "json":
            df.write.mode(mode).json(target, **kwargs)
            logger.info(f"Wrote DataFrame to JSON: {target}")

        elif source_type == "parquet":
            df.write.mode(mode).parquet(target, **kwargs)
            logger.info(f"Wrote DataFrame to Parquet: {target}")

        elif source_type == "avro":
            df.write.mode(mode).format("avro").save(target, **kwargs)
            logger.info(f"Wrote DataFrame to AVRO: {target}")

        elif source_type == "orc":
            df.write.mode(mode).orc(target, **kwargs)
            logger.info(f"Wrote DataFrame to ORC: {target}")

        elif source_type == "delta":
            df.write.mode(mode).format("delta").save(target, **kwargs)
            logger.info(f"Wrote DataFrame to Delta: {target}")

        elif source_type == "jdbc":
            # JDBC database write
            jdbc_url = kwargs.get("jdbc_url")
            table = kwargs.get("table")
            driver = kwargs.get("driver")
            user = kwargs.get("user")
            password = kwargs.get("password")

            if not all([jdbc_url, table, driver]):
                raise ValueError("JDBC write requires: jdbc_url, table, driver")

            jdbc_options = {
                "url": jdbc_url,
                "dbtable": table,
                "driver": driver,
            }

            if user:
                jdbc_options["user"] = user
            if password:
                jdbc_options["password"] = password

            # Add any additional properties
            for k, v in kwargs.items():
                if k not in ["jdbc_url", "table", "driver", "user", "password"]:
                    jdbc_options[k] = v

            df.write.mode(mode).format("jdbc").options(**jdbc_options).save()
            logger.info(f"Wrote DataFrame to JDBC table: {table}")

        else:
            raise ValueError(f"Unsupported target format: {target}")

    def execute_sql(self, query: str, **kwargs: Any) -> Any:
        """
        Execute Spark SQL query.

        Args:
            query: SQL query string
            **kwargs: Execution parameters (unused)

        Returns:
            Spark DataFrame with results

        Example:
            >>> result = ctx.execute_sql("SELECT * FROM temp_view WHERE value > 100")
        """
        if self._spark is None:
            self.connect()

        try:
            result = self._spark.sql(query)
            logger.info(f"Executed SQL query")
            return result
        except Exception as e:
            logger.error(f"SQL execution failed: {e}")
            raise

    def register_temp(self, name: str, df: Any) -> None:
        """
        Register DataFrame as temporary view.

        Args:
            name: View name
            df: Spark DataFrame

        Example:
            >>> ctx.register_temp("bronze", bronze_df)
            >>> result = ctx.execute_sql("SELECT * FROM bronze")
        """
        try:
            df.createOrReplaceTempView(name)
            logger.info(f"Registered temp view '{name}'")
        except Exception as e:
            logger.error(f"Failed to register temp view '{name}': {e}")
            raise

    def collect_sample(self, df: Any, n: int = 5) -> Any:
        """
        Collect sample rows as Pandas DataFrame.

        Uses intelligent sampling for large datasets to avoid OOM.

        Args:
            df: Spark DataFrame
            n: Number of rows

        Returns:
            Pandas DataFrame with sample data

        Example:
            >>> sample = ctx.collect_sample(large_df, n=10)
        """
        try:
            # Get row count (cached if available)
            row_count = df.count()

            # For small datasets, just use limit
            if row_count < 10000:
                return df.limit(n).toPandas()

            # For large datasets, sample first to avoid OOM
            sample_fraction = min(n / row_count, 0.01)  # At least n rows, max 1%
            sampled = df.sample(fraction=sample_fraction, seed=42)
            return sampled.limit(n).toPandas()

        except Exception as e:
            logger.warning(f"Sampling failed, using limit only: {e}")
            return df.limit(n).toPandas()

    def cache_checkpoint(self, df: Any, name: str) -> Any:
        """
        Cache DataFrame to avoid recomputation.

        Args:
            name: Checkpoint name
            df: Spark DataFrame

        Returns:
            Cached DataFrame

        Example:
            >>> df_cached = ctx.cache_checkpoint(expensive_df, "step_1_result")
        """
        # TODO Phase 3: Integrate with tracker for checkpoint logging
        df_cached = df.cache()
        logger.info(f"Cached DataFrame: {name}")
        return df_cached

    def stop(self) -> None:
        """
        Stop SparkSession.

        Should be called when done to free resources.

        Example:
            >>> ctx.stop()
        """
        if self._spark is not None:
            self._spark.stop()
            logger.info("SparkSession stopped")
            self._spark = None
