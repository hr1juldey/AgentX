"""Direct WebSocket fallback handling logic.

Implements direct WebSocket connection to kyutai when SDK is unavailable.

This is a facade for backward compatibility. Actual implementation has been
moved to the voice_direct/ subdirectory.
"""

from agentx.infrastructure.external.voice_direct import VoiceDirectFallback

__all__ = ["VoiceDirectFallback"]
