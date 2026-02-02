"""WebSocket routes for Real AgentX v0.1.

WebSocket endpoint for real-time agent interaction.
Supports query streaming, voice, UI components, and tool updates.

Actual implementation has been moved to the websocket/ subdirectory.
This facade maintains backward compatibility with existing imports.
"""

import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from agentx.ui.protocols.websocket_messages import WebSocketMessage
from agentx.presentation.api.v1.websocket import (
    accept_connection,
    handle_disconnect,
    handle_error,
    handle_ping_message,
    handle_query_message,
    handle_unknown_message,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """WebSocket endpoint for real-time agent interaction.

    Supports:
    - Query streaming
    - Voice input/output
    - UI component streaming
    - Tool execution updates

    Args:
        websocket: The WebSocket connection.
    """
    await accept_connection(websocket)

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            message = WebSocketMessage.from_dict(data)

            logger.info(
                f"[WebSocketRoutes] Received message type: {message.message_type.value}"
            )

            # Handle message types
            if message.message_type.value == "query":
                await handle_query_message(websocket, message)
            elif message.message_type.value == "ping":
                await handle_ping_message(websocket)
            else:
                await handle_unknown_message(websocket, message)

    except WebSocketDisconnect:
        await handle_disconnect(websocket)
    except Exception as e:
        await handle_error(websocket, e)


# Legacy functions for backward compatibility
async def _handle_query_message_legacy(websocket, message):
    """Legacy function for backward compatibility."""
    return await handle_query_message(websocket, message)


async def _handle_ping_message_legacy(websocket):
    """Legacy function for backward compatibility."""
    return await handle_ping_message(websocket)


async def _handle_unknown_message_legacy(websocket, message):
    """Legacy function for backward compatibility."""
    return await handle_unknown_message(websocket, message)
