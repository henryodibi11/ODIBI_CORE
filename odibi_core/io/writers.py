"""
Data writers for various formats.

Abstracts I/O operations for both Pandas and Spark engines.
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseWriter(ABC):
    """
    Abstract base writer.

    Args:
        context: Engine context (Pandas or Spark)
    """

    def __init__(self, context: Any) -> None:
        """
        Initialize writer.

        Args:
            context: EngineContext
        """
        self.context = context

    @abstractmethod
    def write(self, df: Any, target: str, **kwargs: Any) -> None:
        """
        Write DataFrame to target.

        Args:
            df: DataFrame to write
            target: Target path
            **kwargs: Write options
        """
        pass


class ParquetWriter(BaseWriter):
    """
    Parquet writer for both Pandas and Spark.

    Example:
        >>> writer = ParquetWriter(pandas_context)
        >>> writer.write(df, "output/data.parquet", mode="overwrite")
    """

    def write(self, df: Any, target: str, **kwargs: Any) -> None:
        """
        Write to Parquet.

        Args:
            df: DataFrame
            target: Parquet file path
            **kwargs: Write options (mode, compression, etc.)
        """
        # TODO Phase 8: Implement Parquet writing
        # - Pandas: df.to_parquet(target, **kwargs)
        # - Spark: df.write.mode(...).parquet(target)
        pass


class CsvWriter(BaseWriter):
    """
    CSV writer for both Pandas and Spark.

    Example:
        >>> writer = CsvWriter(spark_context)
        >>> writer.write(df, "output/data.csv", header=True)
    """

    def write(self, df: Any, target: str, **kwargs: Any) -> None:
        """
        Write to CSV.

        Args:
            df: DataFrame
            target: CSV file path
            **kwargs: Write options (header, index, etc.)
        """
        # TODO Phase 8: Implement CSV writing
        # - Pandas: df.to_csv(target, **kwargs)
        # - Spark: df.write.csv(target, **kwargs)
        pass


class DeltaWriter(BaseWriter):
    """
    Delta Lake writer (Spark-native, Pandas writes as Parquet).

    Example:
        >>> writer = DeltaWriter(spark_context)
        >>> writer.write(df, "delta_table", mode="append")
    """

    def write(self, df: Any, target: str, **kwargs: Any) -> None:
        """
        Write to Delta table.

        Args:
            df: DataFrame
            target: Delta table path
            **kwargs: Write options (mode, partitionBy, etc.)
        """
        # TODO Phase 8: Implement Delta writing
        # - Spark: df.write.format("delta").mode(...).save(target)
        # - Pandas: Write as Parquet with warning
        pass
