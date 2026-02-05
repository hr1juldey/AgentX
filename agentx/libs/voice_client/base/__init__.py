"""Base WebSocket client components.

Provides the foundation for STT and TTS clients with connection management,
message encoding/decoding, and automatic reconnection.
"""

from agentx.libs.voice_client.base.client import BaseClient

__all__ = ["BaseClient"]
