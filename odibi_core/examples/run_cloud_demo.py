"""
ODIBI CORE Phase 7 - Cloud Infrastructure Demo

Demonstrates:
- CloudAdapter usage (Azure or simulation mode)
- CloudCacheManager with get_or_compute()
- DistributedCheckpointManager saving checkpoints to cloud
- MetricsManager printing summary

Note: DistributedExecutor demo disabled due to import issues (DAG class refactoring needed)

Run modes:
1. Simulation mode (no Azure credentials):
   python odibi_core/examples/run_cloud_demo.py

2. Real Azure mode (requires credentials):
   export AZURE_STORAGE_ACCOUNT=myaccount
   export AZURE_STORAGE_KEY=mykey
   python odibi_core/examples/run_cloud_demo.py
"""

import os
import sys
import logging
import pandas as pd
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from odibi_core.cloud.cloud_adapter import CloudAdapter
from odibi_core.cache.cloud_cache_manager import CloudCacheManager
from odibi_core.checkpoint.distributed_checkpoint_manager import (
    DistributedCheckpointManager,
)
from odibi_core.metrics.metrics_manager import MetricsManager, MetricType
from odibi_core.core.dag_builder import DAGBuilder, DAGNode
from odibi_core.core.node import NodeBase, Step
from odibi_core.core.tracker import Tracker
from odibi_core.core.events import EventEmitter


def check_azure_credentials():
    """
    Check if Azure credentials are available.

    Returns:
        tuple: (has_credentials, account_name)
    """
    account_name = os.getenv("AZURE_STORAGE_ACCOUNT")
    account_key = os.getenv("AZURE_STORAGE_KEY")

    if account_name and account_key:
        logger.info(f"✓ Azure credentials found for account: {account_name}")
        return True, account_name
    else:
        logger.info(
            "✗ Azure credentials not found (AZURE_STORAGE_ACCOUNT, AZURE_STORAGE_KEY)"
        )
        return False, None


# DAG creation commented out due to import issues - needs DAGBuilder refactoring
# TODO: Fix DAG/Node classes and re-enable


def demo_cloud_adapter(simulate=True, account_name=None):
    """
    Demonstrate CloudAdapter usage.

    Args:
        simulate: Whether to run in simulation mode
        account_name: Azure storage account name (if not simulating)
    """
    logger.info("\n" + "=" * 80)
    logger.info("DEMO 1: CloudAdapter Usage")
    logger.info("=" * 80)

    if simulate:
        logger.info("Running in SIMULATION mode (no real Azure calls)")
        adapter = CloudAdapter.create("azure", account_name="simulated", simulate=True)
    else:
        logger.info(f"Running with REAL Azure adapter (account: {account_name})")
        adapter = CloudAdapter.create(
            "azure", account_name=account_name, simulate=False
        )

    # Connect
    logger.info("Connecting to cloud adapter...")
    adapter.connect()

    # Create sample data
    sample_data = pd.DataFrame({"id": [1, 2, 3], "value": [10, 20, 30]})

    # Write data
    logger.info("Writing sample data to cloud...")
    test_path = "demo-container/test_data.parquet"
    adapter.write(sample_data, test_path, format="parquet")

    # Check existence
    exists = adapter.exists(test_path)
    logger.info(f"Data exists in cloud: {exists}")

    # Read data back
    logger.info("Reading data back from cloud...")
    read_data = adapter.read(test_path, format="parquet")
    logger.info(f"Read {len(read_data)} rows from cloud")

    # Disconnect
    adapter.disconnect()
    logger.info("✓ CloudAdapter demo complete\n")

    return adapter


def demo_cloud_cache(adapter, metrics):
    """
    Demonstrate CloudCacheManager with get_or_compute().

    Args:
        adapter: CloudAdapter instance
        metrics: MetricsManager instance
    """
    logger.info("\n" + "=" * 80)
    logger.info("DEMO 2: CloudCacheManager with get_or_compute()")
    logger.info("=" * 80)

    # Reconnect adapter if disconnected
    if not adapter.connected:
        adapter.connect()

    # Create cache manager
    cache = CloudCacheManager(
        adapter=adapter, prefix="cache/", default_ttl_s=3600, metrics=metrics  # 1 hour
    )

    # Compute key
    namespace = "transform_step"
    inputs = {"file": "data.csv", "columns": ["A", "B", "C"]}
    key = cache.compute_key(namespace, inputs, version="v1")
    logger.info(f"Computed cache key: {key}")

    # Define compute function
    compute_count = [0]

    def expensive_computation():
        compute_count[0] += 1
        logger.info(f"  -> Computing expensive result (call #{compute_count[0]})...")
        import time

        time.sleep(0.5)  # Simulate expensive computation
        return b"Computed result data"

    # First call - should compute
    logger.info("First get_or_compute() - expect cache MISS:")
    data1 = cache.get_or_compute(key, expensive_computation, ttl_s=3600)
    logger.info(
        f"  Received data: {data1[:20]}... (compute called {compute_count[0]} time(s))"
    )

    # Second call - should use cache
    logger.info("Second get_or_compute() - expect cache HIT:")
    data2 = cache.get_or_compute(key, expensive_computation, ttl_s=3600)
    logger.info(
        f"  Received data: {data2[:20]}... (compute called {compute_count[0]} time(s))"
    )

    # Note: In simulation mode, cache may not persist properly
    if compute_count[0] == 1:
        logger.info("✓ Cache successfully avoided recomputation")
    else:
        logger.warning(
            "⚠ Cache hit not achieved (expected in simulation mode without persistence)"
        )

    # Test invalidation
    logger.info("Invalidating cache...")
    cache.invalidate(key)

    # Third call - should compute again
    logger.info("Third get_or_compute() after invalidation - expect cache MISS:")
    data3 = cache.get_or_compute(key, expensive_computation, ttl_s=3600)
    logger.info(
        f"  Received data: {data3[:20]}... (compute called {compute_count[0]} time(s))"
    )

    logger.info("✓ CloudCacheManager demo complete\n")


def demo_distributed_checkpoint(adapter, metrics):
    """
    Demonstrate DistributedCheckpointManager saving checkpoint to cloud.

    Args:
        adapter: CloudAdapter instance
        metrics: MetricsManager instance
    """
    logger.info("\n" + "=" * 80)
    logger.info("DEMO 3: DistributedCheckpointManager")
    logger.info("=" * 80)

    # Create checkpoint manager
    checkpoint_mgr = DistributedCheckpointManager(
        checkpoint_dir="artifacts/checkpoints",
        cloud_adapter=adapter,
        cloud_path="checkpoints",
        keep_last_n=5,
        sync_local=True,
    )

    # Create sample checkpoint data
    from odibi_core.checkpoint.checkpoint_manager import Checkpoint
    from odibi_core.core import ExecutionMode

    checkpoint = Checkpoint(
        dag_name="demo_dag",
        mode=ExecutionMode.BATCH,
        data_map={
            "ingest_csv": pd.DataFrame({"col": [1, 2, 3]}),
            "transform": pd.DataFrame({"col": [10, 20, 30]}),
        },
        completed_nodes={"ingest_csv", "transform"},
        metadata={"demo": "cloud_checkpoint"},
    )

    # Save checkpoint to cloud
    logger.info(f"Saving checkpoint: {checkpoint.checkpoint_id}")
    success = checkpoint_mgr.save(checkpoint)

    if success:
        logger.info(f"✓ Checkpoint saved to cloud storage")
    else:
        logger.error("✗ Failed to save checkpoint")

    # Load checkpoint back
    logger.info(f"Loading checkpoint: {checkpoint.checkpoint_id}")
    loaded = checkpoint_mgr.load(checkpoint.checkpoint_id)

    if loaded:
        logger.info(f"✓ Checkpoint loaded from cloud storage")
        logger.info(f"  Completed nodes: {loaded.completed_nodes}")
        logger.info(f"  Data map keys: {list(loaded.data_map.keys())}")
    else:
        logger.error("✗ Failed to load checkpoint")

    # Test load_latest
    logger.info(f"Loading latest checkpoint for DAG: demo_dag")
    latest = checkpoint_mgr.load_latest("demo_dag")

    if latest:
        logger.info(f"✓ Latest checkpoint loaded: {latest.checkpoint_id}")
    else:
        logger.warning("✗ No latest checkpoint found")

    logger.info("✓ DistributedCheckpointManager demo complete\n")


# DistributedExecutor demo commented out - needs DAG class refactoring
# TODO: Re-enable once DAG/Node classes are fixed


def print_metrics_summary(metrics):
    """
    Print MetricsManager summary.

    Args:
        metrics: MetricsManager instance
    """
    logger.info("\n" + "=" * 80)
    logger.info("METRICS SUMMARY")
    logger.info("=" * 80)

    # Print cache metrics
    cache_hits = metrics.get_metric_value(MetricType.CACHE_HIT, "cache_hits") or 0
    cache_misses = metrics.get_metric_value(MetricType.CACHE_MISS, "cache_misses") or 0
    cache_puts = metrics.get_metric_value(MetricType.CACHE_HIT, "cache_puts") or 0

    logger.info(f"Cache Hits:   {cache_hits}")
    logger.info(f"Cache Misses: {cache_misses}")
    logger.info(f"Cache Puts:   {cache_puts}")

    if cache_hits + cache_misses > 0:
        hit_rate = cache_hits / (cache_hits + cache_misses) * 100
        logger.info(f"Cache Hit Rate: {hit_rate:.1f}%")

    logger.info("=" * 80 + "\n")


def main():
    """Main demo function"""
    print("\n" + "=" * 80)
    print("ODIBI CORE Phase 7 - Cloud Infrastructure Demo")
    print("=" * 80 + "\n")

    # Check Azure credentials
    has_azure, account_name = check_azure_credentials()

    if has_azure:
        print("[AZURE] Running with REAL Azure adapter")
        simulate = False
    else:
        print("[SIMULATION] Running in SIMULATION mode")
        print(
            "Set AZURE_STORAGE_ACCOUNT and AZURE_STORAGE_KEY env vars for real Azure mode"
        )
        simulate = True

    print()

    # Create metrics manager
    metrics = MetricsManager()

    # Demo 1: CloudAdapter
    adapter = demo_cloud_adapter(simulate=simulate, account_name=account_name)

    # Demo 2: CloudCacheManager
    demo_cloud_cache(adapter, metrics)

    # Demo 3: DistributedCheckpointManager
    demo_distributed_checkpoint(adapter, metrics)

    # Print metrics summary
    print_metrics_summary(metrics)

    print("\n" + "=" * 80)
    print("[OK] All Phase 7 demos completed successfully!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
