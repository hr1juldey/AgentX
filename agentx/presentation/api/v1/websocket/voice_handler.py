"""Voice WebSocket handler for voice gateway integration."""

import logging
import uuid

from fastapi import WebSocket

from agentx.core.dependencies import get_voice_gateway

logger = logging.getLogger(__name__)


def generate_session_id(websocket: WebSocket) -> str:
    """Generate or retrieve session_id from WebSocket query params.

    Args:
        websocket: WebSocket connection

    Returns:
        Session ID string
    """
    session_id = websocket.query_params.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())
        logger.info(f"Generated new session_id: {session_id}")
    return session_id


async def handle_test_websocket(websocket: WebSocket) -> None:
    """Handle test WebSocket connection - no dependencies.

    Args:
        websocket: WebSocket connection
    """
    await websocket.accept()
    logger.info("Test WebSocket connected successfully!")
    await websocket.send_json({"message": "WebSocket test successful"})
    await websocket.close()


async def handle_voice_websocket(websocket: WebSocket, session_id: str) -> None:
    """Handle voice WebSocket connection through VoiceGatewayService.

    Coordinates STT → Agent → TTS flow through VoiceGatewayService.

    Args:
        websocket: WebSocket connection
        session_id: Session identifier
    """
    await websocket.accept()
    logger.info(f"WebSocket connected: session_id={session_id}")

    voice_gateway = get_voice_gateway()

    try:
        await voice_gateway.handle_session(websocket, session_id)
    except Exception as e:
        logger.error(f"WebSocket error: session_id={session_id}, error={e}")
        try:
            await websocket.close()
        except Exception:
            pass
