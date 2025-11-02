"""
Stream manager for incremental and continuous data processing.

Supports:
- File-based streaming (monitor directories for new files)
- Time-interval based reads (poll databases/APIs)
- Incremental file reading (CSV, JSON, Parquet with watermarks)
- Integration with DAGExecutor for continuous execution cycles
"""

import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import glob
import pandas as pd

logger = logging.getLogger(__name__)


class StreamMode(str, Enum):
    """Stream processing modes."""

    FILE_WATCH = "file_watch"  # Monitor directory for new files
    INTERVAL = "interval"  # Poll at fixed intervals
    INCREMENTAL = "incremental"  # Read new data since last watermark
    EVENT = "event"  # Triggered by external events


@dataclass
class StreamConfig:
    """
    Configuration for a streaming source.

    Attributes:
        mode: Stream processing mode
        source_path: Path to data source (file, directory, or connection string)
        interval_seconds: Poll interval for INTERVAL mode
        file_pattern: Glob pattern for FILE_WATCH mode (e.g., "*.csv")
        watermark_column: Column name for incremental reads
        watermark_file: File to persist last watermark value
        batch_size: Number of records per batch
        format: Data format (csv, json, parquet, delta)
        read_options: Additional read options for engine
    """

    mode: StreamMode
    source_path: str
    interval_seconds: int = 60
    file_pattern: str = "*.*"
    watermark_column: Optional[str] = None
    watermark_file: Optional[str] = None
    batch_size: int = 1000
    format: str = "csv"
    read_options: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StreamSource:
    """
    Represents a streaming data source.

    Attributes:
        name: Source identifier
        config: Stream configuration
        last_watermark: Last processed watermark value
        last_run: Timestamp of last execution
        processed_files: Set of already processed files
        is_active: Whether stream is currently active
    """

    name: str
    config: StreamConfig
    last_watermark: Optional[Any] = None
    last_run: Optional[datetime] = None
    processed_files: set = field(default_factory=set)
    is_active: bool = False


class StreamManager:
    """
    Manages streaming data sources and sinks for continuous processing.

    Features:
    - Multiple stream types (file watch, interval, incremental)
    - Watermark-based incremental reads
    - File tracking to prevent reprocessing
    - Integration with DAGExecutor

    Args:
        checkpoint_dir: Directory to store watermark files

    Example:
        >>> # File watch mode
        >>> stream = StreamManager.from_source(
        ...     "csv",
        ...     path="data/incoming/",
        ...     mode="file_watch",
        ...     pattern="*.csv"
        ... )
        >>> for batch in stream.read():
        ...     process(batch)

        >>> # Incremental mode
        >>> stream = StreamManager.from_source(
        ...     "csv",
        ...     path="data/sensor_data.csv",
        ...     mode="incremental",
        ...     watermark_column="timestamp"
        ... )
    """

    def __init__(self, checkpoint_dir: str = "artifacts/checkpoints"):
        """Initialize stream manager."""
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.sources: Dict[str, StreamSource] = {}
        logger.info(f"StreamManager initialized with checkpoint_dir={checkpoint_dir}")

    @classmethod
    def from_source(
        cls,
        format: str,
        path: str,
        mode: str = "file_watch",
        interval: int = 60,
        pattern: str = "*.*",
        watermark_column: Optional[str] = None,
        name: Optional[str] = None,
        **read_options,
    ) -> "StreamManager":
        """
        Create StreamManager with a single source.

        Args:
            format: Data format (csv, json, parquet)
            path: Source path
            mode: Stream mode (file_watch, interval, incremental)
            interval: Poll interval in seconds
            pattern: File pattern for file_watch mode
            watermark_column: Column for incremental reads
            name: Source name (default: auto-generated)
            **read_options: Additional read options

        Returns:
            StreamManager instance with configured source
        """
        manager = cls()
        source_name = name or f"{format}_stream_{len(manager.sources)}"

        config = StreamConfig(
            mode=StreamMode(mode),
            source_path=path,
            interval_seconds=interval,
            file_pattern=pattern,
            watermark_column=watermark_column,
            watermark_file=str(manager.checkpoint_dir / f"{source_name}_watermark.txt"),
            format=format,
            read_options=read_options,
        )

        source = StreamSource(name=source_name, config=config)
        manager.sources[source_name] = source

        logger.info(f"Created stream source: {source_name} ({mode} mode)")
        return manager

    def add_source(self, name: str, config: StreamConfig) -> None:
        """Add a new streaming source."""
        config.watermark_file = config.watermark_file or str(
            self.checkpoint_dir / f"{name}_watermark.txt"
        )
        self.sources[name] = StreamSource(name=name, config=config)
        logger.info(f"Added stream source: {name}")

    def read_batch(
        self, source_name: str, engine: str = "pandas"
    ) -> Optional[Union[pd.DataFrame, Any]]:
        """
        Read next batch from streaming source.

        Args:
            source_name: Name of the source to read from
            engine: Engine to use (pandas or spark)

        Returns:
            DataFrame with new data, or None if no new data
        """
        if source_name not in self.sources:
            raise ValueError(f"Unknown source: {source_name}")

        source = self.sources[source_name]
        config = source.config

        if config.mode == StreamMode.FILE_WATCH:
            return self._read_file_watch(source, engine)
        elif config.mode == StreamMode.INCREMENTAL:
            return self._read_incremental(source, engine)
        elif config.mode == StreamMode.INTERVAL:
            return self._read_interval(source, engine)
        else:
            raise ValueError(f"Unsupported stream mode: {config.mode}")

    def _read_file_watch(
        self, source: StreamSource, engine: str
    ) -> Optional[Union[pd.DataFrame, Any]]:
        """Read new files from watched directory."""
        config = source.config
        source_path = Path(config.source_path)

        if not source_path.is_dir():
            logger.warning(f"Source path is not a directory: {source_path}")
            return None

        pattern = str(source_path / config.file_pattern)
        all_files = set(glob.glob(pattern))
        new_files = all_files - source.processed_files

        if not new_files:
            logger.debug(f"No new files for source: {source.name}")
            return None

        logger.info(f"Found {len(new_files)} new files for {source.name}")

        dfs = []
        for file_path in sorted(new_files):
            try:
                df = self._read_file(
                    file_path, config.format, config.read_options, engine
                )
                dfs.append(df)
                source.processed_files.add(file_path)
                logger.info(f"Processed file: {file_path}")
            except Exception as e:
                logger.error(f"Error reading {file_path}: {e}")

        if not dfs:
            return None

        source.last_run = datetime.now()

        if engine == "pandas":
            return pd.concat(dfs, ignore_index=True) if len(dfs) > 1 else dfs[0]
        else:
            from pyspark.sql import DataFrame as SparkDataFrame
            from functools import reduce

            return reduce(SparkDataFrame.union, dfs) if len(dfs) > 1 else dfs[0]

    def _read_incremental(
        self, source: StreamSource, engine: str
    ) -> Optional[Union[pd.DataFrame, Any]]:
        """Read incrementally using watermark column."""
        config = source.config

        if not config.watermark_column:
            raise ValueError("watermark_column required for incremental mode")

        watermark = self._load_watermark(source)
        source.last_watermark = watermark

        df = self._read_file(
            config.source_path, config.format, config.read_options, engine
        )

        if df is None or (hasattr(df, "empty") and df.empty):
            return None

        if engine == "pandas":
            if watermark is not None:
                # Ensure watermark column and watermark value are comparable
                watermark_col = df[config.watermark_column]
                try:
                    # Try direct comparison
                    df = df[watermark_col > watermark]
                except TypeError:
                    # If types don't match, try converting watermark
                    try:
                        df = df[
                            pd.to_datetime(watermark_col) > pd.to_datetime(watermark)
                        ]
                    except:
                        # Fallback: convert both to string for comparison
                        df = df[watermark_col.astype(str) > str(watermark)]

            if df.empty:
                logger.debug(f"No new data for {source.name} after watermark filter")
                return None

            new_watermark = df[config.watermark_column].max()
        else:
            if watermark is not None:
                df = df.filter(df[config.watermark_column] > watermark)

            if df.count() == 0:
                logger.debug(f"No new data for {source.name} after watermark filter")
                return None

            new_watermark = df.agg({config.watermark_column: "max"}).collect()[0][0]

        self._save_watermark(source, new_watermark)
        source.last_watermark = new_watermark
        source.last_run = datetime.now()

        logger.info(f"Incremental read: {source.name}, new watermark={new_watermark}")
        return df

    def _read_interval(
        self, source: StreamSource, engine: str
    ) -> Optional[Union[pd.DataFrame, Any]]:
        """Read at fixed intervals (simple full read)."""
        config = source.config

        if source.last_run:
            elapsed = (datetime.now() - source.last_run).total_seconds()
            if elapsed < config.interval_seconds:
                logger.debug(f"Interval not elapsed for {source.name}")
                return None

        df = self._read_file(
            config.source_path, config.format, config.read_options, engine
        )

        source.last_run = datetime.now()
        return df

    def _read_file(
        self, path: str, format: str, options: Dict[str, Any], engine: str
    ) -> Optional[Union[pd.DataFrame, Any]]:
        """Read file using specified engine and format."""
        try:
            if engine == "pandas":
                if format == "csv":
                    return pd.read_csv(path, **options)
                elif format == "json":
                    return pd.read_json(path, **options)
                elif format == "parquet":
                    return pd.read_parquet(path, **options)
                else:
                    raise ValueError(f"Unsupported format for pandas: {format}")
            else:
                from pyspark.sql import SparkSession

                spark = SparkSession.getActiveSession()
                if not spark:
                    raise RuntimeError("No active Spark session")

                if format in ["csv", "json", "parquet", "delta"]:
                    reader = spark.read.format(format)
                    for key, value in options.items():
                        reader = reader.option(key, value)
                    return reader.load(path)
                else:
                    raise ValueError(f"Unsupported format for Spark: {format}")
        except Exception as e:
            logger.error(f"Error reading file {path}: {e}")
            return None

    def _load_watermark(self, source: StreamSource) -> Optional[Any]:
        """Load watermark from checkpoint file."""
        config = source.config
        watermark_file = Path(config.watermark_file)

        if not watermark_file.exists():
            return None

        try:
            with open(watermark_file, "r") as f:
                value = f.read().strip()
                logger.debug(f"Loaded watermark for {source.name}: {value}")

                try:
                    return pd.to_datetime(value)
                except:
                    try:
                        return float(value)
                    except:
                        return value
        except Exception as e:
            logger.error(f"Error loading watermark: {e}")
            return None

    def _save_watermark(self, source: StreamSource, watermark: Any) -> None:
        """Save watermark to checkpoint file."""
        config = source.config
        watermark_file = Path(config.watermark_file)

        try:
            watermark_file.parent.mkdir(parents=True, exist_ok=True)
            with open(watermark_file, "w") as f:
                f.write(str(watermark))
            logger.debug(f"Saved watermark for {source.name}: {watermark}")
        except Exception as e:
            logger.error(f"Error saving watermark: {e}")

    def read(
        self,
        source_name: Optional[str] = None,
        engine: str = "pandas",
        max_iterations: Optional[int] = None,
        sleep_seconds: float = 1.0,
    ):
        """
        Generator for continuous streaming reads.

        Args:
            source_name: Source to read from (uses first source if None)
            engine: Engine to use (pandas or spark)
            max_iterations: Maximum iterations (None = infinite)
            sleep_seconds: Sleep time between iterations

        Yields:
            DataFrames with new data
        """
        if source_name is None:
            if not self.sources:
                raise ValueError("No sources configured")
            source_name = next(iter(self.sources.keys()))

        source = self.sources[source_name]
        source.is_active = True
        iteration = 0

        logger.info(f"Starting stream: {source_name}")

        try:
            while max_iterations is None or iteration < max_iterations:
                df = self.read_batch(source_name, engine)

                if df is not None:
                    yield df
                    iteration += 1
                else:
                    time.sleep(sleep_seconds)

                if not source.is_active:
                    break
        finally:
            source.is_active = False
            logger.info(f"Stream stopped: {source_name}")

    def stop(self, source_name: Optional[str] = None) -> None:
        """Stop streaming source."""
        if source_name:
            if source_name in self.sources:
                self.sources[source_name].is_active = False
                logger.info(f"Stopped source: {source_name}")
        else:
            for source in self.sources.values():
                source.is_active = False
            logger.info("Stopped all sources")

    def get_status(self) -> Dict[str, Any]:
        """Get status of all streaming sources."""
        return {
            name: {
                "mode": source.config.mode.value,
                "is_active": source.is_active,
                "last_run": source.last_run.isoformat() if source.last_run else None,
                "last_watermark": (
                    str(source.last_watermark) if source.last_watermark else None
                ),
                "processed_files_count": len(source.processed_files),
            }
            for name, source in self.sources.items()
        }
