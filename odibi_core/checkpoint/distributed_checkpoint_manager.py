"""
Distributed Checkpoint Manager (Phase 7)

Extends Phase 6 CheckpointManager to support cloud-based distributed checkpointing.

Features:
- Store checkpoints in cloud storage (Azure Blob, S3, HDFS)
- Multi-node checkpoint coordination
- Checkpoint versioning and rollback
- Cross-region checkpoint replication (future)

Usage:
    from odibi_core.checkpoint import DistributedCheckpointManager
    from odibi_core.cloud import CloudAdapter

    # Create cloud adapter
    cloud = CloudAdapter.create("azure", account_name="myaccount", simulate=True)
    cloud.connect()

    # Create distributed checkpoint manager
    checkpoint_mgr = DistributedCheckpointManager(
        checkpoint_dir="/checkpoints",
        cloud_adapter=cloud,
        cloud_path="container/checkpoints"
    )

    # Save checkpoint to cloud
    checkpoint = checkpoint_mgr.create_checkpoint(dag, data_map, mode="batch")

    # Load checkpoint from cloud
    checkpoint = checkpoint_mgr.load_latest("my_dag")
"""

import logging
import json
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime

from .checkpoint_manager import CheckpointManager, Checkpoint
from ..cloud.cloud_adapter import CloudAdapterBase

logger = logging.getLogger(__name__)


class DistributedCheckpointManager(CheckpointManager):
    """
    Distributed checkpoint manager with cloud storage support.

    Extends local CheckpointManager to store/load checkpoints from cloud storage
    for distributed DAG execution across multiple nodes.

    Attributes:
        cloud_adapter: Cloud adapter for remote storage
        cloud_path: Cloud storage path for checkpoints
        sync_local: Whether to maintain local copies of checkpoints
        replicate: Whether to replicate checkpoints across regions (future)
    """

    def __init__(
        self,
        checkpoint_dir: str = "artifacts/checkpoints",
        cloud_adapter: Optional[CloudAdapterBase] = None,
        cloud_path: Optional[str] = None,
        keep_last_n: int = 10,
        sync_local: bool = True,
        replicate: bool = False,
    ):
        """
        Initialize distributed checkpoint manager.

        Args:
            checkpoint_dir: Local checkpoint directory
            cloud_adapter: Cloud adapter instance (Azure, S3, etc.)
            cloud_path: Cloud storage path (e.g., "container/checkpoints")
            keep_last_n: Number of checkpoints to keep (both local and cloud)
            sync_local: Maintain local copies of cloud checkpoints
            replicate: Enable cross-region replication (future feature)
        """
        super().__init__(checkpoint_dir=checkpoint_dir, keep_last_n=keep_last_n)

        self.cloud_adapter = cloud_adapter
        self.cloud_path = cloud_path
        self.sync_local = sync_local
        self.replicate = replicate

        if cloud_adapter and not cloud_adapter.connected:
            logger.warning(
                "Cloud adapter not connected. Call cloud_adapter.connect() first."
            )

        if replicate:
            logger.warning(
                "Cross-region replication is not yet implemented in Phase 7."
            )

    def save(self, checkpoint: Checkpoint) -> bool:
        """
        Save checkpoint to both local and cloud storage.

        Args:
            checkpoint: Checkpoint to save

        Returns:
            bool: True if save successful
        """
        # Save locally (using parent class method)
        if self.sync_local:
            local_success = super().save(checkpoint)
            if not local_success:
                logger.error("Failed to save checkpoint locally")
                return False

        # Save to cloud if adapter is configured
        if self.cloud_adapter and self.cloud_path:
            try:
                cloud_success = self._save_to_cloud(checkpoint)
                if not cloud_success:
                    logger.error("Failed to save checkpoint to cloud")
                    return False
                logger.info(
                    f"Checkpoint {checkpoint.checkpoint_id} saved to cloud storage"
                )
            except Exception as e:
                logger.error(f"Cloud checkpoint save failed: {e}")
                return False

        return True

    def load(self, checkpoint_id: str) -> Optional[Checkpoint]:
        """
        Load checkpoint from cloud or local storage.

        Tries cloud storage first, falls back to local if not found or cloud unavailable.

        Args:
            checkpoint_id: Checkpoint ID to load

        Returns:
            Checkpoint if found, None otherwise
        """
        # Try loading from cloud first
        if self.cloud_adapter and self.cloud_path:
            try:
                checkpoint = self._load_from_cloud(checkpoint_id)
                if checkpoint:
                    logger.info(f"Loaded checkpoint {checkpoint_id} from cloud storage")

                    # Sync to local if enabled
                    if self.sync_local:
                        super().save(checkpoint)

                    return checkpoint
            except Exception as e:
                logger.warning(
                    f"Failed to load checkpoint from cloud: {e}. Trying local..."
                )

        # Fall back to local storage
        if self.sync_local:
            checkpoint = super().load(checkpoint_id)
            if checkpoint:
                logger.info(f"Loaded checkpoint {checkpoint_id} from local storage")
                return checkpoint

        logger.error(f"Checkpoint {checkpoint_id} not found in cloud or local storage")
        return None

    def load_latest(self, dag_name: str) -> Optional[Checkpoint]:
        """
        Load the most recent checkpoint for a DAG.

        Tries cloud storage first, falls back to local.

        Args:
            dag_name: DAG name

        Returns:
            Latest checkpoint if found, None otherwise
        """
        # Try loading from cloud first
        if self.cloud_adapter and self.cloud_path:
            try:
                checkpoint = self._load_latest_from_cloud(dag_name)
                if checkpoint:
                    logger.info(f"Loaded latest checkpoint for {dag_name} from cloud")

                    # Sync to local if enabled
                    if self.sync_local:
                        super().save(checkpoint)

                    return checkpoint
            except Exception as e:
                logger.warning(
                    f"Failed to load latest checkpoint from cloud: {e}. Trying local..."
                )

        # Fall back to local storage
        if self.sync_local:
            checkpoint = super().load_latest(dag_name)
            if checkpoint:
                logger.info(
                    f"Loaded latest checkpoint for {dag_name} from local storage"
                )
                return checkpoint

        return None

    def list_checkpoints(self, dag_name: Optional[str] = None) -> list:
        """
        List all checkpoints (from cloud and local).

        Args:
            dag_name: Optional DAG name filter

        Returns:
            List of checkpoint IDs
        """
        checkpoint_ids = set()

        # List from cloud
        if self.cloud_adapter and self.cloud_path:
            try:
                cloud_ids = self._list_cloud_checkpoints(dag_name)
                checkpoint_ids.update(cloud_ids)
            except Exception as e:
                logger.warning(f"Failed to list cloud checkpoints: {e}")

        # List from local
        if self.sync_local:
            local_ids = super().list_checkpoints(
                dag_name
            )  # Returns list of checkpoint IDs (strings)
            checkpoint_ids.update(local_ids)

        return sorted(list(checkpoint_ids))

    def cleanup_old_checkpoints(self, dag_name: str):
        """
        Clean up old checkpoints from both local and cloud storage.

        Keeps only the most recent keep_last_n checkpoints.

        Args:
            dag_name: DAG name
        """
        # Cleanup local checkpoints
        if self.sync_local:
            super().cleanup_old_checkpoints(dag_name)

        # Cleanup cloud checkpoints
        if self.cloud_adapter and self.cloud_path:
            try:
                self._cleanup_cloud_checkpoints(dag_name)
            except Exception as e:
                logger.error(f"Failed to cleanup cloud checkpoints: {e}")

    def _save_to_cloud(self, checkpoint: Checkpoint) -> bool:
        """Save checkpoint to cloud storage"""
        if not self.cloud_adapter or not self.cloud_path:
            return False

        # Generate cloud path
        filename = f"{checkpoint.checkpoint_id}.json"
        cloud_file_path = f"{self.cloud_path}/{filename}"

        # Convert checkpoint to JSON
        checkpoint_data = checkpoint.to_dict()

        # For cloud adapters that expect DataFrames, convert to JSON string
        import pandas as pd
        import io

        # Create a single-row DataFrame with JSON data
        df = pd.DataFrame([{"checkpoint_data": json.dumps(checkpoint_data)}])

        # Write to cloud
        success = self.cloud_adapter.write(
            df, cloud_file_path, format="parquet"  # Use parquet for efficiency
        )

        return success

    def _load_from_cloud(self, checkpoint_id: str) -> Optional[Checkpoint]:
        """Load checkpoint from cloud storage"""
        if not self.cloud_adapter or not self.cloud_path:
            return None

        # Generate cloud path
        filename = f"{checkpoint_id}.json"
        cloud_file_path = f"{self.cloud_path}/{filename}"

        # Check if exists
        if not self.cloud_adapter.exists(cloud_file_path):
            return None

        # Read from cloud
        df = self.cloud_adapter.read(cloud_file_path, format="parquet")

        # Extract JSON data
        if len(df) == 0:
            return None

        checkpoint_json = df.iloc[0]["checkpoint_data"]
        checkpoint_data = json.loads(checkpoint_json)

        # Convert to Checkpoint object
        checkpoint = Checkpoint.from_dict(checkpoint_data)

        return checkpoint

    def _load_latest_from_cloud(self, dag_name: str) -> Optional[Checkpoint]:
        """Load most recent checkpoint for DAG from cloud"""
        if not self.cloud_adapter or not self.cloud_path:
            return None

        # List all checkpoints for this DAG
        checkpoint_ids = self._list_cloud_checkpoints(dag_name)

        if not checkpoint_ids:
            return None

        # Sort by timestamp (embedded in checkpoint_id)
        # Format: dagname_YYYYMMDD_HHMMSS_microseconds
        checkpoint_ids.sort(reverse=True)

        # Load most recent
        latest_id = checkpoint_ids[0]
        return self._load_from_cloud(latest_id)

    def _list_cloud_checkpoints(self, dag_name: Optional[str] = None) -> list:
        """List checkpoint IDs from cloud storage"""
        if not self.cloud_adapter or not self.cloud_path:
            return []

        # List files in cloud path
        files = self.cloud_adapter.list(self.cloud_path, pattern="*.json")

        # Extract checkpoint IDs
        checkpoint_ids = []
        for file_path in files:
            # Extract filename
            filename = file_path.split("/")[-1]
            checkpoint_id = filename.replace(".json", "")

            # Filter by DAG name if provided
            if dag_name and not checkpoint_id.startswith(dag_name):
                continue

            checkpoint_ids.append(checkpoint_id)

        return checkpoint_ids

    def _cleanup_cloud_checkpoints(self, dag_name: str):
        """Remove old checkpoints from cloud storage"""
        if not self.cloud_adapter or not self.cloud_path:
            return

        # List all checkpoints for this DAG
        checkpoint_ids = self._list_cloud_checkpoints(dag_name)

        if len(checkpoint_ids) <= self.keep_last_n:
            return

        # Sort by timestamp (newest first)
        checkpoint_ids.sort(reverse=True)

        # Delete old checkpoints
        for checkpoint_id in checkpoint_ids[self.keep_last_n :]:
            filename = f"{checkpoint_id}.json"
            cloud_file_path = f"{self.cloud_path}/{filename}"

            try:
                self.cloud_adapter.delete(cloud_file_path)
                logger.info(f"Deleted old cloud checkpoint: {checkpoint_id}")
            except Exception as e:
                logger.warning(
                    f"Failed to delete cloud checkpoint {checkpoint_id}: {e}"
                )
