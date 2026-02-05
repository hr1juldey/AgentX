"""
Combined STT + TTS client for full conversations.

This module provides backward-compatible re-exports from the conversation/ subdirectory.
The actual implementation has been split into focused modules:
- voice.py: Main VoiceClient class
- basic.py: Basic conversation mixin
- streaming.py: Streaming conversation mixin
- events.py: Conversation event types
"""

from agentx.libs.voice_client.conversation.voice import VoiceClient

__all__ = ["VoiceClient"]
