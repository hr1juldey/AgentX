"""Voice direct WebSocket connection handling.

Manages direct WebSocket connections to kyutai when SDK is unavailable.
"""

import asyncio
import logging
from typing import TYPE_CHECKING

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

    def __init__(self, adapter: "VoiceSDKAdapter") -> None:
        """Initialize the direct fallback handler."""
        self._adapter = adapter

    async def handle_via_direct_ws(
        self,
        frontend_ws: WebSocket,
        session_id: UUID,
        agent_callback: "Callable[[str], str] | None" = None,
        state_manager: object = None,
        text_handler: object = None,
    ) -> None:
        """Handle voice session using direct WebSocket (fallback)."""
        from agentx.infrastructure.external.voice_direct.input_task import (
            run_input_task,
        )
        from agentx.infrastructure.external.voice_direct.output_task import (
            run_output_task,
        )

        stt_ws = tts_ws = None

        try:
            stt_ws = await websockets.connect(self._adapter._stt_url)
            tts_ws = await websockets.connect(self._adapter._tts_url)

            config_msg = create_config_message(session_id, streaming_mode="both")
            await stt_ws.send(config_msg.to_json())
            await tts_ws.send(config_msg.to_json())

            self._adapter._sdk_to_agentx_sessions[f"direct_{session_id}"] = session_id

            await asyncio.gather(
                run_input_task(frontend_ws, stt_ws, tts_ws, text_handler),
                run_output_task(
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
                text_handler.cleanup_session(session_id)  # type: ignore[missing-attribute]
