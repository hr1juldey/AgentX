"""Voice direct fallback WebSocket handling.

Provides direct WebSocket connection handling when SDK is unavailable.
"""

from agentx.infrastructure.external.voice_direct.connection import (
    VoiceDirectFallback,
)

__all__ = ["VoiceDirectFallback"]
