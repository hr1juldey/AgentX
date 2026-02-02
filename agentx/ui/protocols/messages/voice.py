"""Voice-related WebSocket messages.

Messages for streaming audio data between client and server.
"""

from dataclasses import dataclass
from typing import override
from uuid import UUID

from agentx.ui.protocols.messages.base import WebSocketMessage
from agentx.ui.protocols.messages.enums import MessageType


@dataclass
class VoiceDataMessage(WebSocketMessage):
    """Voice data message for streaming audio.

    Sent from client for STT processing.
    """

    @override
    def __init__(self, audio_data: bytes, session_id: UUID, sample_rate: int = 16000):
        """Initialize voice data message.

        Args:
            audio_data: Raw audio bytes.
            session_id: Session identifier.
            sample_rate: Audio sample rate.
        """
        # Store audio data as base64 for JSON serialization
        import base64

        super().__init__(
            message_type=MessageType.VOICE_DATA,
            session_id=session_id,
            data={
                "audio_data": base64.b64encode(audio_data).decode(),
                "sample_rate": sample_rate,
            },
        )
