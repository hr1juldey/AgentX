"""Voice API endpoints."""

import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

from agentx.core.dependencies import get_voice_gateway

router = APIRouter(prefix="/voice", tags=["voice"])

logger = logging.getLogger(__name__)


@router.get("/kyutai/status")
async def kyutai_status() -> dict:
    """Check Kyutai voice server status.

    Returns:
        Status information

    Raises:
        NotImplementedError: If not yet implemented
    """
    # TODO: Implement actual health check to kyutai server
    return {
        "status": "ok",
        "kyutai_stt_url": "ws://localhost:16000/stt",
        "kyutai_tts_url": "ws://localhost:16000/tts",
    }


@router.websocket("/ws")
async def voice_websocket(
    websocket: WebSocket,
    session_id: str = Query(..., description="Session identifier"),
) -> None:
    """WebSocket endpoint for voice interactions.

    Accepts audio/text input, returns TTS audio/text output.

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
