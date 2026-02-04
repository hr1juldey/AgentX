"""Voice API endpoints."""

from fastapi import APIRouter, WebSocket

router = APIRouter(prefix="/voice", tags=["voice"])


@router.get("/kyutai/status")
async def kyutai_status() -> dict:
    """Check Kyutai voice server status.

    Returns:
        Status information

    Raises:
        NotImplementedError: If not yet implemented
    """
    raise NotImplementedError("GET /voice/kyutai/status not yet implemented")


@router.websocket("/ws")
async def voice_websocket(websocket: WebSocket) -> None:
    """WebSocket endpoint for voice interactions.

    Args:
        websocket: WebSocket connection

    Raises:
        NotImplementedError: If not yet implemented
    """
    await websocket.accept()
    raise NotImplementedError("WebSocket /voice/ws not yet implemented")
