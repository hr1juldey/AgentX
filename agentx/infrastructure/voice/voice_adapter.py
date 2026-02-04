"""Voice SDK adapter - thin wrapper around agentx/libs/voice_client/ SDK."""

import logging
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

_VOICE_CLIENT_AVAILABLE: bool = False

if TYPE_CHECKING:
    from agentx.libs.voice_client import VoiceClient
else:
    try:
        from agentx.libs.voice_client import VoiceClient

        _VOICE_CLIENT_AVAILABLE = True
    except ImportError:
        VoiceClient = object  # type: ignore[no-redef]
        _VOICE_CLIENT_AVAILABLE = False
        logging.getLogger(__name__).warning(
            "voice_client not available, voice features disabled"
        )

logger = logging.getLogger(__name__)


class VoiceSDKAdapter:
    """Thin wrapper around voice_client SDK for AGENTX integration.

    Uses VoiceClient for STT → Agent → TTS pipeline.
    """

    def __init__(self, stt_url: str, tts_url: str) -> None:
        """Initialize the voice SDK adapter.

        Args:
            stt_url: STT WebSocket URL
            tts_url: TTS WebSocket URL
        """
        self.stt_url = stt_url
        self.tts_url = tts_url
        self._client: VoiceClient | None = None

    async def handle_session(
        self,
        websocket: Any,
        session_id: str,
        agent_callback: Callable[[str], Any],
    ) -> None:
        """Handle voice session using VoiceClient.

        Args:
            websocket: WebSocket connection
            session_id: Session identifier
            agent_callback: Async function that takes transcribed text and returns response
        """
        if not _VOICE_CLIENT_AVAILABLE:
            logger.error("voice_client SDK not available")
            await websocket.close()
            return

        from agentx.libs.voice_client import VoiceClient

        from agentx.infrastructure.voice.stt.transcriber import (
            decode_base64_audio,
            transcribe_audio,
        )
        from agentx.infrastructure.voice.tts.synthesizer import stream_tts_audio

        self._client = VoiceClient(stt_url=self.stt_url, tts_url=self.tts_url)
        audio_buffer: list[bytes] = []

        try:
            async with self._client:
                await self._client.stt.configure()
                await self._client.tts.configure()

                async for msg in self._message_stream(websocket):
                    match msg["type"]:
                        case "Audio":
                            audio_buffer.extend(decode_base64_audio(msg["data"]))

                        case "Eos":
                            if not audio_buffer:
                                return

                            transcription = await transcribe_audio(
                                self._client, audio_buffer
                            )
                            response = await agent_callback(transcription)
                            await stream_tts_audio(self._client, websocket, response)
                            return

                        case "Text":
                            text_input = (
                                msg["data"] if isinstance(msg["data"], str) else ""
                            )
                            response = await agent_callback(text_input)
                            await stream_tts_audio(self._client, websocket, response)
                            return

                        case "Error":
                            logger.error(f"Voice error: {msg['data']}")
                            return

        except Exception as e:
            logger.error(f"Voice session error: {e}")
            await websocket.close()

    async def _message_stream(self, websocket: Any) -> Any:
        """Yield messages from WebSocket stream.

        Args:
            websocket: WebSocket connection

        Yields:
            Message dictionaries with 'type' and 'data' keys
        """
        while True:
            msg = await websocket.receive_json()
            yield msg
