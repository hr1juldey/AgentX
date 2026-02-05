"""Conversation event types."""

from dataclasses import dataclass

from agentx.libs.voice_client.stt import TranscriptionResult
from agentx.libs.voice_client.tts import AudioChunk


@dataclass
class ConversationEvent:
    """Event from a streaming conversation.

    Attributes:
        type: Event type ("stt_partial", "stt_final", "tts_audio", "complete")
        data: Event data (varies by type)
        timestamp: Event timestamp
    """

    type: str
    data: TranscriptionResult | AudioChunk | None
    timestamp: float
