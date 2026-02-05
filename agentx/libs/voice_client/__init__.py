"""
Voice Client SDK for the voice server.

Provides Python clients for Speech-to-Text (STT), Text-to-Speech (TTS),
and combined voice conversations via WebSocket.
"""

__version__ = "0.1.0"

# Audio
from agentx.libs.voice_client.audio import AudioHandler

# Audio I/O
from agentx.libs.voice_client.audio_io import AudioPlayer, AudioRecorder

# Base client
from agentx.libs.voice_client.client import BaseClient

# Voice
from agentx.libs.voice_client.conversation.events import ConversationEvent

# Exceptions
from agentx.libs.voice_client.exceptions import (
    AudioFormatError,
    ConfigurationError,
    PlaybackError,
    ProtocolError,
    RecordingError,
    ServerError,
    VoiceClientError,
)
from agentx.libs.voice_client.exceptions import (
    ConnectionError as VoiceClientConnectionError,
)
from agentx.libs.voice_client.exceptions import (
    TimeoutError as VoiceClientTimeoutError,
)

# Protocol
from agentx.libs.voice_client.protocol import (
    AudioMessage,
    ConfigMessage,
    EOSMessage,
    ErrorMessage,
    JSONEncoder,
    Message,
    MessagePackEncoder,
    MessageType,
    TextMessage,
    create_audio_message,
    create_config_message,
    create_eos_message,
    create_text_message,
    get_encoder,
)

# STT
from agentx.libs.voice_client.stt import STTClient, TranscriptionResult

# TTS
from agentx.libs.voice_client.tts import AudioChunk, TTSClient
from agentx.libs.voice_client.voice import VoiceClient


def _default_agent_callback(text: str) -> str:
    """Default agent callback that echoes the user's input.

    Args:
        text: Transcribed text

    Returns:
        Response text
    """
    return f"You said: {text}"


__all__ = [
    "AudioChunk",
    "AudioFormatError",
    # Audio
    "AudioHandler",
    "AudioMessage",
    "AudioPlayer",
    # Audio I/O
    "AudioRecorder",
    # Clients
    "BaseClient",
    "ConfigMessage",
    "ConfigurationError",
    "ConversationEvent",
    "EOSMessage",
    "ErrorMessage",
    "JSONEncoder",
    "Message",
    "MessagePackEncoder",
    # Protocol
    "MessageType",
    "PlaybackError",
    "ProtocolError",
    "RecordingError",
    "STTClient",
    "ServerError",
    "TTSClient",
    "TextMessage",
    # Dataclasses
    "TranscriptionResult",
    "VoiceClient",
    "VoiceClientConnectionError",
    # Exceptions
    "VoiceClientError",
    "VoiceClientTimeoutError",
    "create_audio_message",
    "create_config_message",
    "create_eos_message",
    "create_text_message",
    "get_encoder",
]
