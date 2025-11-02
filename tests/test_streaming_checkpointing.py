"""
Tests for streaming, checkpointing, and scheduling (Phase 6).

Tests:
- StreamManager with file watch, incremental, and interval modes
- CheckpointManager for DAG state persistence
- ScheduleManager for cron and event-based scheduling
- DAGExecutor with streaming and resume modes
"""

import pytest
import pandas as pd
import time
from pathlib import Path
from datetime import datetime
import shutil

from odibi_core.streaming import StreamManager, StreamMode, StreamConfig
from odibi_core.checkpoint import (
    CheckpointManager,
    Checkpoint,
    NodeCheckpoint,
    CheckpointMode,
)
from odibi_core.scheduler import ScheduleManager, ScheduleMode
from odibi_core.core import (
    DAGBuilder,
    DAGExecutor,
    ExecutionMode,
    create_engine_context,
    Tracker,
    EventEmitter,
    Step,
)


@pytest.fixture
def temp_stream_dir(tmp_path):
    """Create temporary directory for streaming tests."""
    stream_dir = tmp_path / "streaming"
    stream_dir.mkdir()
    return stream_dir


@pytest.fixture
def temp_checkpoint_dir(tmp_path):
    """Create temporary directory for checkpoint tests."""
    checkpoint_dir = tmp_path / "checkpoints"
    checkpoint_dir.mkdir()
    return checkpoint_dir


@pytest.fixture
def sample_dataframe():
    """Create sample DataFrame for testing."""
    return pd.DataFrame(
        {
            "timestamp": pd.date_range("2024-01-01", periods=100, freq="1h"),
            "sensor_id": range(100),
            "value": range(100, 200),
        }
    )


class TestStreamManager:
    """Test StreamManager functionality."""

    def test_file_watch_mode(self, temp_stream_dir, sample_dataframe):
        """Test file watch streaming mode."""
        # Create sample files
        for i in range(3):
            file_path = temp_stream_dir / f"data_{i}.csv"
            sample_dataframe.to_csv(file_path, index=False)

        # Setup stream manager
        stream = StreamManager.from_source(
            "csv",
            path=str(temp_stream_dir),
            mode="file_watch",
            pattern="*.csv",
            name="test_stream",
        )

        # Read all files
        batch = stream.read_batch("test_stream")

        assert batch is not None
        assert len(batch) == 300  # 3 files × 100 rows
        assert list(batch.columns) == ["timestamp", "sensor_id", "value"]

    def test_incremental_mode(self, temp_stream_dir, sample_dataframe, tmp_path):
        """Test incremental streaming with watermark."""
        file_path = temp_stream_dir / "incremental_data.csv"
        sample_dataframe.to_csv(file_path, index=False)

        # Use unique checkpoint dir to avoid conflicts
        checkpoint_dir = tmp_path / "checkpoints"
        checkpoint_dir.mkdir()

        # Setup incremental stream
        stream = StreamManager(checkpoint_dir=str(checkpoint_dir))
        config = StreamConfig(
            mode=StreamMode.INCREMENTAL,
            source_path=str(file_path),
            watermark_column="timestamp",
            watermark_file=str(checkpoint_dir / "test_watermark.txt"),
            format="csv",
        )
        stream.add_source("incremental_stream", config)

        # First read - should get all data (no watermark yet)
        batch1 = stream.read_batch("incremental_stream")
        assert batch1 is not None, "First incremental read should return all data"
        assert len(batch1) == 100

        # Second read - should get nothing (no new data)
        batch2 = stream.read_batch("incremental_stream")
        assert batch2 is None or len(batch2) == 0

        # Append new data
        new_data = pd.DataFrame(
            {
                "timestamp": pd.date_range("2024-01-05", periods=50, freq="1h"),
                "sensor_id": range(100, 150),
                "value": range(200, 250),
            }
        )

        combined = pd.concat([sample_dataframe, new_data], ignore_index=True)
        combined.to_csv(file_path, index=False)

        # Third read - should get only new data
        batch3 = stream.read_batch("incremental_stream")
        assert batch3 is not None
        # Should get approximately 50 rows (might be slightly less due to watermark filtering)
        assert 40 <= len(batch3) <= 50, f"Expected ~50 rows, got {len(batch3)}"

    def test_interval_mode(self, temp_stream_dir, sample_dataframe):
        """Test interval-based streaming."""
        file_path = temp_stream_dir / "interval_data.csv"
        sample_dataframe.to_csv(file_path, index=False)

        stream = StreamManager.from_source(
            "csv",
            path=str(file_path),
            mode="interval",
            interval=1,  # 1 second
            name="interval_stream",
        )

        # First read - should succeed
        batch1 = stream.read_batch("interval_stream")
        assert batch1 is not None
        assert len(batch1) == 100

        # Immediate second read - should return None (interval not elapsed)
        batch2 = stream.read_batch("interval_stream")
        assert batch2 is None

        # Wait and read again
        time.sleep(1.1)
        batch3 = stream.read_batch("interval_stream")
        assert batch3 is not None

    def test_stream_status(self, temp_stream_dir):
        """Test stream status tracking."""
        stream = StreamManager()

        config = StreamConfig(
            mode=StreamMode.FILE_WATCH,
            source_path=str(temp_stream_dir),
            file_pattern="*.csv",
        )

        stream.add_source("test_source", config)

        status = stream.get_status()

        assert "test_source" in status
        assert status["test_source"]["mode"] == "file_watch"
        assert status["test_source"]["is_active"] == False


class TestCheckpointManager:
    """Test CheckpointManager functionality."""

    def test_create_and_save_checkpoint(self, temp_checkpoint_dir):
        """Test checkpoint creation and persistence."""
        manager = CheckpointManager(checkpoint_dir=str(temp_checkpoint_dir))

        # Create checkpoint
        completed = [
            NodeCheckpoint(
                node_name="node1",
                state="SUCCESS",
                completed_at=datetime.now().isoformat(),
                duration_ms=100.5,
                attempts=1,
            ),
            NodeCheckpoint(
                node_name="node2",
                state="SUCCESS",
                completed_at=datetime.now().isoformat(),
                duration_ms=200.3,
                attempts=2,
                cached=True,
            ),
        ]

        checkpoint = manager.create_checkpoint(
            dag_name="test_dag",
            completed_nodes=completed,
            pending_nodes={"node3", "node4"},
            failed_nodes=set(),
            mode="batch",
            iteration=1,
        )

        assert checkpoint.dag_name == "test_dag"
        assert len(checkpoint.completed_nodes) == 2
        assert len(checkpoint.pending_nodes) == 2
        assert checkpoint.iteration == 1

        # Save checkpoint
        path = manager.save(checkpoint)
        assert path.exists()

    def test_load_checkpoint(self, temp_checkpoint_dir):
        """Test loading checkpoint from disk."""
        manager = CheckpointManager(checkpoint_dir=str(temp_checkpoint_dir))

        # Create and save
        completed = [
            NodeCheckpoint(
                node_name="node1",
                state="SUCCESS",
                completed_at=datetime.now().isoformat(),
                duration_ms=100.0,
                attempts=1,
            )
        ]

        checkpoint = manager.create_checkpoint(
            dag_name="load_test",
            completed_nodes=completed,
            pending_nodes={"node2"},
            mode="batch",
        )

        manager.save(checkpoint)

        # Load by ID
        loaded = manager.load(checkpoint.checkpoint_id)

        assert loaded is not None
        assert loaded.checkpoint_id == checkpoint.checkpoint_id
        assert len(loaded.completed_nodes) == 1
        assert loaded.completed_nodes[0].node_name == "node1"

    def test_load_latest_checkpoint(self, temp_checkpoint_dir):
        """Test loading most recent checkpoint."""
        manager = CheckpointManager(checkpoint_dir=str(temp_checkpoint_dir))

        # Create multiple checkpoints
        for i in range(3):
            checkpoint = manager.create_checkpoint(
                dag_name="multi_test",
                completed_nodes=[],
                pending_nodes=set(),
                iteration=i,
            )
            manager.save(checkpoint)
            time.sleep(0.1)  # Ensure different timestamps

        # Load latest
        latest = manager.load_latest("multi_test")

        assert latest is not None
        assert latest.iteration == 2  # Last iteration

    def test_checkpoint_cleanup(self, temp_checkpoint_dir):
        """Test automatic cleanup of old checkpoints."""
        manager = CheckpointManager(
            checkpoint_dir=str(temp_checkpoint_dir), keep_last_n=2
        )

        # Create 5 checkpoints
        for i in range(5):
            checkpoint = manager.create_checkpoint(
                dag_name="cleanup_test",
                completed_nodes=[],
                pending_nodes=set(),
                iteration=i,
            )
            manager.save(checkpoint)
            time.sleep(0.1)

        # Should only keep last 2
        checkpoints = manager.list_checkpoints("cleanup_test")
        assert len(checkpoints) == 2

    def test_resume_point(self, temp_checkpoint_dir):
        """Test getting resume point from checkpoint."""
        manager = CheckpointManager(checkpoint_dir=str(temp_checkpoint_dir))

        completed = [
            NodeCheckpoint(
                node_name="node1",
                state="SUCCESS",
                completed_at=datetime.now().isoformat(),
                duration_ms=100.0,
                attempts=1,
            ),
            NodeCheckpoint(
                node_name="node2",
                state="SUCCESS",
                completed_at=datetime.now().isoformat(),
                duration_ms=200.0,
                attempts=1,
            ),
        ]

        checkpoint = manager.create_checkpoint(
            dag_name="resume_test",
            completed_nodes=completed,
            pending_nodes={"node3", "node4"},
        )

        resume_nodes = manager.get_resume_point(checkpoint)

        assert resume_nodes == {"node1", "node2"}


class TestScheduleManager:
    """Test ScheduleManager functionality."""

    def test_interval_scheduling(self):
        """Test interval-based scheduling."""
        execution_count = [0]

        def test_job():
            execution_count[0] += 1

        scheduler = ScheduleManager(check_interval=0.5)

        # Schedule every 1 second
        scheduler.schedule_interval(seconds=1, function=test_job, name="interval_test")

        scheduler.start(daemon=True)
        time.sleep(2.5)  # Should execute ~2 times
        scheduler.stop()

        assert execution_count[0] >= 2

    def test_schedule_status(self):
        """Test schedule status retrieval."""

        def dummy_job():
            pass

        scheduler = ScheduleManager()

        scheduler.schedule_interval(seconds=10, function=dummy_job, name="status_test")

        status = scheduler.get_status()

        assert status["schedule_count"] == 1
        assert "status_test" in status["schedules"]
        assert status["schedules"]["status_test"]["mode"] == "interval"

    def test_unschedule(self):
        """Test removing a schedule."""

        def dummy_job():
            pass

        scheduler = ScheduleManager()

        scheduler.schedule_interval(seconds=10, function=dummy_job, name="remove_test")
        assert len(scheduler.list_schedules()) == 1

        scheduler.unschedule("remove_test")
        assert len(scheduler.list_schedules()) == 0


class TestDAGExecutorStreaming:
    """Test DAGExecutor streaming and resume modes."""

    def test_execution_modes(self):
        """Test different execution modes."""
        steps = [
            Step(
                layer="ingestion",
                name="test_step",
                type="config_op",
                engine="pandas",
                value="test.csv",
                inputs={},
                outputs={"out": "data"},
                params={},
            )
        ]

        builder = DAGBuilder(steps)
        dag = builder.build()

        context = create_engine_context("pandas")
        tracker = Tracker()
        events = EventEmitter()

        # Test different modes
        for mode in [ExecutionMode.BATCH, ExecutionMode.STREAM, ExecutionMode.RESUME]:
            executor = DAGExecutor(
                dag=dag, context=context, tracker=tracker, events=events, mode=mode
            )

            assert executor.mode == mode

    def test_skip_nodes_in_resume_mode(self):
        """Test skipping nodes in resume mode."""
        steps = [
            Step(
                layer="ingestion",
                name="step1",
                type="config_op",
                engine="pandas",
                value="test.csv",
                inputs={},
                outputs={"out": "data1"},
                params={},
            ),
            Step(
                layer="transformation",
                name="step2",
                type="sql",
                engine="pandas",
                value="select",
                inputs={"in": "data1"},
                outputs={"out": "data2"},
                params={"columns": ["col1"]},
            ),
        ]

        builder = DAGBuilder(steps)
        dag = builder.build()

        context = create_engine_context("pandas")
        tracker = Tracker()
        events = EventEmitter()

        # Create executor with skip_nodes
        executor = DAGExecutor(
            dag=dag,
            context=context,
            tracker=tracker,
            events=events,
            mode=ExecutionMode.RESUME,
            skip_nodes={"step1"},  # Skip step1
        )

        assert "step1" in executor.skip_nodes
        assert executor.mode == ExecutionMode.RESUME


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
