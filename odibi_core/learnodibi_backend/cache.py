"""
Result caching for UI performance.

Provides caching functionality for dataset previews, function lists,
and pipeline results with configurable TTL.
"""

import time
from typing import Any, Dict, Optional
from dataclasses import dataclass
from threading import Lock


@dataclass
class CacheEntry:
    """Cache entry with value and expiration time."""

    value: Any
    expires_at: float


class ResultCache:
    """
    Thread-safe result cache with TTL support.

    Attributes:
        default_ttl_seconds: Default time-to-live in seconds

    Example:
        >>> cache = ResultCache(default_ttl_seconds=300)
        >>> cache.set("key", {"data": "value"}, ttl=60)
        >>> result = cache.get("key")
        >>> cache.clear()
    """

    def __init__(self, default_ttl_seconds: int = 300):
        """
        Initialize cache.

        Args:
            default_ttl_seconds: Default TTL in seconds (default: 300)
        """
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = Lock()
        self.default_ttl_seconds = default_ttl_seconds

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache if not expired.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired

        Example:
            >>> value = cache.get("dataset_preview_sales")
        """
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return None

            if time.time() > entry.expires_at:
                del self._cache[key]
                return None

            return entry.value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set value in cache with TTL.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if None)

        Example:
            >>> cache.set("preview", df_dict, ttl=300)
        """
        ttl_seconds = ttl if ttl is not None else self.default_ttl_seconds
        expires_at = time.time() + ttl_seconds

        with self._lock:
            self._cache[key] = CacheEntry(value=value, expires_at=expires_at)

    def invalidate(self, key: str) -> bool:
        """
        Remove specific key from cache.

        Args:
            key: Cache key to invalidate

        Returns:
            True if key existed, False otherwise

        Example:
            >>> cache.invalidate("pipeline_result_123")
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    def clear(self) -> None:
        """
        Clear all cache entries.

        Example:
            >>> cache.clear()
        """
        with self._lock:
            self._cache.clear()

    def cleanup_expired(self) -> int:
        """
        Remove all expired entries.

        Returns:
            Number of entries removed

        Example:
            >>> removed_count = cache.cleanup_expired()
        """
        current_time = time.time()
        expired_keys = []

        with self._lock:
            for key, entry in self._cache.items():
                if current_time > entry.expires_at:
                    expired_keys.append(key)

            for key in expired_keys:
                del self._cache[key]

        return len(expired_keys)

    def size(self) -> int:
        """
        Get number of cached entries.

        Returns:
            Cache size

        Example:
            >>> count = cache.size()
        """
        with self._lock:
            return len(self._cache)

    def keys(self) -> list:
        """
        Get all cache keys.

        Returns:
            List of cache keys

        Example:
            >>> all_keys = cache.keys()
        """
        with self._lock:
            return list(self._cache.keys())
