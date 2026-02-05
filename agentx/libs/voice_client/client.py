"""Base WebSocket client with auto-reconnection and protocol handling.

This module provides backward-compatible re-exports from the base/ subdirectory.
The actual implementation has been split into focused modules:
- connection.py: Connection management with auto-reconnection
- messaging.py: Send/receive message handling
- client.py: Main BaseClient class composing the mixins
"""

from voice_client.base.client import BaseClient

__all__ = ["BaseClient"]
