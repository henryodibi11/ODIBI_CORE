"""
Unit tests for engine context contracts.

Tests:
- Both engines implement EngineContext interface
- Secret resolution works correctly
- All required methods exist
"""

import pytest
from odibi_core.engine.base_context import EngineContext
from odibi_core.engine.pandas_context import PandasEngineContext
from odibi_core.engine.spark_context import SparkEngineContext


def test_pandas_context_implements_interface():
    """Test PandasEngineContext implements all EngineContext methods."""
    ctx = PandasEngineContext()
    assert isinstance(ctx, EngineContext)
    assert hasattr(ctx, "connect")
    assert hasattr(ctx, "read")
    assert hasattr(ctx, "write")
    assert hasattr(ctx, "execute_sql")
    assert hasattr(ctx, "register_temp")
    assert hasattr(ctx, "get_secret")
    assert hasattr(ctx, "collect_sample")


def test_spark_context_implements_interface():
    """Test SparkEngineContext implements all EngineContext methods."""
    ctx = SparkEngineContext()
    assert isinstance(ctx, EngineContext)
    assert hasattr(ctx, "connect")
    assert hasattr(ctx, "read")
    assert hasattr(ctx, "write")
    assert hasattr(ctx, "execute_sql")
    assert hasattr(ctx, "register_temp")
    assert hasattr(ctx, "get_secret")
    assert hasattr(ctx, "collect_sample")


def test_secret_resolution_with_dict():
    """Test secret resolution with dictionary."""
    secrets = {"db_user": "admin", "db_pass": "secret123"}
    ctx = PandasEngineContext(secrets=secrets)
    assert ctx.get_secret("db_user") == "admin"
    assert ctx.get_secret("db_pass") == "secret123"


def test_secret_resolution_with_callable():
    """Test secret resolution with callable."""

    def secret_provider(key: str) -> str:
        secrets = {"api_key": "abc123"}
        return secrets[key]

    ctx = PandasEngineContext(secrets=secret_provider)
    assert ctx.get_secret("api_key") == "abc123"


def test_secret_resolution_missing_key():
    """Test secret resolution raises error for missing key."""
    ctx = PandasEngineContext(secrets={"known_key": "value"})
    with pytest.raises(ValueError, match="Secret not found"):
        ctx.get_secret("unknown_key")


def test_secret_resolution_no_secrets_configured():
    """Test secret resolution raises error when no secrets configured."""
    ctx = PandasEngineContext()
    with pytest.raises(ValueError, match="No secrets configured"):
        ctx.get_secret("any_key")


# TODO Phase 1: Add more tests
# - Test engine context initialization with config
# - Test method signatures match base class
# - Test error handling
