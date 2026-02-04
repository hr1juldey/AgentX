"""Real-time WebSocket API endpoints."""

from fastapi import APIRouter, WebSocket

router = APIRouter(prefix="/ws", tags=["websocket"])


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
