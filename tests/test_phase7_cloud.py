"""
Phase 7 Cloud Infrastructure Tests

Tests for cloud adapters, distributed execution, and cloud caching in simulation mode.
Includes optional Azure integration tests (run with AZURE_TESTS=1).

Run tests:
    pytest -v tests/test_phase7_cloud.py                    # Simulation tests only
    AZURE_TESTS=1 pytest -v tests/test_phase7_cloud.py      # Include Azure integration tests
"""

import pytest
import time
import os
import hashlib
import json
from unittest.mock import MagicMock, patch
from concurrent.futures import ThreadPoolExecutor

from odibi_core.cache.cloud_cache_manager import CloudCacheManager
from odibi_core.cloud.cloud_adapter import CloudAdapter, CloudAdapterBase
from odibi_core.checkpoint.distributed_checkpoint_manager import (
    DistributedCheckpointManager,
)
from odibi_core.metrics.metrics_manager import MetricsManager, MetricType
from odibi_core.core.dag_builder import DAGBuilder, DAGNode
from odibi_core.core.node import NodeBase
from odibi_core.core.tracker import Tracker
from odibi_core.core.events import EventEmitter


# ============================================================================
# CloudCacheManager Simulation Tests
# ============================================================================


class TestCloudCacheManager:
    """Test CloudCacheManager with simulated cloud adapter"""

    @pytest.fixture
    def mock_adapter(self):
        """Create a mock cloud adapter for testing"""
        adapter = MagicMock(spec=CloudAdapterBase)
        adapter.connected = True
        adapter.simulate = True

        # Storage for simulated cloud data
        adapter._storage = {}

        def mock_write(data, path, format="parquet", **kwargs):
            adapter._storage[path] = data
            return True

        def mock_read(path, format="parquet", **kwargs):
            if path not in adapter._storage:
                raise FileNotFoundError(f"Path not found: {path}")
            return adapter._storage[path]

        def mock_exists(path):
            return path in adapter._storage

        def mock_delete(path):
            if path in adapter._storage:
                del adapter._storage[path]
                return True
            return False

        def mock_list(path, pattern=None):
            # Return manifest files matching path prefix
            files = []
            for key in adapter._storage.keys():
                if key.startswith(path):
                    files.append(key)
            return files

        adapter.write.side_effect = mock_write
        adapter.read.side_effect = mock_read
        adapter.exists.side_effect = mock_exists
        adapter.delete.side_effect = mock_delete
        adapter.list.side_effect = mock_list

        return adapter

    @pytest.fixture
    def cache_manager(self, mock_adapter):
        """Create CloudCacheManager with mock adapter"""
        metrics = MetricsManager()
        return CloudCacheManager(
            adapter=mock_adapter,
            prefix="test_cache/",
            default_ttl_s=3600,
            metrics=metrics,
        )

    def test_compute_key_determinism(self, cache_manager):
        """Test that compute_key() produces deterministic keys"""
        namespace = "transform_step"
        inputs = {"file": "data.csv", "columns": ["A", "B", "C"]}
        version = "v1"

        # Compute key multiple times
        key1 = cache_manager.compute_key(namespace, inputs, version)
        key2 = cache_manager.compute_key(namespace, inputs, version)
        key3 = cache_manager.compute_key(namespace, inputs, version)

        # All should be identical
        assert key1 == key2 == key3

        # Different inputs should produce different keys
        inputs2 = {"file": "data.csv", "columns": ["A", "B"]}
        key4 = cache_manager.compute_key(namespace, inputs2, version)
        assert key4 != key1

        # Key format should be namespace_hash
        assert key1.startswith(f"{namespace}_")
        assert len(key1.split("_")[-1]) == 16  # 16-char hash

    def test_put_get_happy_path(self, cache_manager):
        """Test put/get happy path with bytes data"""
        key = "test_key_1"
        data = b"Hello, world! This is test data."

        # Put data in cache
        success = cache_manager.put(key, data, ttl_s=3600)
        assert success is True

        # Get data from cache
        retrieved = cache_manager.get(key)
        assert retrieved == data

        # Verify metrics were recorded
        counter_key = f"{MetricType.CACHE_HIT.value}:cache_hits"
        assert cache_manager.metrics.counters.get(counter_key, 0) >= 1

    def test_ttl_expiry(self, cache_manager):
        """Test TTL expiry (set TTL=1s, wait 2s, verify exists() returns False)"""
        key = "test_key_ttl"
        data = b"Short-lived data"

        # Put data with 1-second TTL
        success = cache_manager.put(key, data, ttl_s=1)
        assert success is True

        # Immediately check - should exist
        assert cache_manager.exists(key) is True

        # Wait 2 seconds
        time.sleep(2)

        # Check again - should be expired
        assert cache_manager.exists(key) is False

        # Get should return None
        retrieved = cache_manager.get(key)
        assert retrieved is None

    def test_invalidate(self, cache_manager):
        """Test invalidate() removes cache entry"""
        key = "test_key_invalidate"
        data = b"Data to invalidate"

        # Put data
        cache_manager.put(key, data)

        # Verify it exists
        assert cache_manager.exists(key) is True

        # Invalidate
        success = cache_manager.invalidate(key)
        assert success is True

        # Verify it's gone
        assert cache_manager.exists(key) is False
        retrieved = cache_manager.get(key)
        assert retrieved is None

    def test_get_or_compute_caching(self, cache_manager):
        """Test get_or_compute() caching behavior"""
        key = "test_key_compute"

        # Mock compute function
        compute_count = [0]  # Use list to allow mutation in closure

        def compute_fn():
            compute_count[0] += 1
            return b"Computed data"

        # First call - should compute
        data1 = cache_manager.get_or_compute(key, compute_fn, ttl_s=3600)
        assert data1 == b"Computed data"
        assert compute_count[0] == 1

        # Second call - should use cache
        data2 = cache_manager.get_or_compute(key, compute_fn, ttl_s=3600)
        assert data2 == b"Computed data"
        assert compute_count[0] == 1  # Compute not called again

        # Invalidate and try again
        cache_manager.invalidate(key)
        data3 = cache_manager.get_or_compute(key, compute_fn, ttl_s=3600)
        assert data3 == b"Computed data"
        assert compute_count[0] == 2  # Compute called again

    def test_metrics_counters_increment(self, cache_manager):
        """Test that metrics counters increment correctly"""
        hits_key = f"{MetricType.CACHE_HIT.value}:cache_hits"
        misses_key = f"{MetricType.CACHE_MISS.value}:cache_misses"

        initial_hits = cache_manager.metrics.counters.get(hits_key, 0)
        initial_misses = cache_manager.metrics.counters.get(misses_key, 0)

        # Cache miss
        cache_manager.get("nonexistent_key")
        misses_after = cache_manager.metrics.counters.get(misses_key, 0)
        assert misses_after > initial_misses

        # Cache hit
        cache_manager.put("hit_key", b"data")
        cache_manager.get("hit_key")
        hits_after = cache_manager.metrics.counters.get(hits_key, 0)
        assert hits_after > initial_hits


# ============================================================================
# DistributedExecutor Simulation Tests
# ============================================================================
# SKIPPED: DistributedExecutor has import dependencies issues
# TODO: Fix distributed_executor.py imports (DAG class doesn't exist, should use DAGBuilder)
# Then re-enable the tests for:
# - test_parallel_execution_thread_pool
# - test_retry_logic
# - test_node_grouping_by_level


# ============================================================================
# DistributedCheckpointManager Simulation Tests
# ============================================================================


class TestDistributedCheckpointManager:
    """Test DistributedCheckpointManager with simulated cloud adapter"""

    @pytest.fixture
    def mock_adapter(self):
        """Create a mock cloud adapter for testing"""
        adapter = MagicMock(spec=CloudAdapterBase)
        adapter.connected = True
        adapter.simulate = True

        # Storage for simulated cloud data
        adapter._storage = {}

        def mock_write(data, path, format="parquet", **kwargs):
            adapter._storage[path] = data
            return True

        def mock_read(path, format="parquet", **kwargs):
            if path not in adapter._storage:
                raise FileNotFoundError(f"Path not found: {path}")
            return adapter._storage[path]

        def mock_exists(path):
            return path in adapter._storage

        def mock_delete(path):
            if path in adapter._storage:
                del adapter._storage[path]
                return True
            return False

        def mock_list(path, pattern=None):
            files = []
            for key in adapter._storage.keys():
                if key.startswith(path):
                    if pattern:
                        # Simple pattern matching for *.json
                        if pattern == "*.json" and key.endswith(".json"):
                            files.append(key)
                    else:
                        files.append(key)
            return files

        adapter.write.side_effect = mock_write
        adapter.read.side_effect = mock_read
        adapter.exists.side_effect = mock_exists
        adapter.delete.side_effect = mock_delete
        adapter.list.side_effect = mock_list

        return adapter

    @pytest.fixture
    def checkpoint_manager(self, mock_adapter, tmp_path):
        """Create DistributedCheckpointManager with mock adapter"""
        return DistributedCheckpointManager(
            checkpoint_dir=str(tmp_path / "checkpoints"),
            cloud_adapter=mock_adapter,
            cloud_path="test_checkpoints",
            keep_last_n=5,
            sync_local=True,
        )

    def test_save_to_cloud(self, checkpoint_manager, mock_adapter):
        """Test saving checkpoint to cloud storage"""
        from odibi_core.checkpoint.checkpoint_manager import Checkpoint, NodeCheckpoint
        from odibi_core.core import ExecutionMode

        # Create a checkpoint
        checkpoint = checkpoint_manager.create_checkpoint(
            dag_name="test_dag",
            completed_nodes=[
                NodeCheckpoint(
                    node_name="node1",
                    state="SUCCESS",
                    completed_at="2024-01-01T00:00:00",
                    duration_ms=100.0,
                )
            ],
            pending_nodes=set(),
            mode=str(ExecutionMode.BATCH.value),
            metadata={"test": "value"},
        )

        # Save checkpoint
        success = checkpoint_manager.save(checkpoint)
        assert success is True

        # Verify data was written to cloud
        expected_path = f"test_checkpoints/{checkpoint.checkpoint_id}.json"
        assert expected_path in mock_adapter._storage

    def test_load_from_cloud(self, checkpoint_manager, mock_adapter):
        """Test loading checkpoint from cloud storage"""
        from odibi_core.checkpoint.checkpoint_manager import Checkpoint, NodeCheckpoint
        from odibi_core.core import ExecutionMode

        # Create and save a checkpoint
        checkpoint = checkpoint_manager.create_checkpoint(
            dag_name="test_dag",
            completed_nodes=[
                NodeCheckpoint(
                    node_name="node1",
                    state="SUCCESS",
                    completed_at="2024-01-01T00:00:00",
                    duration_ms=100.0,
                )
            ],
            pending_nodes=set(),
            mode=str(ExecutionMode.BATCH.value),
            metadata={"test": "value"},
        )

        checkpoint_manager.save(checkpoint)

        # Load checkpoint
        loaded = checkpoint_manager.load(checkpoint.checkpoint_id)

        assert loaded is not None
        assert loaded.checkpoint_id == checkpoint.checkpoint_id
        assert loaded.dag_name == checkpoint.dag_name
        assert len(loaded.completed_nodes) == 1
        assert loaded.completed_nodes[0].node_name == "node1"

    def test_load_latest(self, checkpoint_manager):
        """Test loading the latest checkpoint for a DAG"""
        from odibi_core.checkpoint.checkpoint_manager import Checkpoint, NodeCheckpoint
        from odibi_core.core import ExecutionMode
        import time

        # Create multiple checkpoints
        for i in range(3):
            checkpoint = checkpoint_manager.create_checkpoint(
                dag_name="test_dag",
                completed_nodes=[
                    NodeCheckpoint(
                        node_name=f"node{i}",
                        state="SUCCESS",
                        completed_at="2024-01-01T00:00:00",
                        duration_ms=100.0,
                    )
                ],
                pending_nodes=set(),
                mode=str(ExecutionMode.BATCH.value),
                metadata={"iteration": i},
            )
            checkpoint_manager.save(checkpoint)
            time.sleep(0.02)  # Ensure different timestamps

        # Load latest
        latest = checkpoint_manager.load_latest("test_dag")

        assert latest is not None
        assert latest.metadata["iteration"] == 2  # Last checkpoint


# ============================================================================
# DistributedExecutor Tests
# ============================================================================


class TestDistributedExecutor:
    """Test DistributedExecutor with simulated DAGs"""

    @pytest.fixture
    def simple_dag_and_context(self):
        """Create a simple 3-node DAG for testing"""
        from odibi_core.core.config_loader import Step
        from odibi_core.core.dag_builder import DAGBuilder
        from odibi_core.engine.pandas_context import PandasEngineContext

        # Create simple steps
        steps = [
            Step(
                layer="ingest",
                name="read_data",
                type="config_op",
                engine="pandas",
                value="test_data.csv",
                inputs={},
                outputs={"data": "raw_data"},
            ),
            Step(
                layer="transform",
                name="transform_data",
                type="sql",
                engine="pandas",
                value="SELECT * FROM data",
                inputs={"data": "raw_data"},
                outputs={"data": "transformed_data"},
            ),
            Step(
                layer="store",
                name="write_data",
                type="config_op",
                engine="pandas",
                value="output.csv",
                inputs={"data": "transformed_data"},
                outputs={},
            ),
        ]

        # Build DAG
        builder = DAGBuilder(steps)
        dag = builder.build()

        # Create context
        context = PandasEngineContext()

        return dag, context, steps

    def test_distributed_executor_creation(self, simple_dag_and_context):
        """Test DistributedExecutor can be created with DAGBuilder output"""
        from odibi_core.distributed import DistributedExecutor, ExecutionBackend

        dag, context, steps = simple_dag_and_context
        tracker = Tracker()
        events = EventEmitter()

        # Create distributed executor
        executor = DistributedExecutor(
            dag=dag,
            context=context,
            tracker=tracker,
            events=events,
            backend=ExecutionBackend.THREAD_POOL,
            distributed_max_workers=2,
        )

        assert executor is not None
        assert executor.backend == ExecutionBackend.THREAD_POOL
        assert executor.distributed_max_workers == 2
        assert len(executor.dag) == 3  # 3 nodes in DAG

    def test_distributed_executor_backend_fallback(self, simple_dag_and_context):
        """Test that RAY backend falls back to THREAD_POOL"""
        from odibi_core.distributed import DistributedExecutor, ExecutionBackend

        dag, context, steps = simple_dag_and_context
        tracker = Tracker()
        events = EventEmitter()

        # Create executor with RAY (not implemented yet)
        executor = DistributedExecutor(
            dag=dag,
            context=context,
            tracker=tracker,
            events=events,
            backend=ExecutionBackend.RAY,  # Should fall back
            distributed_max_workers=4,
        )

        # Verify fallback to THREAD_POOL
        assert executor.backend == ExecutionBackend.THREAD_POOL

    def test_distributed_executor_metrics_tracking(self, simple_dag_and_context):
        """Test that distributed executor tracks metrics"""
        from odibi_core.distributed import DistributedExecutor, ExecutionBackend

        dag, context, steps = simple_dag_and_context
        tracker = Tracker()
        events = EventEmitter()

        executor = DistributedExecutor(
            dag=dag,
            context=context,
            tracker=tracker,
            events=events,
            backend=ExecutionBackend.THREAD_POOL,
            distributed_max_workers=2,
        )

        # Verify metrics tracking setup
        assert executor.tracker is not None
        assert executor.retry_counts == {}  # Initially empty


# ============================================================================
# Optional Azure Integration Tests
# ============================================================================


@pytest.mark.azure
@pytest.mark.skipif(
    os.getenv("AZURE_TESTS") != "1",
    reason="Azure integration tests disabled. Set AZURE_TESTS=1 to run.",
)
class TestAzureIntegration:
    """
    Optional Azure integration tests.

    Requires:
        - AZURE_STORAGE_ACCOUNT env var
        - AZURE_STORAGE_KEY or Azure credentials
        - AZURE_TESTS=1 env var
    """

    def test_azure_adapter_round_trip(self):
        """Test Azure adapter: connect, write parquet, read back, verify"""
        import pandas as pd

        # Check for Azure credentials
        account_name = os.getenv("AZURE_STORAGE_ACCOUNT")
        if not account_name:
            pytest.skip("AZURE_STORAGE_ACCOUNT not set")

        # Create adapter
        adapter = CloudAdapter.create(
            "azure", account_name=account_name, container="odibi-test", simulate=False
        )

        # Connect
        success = adapter.connect()
        assert success is True
        assert adapter.connected is True

        # Create test data
        test_data = pd.DataFrame(
            {
                "col1": [1, 2, 3, 4, 5],
                "col2": ["a", "b", "c", "d", "e"],
                "col3": [1.1, 2.2, 3.3, 4.4, 5.5],
            }
        )

        # Write to Azure
        test_path = "odibi-test/test_phase7/test_data.parquet"
        write_success = adapter.write(test_data, test_path, format="parquet")
        assert write_success is True

        # Verify existence
        exists = adapter.exists(test_path)
        assert exists is True

        # Read back
        read_data = adapter.read(test_path, format="parquet")

        # Verify data matches
        pd.testing.assert_frame_equal(test_data, read_data)

        # Cleanup
        adapter.delete(test_path)
        adapter.disconnect()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
