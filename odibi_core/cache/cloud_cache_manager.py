"""
Cloud Cache Manager (Phase 7)

Provides content-addressed cloud caching with TTL-based validity.

Features:
- Content-addressed key generation (SHA256-based)
- TTL-based cache validity
- Metrics integration
- Works with any CloudAdapter (Azure, S3, HDFS)

Usage:
    from odibi_core.cache import CloudCacheManager
    from odibi_core.cloud import CloudAdapter
    from odibi_core.metrics import MetricsManager

    # Create cloud adapter and metrics
    cloud = CloudAdapter.create("azure", account_name="myaccount", simulate=True)
    cloud.connect()
    metrics = MetricsManager()

    # Create cache manager
    cache = CloudCacheManager(
        adapter=cloud,
        prefix="cache/",
        default_ttl_s=86400,  # 24 hours
        metrics=metrics
    )

    # Put data in cache
    cache.put("my_key", b"my_data", ttl_s=3600)

    # Get data from cache
    data = cache.get("my_key")  # Returns bytes or None if expired/missing

    # Check existence
    if cache.exists("my_key"):
        print("Cache hit!")

    # Invalidate cache entry
    cache.invalidate("my_key")

    # Purge expired entries
    cache.purge_expired()
"""

import logging
import json
import hashlib
import time
from typing import Optional, Dict, Any, Callable
from pathlib import Path
import pandas as pd

from ..cloud.cloud_adapter import CloudAdapterBase
from ..metrics.metrics_manager import MetricsManager, MetricType

logger = logging.getLogger(__name__)


class CloudCacheManager:
    """
    Cloud-backed cache manager with content-addressed keys and TTL.

    Stores cache artifacts in cloud storage with manifest files for metadata.

    Storage layout:
        {prefix}/{key}/manifest.json
        {prefix}/{key}/data.bin

    Manifest format:
        {
            "schema": "v1",
            "created_at": 1704067200.0,
            "ttl_s": 86400,
            "size": 1024,
            "checksum": "sha256:abc123...",
            "tags": {...}
        }

    Attributes:
        adapter: Cloud adapter for storage
        prefix: Cache storage prefix
        default_ttl_s: Default TTL in seconds (None = no expiry)
        metrics: Metrics manager for cache stats
    """

    def __init__(
        self,
        adapter: CloudAdapterBase,
        prefix: str = "cache/",
        default_ttl_s: Optional[int] = 86400,  # 24 hours
        metrics: Optional[MetricsManager] = None,
    ):
        """
        Initialize cloud cache manager.

        Args:
            adapter: Cloud adapter instance
            prefix: Cache storage prefix
            default_ttl_s: Default TTL in seconds (None = no expiry)
            metrics: Metrics manager for stats
        """
        self.adapter = adapter
        self.prefix = prefix.rstrip("/") + "/"
        self.default_ttl_s = default_ttl_s
        self.metrics = metrics or MetricsManager()

        if not adapter.connected:
            logger.warning("Cloud adapter not connected")

    def compute_key(
        self, namespace: str, inputs: Dict[str, Any], version: str = "v1"
    ) -> str:
        """
        Compute content-addressed cache key.

        Args:
            namespace: Namespace (e.g., "transform_step")
            inputs: Input parameters/data identifiers
            version: Version string for cache invalidation

        Returns:
            SHA256-based cache key
        """
        # Create deterministic key from namespace + inputs + version
        key_data = {"namespace": namespace, "inputs": inputs, "version": version}

        # Sort keys for determinism
        key_json = json.dumps(key_data, sort_keys=True)
        key_hash = hashlib.sha256(key_json.encode()).hexdigest()

        return f"{namespace}_{key_hash[:16]}"

    def put(
        self,
        key: str,
        data: bytes,
        ttl_s: Optional[int] = None,
        tags: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Put data in cache.

        Args:
            key: Cache key
            data: Data bytes to cache
            ttl_s: TTL in seconds (uses default_ttl_s if None)
            tags: Optional metadata tags

        Returns:
            True if successful
        """
        try:
            ttl = ttl_s if ttl_s is not None else self.default_ttl_s

            # Create manifest
            manifest = {
                "schema": "v1",
                "created_at": time.time(),
                "ttl_s": ttl,
                "size": len(data),
                "checksum": f"sha256:{hashlib.sha256(data).hexdigest()}",
                "tags": tags or {},
            }

            # Write data to cloud
            data_path = f"{self.prefix}{key}/data.bin"

            # Convert bytes to DataFrame for cloud adapter
            df_data = pd.DataFrame([{"data": data}])
            self.adapter.write(df_data, data_path, format="parquet")

            # Write manifest
            manifest_path = f"{self.prefix}{key}/manifest.json"
            df_manifest = pd.DataFrame([{"manifest": json.dumps(manifest)}])
            self.adapter.write(df_manifest, manifest_path, format="parquet")

            # Record metrics
            self.metrics.increment(MetricType.CACHE_HIT, "cache_puts")
            self.metrics.record(MetricType.DATA_SIZE, key, len(data))

            logger.info(f"Cached {len(data)} bytes to key: {key}")
            return True

        except Exception as e:
            logger.error(f"Failed to cache data for key {key}: {e}")
            return False

    def get(self, key: str) -> Optional[bytes]:
        """
        Get data from cache.

        Args:
            key: Cache key

        Returns:
            Data bytes if found and valid, None otherwise
        """
        try:
            # Read manifest
            manifest_path = f"{self.prefix}{key}/manifest.json"

            if not self.adapter.exists(manifest_path):
                self.metrics.increment(MetricType.CACHE_MISS, "cache_misses")
                return None

            df_manifest = self.adapter.read(manifest_path, format="parquet")
            manifest = json.loads(df_manifest.iloc[0]["manifest"])

            # Check TTL
            if manifest["ttl_s"] is not None:
                age = time.time() - manifest["created_at"]
                if age > manifest["ttl_s"]:
                    logger.info(
                        f"Cache key {key} expired (age={age:.0f}s, ttl={manifest['ttl_s']}s)"
                    )
                    self.metrics.increment(MetricType.CACHE_MISS, "cache_misses")
                    return None

            # Read data
            data_path = f"{self.prefix}{key}/data.bin"
            df_data = self.adapter.read(data_path, format="parquet")
            data = df_data.iloc[0]["data"]

            # Verify checksum if present
            if "checksum" in manifest:
                expected_checksum = manifest["checksum"].replace("sha256:", "")
                actual_checksum = hashlib.sha256(data).hexdigest()

                if expected_checksum != actual_checksum:
                    logger.error(f"Checksum mismatch for key {key}")
                    self.metrics.increment(MetricType.ERROR_COUNT, "checksum_errors")
                    return None

            # Record metrics
            self.metrics.increment(MetricType.CACHE_HIT, "cache_hits")
            self.metrics.record(MetricType.DATA_SIZE, key, len(data))

            logger.info(f"Cache hit for key: {key} ({len(data)} bytes)")
            return data

        except Exception as e:
            logger.error(f"Failed to get cache for key {key}: {e}")
            self.metrics.increment(MetricType.CACHE_MISS, "cache_misses")
            return None

    def exists(self, key: str) -> bool:
        """
        Check if cache key exists and is valid.

        Args:
            key: Cache key

        Returns:
            True if exists and not expired
        """
        try:
            # Read manifest
            manifest_path = f"{self.prefix}{key}/manifest.json"

            if not self.adapter.exists(manifest_path):
                return False

            df_manifest = self.adapter.read(manifest_path, format="parquet")
            manifest = json.loads(df_manifest.iloc[0]["manifest"])

            # Check TTL
            if manifest["ttl_s"] is not None:
                age = time.time() - manifest["created_at"]
                if age > manifest["ttl_s"]:
                    return False

            return True

        except Exception as e:
            logger.error(f"Failed to check existence for key {key}: {e}")
            return False

    def invalidate(self, key: str) -> bool:
        """
        Invalidate cache entry by deleting it.

        Args:
            key: Cache key

        Returns:
            True if successful
        """
        try:
            # Delete manifest and data
            manifest_path = f"{self.prefix}{key}/manifest.json"
            data_path = f"{self.prefix}{key}/data.bin"

            success = True

            if self.adapter.exists(manifest_path):
                success &= self.adapter.delete(manifest_path)

            if self.adapter.exists(data_path):
                success &= self.adapter.delete(data_path)

            self.metrics.increment(MetricType.CACHE_HIT, "cache_invalidations")
            logger.info(f"Invalidated cache key: {key}")
            return success

        except Exception as e:
            logger.error(f"Failed to invalidate cache key {key}: {e}")
            return False

    def get_or_compute(
        self,
        key: str,
        compute_fn: Callable[[], bytes],
        ttl_s: Optional[int] = None,
        tags: Optional[Dict[str, Any]] = None,
    ) -> Optional[bytes]:
        """
        Get from cache or compute if missing/expired.

        Args:
            key: Cache key
            compute_fn: Function to compute data if cache miss
            ttl_s: TTL for newly computed data
            tags: Tags for newly computed data

        Returns:
            Data bytes
        """
        # Try cache first
        data = self.get(key)

        if data is not None:
            logger.info(f"Cache hit for key: {key}")
            return data

        # Cache miss - compute
        logger.info(f"Cache miss for key: {key}, computing...")

        try:
            data = compute_fn()

            # Store in cache
            self.put(key, data, ttl_s=ttl_s, tags=tags)

            return data

        except Exception as e:
            logger.error(f"Failed to compute data for key {key}: {e}")
            return None

    def purge_expired(self, prefix: Optional[str] = None) -> int:
        """
        Purge expired cache entries.

        Args:
            prefix: Optional prefix filter

        Returns:
            Number of entries purged
        """
        try:
            search_prefix = f"{self.prefix}{prefix}" if prefix else self.prefix

            # List all cache keys
            files = self.adapter.list(search_prefix, pattern="*/manifest.json")

            purged = 0

            for file_path in files:
                # Extract key from path
                # Format: prefix/key/manifest.json
                parts = file_path.replace(self.prefix, "").split("/")
                if len(parts) < 2:
                    continue

                key = parts[0]

                # Check if expired
                if not self.exists(key):
                    # Expired - delete
                    self.invalidate(key)
                    purged += 1

            self.metrics.increment(
                MetricType.CACHE_HIT, "cache_evictions", value=purged
            )
            logger.info(f"Purged {purged} expired cache entries")

            return purged

        except Exception as e:
            logger.error(f"Failed to purge expired entries: {e}")
            return 0
