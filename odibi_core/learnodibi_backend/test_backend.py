"""
Quick test for LearnODIBI Backend functionality.
"""

from odibi_core.learnodibi_backend import LearnODIBIBackend


def test_backend_initialization():
    """Test backend initialization."""
    backend = LearnODIBIBackend()
    assert backend is not None
    assert backend.cache is not None
    assert backend.session_pipelines == {}


def test_validate_config():
    """Test configuration validation."""
    backend = LearnODIBIBackend()

    valid_config = {"steps": [{"type": "load", "params": {"path": "test.csv"}}]}

    result = backend.validate_config(valid_config)

    assert result["success"] is True
    assert result["data"]["valid"] is True
    assert len(result["data"]["errors"]) == 0


def test_validate_config_empty():
    """Test empty configuration validation."""
    backend = LearnODIBIBackend()

    result = backend.validate_config({})

    assert result["success"] is False
    assert result["data"]["valid"] is False
    assert len(result["data"]["errors"]) > 0


def test_list_demo_datasets():
    """Test listing demo datasets."""
    backend = LearnODIBIBackend()

    result = backend.list_demo_datasets()

    assert result["success"] is True
    assert "datasets" in result["data"]
    assert "count" in result["data"]


def test_get_available_functions():
    """Test getting available functions."""
    backend = LearnODIBIBackend()

    result = backend.get_available_functions()

    assert result["success"] is True
    assert "functions" in result["data"]
    assert "count" in result["data"]


def test_cache_stats():
    """Test cache statistics."""
    backend = LearnODIBIBackend()

    result = backend.get_cache_stats()

    assert result["success"] is True
    assert "size" in result["data"]
    assert "keys" in result["data"]


def test_clear_cache():
    """Test cache clearing."""
    backend = LearnODIBIBackend()

    backend.get_available_functions()
    assert backend.cache.size() > 0

    result = backend.clear_cache()

    assert result["success"] is True
    assert backend.cache.size() == 0


if __name__ == "__main__":
    print("Running LearnODIBI Backend tests...")

    test_backend_initialization()
    print("✓ Backend initialization test passed")

    test_validate_config()
    print("✓ Config validation test passed")

    test_validate_config_empty()
    print("✓ Empty config validation test passed")

    test_list_demo_datasets()
    print("✓ List demo datasets test passed")

    test_get_available_functions()
    print("✓ Get available functions test passed")

    test_cache_stats()
    print("✓ Cache stats test passed")

    test_clear_cache()
    print("✓ Clear cache test passed")

    print("\n✅ All tests passed!")
