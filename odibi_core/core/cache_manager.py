"""
Cache manager for DAG node execution.

Implements hash-based caching to skip node re-execution when inputs unchanged.
Supports both Pandas and Spark DataFrames with serialization to disk.
"""

import hashlib
import json
import logging
import pickle
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Manage cached DataFrame outputs for DAG nodes.

    Uses content hashing to determine cache validity:
    - Hash = f(node_name, params, input_checksums, SQL/code)
    - Cache hit: Load serialized DataFrame from disk
    - Cache miss: Execute node and store result

    Args:
        cache_dir: Directory to store cached DataFrames
        enabled: Enable/disable caching globally

    Example:
        >>> cache = CacheManager("artifacts/cache")
        >>> key = cache.compute_cache_key("transform_gold", params, inputs_hash, sql)
        >>> if cached_df := cache.get(key):
        ...     df = cached_df
        ... else:
        ...     df = execute_transformation()
        ...     cache.put(key, df, engine="pandas")
    """

    def __init__(
        self,
        cache_dir: str = "artifacts/cache",
        enabled: bool = True,
    ) -> None:
        """
        Initialize cache manager.

        Args:
            cache_dir: Directory for cache storage
            enabled: Whether caching is enabled
        """
        self.cache_dir = Path(cache_dir)
        self.enabled = enabled
        self._metadata: Dict[str, Dict[str, Any]] = {}

        if self.enabled:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            self._load_metadata()

    def compute_cache_key(
        self,
        node_name: str,
        params: Dict[str, Any],
        inputs_hash: str,
        code: str = "",
    ) -> str:
        """
        Compute cache key from node configuration.

        Args:
            node_name: Name of the node
            params: Node parameters (dict)
            inputs_hash: Hash of input DataFrames
            code: SQL query or function code

        Returns:
            Cache key (hex string)

        Example:
            >>> key = cache.compute_cache_key(
            ...     "calc_efficiency",
            ...     {"threshold": 0.8},
            ...     "abc123def",
            ...     "SELECT * FROM silver WHERE efficiency > {threshold}"
            ... )
        """
        # Combine all components
        components = {
            "node_name": node_name,
            "params": params,
            "inputs_hash": inputs_hash,
            "code": code.strip(),
        }

        # Serialize to deterministic JSON
        serialized = json.dumps(components, sort_keys=True)

        # Hash
        cache_key = hashlib.sha256(serialized.encode()).hexdigest()[:16]

        logger.debug(f"Cache key for '{node_name}': {cache_key}")

        return cache_key

    def compute_dataframe_hash(self, df: Any, engine: str = "pandas") -> str:
        """
        Compute hash of DataFrame content.

        For Pandas: Hash schema + row count + sample rows
        For Spark: Hash schema + row count (full data hash too expensive)

        Args:
            df: DataFrame to hash
            engine: "pandas" or "spark"

        Returns:
            Hash string

        Example:
            >>> df_hash = cache.compute_dataframe_hash(df, "pandas")
        """
        try:
            if engine == "pandas":
                # Hash schema + shape + sample
                import pandas as pd

                if not isinstance(df, pd.DataFrame):
                    raise ValueError(f"Expected pandas DataFrame, got {type(df)}")

                components = {
                    "columns": list(df.columns),
                    "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
                    "shape": df.shape,
                    "sample": (
                        df.head(5).to_dict(orient="records") if len(df) > 0 else []
                    ),
                }

            elif engine == "spark":
                # Hash schema + count (avoid collecting data)
                components = {
                    "columns": df.columns,
                    "dtypes": [(f.name, str(f.dataType)) for f in df.schema.fields],
                    "count": df.count(),
                }

            else:
                raise ValueError(f"Unknown engine: {engine}")

            serialized = json.dumps(components, sort_keys=True, default=str)
            df_hash = hashlib.sha256(serialized.encode()).hexdigest()[:16]

            return df_hash

        except Exception as e:
            logger.warning(f"Failed to compute DataFrame hash: {e}")
            # Return random hash to disable caching for this DataFrame
            return hashlib.sha256(str(datetime.now()).encode()).hexdigest()[:16]

    def get(self, cache_key: str, engine: str = "pandas") -> Optional[Any]:
        """
        Retrieve cached DataFrame.

        Args:
            cache_key: Cache key
            engine: "pandas" or "spark"

        Returns:
            Cached DataFrame or None if not found

        Example:
            >>> df = cache.get("abc123def", engine="pandas")
            >>> if df is not None:
            ...     print("Cache hit!")
        """
        if not self.enabled:
            return None

        cache_file = self.cache_dir / f"{cache_key}.{engine}.pkl"

        if not cache_file.exists():
            logger.debug(f"Cache miss: {cache_key}")
            return None

        try:
            with open(cache_file, "rb") as f:
                df = pickle.load(f)

            logger.info(f"Cache hit: {cache_key}")

            # Update metadata
            if cache_key in self._metadata:
                self._metadata[cache_key]["hits"] += 1
                self._metadata[cache_key]["last_accessed"] = datetime.now().isoformat()

            return df

        except Exception as e:
            logger.error(f"Failed to load cache {cache_key}: {e}")
            return None

    def put(
        self,
        cache_key: str,
        df: Any,
        engine: str = "pandas",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Store DataFrame in cache.

        Args:
            cache_key: Cache key
            df: DataFrame to cache
            engine: "pandas" or "spark"
            metadata: Optional metadata to store with cache

        Example:
            >>> cache.put("abc123", df, engine="pandas",
            ...           metadata={"node": "transform_gold"})
        """
        if not self.enabled:
            return

        cache_file = self.cache_dir / f"{cache_key}.{engine}.pkl"

        try:
            # For Spark, convert to Pandas for pickling
            if engine == "spark":
                df_to_cache = df.toPandas()
            else:
                df_to_cache = df

            # Pickle DataFrame
            with open(cache_file, "wb") as f:
                pickle.dump(df_to_cache, f, protocol=pickle.HIGHEST_PROTOCOL)

            # Store metadata
            self._metadata[cache_key] = {
                "engine": engine,
                "created": datetime.now().isoformat(),
                "last_accessed": datetime.now().isoformat(),
                "hits": 0,
                "size_bytes": cache_file.stat().st_size,
                "custom": metadata or {},
            }

            self._save_metadata()

            logger.info(f"Cached DataFrame: {cache_key} ({engine})")

        except Exception as e:
            logger.error(f"Failed to cache DataFrame {cache_key}: {e}")

    def invalidate(self, cache_key: str, engine: str = "pandas") -> None:
        """
        Invalidate (delete) cached entry.

        Args:
            cache_key: Cache key to invalidate
            engine: "pandas" or "spark"

        Example:
            >>> cache.invalidate("abc123", engine="pandas")
        """
        cache_file = self.cache_dir / f"{cache_key}.{engine}.pkl"

        if cache_file.exists():
            cache_file.unlink()
            logger.info(f"Invalidated cache: {cache_key}")

        if cache_key in self._metadata:
            del self._metadata[cache_key]
            self._save_metadata()

    def clear_all(self) -> None:
        """
        Clear all cached entries.

        Example:
            >>> cache.clear_all()
            >>> # All cache files deleted
        """
        for cache_file in self.cache_dir.glob("*.pkl"):
            cache_file.unlink()

        self._metadata.clear()
        self._save_metadata()

        logger.info("Cleared all cache entries")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dict with entry count, total size, hit counts, etc.

        Example:
            >>> stats = cache.get_stats()
            >>> print(f"Cache entries: {stats['entry_count']}")
            >>> print(f"Total size: {stats['total_size_mb']:.2f} MB")
        """
        total_size = sum(meta.get("size_bytes", 0) for meta in self._metadata.values())
        total_hits = sum(meta.get("hits", 0) for meta in self._metadata.values())

        return {
            "enabled": self.enabled,
            "entry_count": len(self._metadata),
            "total_size_bytes": total_size,
            "total_size_mb": total_size / (1024 * 1024),
            "total_hits": total_hits,
            "cache_dir": str(self.cache_dir),
        }

    def _load_metadata(self) -> None:
        """Load cache metadata from disk."""
        metadata_file = self.cache_dir / "cache_metadata.json"

        if metadata_file.exists():
            try:
                with open(metadata_file, "r") as f:
                    self._metadata = json.load(f)
                logger.debug(f"Loaded cache metadata: {len(self._metadata)} entries")
            except Exception as e:
                logger.warning(f"Failed to load cache metadata: {e}")
                self._metadata = {}
        else:
            self._metadata = {}

    def _save_metadata(self) -> None:
        """Save cache metadata to disk."""
        metadata_file = self.cache_dir / "cache_metadata.json"

        try:
            with open(metadata_file, "w") as f:
                json.dump(self._metadata, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save cache metadata: {e}")
