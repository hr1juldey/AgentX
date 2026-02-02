"""Voice direct input task handling.

Handles messages from frontend to kyutai.
"""

import logging
from typing import TYPE_CHECKING, Any

from agentx.application.dtos.voice_gateway_dtos import KyutaiMessage, KyutaiMessageType

if TYPE_CHECKING:
    from fastapi import WebSocket

logger = logging.getLogger(__name__)


async def run_input_task(
    frontend_ws: "WebSocket",
    stt_ws: Any,
    tts_ws: Any,
    text_handler: object = None,
) -> None:
    """Handle messages from frontend to kyutai.

    Args:
        frontend_ws: Frontend WebSocket connection
        stt_ws: STT WebSocket connection
        tts_ws: TTS WebSocket connection
        text_handler: Text stream handler
    """
    while True:
        data = await frontend_ws.receive_json()
        message = KyutaiMessage.from_dict(data)

        if message.type == KyutaiMessageType.AUDIO:
            await stt_ws.send(message.to_json())
        elif message.type == KyutaiMessageType.TEXT:
            if message.data.get("action") == "interrupt":
                logger.debug("Interruption requested via direct WS")
            await tts_ws.send(message.to_json())
