"""
Tests for cache manager (Phase 5).
"""

import pytest
import pandas as pd
import tempfile
import shutil
from pathlib import Path
from odibi_core.core import CacheManager


@pytest.fixture
def temp_cache_dir():
    """Create temporary cache directory."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_df():
    """Create sample DataFrame for testing."""
    return pd.DataFrame(
        {
            "id": [1, 2, 3],
            "value": [10, 20, 30],
            "name": ["A", "B", "C"],
        }
    )


def test_cache_manager_initialization(temp_cache_dir):
    """Test cache manager initialization."""
    cache = CacheManager(cache_dir=temp_cache_dir, enabled=True)

    assert cache.enabled
    assert Path(cache.cache_dir).exists()


def test_cache_compute_key():
    """Test cache key computation."""
    cache = CacheManager(enabled=False)

    key1 = cache.compute_cache_key(
        "transform_1", {"threshold": 0.8}, "abc123", "SELECT * FROM data WHERE x > 0.8"
    )

    key2 = cache.compute_cache_key(
        "transform_1", {"threshold": 0.8}, "abc123", "SELECT * FROM data WHERE x > 0.8"
    )

    # Same inputs should produce same key
    assert key1 == key2

    # Different params should produce different key
    key3 = cache.compute_cache_key(
        "transform_1", {"threshold": 0.9}, "abc123", "SELECT * FROM data WHERE x > 0.8"
    )
    assert key1 != key3


def test_cache_put_and_get(temp_cache_dir, sample_df):
    """Test storing and retrieving cached DataFrames."""
    cache = CacheManager(cache_dir=temp_cache_dir, enabled=True)

    cache_key = "test_key_123"

    # Store DataFrame
    cache.put(cache_key, sample_df, engine="pandas")

    # Retrieve DataFrame
    retrieved_df = cache.get(cache_key, engine="pandas")

    assert retrieved_df is not None
    pd.testing.assert_frame_equal(sample_df, retrieved_df)


def test_cache_miss(temp_cache_dir):
    """Test cache miss (key doesn't exist)."""
    cache = CacheManager(cache_dir=temp_cache_dir, enabled=True)

    result = cache.get("nonexistent_key", engine="pandas")

    assert result is None


def test_cache_disabled():
    """Test that caching is disabled when enabled=False."""
    cache = CacheManager(enabled=False)

    # Attempt to cache
    df = pd.DataFrame({"x": [1, 2, 3]})
    cache.put("key", df, engine="pandas")

    # Should not retrieve anything
    result = cache.get("key", engine="pandas")
    assert result is None


def test_cache_invalidate(temp_cache_dir, sample_df):
    """Test cache invalidation."""
    cache = CacheManager(cache_dir=temp_cache_dir, enabled=True)

    cache_key = "test_key"
    cache.put(cache_key, sample_df, engine="pandas")

    # Verify it's cached
    assert cache.get(cache_key, engine="pandas") is not None

    # Invalidate
    cache.invalidate(cache_key, engine="pandas")

    # Should be gone
    assert cache.get(cache_key, engine="pandas") is None


def test_cache_clear_all(temp_cache_dir, sample_df):
    """Test clearing all cache entries."""
    cache = CacheManager(cache_dir=temp_cache_dir, enabled=True)

    # Store multiple entries
    cache.put("key1", sample_df, engine="pandas")
    cache.put("key2", sample_df, engine="pandas")

    # Clear all
    cache.clear_all()

    # Both should be gone
    assert cache.get("key1", engine="pandas") is None
    assert cache.get("key2", engine="pandas") is None


def test_cache_stats(temp_cache_dir, sample_df):
    """Test cache statistics."""
    cache = CacheManager(cache_dir=temp_cache_dir, enabled=True)

    cache.put("key1", sample_df, engine="pandas")

    stats = cache.get_stats()

    assert stats["enabled"]
    assert stats["entry_count"] == 1
    assert stats["total_size_bytes"] > 0


def test_cache_dataframe_hash_pandas(sample_df):
    """Test DataFrame hashing for Pandas."""
    cache = CacheManager(enabled=False)

    hash1 = cache.compute_dataframe_hash(sample_df, engine="pandas")
    hash2 = cache.compute_dataframe_hash(sample_df, engine="pandas")

    # Same DataFrame should produce same hash
    assert hash1 == hash2

    # Different DataFrame should produce different hash
    df2 = sample_df.copy()
    df2["value"] = df2["value"] * 2
    hash3 = cache.compute_dataframe_hash(df2, engine="pandas")
    assert hash1 != hash3


def test_cache_metadata(temp_cache_dir, sample_df):
    """Test that metadata is stored and updated."""
    cache = CacheManager(cache_dir=temp_cache_dir, enabled=True)

    cache_key = "test_key"
    cache.put(cache_key, sample_df, engine="pandas", metadata={"node": "transform_1"})

    # Retrieve to increment hit counter
    cache.get(cache_key, engine="pandas")
    cache.get(cache_key, engine="pandas")

    # Check metadata
    assert cache_key in cache._metadata
    assert cache._metadata[cache_key]["hits"] == 2
    assert cache._metadata[cache_key]["custom"]["node"] == "transform_1"
