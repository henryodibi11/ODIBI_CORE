"""TransformNode for data transformations."""

from typing import Any, Dict
from odibi_core.core.node import NodeBase, NodeState


class TransformNode(NodeBase):
    """
    Node for data transformations.

    Supports two modes:
    1. SQL Transform: Register inputs as temp tables, execute SQL, capture result
    2. Function Transform: Import Python function from registry, call with inputs

    Args:
        step: Step configuration with SQL or function reference
        context: Engine context
        tracker: Execution tracker
        events: Event emitter

    Example (SQL):
        >>> step = Step(
        ...     layer="transform",
        ...     name="filter_high_efficiency",
        ...     type="sql",
        ...     engine="pandas",
        ...     value="SELECT * FROM bronze WHERE efficiency > 80",
        ...     inputs={"bronze": "raw_data"},
        ...     outputs={"data": "filtered_data"}
        ... )
        >>> node = TransformNode(step, context, tracker, events)
        >>> data_map = node.run({"raw_data": bronze_df})
        >>> assert "filtered_data" in data_map

    Example (Function):
        >>> step = Step(
        ...     layer="transform",
        ...     name="calc_enthalpy",
        ...     type="function",
        ...     engine="pandas",
        ...     value="thermo.steam.calc_enthalpy",
        ...     inputs={"data": "raw_data"},
        ...     outputs={"data": "enriched_data"}
        ... )
        >>> node = TransformNode(step, context, tracker, events)
        >>> data_map = node.run({"raw_data": input_df})
    """

    def run(self, data_map: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute transformation.

        Args:
            data_map: Input data_map with source DataFrames

        Returns:
            Updated data_map with transformed data

        Raises:
            Exception: On transformation failure
        """
        # TODO Phase 4: Implement transformation logic
        if self.step.type == "sql":
            return self._run_sql_transform(data_map)
        elif self.step.type == "function":
            return self._run_function_transform(data_map)
        else:
            raise ValueError(f"Unknown transform type: {self.step.type}")

    def _run_sql_transform(self, data_map: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute SQL transformation.

        Args:
            data_map: Input data_map

        Returns:
            Updated data_map
        """
        import logging

        logger = logging.getLogger(__name__)

        try:
            # Register all inputs as temp tables
            for logical_name, dataset_key in self.step.inputs.items():
                if dataset_key not in data_map:
                    raise ValueError(
                        f"Input dataset '{dataset_key}' not found in data_map"
                    )

                df = data_map[dataset_key]
                self.context.register_temp(logical_name, df)
                logger.info(
                    f"Registered temp table '{logical_name}' from '{dataset_key}'"
                )

                # Log before snapshot
                self.tracker.snapshot("before", df, self.context)

            # Execute SQL
            result = self.context.execute_sql(self.step.value)
            logger.info(f"Executed SQL transform: {self.step.name}")

            # Log after snapshot
            self.tracker.snapshot("after", result, self.context)

            # Write to data_map
            for logical_name, dataset_key in self.step.outputs.items():
                data_map[dataset_key] = result
                logger.info(f"Stored result in data_map['{dataset_key}']")

            # Update state
            self._update_state(NodeState.SUCCESS)

        except Exception as e:
            self._update_state(NodeState.FAILED)
            logger.error(f"SQL transform failed: {e}")
            raise

        return data_map

    def _run_function_transform(self, data_map: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute function transformation.

        Args:
            data_map: Input data_map

        Returns:
            Updated data_map
        """
        # TODO Phase 4: Implement function transform
        # - Import function from registry: func = resolve_function(step.value)
        # - Prepare inputs: input_df = data_map[step.inputs['data']]
        # - Call function: result = func(input_df, **step.params)
        # - Log snapshots
        # - Write to data_map: data_map[step.outputs['data']] = result
        self._update_state(NodeState.SUCCESS)
        return data_map
