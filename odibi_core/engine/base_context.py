"""
Base engine context contract.

All engines (Pandas, Spark) must implement this interface.
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Optional, Union


class EngineContext(ABC):
    """
    Abstract base class for engine contexts.

    All engines must implement:
    - connect: Establish connections (databases, storage)
    - read: Read data from sources
    - write: Write data to targets
    - execute_sql: Execute SQL queries
    - register_temp: Register temporary tables/views
    - get_secret: Retrieve secrets securely
    - collect_sample: Get sample data as Pandas DataFrame

    Args:
        secrets: Dictionary of secrets or callable that returns secret values

    Example:
        >>> # With dict
        >>> ctx = PandasEngineContext(secrets={"db_user": "admin", "db_pass": "secret"})
        >>>
        >>> # With callable (Databricks)
        >>> ctx = SparkEngineContext(secrets=lambda key: dbutils.secrets.get("scope", key))
    """

    def __init__(
        self,
        secrets: Optional[Union[Dict[str, str], Callable[[str], str]]] = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize engine context.

        Args:
            secrets: Secret store (dict or callable)
            **kwargs: Engine-specific configuration
        """
        self.secrets = secrets
        self.config = kwargs

    @abstractmethod
    def connect(self, **kwargs: Any) -> "EngineContext":
        """
        Establish connection to data sources.

        Args:
            **kwargs: Connection parameters

        Returns:
            Self for method chaining

        Example:
            >>> ctx.connect(host="localhost", port=5432)
        """
        pass

    @abstractmethod
    def read(self, source: str, **kwargs: Any) -> Any:
        """
        Read data from source.

        Args:
            source: Source path or query
            **kwargs: Read parameters (format, options, etc.)

        Returns:
            DataFrame (Pandas or Spark)

        Example:
            >>> df = ctx.read("data/input.csv", format="csv", header=True)
            >>> df = ctx.read("SELECT * FROM table", source_type="sql")
        """
        pass

    @abstractmethod
    def write(self, df: Any, target: str, **kwargs: Any) -> None:
        """
        Write DataFrame to target.

        Args:
            df: DataFrame to write
            target: Target path
            **kwargs: Write parameters (format, mode, partitionBy, etc.)

        Example:
            >>> ctx.write(df, "output/data.parquet", format="parquet", mode="overwrite")
        """
        pass

    @abstractmethod
    def execute_sql(self, query: str, **kwargs: Any) -> Any:
        """
        Execute SQL query.

        Args:
            query: SQL query string
            **kwargs: Execution parameters

        Returns:
            DataFrame result

        Example:
            >>> result = ctx.execute_sql("SELECT * FROM temp_table WHERE value > 100")
        """
        pass

    @abstractmethod
    def register_temp(self, name: str, df: Any) -> None:
        """
        Register DataFrame as temporary table/view.

        Args:
            name: Table/view name
            df: DataFrame to register

        Example:
            >>> ctx.register_temp("bronze_data", bronze_df)
            >>> result = ctx.execute_sql("SELECT * FROM bronze_data")
        """
        pass

    def get_secret(self, key: str) -> str:
        """
        Retrieve secret value.

        Args:
            key: Secret key

        Returns:
            Secret value

        Raises:
            ValueError: If secret not found

        Example:
            >>> password = ctx.get_secret("db_password")
        """
        # TODO Phase 2: Implement secret resolution
        if self.secrets is None:
            raise ValueError(f"No secrets configured, cannot retrieve: {key}")

        if callable(self.secrets):
            return self.secrets(key)
        elif isinstance(self.secrets, dict):
            if key not in self.secrets:
                raise ValueError(f"Secret not found: {key}")
            return self.secrets[key]
        else:
            raise ValueError("Secrets must be dict or callable")

    @abstractmethod
    def collect_sample(self, df: Any, n: int = 5) -> Any:
        """
        Collect sample rows as Pandas DataFrame.

        For Pandas, returns head(n).
        For Spark, returns limit(n).toPandas().

        Args:
            df: DataFrame to sample
            n: Number of rows

        Returns:
            Pandas DataFrame with sample data

        Example:
            >>> sample = ctx.collect_sample(large_df, n=10)
            >>> print(sample.head())
        """
        pass
