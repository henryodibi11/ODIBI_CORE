"""
Unit tests for ConfigLoader and ConfigValidator.

Tests:
- Loading from JSON
- Config validation rules
- Error handling
"""

import pytest
import json
from pathlib import Path
from odibi_core.core import ConfigLoader, ConfigValidator, ConfigValidationError, Step


@pytest.fixture
def simple_config_json(tmp_path):
    """Create a simple JSON config file."""
    config = [
        {
            "layer": "ingest",
            "name": "read_data",
            "type": "config_op",
            "engine": "pandas",
            "value": "input.csv",
            "outputs": {"data": "raw_data"},
        },
        {
            "layer": "transform",
            "name": "filter",
            "type": "sql",
            "engine": "pandas",
            "value": "SELECT * FROM data WHERE value > 100",
            "inputs": {"data": "raw_data"},
            "outputs": {"data": "filtered_data"},
        },
    ]

    config_file = tmp_path / "config.json"
    with open(config_file, "w") as f:
        json.dump(config, f)

    return config_file


def test_config_loader_json(simple_config_json):
    """Test loading config from JSON file."""
    loader = ConfigLoader()
    steps = loader.load(str(simple_config_json))

    assert len(steps) == 2
    assert steps[0].name == "read_data"
    assert steps[0].layer == "ingest"
    assert steps[1].name == "filter"
    assert steps[1].type == "sql"


def test_config_loader_missing_file():
    """Test error when file doesn't exist."""
    loader = ConfigLoader()

    with pytest.raises(FileNotFoundError):
        loader.load("nonexistent.json")


def test_config_validator_valid_config():
    """Test validation passes for valid config."""
    steps = [
        Step(
            layer="ingest",
            name="read",
            type="config_op",
            engine="pandas",
            value="input.csv",
            outputs={"data": "raw"},
        ),
        Step(
            layer="transform",
            name="filter",
            type="sql",
            engine="pandas",
            value="SELECT * FROM data",
            inputs={"data": "raw"},
            outputs={"data": "filtered"},
        ),
    ]

    validator = ConfigValidator()
    validator.validate_config(steps)  # Should not raise


def test_config_validator_duplicate_names():
    """Test validation fails for duplicate step names."""
    steps = [
        Step(
            layer="ingest",
            name="read",
            type="config_op",
            engine="pandas",
            value="input.csv",
            outputs={"data": "raw1"},
        ),
        Step(
            layer="ingest",
            name="read",
            type="config_op",
            engine="pandas",
            value="input2.csv",
            outputs={"data": "raw2"},
        ),
    ]

    validator = ConfigValidator()
    with pytest.raises(ConfigValidationError, match="Duplicate step names"):
        validator.validate_config(steps)


def test_config_validator_duplicate_outputs():
    """Test validation fails for duplicate output keys."""
    steps = [
        Step(
            layer="ingest",
            name="read1",
            type="config_op",
            engine="pandas",
            value="input.csv",
            outputs={"data": "raw_data"},
        ),
        Step(
            layer="ingest",
            name="read2",
            type="config_op",
            engine="pandas",
            value="input2.csv",
            outputs={"data": "raw_data"},
        ),  # Duplicate!
    ]

    validator = ConfigValidator()
    with pytest.raises(ConfigValidationError, match="Duplicate output keys"):
        validator.validate_config(steps)


def test_config_validator_missing_input():
    """Test validation fails when input doesn't exist."""
    steps = [
        Step(
            layer="transform",
            name="filter",
            type="sql",
            engine="pandas",
            value="SELECT * FROM data",
            inputs={"data": "nonexistent"},
            outputs={"data": "filtered"},
        ),
    ]

    validator = ConfigValidator()
    with pytest.raises(ConfigValidationError, match="undefined input"):
        validator.validate_config(steps)


def test_config_validator_circular_dependency():
    """Test validation detects circular dependencies."""
    steps = [
        Step(
            layer="transform",
            name="step1",
            type="sql",
            engine="pandas",
            value="SELECT * FROM data",
            inputs={"data": "output2"},
            outputs={"data": "output1"},
        ),
        Step(
            layer="transform",
            name="step2",
            type="sql",
            engine="pandas",
            value="SELECT * FROM data",
            inputs={"data": "output1"},
            outputs={"data": "output2"},
        ),
    ]

    validator = ConfigValidator()
    with pytest.raises(ConfigValidationError, match="Circular dependency"):
        validator.validate_config(steps)


def test_config_validator_invalid_engine():
    """Test validation fails for invalid engine."""
    steps = [
        Step(
            layer="ingest",
            name="read",
            type="config_op",
            engine="invalid_engine",
            value="input.csv",
            outputs={"data": "raw"},
        ),
    ]

    validator = ConfigValidator()
    with pytest.raises(ConfigValidationError, match="invalid engine"):
        validator.validate_config(steps)


def test_config_validator_invalid_layer():
    """Test validation fails for invalid layer."""
    steps = [
        Step(
            layer="invalid_layer",
            name="read",
            type="config_op",
            engine="pandas",
            value="input.csv",
            outputs={"data": "raw"},
        ),
    ]

    validator = ConfigValidator()
    with pytest.raises(ConfigValidationError, match="invalid layer"):
        validator.validate_config(steps)


def test_config_validator_empty_config():
    """Test validation fails for empty config."""
    validator = ConfigValidator()

    with pytest.raises(ConfigValidationError, match="empty"):
        validator.validate_config([])
