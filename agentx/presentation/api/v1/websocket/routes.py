"""Real-time WebSocket API endpoints."""

import logging
import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from agentx.core.dependencies import get_voice_gateway


router = APIRouter(prefix="/ws", tags=["websocket"])

logger = logging.getLogger(__name__)


@router.websocket("/test")
async def test_websocket(websocket: WebSocket) -> None:
    """Simple test WebSocket endpoint - no dependencies."""
    await websocket.accept()
    logger.info("Test WebSocket connected successfully!")
    await websocket.send_json({"message": "WebSocket test successful"})
    await websocket.close()


@router.websocket("/root")
async def root_websocket(websocket: WebSocket) -> None:
    """Root WebSocket endpoint - routes to voice gateway.

    This is the primary endpoint for voice conversations with memory.
    Coordinates STT → Agent → TTS flow through VoiceGatewayService.

    Args:
        websocket: WebSocket connection

    Query Params:
        session_id: Optional session identifier (auto-generated if not provided)
    """
    await websocket.accept()

    # Get session_id from query params, generate if not provided
    session_id = websocket.query_params.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())
        logger.info(f"Generated new session_id: {session_id}")
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
