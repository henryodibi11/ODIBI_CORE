"""
Unit tests for Tracker.

Tests:
- Step tracking
- Snapshot capture
- Schema diff calculation
- Summary generation
- Log saving
"""

import pytest
import pandas as pd
import json
from pathlib import Path
from odibi_core.core import Tracker
from odibi_core.engine import PandasEngineContext


@pytest.fixture
def tracker():
    """Tracker instance for testing."""
    return Tracker(log_dir="test_tracker_logs")


@pytest.fixture
def pandas_context():
    """Pandas context for snapshots."""
    ctx = PandasEngineContext()
    ctx.connect()
    return ctx


@pytest.fixture
def sample_dataframe():
    """Sample DataFrame for testing."""
    return pd.DataFrame(
        {"id": [1, 2, 3], "name": ["A", "B", "C"], "value": [100, 200, 300]}
    )


def test_tracker_start_step(tracker):
    """Test starting step tracking."""
    tracker.start_step("test_step", "ingest")

    assert len(tracker.executions) == 1
    assert tracker.executions[0].step_name == "test_step"
    assert tracker.executions[0].layer == "ingest"
    assert tracker.executions[0].state == "pending"


def test_tracker_end_step(tracker):
    """Test ending step tracking."""
    tracker.start_step("test_step", "ingest")
    tracker.end_step("test_step", "success")

    execution = tracker.executions[0]
    assert execution.state == "success"
    assert execution.end_time is not None
    assert execution.duration_ms is not None
    assert execution.duration_ms >= 0  # Can be 0 for very fast operations


def test_tracker_snapshot(tracker, pandas_context, sample_dataframe):
    """Test snapshot capture."""
    tracker.start_step("test_step", "ingest")

    tracker.snapshot("after", sample_dataframe, pandas_context)

    execution = tracker.executions[0]

    # Check snapshot exists
    assert execution.after_snapshot is not None, "After snapshot should be captured"

    # Check snapshot properties
    snapshot = execution.after_snapshot
    assert snapshot.row_count == 3, f"Expected 3 rows, got {snapshot.row_count}"
    assert len(snapshot.schema) == 3, f"Expected 3 columns, got {len(snapshot.schema)}"
    assert len(snapshot.sample_data) <= 5, f"Sample data should be <= 5 rows"


def test_tracker_schema_diff(tracker, pandas_context):
    """Test schema diff calculation."""
    # Before DataFrame
    df_before = pd.DataFrame({"id": [1, 2], "name": ["A", "B"]})

    # After DataFrame (added column)
    df_after = pd.DataFrame(
        {"id": [1, 2, 3], "name": ["A", "B", "C"], "value": [100, 200, 300]}
    )

    tracker.start_step("transform", "transform")
    tracker.snapshot("before", df_before, pandas_context)
    tracker.snapshot("after", df_after, pandas_context)

    execution = tracker.executions[0]

    # Check schema diff exists
    assert execution.schema_diff is not None, "Schema diff should be calculated"

    # Check added columns
    added = execution.schema_diff["added_columns"]
    assert "value" in added, f"'value' column should be in added columns: {added}"

    # Check row delta
    assert (
        execution.row_delta == 1
    ), f"Expected row delta of 1, got {execution.row_delta}"


def test_tracker_get_stats(tracker):
    """Test statistics calculation."""
    tracker.start_step("step1", "ingest")
    tracker.end_step("step1", "success")

    tracker.start_step("step2", "transform")
    tracker.end_step("step2", "success")

    tracker.start_step("step3", "store")
    tracker.end_step("step3", "failed", "Test error")

    stats = tracker.get_stats()

    assert stats["total_steps"] == 3
    assert stats["success_count"] == 2
    assert stats["failed_count"] == 1
    assert stats["success_rate"] == pytest.approx(66.67, rel=0.1)


def test_tracker_export_lineage(tracker):
    """Test lineage export."""
    tracker.start_pipeline("test_pipeline")
    tracker.start_step("step1", "ingest")
    tracker.end_step("step1", "success")

    lineage = tracker.export_lineage()

    assert "pipeline_id" in lineage
    assert "steps" in lineage
    assert "summary" in lineage
    assert len(lineage["steps"]) == 1


def test_tracker_save(tracker, tmp_path):
    """Test saving tracker logs."""
    tracker.log_dir = tmp_path
    tracker.start_step("step1", "ingest")
    tracker.end_step("step1", "success")

    log_path = tracker.save()

    assert Path(log_path).exists()

    # Verify JSON is valid
    with open(log_path, "r") as f:
        data = json.load(f)
        assert "steps" in data
        assert len(data["steps"]) == 1


def test_tracker_get_summary(tracker):
    """Test summary generation."""
    tracker.start_step("step1", "ingest")
    tracker.end_step("step1", "success")

    summary = tracker.get_summary()

    assert "Pipeline Execution Summary" in summary
    assert "step1" in summary
    assert "success" in summary.lower() or "✓" in summary
