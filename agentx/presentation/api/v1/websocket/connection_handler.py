"""WebSocket connection handling.

Manages WebSocket connection lifecycle and connection events.
"""

import logging

from fastapi import WebSocket

from agentx.ui.protocols.websocket_messages import (
    ErrorMessage,
    StatusMessage,
)

logger = logging.getLogger(__name__)


async def accept_connection(websocket: WebSocket) -> None:
    """Accept WebSocket connection and send status message.

    Args:
        websocket: The WebSocket connection.
    """
    await websocket.accept()
    logger.info("[WebSocketRoutes] Connection accepted")

    # Send connection established message
    status_msg = StatusMessage(
        status="connected", details="WebSocket connection established"
    )
    await websocket.send_json(status_msg.to_dict())
    logger.debug("[WebSocketRoutes] Sent status message: connected")


async def handle_disconnect(websocket: WebSocket) -> None:
    """Handle WebSocket disconnection.

    Args:
        websocket: The WebSocket connection.
    """
    logger.info("[WebSocketRoutes] WebSocket disconnected by client")


async def handle_error(websocket: WebSocket, error: Exception) -> None:
    """Handle WebSocket error.

    Args:
        websocket: The WebSocket connection.
        error: The exception that occurred.
    """
    logger.error(f"[WebSocketRoutes] Exception: {error}", exc_info=True)
    error_msg = ErrorMessage(error_message=str(error))
    await websocket.send_json(error_msg.to_dict())
