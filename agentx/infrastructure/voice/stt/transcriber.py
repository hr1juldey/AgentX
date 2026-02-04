"""STT transcriber - speech-to-text using VoiceClient."""

import base64
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agentx.libs.voice_client import VoiceClient

logger = logging.getLogger(__name__)


async def transcribe_audio(client: "VoiceClient", audio_chunks: list[bytes]) -> str:
    """Transcribe buffered audio chunks using VoiceClient STT.

    Args:
        client: VoiceClient instance
        audio_chunks: List of audio bytes

    Returns:
        Transcribed text
    """
    if not client:
        return ""

    # Combine audio chunks
    combined_audio = b"".join(audio_chunks)

    # Transcribe using STT client
    transcription = await client.stt.transcribe(combined_audio)  # type: ignore[missing-attribute]
    logger.info(f"STT transcription: {transcription[:50]}...")

    return transcription


def decode_base64_audio(data: dict) -> list[bytes]:
    """Decode base64 audio data from WebSocket message.

    Args:
        data: Message data dict with 'audio' key

    Returns:
        List of decoded audio bytes
    """
    audio_data = data.get("audio")
    if not audio_data:
        return []

    audio_bytes = base64.b64decode(audio_data)
    return [audio_bytes]
