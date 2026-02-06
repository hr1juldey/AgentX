"""Real-time WebSocket API endpoints."""

import logging

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from fastapi import WebSocket as WebSocketType

from agentx.core.dependencies import get_voice_gateway

router = APIRouter(prefix="/ws", tags=["websocket"])

logger = logging.getLogger(__name__)


@router.websocket("/")
async def root_websocket(
    websocket: WebSocketType,
    session_id: str = Query(..., description="Session identifier"),
) -> None:
    """Generic WebSocket endpoint - routes to voice gateway.

    This is the primary endpoint for voice conversations with memory.
    Coordinates STT → Agent → TTS flow through VoiceGatewayService.

    Args:
        websocket: WebSocket connection
        session_id: Session identifier for conversation state
    """
    await websocket.accept()
    logger.info(f"WebSocket connected: session_id={session_id}")

    voice_gateway = get_voice_gateway()

    try:
        await voice_gateway.handle_session(websocket, session_id)
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: session_id={session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: session_id={session_id}, error={e}")
        try:
            await websocket.close()
        except Exception:
            pass


@router.websocket("/chat")
async def chat_websocket(websocket: WebSocket) -> None:
    """WebSocket endpoint for real-time chat.

    Args:
        websocket: WebSocket connection

    Raises:
        NotImplementedError: If not yet implemented
    """
    await websocket.accept()
    raise NotImplementedError("WebSocket /ws/chat not yet implemented")
