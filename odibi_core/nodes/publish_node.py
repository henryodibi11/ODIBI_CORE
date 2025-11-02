"""PublishNode for exporting data to external systems."""

from typing import Any, Dict
from odibi_core.core.node import NodeBase, NodeState


class PublishNode(NodeBase):
    """
    Node for publishing data to external systems.

    Similar to StoreNode but targets downstream systems (APIs, databases, Delta Lake).

    Args:
        step: Step configuration with target endpoint
        context: Engine context
        tracker: Execution tracker
        events: Event emitter

    Example:
        >>> step = Step(
        ...     layer="publish",
        ...     name="publish_to_delta",
        ...     type="config_op",
        ...     engine="spark",
        ...     value="delta_table_name",
        ...     inputs={"data": "gold_data"},
        ...     params={"mode": "append"}
        ... )
        >>> node = PublishNode(step, context, tracker, events)
        >>> node.run({"gold_data": gold_df})
    """

    def run(self, data_map: Dict[str, Any]) -> Dict[str, Any]:
        """
        Publish data to external system.

        Args:
            data_map: Input data_map containing data to publish

        Returns:
            Unchanged data_map

        Raises:
            Exception: On publish failure
        """
        import logging

        logger = logging.getLogger(__name__)

        try:
            # Get data from data_map
            if not self.step.inputs:
                raise ValueError(
                    f"PublishNode '{self.step.name}' has no inputs defined"
                )

            # Get first input (typically "data")
            dataset_key = list(self.step.inputs.values())[0]

            if dataset_key not in data_map:
                raise ValueError(f"Input dataset '{dataset_key}' not found in data_map")

            df = data_map[dataset_key]

            # Log snapshot before publishing
            self.tracker.snapshot("before", df, self.context)

            # Write to target (Gold layer output)
            self.context.write(df, self.step.value, **self.step.params)
            logger.info(f"Published data to: {self.step.value}")

            # Update state
            self._update_state(NodeState.SUCCESS)

        except Exception as e:
            self._update_state(NodeState.FAILED)
            logger.error(f"PublishNode failed: {e}")
            raise

        return data_map
