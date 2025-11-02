"""
Universal Cloud Adapter Interface (Phase 7)

Provides a unified API for interacting with cloud storage backends:
- Azure Blob/ADLS Gen2 (fully implemented)
- AWS S3 (simulation stub)
- HDFS (simulation stub)
- Kafka (simulation stub)

Usage:
    adapter = CloudAdapter.create("azure", account_name="myaccount")
    data = adapter.read("container/path/data.parquet")
    adapter.write(data, "container/path/output.parquet")
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, Optional, Union
import logging

logger = logging.getLogger(__name__)


class CloudBackend(Enum):
    """Supported cloud backends"""

    AZURE = "azure"
    S3 = "s3"
    HDFS = "hdfs"
    KAFKA = "kafka"
    LOCAL = "local"


class CloudAdapterBase(ABC):
    """
    Base class for all cloud adapters.

    All adapters must implement:
    - connect(): Establish connection to cloud backend
    - read(): Read data from cloud storage
    - write(): Write data to cloud storage
    - exists(): Check if path exists
    - list(): List files/objects in path
    - delete(): Delete file/object
    """

    def __init__(self, simulate: bool = False, **kwargs):
        """
        Initialize cloud adapter.

        Args:
            simulate: If True, run in simulation mode (no real cloud calls)
            **kwargs: Backend-specific configuration
        """
        self.simulate = simulate
        self.config = kwargs
        self.connected = False

    @abstractmethod
    def connect(self) -> bool:
        """
        Establish connection to cloud backend.

        Returns:
            bool: True if connection successful
        """
        pass

    @abstractmethod
    def read(self, path: str, **kwargs) -> Any:
        """
        Read data from cloud storage.

        Args:
            path: Cloud storage path (e.g., "container/path/file.parquet")
            **kwargs: Read options (format, columns, etc.)

        Returns:
            Data object (DataFrame, bytes, etc.)
        """
        pass

    @abstractmethod
    def write(self, data: Any, path: str, **kwargs) -> bool:
        """
        Write data to cloud storage.

        Args:
            data: Data to write (DataFrame, bytes, etc.)
            path: Cloud storage path
            **kwargs: Write options (format, compression, etc.)

        Returns:
            bool: True if write successful
        """
        pass

    @abstractmethod
    def exists(self, path: str) -> bool:
        """Check if path exists in cloud storage"""
        pass

    @abstractmethod
    def list(self, path: str, pattern: Optional[str] = None) -> list:
        """List files/objects in cloud storage path"""
        pass

    @abstractmethod
    def delete(self, path: str) -> bool:
        """Delete file/object from cloud storage"""
        pass

    def disconnect(self):
        """Disconnect from cloud backend"""
        self.connected = False
        logger.info(f"Disconnected from {self.__class__.__name__}")


class CloudAdapter:
    """
    Factory class for creating cloud adapters.

    Usage:
        # Azure adapter
        azure = CloudAdapter.create("azure", account_name="myaccount",
                                    account_key="...", simulate=False)

        # S3 adapter (simulation)
        s3 = CloudAdapter.create("s3", bucket="my-bucket", simulate=True)
    """

    _adapters: Dict[str, type] = {}

    @classmethod
    def register(cls, backend: CloudBackend, adapter_class: type):
        """Register a cloud adapter class"""
        cls._adapters[backend.value] = adapter_class
        logger.debug(f"Registered adapter: {backend.value} -> {adapter_class.__name__}")

    @classmethod
    def create(cls, backend: Union[str, CloudBackend], **kwargs) -> CloudAdapterBase:
        """
        Create a cloud adapter instance.

        Args:
            backend: Backend type ("azure", "s3", "hdfs", "kafka", "local")
            **kwargs: Backend-specific configuration

        Returns:
            CloudAdapterBase: Adapter instance

        Raises:
            ValueError: If backend not supported
        """
        if isinstance(backend, CloudBackend):
            backend = backend.value

        backend = backend.lower()

        if backend not in cls._adapters:
            raise ValueError(
                f"Unsupported backend: {backend}. "
                f"Available: {list(cls._adapters.keys())}"
            )

        adapter_class = cls._adapters[backend]
        logger.info(f"Creating {backend} adapter with config: {kwargs}")

        return adapter_class(**kwargs)

    @classmethod
    def list_backends(cls) -> list:
        """List all registered backends"""
        return list(cls._adapters.keys())


# Import and auto-register adapters
def _register_adapters():
    """Auto-register all available adapters"""
    try:
        from .azure_adapter import AzureAdapter

        CloudAdapter.register(CloudBackend.AZURE, AzureAdapter)
    except ImportError as e:
        logger.warning(f"Could not register Azure adapter: {e}")

    try:
        from .s3_adapter import S3Adapter

        CloudAdapter.register(CloudBackend.S3, S3Adapter)
    except ImportError as e:
        logger.debug(f"S3 adapter not available (simulation stub): {e}")

    try:
        from .hdfs_adapter import HDFSAdapter

        CloudAdapter.register(CloudBackend.HDFS, HDFSAdapter)
    except ImportError as e:
        logger.debug(f"HDFS adapter not available (simulation stub): {e}")

    try:
        from .kafka_adapter import KafkaAdapter

        CloudAdapter.register(CloudBackend.KAFKA, KafkaAdapter)
    except ImportError as e:
        logger.debug(f"Kafka adapter not available (simulation stub): {e}")


_register_adapters()
