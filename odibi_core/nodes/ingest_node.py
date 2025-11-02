"""IngestNode for reading data from sources."""

from typing import Any, Dict
from odibi_core.core.node import NodeBase, NodeState


class IngestNode(NodeBase):
    """
    Node for ingesting data from sources.

    Reads data from CSV, Parquet, databases, APIs, etc., and writes to data_map.

    Args:
        step: Step configuration with source path/query
        context: Engine context
        tracker: Execution tracker
        events: Event emitter

    Example:
        >>> step = Step(
        ...     layer="ingest",
        ...     name="read_csv",
        ...     type="config_op",
        ...     engine="pandas",
        ...     value="data/input.csv",
        ...     outputs={"data": "raw_data"}
        ... )
        >>> node = IngestNode(step, context, tracker, events)
        >>> data_map = node.run({})
        >>> assert "raw_data" in data_map
    """

    def run(self, data_map: Dict[str, Any]) -> Dict[str, Any]:
        """
        Read data from source.

        Args:
            data_map: Input data_map

        Returns:
            Updated data_map with ingested data

        Raises:
            Exception: On read failure
        """
        import logging

        logger = logging.getLogger(__name__)

        try:
            # Read data from source
            df = self.context.read(self.step.value, **self.step.params)
            logger.info(f"Read data from: {self.step.value}")

            # Log snapshot
            self.tracker.snapshot("after", df, self.context)

            # Write to data_map
            for logical_name, dataset_key in self.step.outputs.items():
                data_map[dataset_key] = df
                logger.info(f"Stored data in data_map['{dataset_key}']")

            # Update state
            self._update_state(NodeState.SUCCESS)

        except Exception as e:
            self._update_state(NodeState.FAILED)
            logger.error(f"IngestNode failed: {e}")
            raise

        return data_map
