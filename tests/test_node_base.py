"""
Unit tests for NodeBase and NodeState.

Tests:
- NodeState enum values
- NodeBase instantiation
- State transitions
"""

import pytest
from odibi_core.core.node import NodeBase, NodeState, Step


def test_node_state_enum():
    """Test NodeState enum has all required states."""
    assert NodeState.PENDING.value == "pending"
    assert NodeState.SUCCESS.value == "success"
    assert NodeState.FAILED.value == "failed"
    assert NodeState.RETRY.value == "retry"


def test_step_dataclass_creation(sample_step_config):
    """Test Step dataclass initialization."""
    step = Step(**sample_step_config)
    assert step.layer == "ingest"
    assert step.name == "read_csv"
    assert step.type == "config_op"
    assert step.engine == "pandas"


def test_step_default_values():
    """Test Step dataclass default values for optional fields."""
    step = Step(
        layer="ingest", name="test", type="config_op", engine="pandas", value="test.csv"
    )
    assert step.params == {}
    assert step.inputs == {}
    assert step.outputs == {}
    assert step.metadata == {}


# TODO Phase 1: Add more tests
# - Test NodeBase state transitions
# - Test abstract method enforcement
# - Test node initialization with different configs
