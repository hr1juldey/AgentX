"""Kyutai voice-server protocol helpers."""

import base64
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from agentx.application.dtos.voice_gateway_dtos import (
    KyutaiMessage,
    KyutaiMessageType,
)


# Kyutai server endpoints
KYUTAI_STT_URL = "ws://localhost:16000/api/v1/ws/stt?encoding=json"
KYUTAI_TTS_URL = "ws://localhost:16000/api/v1/ws/tts?encoding=json"


def create_config_message(session_id: UUID | str, **config: Any) -> KyutaiMessage:
    """Create a kyutai Config message.

    Args:
        session_id: Session identifier.
        **config: Additional config parameters.

    Returns:
        Kyutai Config message.
    """
    default_config = {
        "streaming_mode": "both",
        "input_format": "int16",
        "output_format": "int16",
    }
    default_config.update(config)

    return KyutaiMessage(
        type=KyutaiMessageType.CONFIG,
        data=default_config,
        sessionId=str(session_id),
        timestamp=datetime.now(timezone.utc).timestamp(),
    )


def create_audio_message(
    audio_data: bytes | str,
    session_id: UUID | str,
) -> KyutaiMessage:
    """Create a kyutai Audio message.

    Args:
        audio_data: Audio data (bytes or base64 string).
        session_id: Session identifier.

    Returns:
        Kyutai Audio message.
    """
    if isinstance(audio_data, bytes):
        audio_base64 = base64.b64encode(audio_data).decode("utf-8")
    else:
        audio_base64 = audio_data

    return KyutaiMessage(
        type=KyutaiMessageType.AUDIO,
        data=audio_base64,
        sessionId=str(session_id),
        timestamp=datetime.now(timezone.utc).timestamp(),
    )


def create_text_message(
    text: str,
    session_id: UUID | str,
) -> KyutaiMessage:
    """Create a kyutai Text message.

    Args:
        text: Text content.
        session_id: Session identifier.

    Returns:
        Kyutai Text message.
    """
    return KyutaiMessage(
        type=KyutaiMessageType.TEXT,
        data=text,
        sessionId=str(session_id),
        timestamp=datetime.now(timezone.utc).timestamp(),
    )


def create_eos_message(session_id: UUID | str) -> KyutaiMessage:
    """Create a kyutai Eos (End of Speech) message.

    Args:
        session_id: Session identifier.

    Returns:
        Kyutai Eos message.
    """
    return KyutaiMessage(
        type=KyutaiMessageType.EOS,
        data="",
        sessionId=str(session_id),
        timestamp=datetime.now(timezone.utc).timestamp(),
    )


def decode_audio_message(message: KyutaiMessage) -> bytes:
    """Decode base64 audio data from Audio message.

    Args:
        message: Kyutai Audio message.

    Returns:
        Decoded audio bytes.
    """
    if message.type != KyutaiMessageType.AUDIO:
        msg = f"Expected Audio message, got {message.type}"
        raise ValueError(msg)

    audio_base64 = message.data if isinstance(message.data, str) else ""
    return base64.b64decode(audio_base64)


def validate_kyutai_message(data: dict[str, Any]) -> KyutaiMessage:
    """Validate and parse kyutai message from dict.

    Args:
        data: Message data as dictionary.

    Returns:
        Validated KyutaiMessage.
    """
    try:
        return KyutaiMessage.from_dict(data)
    except Exception as e:
        msg = f"Invalid kyutai message: {e}"
        raise ValueError(msg) from e
