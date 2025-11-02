"""
ODIBI CORE - Distributed Execution Module (Phase 7)

Provides multi-node DAG execution with distributed checkpointing.
"""

from .distributed_executor import DistributedExecutor, ExecutionBackend

__all__ = [
    "DistributedExecutor",
    "ExecutionBackend",
]
