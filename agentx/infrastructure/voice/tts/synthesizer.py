"""TTS synthesizer - text-to-speech using VoiceClient."""

import base64
import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from agentx.libs.voice_client import VoiceClient

logger = logging.getLogger(__name__)


async def stream_tts_audio(client: "VoiceClient", websocket: Any, text: str) -> None:
    """Stream TTS audio to WebSocket.

    Args:
        client: VoiceClient instance
        websocket: WebSocket connection
        text: Text to synthesize
    """
    # Send text first for display
    await websocket.send_json({"type": "Text", "data": text})

    if not client:
        return

    # Stream TTS audio chunks
    async for chunk in client.tts.synthesize(text):  # type: ignore[missing-attribute]
        # Encode audio as base64 and send
        audio_base64 = base64.b64encode(chunk.data).decode()
        await websocket.send_json(
            {
                "type": "Audio",
                "data": {
                    "audio": audio_base64,
                    "format": chunk.format,
                    "sample_rate": chunk.sample_rate,
                },
            }
        )

    # Send EOS to signal audio stream complete
    await websocket.send_json({"type": "Eos"})

    logger.info(f"TTS synthesis complete for: {text[:50]}...")
