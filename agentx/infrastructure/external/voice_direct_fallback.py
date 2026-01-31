"""Direct WebSocket fallback handling logic.

Implements direct WebSocket connection to kyutai when SDK is unavailable.
"""

import asyncio
import logging
from typing import TYPE_CHECKING, Any

import websockets

from agentx.application.dtos.voice_gateway_dtos import KyutaiMessage, KyutaiMessageType
from agentx.infrastructure.external.voice_protocol import create_config_message

if TYPE_CHECKING:
    from collections.abc import Callable
    from uuid import UUID

    from fastapi import WebSocket
    from agentx.infrastructure.external.voice_sdk_adapter import VoiceSDKAdapter


logger = logging.getLogger(__name__)


class VoiceDirectFallback:
    """Fallback handler for direct WebSocket connections."""

    def __init__(self, adapter: VoiceSDKAdapter) -> None:
        """Initialize the direct fallback handler."""

        self._adapter = adapter

    async def handle_via_direct_ws(
        self,
        frontend_ws: WebSocket,
        session_id: UUID,
        agent_callback: Callable[[str], str] | None = None,
        state_manager: object = None,
        text_handler: object = None,
    ) -> None:
        """Handle voice session using direct WebSocket (fallback)."""
        stt_ws = tts_ws = None

        try:
            stt_ws = await websockets.connect(self._adapter._stt_url)
            tts_ws = await websockets.connect(self._adapter._tts_url)

            config_msg = create_config_message(session_id, streaming_mode="both")
            await stt_ws.send(config_msg.to_json())
            await tts_ws.send(config_msg.to_json())

            self._adapter._sdk_to_agentx_sessions[f"direct_{session_id}"] = session_id

            await asyncio.gather(
                self._input_task(frontend_ws, stt_ws, tts_ws, text_handler),
                self._output_task(
                    frontend_ws,
                    session_id,
                    stt_ws,
                    tts_ws,
                    agent_callback,
                    state_manager,
                    text_handler,
                ),
            )

        except Exception as e:
            logger.error(f"Direct WebSocket handling error: {e}")
            await frontend_ws.send_json(
                KyutaiMessage(
                    type=KyutaiMessageType.ERROR,
                    data={"error": str(e)},
                    sessionId=str(session_id),
                    timestamp=0,
                ).to_dict()
            )

        finally:
            for ws in (stt_ws, tts_ws):
                if ws:
                    await ws.close()
            if text_handler:
                text_handler.cleanup_session(session_id)

    async def _input_task(
        self,
        frontend_ws: WebSocket,
        stt_ws: Any,
        tts_ws: Any,
        text_handler: object = None,
    ) -> None:
        """Handle messages from frontend to kyutai."""
        while True:
            data = await frontend_ws.receive_json()
            message = KyutaiMessage.from_dict(data)

            if message.type == KyutaiMessageType.AUDIO:
                await stt_ws.send(message.to_json())
            elif message.type == KyutaiMessageType.TEXT:
                if message.data.get("action") == "interrupt":
                    logger.debug("Interruption requested via direct WS")
                await tts_ws.send(message.to_json())

    async def _output_task(
        self,
        frontend_ws: WebSocket,
        session_id: UUID,
        stt_ws: Any,
        tts_ws: Any,
        agent_callback: Callable[[str], str] | None = None,
        state_manager: object = None,
        text_handler: object = None,
    ) -> None:
        """Handle messages from kyutai to frontend."""
        stt_task: asyncio.Task | None = None
        tts_task: asyncio.Task | None = None

        try:
            while True:
                # Cancel previous pending tasks if they exist
                for task in [stt_task, tts_task]:
                    if task and not task.done():
                        task.cancel()
                        try:
                            await task
                        except asyncio.CancelledError:
                            pass  # Expected cancellation

                # Create new recv tasks
                stt_task = asyncio.create_task(stt_ws.recv())
                tts_task = asyncio.create_task(tts_ws.recv())

                # Wait for first to complete
                done, pending = await asyncio.wait(
                    [stt_task, tts_task],
                    return_when=asyncio.FIRST_COMPLETED,
                )

                # Cancel pending tasks immediately
                for task in pending:
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass  # Expected

                # Process completed message
                message = KyutaiMessage.from_json(list(done)[0].result())

                if (
                    message.type == KyutaiMessageType.TEXT
                    and message.data.get("source") == "stt"
                ):
                    text = message.data.get("text", "")
                    if text_handler and agent_callback:
                        transcript = text_handler.buffer_stt_chunk(session_id, text)
                        if transcript:
                            response = agent_callback(transcript)
                            if state_manager:
                                state_manager.add_user_message(session_id, transcript)
                                state_manager.add_assistant_message(
                                    session_id, response
                                )

                            async def send_sentence(sentence: str) -> None:
                                await tts_ws.send(
                                    KyutaiMessage(
                                        type=KyutaiMessageType.TEXT,
                                        data={"text": sentence, "action": "speak"},
                                        sessionId=str(session_id),
                                        timestamp=0,
                                    ).to_json()
                                )

                            await text_handler.stream_tts_sentences(
                                session_id, response, send_sentence
                            )
                    await frontend_ws.send_json(message.to_dict())
                else:
                    await frontend_ws.send_json(message.to_dict())

        except Exception as e:
            logger.error(f"Output task error: {e}")
            raise
        finally:
            # Final cleanup
            for task in [stt_task, tts_task]:
                if task and not task.done():
                    task.cancel()
