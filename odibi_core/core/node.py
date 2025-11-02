"""
Base Node abstraction for ODIBI CORE.

All operations (connect, ingest, store, transform, publish) are modeled as Nodes.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, Optional
from dataclasses import dataclass


class NodeState(Enum):
    """Node execution state."""

    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    RETRY = "retry"


@dataclass
class Step:
    """
    Pipeline step configuration.

    Attributes:
        layer: Pipeline layer (connect, ingest, store, transform, publish)
        name: Unique step identifier
        type: Step type (sql, function, config_op, api)
        engine: Execution engine (pandas, spark)
        value: SQL text, function reference, or config value
        params: Optional parameters for the step
        inputs: Logical name → dataset key mapping for inputs
        outputs: Logical name → dataset key mapping for outputs
        metadata: Optional metadata for documentation
    """

    layer: str
    name: str
    type: str
    engine: str
    value: str
    params: Optional[Dict[str, Any]] = None
    inputs: Optional[Dict[str, str]] = None
    outputs: Optional[Dict[str, str]] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        """Initialize default values for optional fields."""
        if self.params is None:
            self.params = {}
        if self.inputs is None:
            self.inputs = {}
        if self.outputs is None:
            self.outputs = {}
        if self.metadata is None:
            self.metadata = {}


class NodeBase(ABC):
    """
    Abstract base class for all ODIBI CORE Nodes.

    Every operation in the framework is a Node that:
    - Receives a data_map (dict of logical name → DataFrame)
    - Reads from inputs (references to data_map keys)
    - Executes engine-specific logic via EngineContext
    - Writes to outputs (new entries in data_map)
    - Updates NodeState (PENDING → SUCCESS/FAILED)

    Args:
        step: Step configuration for this node
        context: Engine context (Pandas or Spark)
        tracker: Execution tracker for snapshots
        events: Event emitter for pipeline hooks

    Example:
        >>> step = Step(layer="ingest", name="read_csv", type="config_op",
        ...             engine="pandas", value="data/input.csv",
        ...             outputs={"data": "raw_data"})
        >>> node = IngestNode(step, pandas_context, tracker, events)
        >>> data_map = node.run({})
        >>> assert "raw_data" in data_map
    """

    def __init__(
        self,
        step: Step,
        context: Any,  # EngineContext (avoiding circular import)
        tracker: Any,  # Tracker
        events: Any,  # EventEmitter
    ) -> None:
        """
        Initialize Node.

        Args:
            step: Step configuration
            context: Engine context for execution
            tracker: Tracker for logging snapshots
            events: Event emitter for hooks
        """
        self.step = step
        self.context = context
        self.tracker = tracker
        self.events = events
        self.state = NodeState.PENDING

    @abstractmethod
    def run(self, data_map: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the node's operation.

        Args:
            data_map: Dictionary mapping logical names to DataFrames

        Returns:
            Updated data_map with new outputs

        Raises:
            Exception: On execution failure (sets state to FAILED)
        """
        pass

    def _update_state(self, state: NodeState) -> None:
        """
        Update node execution state.

        Args:
            state: New state
        """
        self.state = state
        # TODO Phase 6: Emit state change event
