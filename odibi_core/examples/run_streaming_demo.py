"""
Streaming DAG execution demo with checkpoint/resume support.

Demonstrates:
- Incremental data processing with StreamManager
- Continuous DAG execution
- Checkpoint creation and resume
- Scheduled execution
"""

import pandas as pd
import numpy as np
import time
import logging
from pathlib import Path
from datetime import datetime

from odibi_core.core import (
    ConfigLoader,
    Tracker,
    EventEmitter,
    create_engine_context,
    DAGBuilder,
    DAGExecutor,
    ExecutionMode,
)
from odibi_core.streaming import StreamManager, StreamConfig, StreamMode
from odibi_core.checkpoint import CheckpointManager, CheckpointMode
from odibi_core.scheduler import ScheduleManager

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_sample_data_files():
    """Create sample incremental data files for demonstration."""
    data_dir = Path("artifacts/streaming_demo/incoming")
    data_dir.mkdir(parents=True, exist_ok=True)

    # Create 3 batches of data
    for i in range(1, 4):
        df = pd.DataFrame(
            {
                "timestamp": pd.date_range(
                    start=f"2024-01-{i:02d}", periods=100, freq="1h"
                ),
                "sensor_id": range(i * 100, (i + 1) * 100),
                "temperature": 20 + (i * 2) + np.random.randn(100),
                "humidity": 50 + (i * 3) + np.random.randn(100),
            }
        )

        filepath = data_dir / f"sensor_data_batch_{i}.csv"
        df.to_csv(filepath, index=False)
        logger.info(f"Created sample file: {filepath}")


def demo_streaming_basic():
    """Demo 1: Basic streaming with file watch."""
    logger.info("=== Demo 1: Basic Streaming (File Watch) ===")

    # Create sample data
    create_sample_data_files()

    # Setup stream manager
    stream = StreamManager.from_source(
        "csv",
        path="artifacts/streaming_demo/incoming",
        mode="file_watch",
        pattern="*.csv",
        name="sensor_stream",
    )

    # Read batches
    batch_count = 0
    for batch in stream.read(max_iterations=3, sleep_seconds=1):
        batch_count += 1
        logger.info(f"Batch {batch_count}: {len(batch)} rows")
        logger.info(f"Columns: {list(batch.columns)}")
        logger.info(f"Sample:\n{batch.head(2)}")

    logger.info(f"Processed {batch_count} batches")


def demo_incremental_processing():
    """Demo 2: Incremental processing with watermarks."""
    logger.info("=== Demo 2: Incremental Processing (Watermark) ===")

    # Create data with timestamp watermark
    data_path = Path("artifacts/streaming_demo/sensor_log.csv")
    data_path.parent.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(
        {
            "timestamp": pd.date_range("2024-01-01", periods=1000, freq="1h"),
            "sensor_id": range(1000),
            "value": np.random.randn(1000),
        }
    )
    df.to_csv(data_path, index=False)

    # Setup incremental stream
    stream = StreamManager.from_source(
        "csv",
        path=str(data_path),
        mode="incremental",
        watermark_column="timestamp",
        name="incremental_sensor",
    )

    # Read incrementally (simulates new data arriving)
    for i in range(3):
        logger.info(f"\n--- Incremental read {i + 1} ---")
        batch = stream.read_batch("incremental_sensor")

        if batch is not None:
            logger.info(f"Read {len(batch)} new rows")
            logger.info(
                f"Timestamp range: {batch['timestamp'].min()} to {batch['timestamp'].max()}"
            )
        else:
            logger.info("No new data")

        # Append new data to simulate growth
        new_data = pd.DataFrame(
            {
                "timestamp": pd.date_range(
                    df["timestamp"].max() + pd.Timedelta(hours=1),
                    periods=100,
                    freq="1h",
                ),
                "sensor_id": range(1000, 1100),
                "value": np.random.randn(100),
            }
        )

        existing = pd.read_csv(data_path)
        updated = pd.concat([existing, new_data], ignore_index=True)
        updated.to_csv(data_path, index=False)
        logger.info(f"Appended {len(new_data)} rows to source file")

        time.sleep(0.5)


def demo_checkpoint_resume():
    """Demo 3: Checkpoint and resume."""
    logger.info("=== Demo 3: Checkpoint & Resume ===")

    # Create simple pipeline config
    from odibi_core.core import Step

    steps = [
        Step(
            step_name="read_data",
            layer="ingestion",
            engine="pandas",
            value="artifacts/streaming_demo/sensor_log.csv",
            inputs={},
            outputs={"out": "raw_data"},
            params={},
        ),
        Step(
            step_name="transform_data",
            layer="transformation",
            engine="pandas",
            value="select",
            inputs={"in": "raw_data"},
            outputs={"out": "transformed_data"},
            params={"columns": ["timestamp", "sensor_id", "value"]},
        ),
    ]

    # Create checkpoint manager
    checkpoint_mgr = CheckpointManager(
        checkpoint_dir="artifacts/checkpoints", mode=CheckpointMode.AUTO
    )

    # Build DAG
    builder = DAGBuilder(steps)
    dag = builder.build()

    # Create executor with checkpoint support
    context = create_engine_context("pandas")
    tracker = Tracker()
    events = EventEmitter()

    executor = DAGExecutor(
        dag=dag,
        context=context,
        tracker=tracker,
        events=events,
        checkpoint_manager=checkpoint_mgr,
        mode=ExecutionMode.BATCH,
    )

    # Execute and create checkpoint
    logger.info("Executing DAG...")
    try:
        data_map = executor.execute()
        logger.info(f"Execution complete. Outputs: {list(data_map.keys())}")

        # Create checkpoint manually
        executor._create_checkpoint()

        # List checkpoints
        checkpoints = checkpoint_mgr.list_checkpoints("dag_0")
        logger.info(f"Checkpoints created: {checkpoints}")

        if checkpoints:
            # Load and inspect checkpoint
            checkpoint = checkpoint_mgr.load_latest("dag_0")
            logger.info(f"Latest checkpoint: {checkpoint.checkpoint_id}")
            logger.info(f"Completed nodes: {len(checkpoint.completed_nodes)}")
            logger.info(f"Pending nodes: {len(checkpoint.pending_nodes)}")

    except Exception as e:
        logger.error(f"Execution failed: {e}")


def demo_continuous_execution():
    """Demo 4: Continuous DAG execution with streaming data."""
    logger.info("=== Demo 4: Continuous Execution ===")

    # Setup streaming source
    stream_mgr = StreamManager.from_source(
        "csv",
        path="artifacts/streaming_demo/sensor_log.csv",
        mode="incremental",
        watermark_column="timestamp",
        name="continuous_source",
    )

    # Create simple pipeline
    from odibi_core.core import Step

    steps = [
        Step(
            step_name="load_stream",
            layer="ingestion",
            engine="pandas",
            value="artifacts/streaming_demo/sensor_log.csv",
            inputs={},
            outputs={"out": "stream_data"},
            params={},
        ),
    ]

    builder = DAGBuilder(steps)
    dag = builder.build()

    context = create_engine_context("pandas")
    tracker = Tracker()
    events = EventEmitter()
    checkpoint_mgr = CheckpointManager()

    executor = DAGExecutor(
        dag=dag,
        context=context,
        tracker=tracker,
        events=events,
        checkpoint_manager=checkpoint_mgr,
        mode=ExecutionMode.STREAM,
    )

    # Define data update callback
    iteration_counter = [0]

    def update_stream_data(data_map):
        """Update data_map with new streaming data."""
        batch = stream_mgr.read_batch("continuous_source")
        if batch is not None:
            data_map["stream_input"] = batch
            logger.info(
                f"Loaded {len(batch)} new rows for iteration {iteration_counter[0] + 1}"
            )
        iteration_counter[0] += 1

    # Run continuous execution
    logger.info("Starting continuous execution (3 iterations)...")

    try:
        executor.run_continuous(
            data_callback=update_stream_data,
            max_iterations=3,
            sleep_seconds=2,
            checkpoint_interval=1,
        )

        logger.info(f"Continuous execution completed: {executor._iteration} iterations")

        # Show checkpoint stats
        stats = checkpoint_mgr.get_stats("dag_0")
        logger.info(f"Checkpoint stats: {stats}")

    except Exception as e:
        logger.error(f"Continuous execution failed: {e}")


def demo_scheduled_execution():
    """Demo 5: Scheduled pipeline execution."""
    logger.info("=== Demo 5: Scheduled Execution ===")

    execution_count = [0]

    def run_pipeline():
        """Simple pipeline task."""
        execution_count[0] += 1
        logger.info(f"Executing scheduled pipeline (run #{execution_count[0]})")
        time.sleep(0.5)
        logger.info(f"Pipeline completed")

    # Create scheduler
    scheduler = ScheduleManager(check_interval=2)

    # Schedule interval-based execution (every 5 seconds)
    scheduler.schedule_interval(seconds=5, function=run_pipeline, name="interval_job")

    # Start scheduler
    scheduler.start(daemon=False)

    logger.info("Scheduler started. Running for 12 seconds...")
    time.sleep(12)

    # Stop scheduler
    scheduler.stop()

    logger.info(f"Scheduler stopped. Total executions: {execution_count[0]}")

    # Show status
    status = scheduler.get_status()
    logger.info(f"Scheduler status: {status}")


if __name__ == "__main__":
    print("ODIBI CORE Phase 6: Streaming & Scheduling Demo\n")

    try:
        # Run demos
        demo_streaming_basic()
        print("\n" + "=" * 80 + "\n")

        demo_incremental_processing()
        print("\n" + "=" * 80 + "\n")

        demo_checkpoint_resume()
        print("\n" + "=" * 80 + "\n")

        demo_continuous_execution()
        print("\n" + "=" * 80 + "\n")

        demo_scheduled_execution()

        print("\n" + "=" * 80)
        print("All demos completed successfully! ✅")
        print("=" * 80)

    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)
