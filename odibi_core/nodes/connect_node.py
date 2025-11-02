"""ConnectNode for establishing database/storage connections."""

from typing import Any, Dict
from odibi_core.core.node import NodeBase, NodeState


class ConnectNode(NodeBase):
    """
    Node for establishing connections.

    Initializes database connections, API clients, or storage account access.
    Does not produce data outputs - only side effects (connection state).

    Args:
        step: Step configuration with connection parameters
        context: Engine context
        tracker: Execution tracker
        events: Event emitter

    Example:
        >>> step = Step(
        ...     layer="connect",
        ...     name="connect_postgres",
        ...     type="config_op",
        ...     engine="pandas",
        ...     value="postgresql://host:port/db",
        ...     params={"user": "admin", "password_key": "db_pass"}
        ... )
        >>> node = ConnectNode(step, context, tracker, events)
        >>> data_map = node.run({})
    """

    def run(self, data_map: Dict[str, Any]) -> Dict[str, Any]:
        """
        Establish connection.

        Args:
            data_map: Input data_map (not used for connections)

        Returns:
            Unchanged data_map (connections are side effects)

        Raises:
            Exception: On connection failure
        """
        import logging

        logger = logging.getLogger(__name__)

        try:
            # Extract connection parameters
            conn_params = self.step.params.copy()

            # Resolve secrets if needed
            for key, value in list(conn_params.items()):
                if key.endswith("_secret") or key.endswith("_key"):
                    # Value is the secret key name
                    conn_params[key.replace("_secret", "").replace("_key", "")] = (
                        self.context.get_secret(value)
                    )
                    del conn_params[key]

            # Call context.connect()
            self.context.connect(**conn_params)
            logger.info(f"Connection established: {self.step.name}")

            # Update state
            self._update_state(NodeState.SUCCESS)

        except Exception as e:
            self._update_state(NodeState.FAILED)
            logger.error(f"ConnectNode failed: {e}")
            raise

        return data_map
