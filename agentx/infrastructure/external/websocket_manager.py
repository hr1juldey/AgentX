"""WebSocket connection manager for Real AgentX v0.1.

Manages WebSocket connections for real-time streaming.
Supports broadcasting messages to sessions.
"""

from typing import Any
from uuid import UUID

from fastapi import WebSocket

from agentx.ui.protocols.websocket_messages import WebSocketMessage


class WebSocketManager:
    """Manages active WebSocket connections.

    Provides methods for:
    - Connection lifecycle (connect/disconnect)
    - Broadcasting messages to sessions
    - Tracking active connections by session_id
    """

    def __init__(self) -> None:
        """Initialize manager with empty connection storage."""
        self._connections: dict[UUID, WebSocket] = {}
        self._active_connections: set[WebSocket] = set()

    async def connect(self, websocket: WebSocket, session_id: UUID) -> None:
        """Connect a WebSocket and register by session_id.

        Args:
            websocket: The WebSocket connection.
            session_id: Session identifier for routing.
        """
        await websocket.accept()
        self._connections[session_id] = websocket
        self._active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        """Disconnect a WebSocket and clean up.

        Args:
            websocket: The WebSocket connection to remove.
        """
        self._active_connections.discard(websocket)
        # Remove from session_id mapping
        for sid, ws in list(self._connections.items()):
            if ws == websocket:
                del self._connections[sid]
                break

    async def send_to_session(
        self, message: WebSocketMessage, session_id: UUID
    ) -> bool:
        """Send message to specific session.

        Args:
            message: WebSocket message to send.
            session_id: Target session identifier.

        Returns:
            True if sent, False if session not connected.
        """
        websocket = self._connections.get(session_id)
        if websocket is None:
            return False
        await websocket.send_json(message.to_dict())
        return True

    async def broadcast(self, message: WebSocketMessage | dict[str, Any]) -> None:
        """Broadcast message to all active connections.

        Args:
            message: Message to broadcast (WebSocketMessage or dict).
        """
        if isinstance(message, WebSocketMessage):
            payload = message.to_dict()
        else:
            payload = message

        # Create copy to avoid RuntimeError if set changes during iteration
        for websocket in list(self._active_connections):
            try:
                await websocket.send_json(payload)
            except Exception:
                # Connection may be closed, remove it
                self.disconnect(websocket)

    async def broadcast_to_sessions(
        self, message: WebSocketMessage, session_ids: list[UUID]
    ) -> None:
        """Broadcast to specific sessions.

        Args:
            message: Message to broadcast.
            session_ids: List of target session IDs.
        """
        for session_id in session_ids:
            await self.send_to_session(message, session_id)

    def get_connection_count(self) -> int:
        """Get total number of active connections.

        Returns:
            Number of active WebSocket connections.
        """
        return len(self._active_connections)

    def is_connected(self, session_id: UUID) -> bool:
        """Check if session has active connection.

        Args:
            session_id: Session identifier.

        Returns:
            True if session has active WebSocket connection.
        """
        return session_id in self._connections


# Global singleton instance
_websocket_manager: WebSocketManager | None = None


def get_websocket_manager() -> WebSocketManager:
    """Get global WebSocket manager instance.

    Returns:
        Shared WebSocketManager instance.

    Raises:
        RuntimeError: If manager not initialized.
    """
    global _websocket_manager
    if _websocket_manager is None:
        _websocket_manager = WebSocketManager()
    return _websocket_manager
