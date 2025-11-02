"""Node type implementations."""

from odibi_core.nodes.connect_node import ConnectNode
from odibi_core.nodes.ingest_node import IngestNode
from odibi_core.nodes.store_node import StoreNode
from odibi_core.nodes.transform_node import TransformNode
from odibi_core.nodes.publish_node import PublishNode

# Node registry for dynamic instantiation
NODE_REGISTRY = {
    "connect": ConnectNode,
    "ingest": IngestNode,
    "store": StoreNode,
    "transform": TransformNode,
    "publish": PublishNode,
}


def register_node(name: str):
    """
    Decorator to register custom Node types.

    Args:
        name: Node type name

    Example:
        >>> @register_node("custom_transform")
        >>> class CustomTransformNode(NodeBase):
        ...     def run(self, data_map):
        ...         # Custom logic
        ...         return data_map
    """

    def decorator(cls):
        NODE_REGISTRY[name] = cls
        return cls

    return decorator


__all__ = [
    "ConnectNode",
    "IngestNode",
    "StoreNode",
    "TransformNode",
    "PublishNode",
    "NODE_REGISTRY",
    "register_node",
]
