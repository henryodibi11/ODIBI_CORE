"""StoreNode for persisting data to storage."""

from typing import Any, Dict
from odibi_core.core.node import NodeBase, NodeState


class StoreNode(NodeBase):
    """
    Node for storing data to Bronze/Silver/Gold layers.

    Writes DataFrames to Parquet, Delta, CSV, or databases.

    Args:
        step: Step configuration with target path
        context: Engine context
        tracker: Execution tracker
        events: Event emitter

    Example:
        >>> step = Step(
        ...     layer="store",
        ...     name="write_bronze",
        ...     type="config_op",
        ...     engine="pandas",
        ...     value="output/bronze.parquet",
        ...     inputs={"data": "raw_data"}
        ... )
        >>> node = StoreNode(step, context, tracker, events)
        >>> node.run({"raw_data": bronze_df})
    """

    def run(self, data_map: Dict[str, Any]) -> Dict[str, Any]:
        """
        Write data to storage.

        Args:
            data_map: Input data_map containing data to store

        Returns:
            Unchanged data_map

        Raises:
            Exception: On write failure
        """
        import logging

        logger = logging.getLogger(__name__)

        try:
            # Get data from data_map
            if not self.step.inputs:
                raise ValueError(f"StoreNode '{self.step.name}' has no inputs defined")

            # Get first input (typically "data")
            dataset_key = list(self.step.inputs.values())[0]

            if dataset_key not in data_map:
                raise ValueError(f"Input dataset '{dataset_key}' not found in data_map")

            df = data_map[dataset_key]

            # Log snapshot before writing
            self.tracker.snapshot("before", df, self.context)

            # Write to storage
            self.context.write(df, self.step.value, **self.step.params)
            logger.info(f"Wrote data to: {self.step.value}")

            # Update state
            self._update_state(NodeState.SUCCESS)

        except Exception as e:
            self._update_state(NodeState.FAILED)
            logger.error(f"StoreNode failed: {e}")
            raise

        return data_map
