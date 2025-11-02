"""
Checkpoint manager for DAG execution state persistence and recovery.

Enables:
- Save DAG progress at any point
- Resume from last successful node
- Handle failures gracefully with rollback
- Store node outputs and cache metadata
"""

import json
import logging
import pickle
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class CheckpointMode(str, Enum):
    """Checkpoint creation modes."""

    MANUAL = "manual"  # User-triggered checkpoints
    AUTO = "auto"  # After each successful node
    INTERVAL = "interval"  # At regular intervals
    LAYER = "layer"  # After completing each DAG layer


@dataclass
class NodeCheckpoint:
    """
    Checkpoint data for a single node.

    Attributes:
        node_name: Name of the node
        state: Final state (SUCCESS, FAILED, CACHED)
        completed_at: Timestamp when completed
        duration_ms: Execution duration
        attempts: Number of attempts
        cached: Whether output was cached
        output_path: Path to output data (if saved)
    """

    node_name: str
    state: str
    completed_at: str
    duration_ms: float
    attempts: int = 1
    cached: bool = False
    output_path: Optional[str] = None
    error: Optional[str] = None


@dataclass
class Checkpoint:
    """
    Complete checkpoint of DAG execution state.

    Attributes:
        checkpoint_id: Unique identifier
        dag_name: Name of the DAG
        created_at: Creation timestamp
        mode: Execution mode (batch, stream, resume)
        completed_nodes: List of completed node checkpoints
        pending_nodes: Set of pending node names
        failed_nodes: Set of failed node names
        iteration: Iteration number (for streaming)
        metadata: Additional metadata
    """

    checkpoint_id: str
    dag_name: str
    created_at: str
    mode: str
    completed_nodes: List[NodeCheckpoint] = field(default_factory=list)
    pending_nodes: Set[str] = field(default_factory=set)
    failed_nodes: Set[str] = field(default_factory=set)
    iteration: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "checkpoint_id": self.checkpoint_id,
            "dag_name": self.dag_name,
            "created_at": self.created_at,
            "mode": self.mode,
            "completed_nodes": [asdict(n) for n in self.completed_nodes],
            "pending_nodes": list(self.pending_nodes),
            "failed_nodes": list(self.failed_nodes),
            "iteration": self.iteration,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Checkpoint":
        """Create from dictionary."""
        data = data.copy()
        data["completed_nodes"] = [
            NodeCheckpoint(**n) for n in data.get("completed_nodes", [])
        ]
        data["pending_nodes"] = set(data.get("pending_nodes", []))
        data["failed_nodes"] = set(data.get("failed_nodes", []))
        return cls(**data)


class CheckpointManager:
    """
    Manages checkpoints for DAG execution state.

    Features:
    - Create checkpoints at configurable intervals
    - Resume from last successful checkpoint
    - Store node outputs for recovery
    - Track cache metadata
    - Clean up old checkpoints

    Args:
        checkpoint_dir: Directory to store checkpoints
        mode: Checkpoint creation mode
        keep_last_n: Number of checkpoints to retain
        save_outputs: Whether to save node outputs

    Example:
        >>> manager = CheckpointManager()
        >>> checkpoint = manager.create_checkpoint("my_dag", completed_nodes, pending_nodes)
        >>> manager.save(checkpoint)
        >>>
        >>> # Later, resume from checkpoint
        >>> checkpoint = manager.load_latest("my_dag")
        >>> completed = {n.node_name for n in checkpoint.completed_nodes}
    """

    def __init__(
        self,
        checkpoint_dir: str = "artifacts/checkpoints",
        mode: CheckpointMode = CheckpointMode.AUTO,
        keep_last_n: int = 5,
        save_outputs: bool = False,
    ):
        """Initialize checkpoint manager."""
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.mode = mode
        self.keep_last_n = keep_last_n
        self.save_outputs = save_outputs
        logger.info(f"CheckpointManager initialized: dir={checkpoint_dir}, mode={mode}")

    def create_checkpoint(
        self,
        dag_name: str,
        completed_nodes: List[NodeCheckpoint],
        pending_nodes: Set[str],
        failed_nodes: Set[str] = None,
        mode: str = "batch",
        iteration: int = 0,
        metadata: Dict[str, Any] = None,
    ) -> Checkpoint:
        """
        Create a new checkpoint.

        Args:
            dag_name: Name of the DAG
            completed_nodes: List of completed node checkpoints
            pending_nodes: Set of pending node names
            failed_nodes: Set of failed node names
            mode: Execution mode
            iteration: Iteration number (for streaming)
            metadata: Additional metadata

        Returns:
            Checkpoint object
        """
        checkpoint_id = f"{dag_name}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        checkpoint = Checkpoint(
            checkpoint_id=checkpoint_id,
            dag_name=dag_name,
            created_at=datetime.now().isoformat(),
            mode=mode,
            completed_nodes=completed_nodes,
            pending_nodes=pending_nodes,
            failed_nodes=failed_nodes or set(),
            iteration=iteration,
            metadata=metadata or {},
        )

        logger.info(
            f"Created checkpoint: {checkpoint_id} "
            f"(completed={len(completed_nodes)}, pending={len(pending_nodes)})"
        )

        return checkpoint

    def save(self, checkpoint: Checkpoint) -> Path:
        """
        Save checkpoint to disk.

        Args:
            checkpoint: Checkpoint to save

        Returns:
            Path to saved checkpoint file
        """
        checkpoint_path = self.checkpoint_dir / f"{checkpoint.checkpoint_id}.json"

        try:
            with open(checkpoint_path, "w") as f:
                json.dump(checkpoint.to_dict(), f, indent=2)

            logger.info(f"Saved checkpoint: {checkpoint_path}")

            self._cleanup_old_checkpoints(checkpoint.dag_name)

            return checkpoint_path
        except Exception as e:
            logger.error(f"Error saving checkpoint: {e}")
            raise

    def load(self, checkpoint_id: str) -> Optional[Checkpoint]:
        """
        Load checkpoint by ID.

        Args:
            checkpoint_id: Checkpoint identifier

        Returns:
            Checkpoint object or None if not found
        """
        checkpoint_path = self.checkpoint_dir / f"{checkpoint_id}.json"

        if not checkpoint_path.exists():
            logger.warning(f"Checkpoint not found: {checkpoint_id}")
            return None

        try:
            with open(checkpoint_path, "r") as f:
                data = json.load(f)

            checkpoint = Checkpoint.from_dict(data)
            logger.info(f"Loaded checkpoint: {checkpoint_id}")
            return checkpoint
        except Exception as e:
            logger.error(f"Error loading checkpoint: {e}")
            return None

    def load_latest(self, dag_name: str) -> Optional[Checkpoint]:
        """
        Load most recent checkpoint for a DAG.

        Args:
            dag_name: Name of the DAG

        Returns:
            Latest checkpoint or None if no checkpoints exist
        """
        checkpoints = self.list_checkpoints(dag_name)

        if not checkpoints:
            logger.info(f"No checkpoints found for DAG: {dag_name}")
            return None

        latest_id = checkpoints[0]
        return self.load(latest_id)

    def list_checkpoints(self, dag_name: str) -> List[str]:
        """
        List all checkpoints for a DAG, sorted by creation time (newest first).

        Args:
            dag_name: Name of the DAG

        Returns:
            List of checkpoint IDs
        """
        pattern = f"{dag_name}_*.json"
        checkpoint_files = sorted(
            self.checkpoint_dir.glob(pattern),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )

        return [f.stem for f in checkpoint_files]

    def delete(self, checkpoint_id: str) -> bool:
        """
        Delete a checkpoint.

        Args:
            checkpoint_id: Checkpoint to delete

        Returns:
            True if deleted, False if not found
        """
        checkpoint_path = self.checkpoint_dir / f"{checkpoint_id}.json"

        if not checkpoint_path.exists():
            return False

        try:
            checkpoint_path.unlink()
            logger.info(f"Deleted checkpoint: {checkpoint_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting checkpoint: {e}")
            return False

    def _cleanup_old_checkpoints(self, dag_name: str) -> None:
        """Remove old checkpoints beyond keep_last_n."""
        checkpoints = self.list_checkpoints(dag_name)

        if len(checkpoints) <= self.keep_last_n:
            return

        to_delete = checkpoints[self.keep_last_n :]

        for checkpoint_id in to_delete:
            self.delete(checkpoint_id)

        logger.info(f"Cleaned up {len(to_delete)} old checkpoints for {dag_name}")

    def save_node_output(
        self, checkpoint_id: str, node_name: str, data: Any
    ) -> Optional[Path]:
        """
        Save node output data.

        Args:
            checkpoint_id: Checkpoint ID
            node_name: Node name
            data: Data to save (DataFrame or other)

        Returns:
            Path to saved data or None if save_outputs is False
        """
        if not self.save_outputs:
            return None

        output_dir = self.checkpoint_dir / checkpoint_id / "outputs"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{node_name}.pkl"

        try:
            with open(output_path, "wb") as f:
                pickle.dump(data, f)

            logger.debug(f"Saved node output: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error saving node output: {e}")
            return None

    def load_node_output(self, checkpoint_id: str, node_name: str) -> Optional[Any]:
        """
        Load node output data.

        Args:
            checkpoint_id: Checkpoint ID
            node_name: Node name

        Returns:
            Loaded data or None if not found
        """
        output_path = (
            self.checkpoint_dir / checkpoint_id / "outputs" / f"{node_name}.pkl"
        )

        if not output_path.exists():
            return None

        try:
            with open(output_path, "rb") as f:
                data = pickle.load(f)

            logger.debug(f"Loaded node output: {output_path}")
            return data
        except Exception as e:
            logger.error(f"Error loading node output: {e}")
            return None

    def should_checkpoint(self, nodes_since_last: int = 0) -> bool:
        """
        Determine if checkpoint should be created.

        Args:
            nodes_since_last: Number of nodes completed since last checkpoint

        Returns:
            True if checkpoint should be created
        """
        if self.mode == CheckpointMode.MANUAL:
            return False
        elif self.mode == CheckpointMode.AUTO:
            return True
        elif self.mode == CheckpointMode.INTERVAL:
            return nodes_since_last >= 5
        elif self.mode == CheckpointMode.LAYER:
            return False

        return False

    def get_resume_point(self, checkpoint: Checkpoint) -> Set[str]:
        """
        Get set of nodes to skip when resuming.

        Args:
            checkpoint: Checkpoint to resume from

        Returns:
            Set of node names that are already completed
        """
        completed = {
            n.node_name for n in checkpoint.completed_nodes if n.state == "SUCCESS"
        }
        logger.info(f"Resume point: {len(completed)} nodes already completed")
        return completed

    def get_stats(self, dag_name: str) -> Dict[str, Any]:
        """
        Get checkpoint statistics for a DAG.

        Args:
            dag_name: Name of the DAG

        Returns:
            Statistics dictionary
        """
        checkpoints = self.list_checkpoints(dag_name)

        if not checkpoints:
            return {"checkpoint_count": 0}

        latest = self.load_latest(dag_name)

        return {
            "checkpoint_count": len(checkpoints),
            "latest_checkpoint": checkpoints[0] if checkpoints else None,
            "latest_created_at": latest.created_at if latest else None,
            "latest_completed_nodes": len(latest.completed_nodes) if latest else 0,
            "latest_pending_nodes": len(latest.pending_nodes) if latest else 0,
            "latest_iteration": latest.iteration if latest else 0,
        }
