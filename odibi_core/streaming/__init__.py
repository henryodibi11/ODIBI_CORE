"""
Streaming and incremental processing support for ODIBI CORE.

Modules:
    stream_manager: Manages streaming data sources and sinks
"""

from odibi_core.streaming.stream_manager import (
    StreamManager,
    StreamSource,
    StreamConfig,
    StreamMode,
)

__all__ = ["StreamManager", "StreamSource", "StreamConfig", "StreamMode"]
