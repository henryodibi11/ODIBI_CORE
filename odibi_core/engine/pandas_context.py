"""
Pandas engine context implementation.

Uses DuckDB for SQL operations and native Pandas for data manipulation.
"""

import logging
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Union

from odibi_core.engine.base_context import EngineContext

logger = logging.getLogger(__name__)


class PandasEngineContext(EngineContext):
    """
    Pandas engine context with DuckDB SQL support.

    Supports:
    - CSV, Parquet, SQLite file I/O
    - SQL queries via DuckDB
    - Temporary table registration in DuckDB
    - Local file system operations

    Args:
        secrets: Secret store (dict or callable)
        **kwargs: Additional configuration

    Example:
        >>> ctx = PandasEngineContext(secrets={"db_pass": "secret"})
        >>> df = ctx.read("data/input.csv")
        >>> ctx.register_temp("data", df)
        >>> result = ctx.execute_sql("SELECT * FROM data WHERE value > 100")
        >>> ctx.write(result, "output/filtered.parquet")
    """

    def __init__(
        self,
        secrets: Optional[Union[Dict[str, str], Callable[[str], str]]] = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize Pandas context.

        Args:
            secrets: Secret store
            **kwargs: Configuration options
        """
        super().__init__(secrets, **kwargs)
        self._duckdb_conn: Optional[Any] = None  # DuckDB connection
        self._temp_tables: Dict[str, Any] = {}

    def connect(self, **kwargs: Any) -> "PandasEngineContext":
        """
        Establish connection (initializes DuckDB).

        Args:
            **kwargs: Connection parameters (unused for local)

        Returns:
            Self for chaining
        """
        try:
            import duckdb

            self._duckdb_conn = duckdb.connect(":memory:")
            logger.info("DuckDB connection initialized (in-memory)")
        except ImportError:
            logger.warning("DuckDB not available, SQL operations will fail")
            self._duckdb_conn = None
        return self

    def read(self, source: str, **kwargs: Any) -> Any:
        """
        Read data from source.

        Supported formats:
        - CSV: Auto-detected by .csv extension
        - JSON: Auto-detected by .json extension
        - Parquet: Auto-detected by .parquet extension
        - AVRO: Auto-detected by .avro extension (requires pandavro)
        - SQL Database: source_type="sql", requires connection_string and query/table
        - SQLite: source_type="sqlite", table="table_name"

        Args:
            source: File path or connection string
            **kwargs: Read parameters
                - header (bool): For CSV, default True
                - source_type (str): Override format detection

        Returns:
            Pandas DataFrame

        Raises:
            ImportError: If pandas is not installed

        Example:
            >>> df = ctx.read("data.csv")
            >>> df = ctx.read("data.parquet")
            >>> df = ctx.read("data.db", source_type="sqlite", table="my_table")
        """
        try:
            import pandas as pd
        except ImportError:
            raise ImportError("pandas is required. Install with: pip install pandas")

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
            elif source.endswith(".db") or source.endswith(".sqlite"):
                source_type = "sqlite"
            else:
                raise ValueError(f"Cannot detect format for: {source}")

        # Read based on type
        if source_type == "csv":
            header = kwargs.get("header", True)
            df = pd.read_csv(
                source,
                header=0 if header else None,
                **{k: v for k, v in kwargs.items() if k != "header"},
            )
            logger.info(f"Read {len(df)} rows from CSV: {source}")
            return df

        elif source_type == "json":
            df = pd.read_json(source, **kwargs)
            logger.info(f"Read {len(df)} rows from JSON: {source}")
            return df

        elif source_type == "parquet":
            df = pd.read_parquet(source)
            logger.info(f"Read {len(df)} rows from Parquet: {source}")
            return df

        elif source_type == "avro":
            try:
                import pandavro as pdx

                df = pdx.read_avro(source, **kwargs)
                logger.info(f"Read {len(df)} rows from AVRO: {source}")
                return df
            except ImportError:
                raise ImportError(
                    "AVRO support requires pandavro. Install with: pip install pandavro"
                )

        elif source_type == "sql":
            # Full SQL database support (PostgreSQL, SQL Server, MySQL, etc.)
            connection_string = kwargs.get("connection_string")
            query = kwargs.get("query")
            table = kwargs.get("table")

            if not connection_string:
                raise ValueError(
                    "SQL database read requires 'connection_string' parameter"
                )
            if not query and not table:
                raise ValueError(
                    "SQL database read requires either 'query' or 'table' parameter"
                )

            try:
                from sqlalchemy import create_engine

                engine = create_engine(connection_string)

                if query:
                    df = pd.read_sql(query, engine)
                else:
                    df = pd.read_sql_table(table, engine)

                logger.info(f"Read {len(df)} rows from SQL database")
                return df
            except ImportError:
                raise ImportError(
                    "SQL database support requires sqlalchemy. Install with: pip install sqlalchemy"
                )

        elif source_type == "sqlite":
            # SQLite file support (no SQLAlchemy needed)
            table = kwargs.get("table")
            if not table:
                raise ValueError("SQLite read requires 'table' parameter")
            import sqlite3

            conn = sqlite3.connect(source)
            df = pd.read_sql(f"SELECT * FROM {table}", conn)
            conn.close()
            logger.info(f"Read {len(df)} rows from SQLite table {table}: {source}")
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
        - AVRO: Auto-detected by .avro extension (requires pandavro)

        Args:
            df: Pandas DataFrame
            target: Output file path
            **kwargs: Write parameters
                - index (bool): Write index, default False

        Raises:
            ImportError: If pandas is not installed

        Example:
            >>> ctx.write(df, "output.csv")
            >>> ctx.write(df, "output.parquet", index=False)
        """
        try:
            import pandas as pd
        except ImportError:
            raise ImportError("pandas is required. Install with: pip install pandas")

        # Auto-detect format
        if target.endswith(".csv"):
            index = kwargs.get("index", False)
            df.to_csv(
                target, index=index, **{k: v for k, v in kwargs.items() if k != "index"}
            )
            logger.info(f"Wrote {len(df)} rows to CSV: {target}")

        elif target.endswith(".json"):
            orient = kwargs.get("orient", "records")
            df.to_json(
                target,
                orient=orient,
                **{k: v for k, v in kwargs.items() if k != "orient"},
            )
            logger.info(f"Wrote {len(df)} rows to JSON: {target}")

        elif target.endswith(".parquet"):
            df.to_parquet(target, **kwargs)
            logger.info(f"Wrote {len(df)} rows to Parquet: {target}")

        elif target.endswith(".avro"):
            try:
                import pandavro as pdx

                pdx.to_avro(target, df)
                logger.info(f"Wrote {len(df)} rows to AVRO: {target}")
            except ImportError:
                raise ImportError(
                    "AVRO support requires pandavro. Install with: pip install pandavro"
                )

        else:
            raise ValueError(f"Unsupported target format: {target}")

    def execute_sql(self, query: str, **kwargs: Any) -> Any:
        """
        Execute SQL query using DuckDB.

        Queries can reference registered temp tables.

        Args:
            query: SQL query string
            **kwargs: Execution parameters (unused)

        Returns:
            Pandas DataFrame with results

        Raises:
            RuntimeError: If DuckDB not initialized

        Example:
            >>> ctx.register_temp("data", df)
            >>> result = ctx.execute_sql("SELECT COUNT(*) as cnt FROM data")
        """
        if self._duckdb_conn is None:
            self.connect()

        if self._duckdb_conn is None:
            raise RuntimeError("DuckDB not available. Install with: pip install duckdb")

        try:
            # Register all temp tables with DuckDB
            for name, df in self._temp_tables.items():
                self._duckdb_conn.register(name, df)

            # Execute query
            result = self._duckdb_conn.execute(query).fetchdf()
            logger.info(f"Executed SQL, returned {len(result)} rows")
            return result

        except Exception as e:
            logger.error(f"SQL execution failed: {e}")
            raise

    def register_temp(self, name: str, df: Any) -> None:
        """
        Register DataFrame as temporary table for SQL queries.

        Args:
            name: Table name (used in SQL)
            df: Pandas DataFrame

        Raises:
            ImportError: If pandas is not installed
            TypeError: If df is not a Pandas DataFrame

        Example:
            >>> ctx.register_temp("bronze_data", bronze_df)
            >>> filtered = ctx.execute_sql("SELECT * FROM bronze_data WHERE id > 100")
        """
        try:
            import pandas as pd
        except ImportError:
            raise ImportError("pandas is required. Install with: pip install pandas")

        if not isinstance(df, pd.DataFrame):
            raise TypeError(f"Expected pandas DataFrame, got {type(df)}")

        self._temp_tables[name] = df
        logger.info(f"Registered temp table '{name}' with {len(df)} rows")

    def collect_sample(self, df: Any, n: int = 5) -> Any:
        """
        Collect sample rows.

        For Pandas, simply returns df.head(n).

        Args:
            df: Pandas DataFrame
            n: Number of rows to sample

        Returns:
            Pandas DataFrame with first n rows

        Raises:
            ImportError: If pandas is not installed
            TypeError: If df is not a Pandas DataFrame

        Example:
            >>> sample = ctx.collect_sample(large_df, n=10)
        """
        try:
            import pandas as pd
        except ImportError:
            raise ImportError("pandas is required. Install with: pip install pandas")

        if not isinstance(df, pd.DataFrame):
            raise TypeError(f"Expected pandas DataFrame, got {type(df)}")

        return df.head(n)
