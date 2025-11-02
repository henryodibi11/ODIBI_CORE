"""
ODIBI CORE - Cloud Integration Module (Phase 7)

Provides unified cloud adapters for Azure, AWS S3, HDFS, and Kafka.
Azure adapters are fully implemented; others are simulation stubs for future use.
"""

from .cloud_adapter import CloudAdapter, CloudBackend
from .azure_adapter import AzureAdapter

__all__ = [
    "CloudAdapter",
    "CloudBackend",
    "AzureAdapter",
]
