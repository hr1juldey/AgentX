"""SDK-specific voice handling logic.

Implements the voice_client SDK integration for conversations.
"""

import base64
import logging
from typing import TYPE_CHECKING

from agentx.application.dtos.voice_gateway_dtos import KyutaiMessage, KyutaiMessageType

if TYPE_CHECKING:
    from collections.abc import Callable
    from uuid import UUID

    from fastapi import WebSocket
    from voice_client import ConversationEvent
    from voice_client.voice import VoiceClient
    from agentx.infrastructure.external.voice_sdk_adapter import VoiceSDKAdapter


logger = logging.getLogger(__name__)


class VoiceSDKHandler:
    """Handler for voice_client SDK-based voice sessions."""

    def __init__(self, adapter: VoiceSDKAdapter) -> None:
        """Initialize the SDK handler.

        Args:
            adapter: The parent VoiceSDKAdapter instance
        """

        self._adapter = adapter

    async def handle_via_sdk(
        self,
        voice_client: VoiceClient,
        frontend_ws: WebSocket,
        session_id: UUID,
        agent_callback: Callable[[str], str] | None = None,
    ) -> None:
        """Handle voice session using voice_client SDK."""

        self._adapter._map_sdk_session_to_agentx(
            voice_client.stt.session_id, session_id
        )
        logger.info(
            f"SDK session {voice_client.stt.session_id} mapped to AgentX {session_id}"
        )

        audio_buffer: list[bytes] = []

        try:
            while True:
                data = await frontend_ws.receive_json()
                message = KyutaiMessage.from_dict(data)

                if message.type == KyutaiMessageType.AUDIO:
                    audio_chunk = message.data.get("audio", b"")
                    if isinstance(audio_chunk, str):
                        audio_chunk = base64.b64decode(audio_chunk)
                    audio_buffer.append(audio_chunk)
                    logger.debug(f"Buffered audio chunk: {len(audio_chunk)} bytes")
                elif message.type == KyutaiMessageType.TEXT:
                    action = message.data.get("action", "")
                    if action == "interrupt":
                        logger.info("Interruption requested via SDK")
                        break
                    elif action == "eos":
                        logger.debug(
                            f"EOS received, processing {len(audio_buffer)} chunks"
                        )
                        break

            if audio_buffer:
                combined_audio = b"".join(audio_buffer)
                logger.info(f"Processing {len(combined_audio)} bytes via SDK")

                async for event in voice_client.converse_stream(
                    combined_audio, agent_callback=agent_callback
                ):
                    await self._handle_conversation_event(
                        event, frontend_ws, session_id
                    )

        except Exception as e:
            logger.error(f"SDK handling error: {e}")
            await frontend_ws.send_json(
                KyutaiMessage(
                    type=KyutaiMessageType.ERROR,
                    data={"error": str(e)},
                    sessionId=str(session_id),
                    timestamp=0,
                ).to_dict()
            )

    async def _handle_conversation_event(
        self, event: ConversationEvent, frontend_ws: WebSocket, session_id: UUID
    ) -> None:
        """Handle a conversation event from SDK."""
        import time

        if event.type == "stt_partial":
            await frontend_ws.send_json(
                KyutaiMessage(
                    type=KyutaiMessageType.TEXT,
                    data={"text": event.data.text, "source": "stt", "is_final": False},
                    sessionId=str(session_id),
                    timestamp=event.timestamp,
                ).to_dict()
            )
        elif event.type == "stt_final":
            await frontend_ws.send_json(
                KyutaiMessage(
                    type=KyutaiMessageType.TEXT,
                    data={"text": event.data.text, "source": "stt", "is_final": True},
                    sessionId=str(session_id),
                    timestamp=event.timestamp,
                ).to_dict()
            )
        elif event.type == "tts_audio":
            audio_b64 = base64.b64encode(event.data.audio).decode("utf-8")
            await frontend_ws.send_json(
                KyutaiMessage(
                    type=KyutaiMessageType.AUDIO,
                    data={
                        "audio": audio_b64,
                        "format": "wav",
                        "sample_rate": event.data.sample_rate,
                    },
                    sessionId=str(session_id),
                    timestamp=time.time(),
                ).to_dict()
            )
        elif event.type == "complete":
            logger.debug("Conversation complete via SDK")
