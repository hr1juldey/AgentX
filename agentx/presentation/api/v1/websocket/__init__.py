"""WebSocket routes for Real AgentX v0.1.

WebSocket endpoint for real-time agent interaction.
Supports query streaming, voice, UI components, and tool updates.
"""

from agentx.presentation.api.v1.websocket.connection_handler import (
    accept_connection,
    handle_disconnect,
    handle_error,
)
from agentx.presentation.api.v1.websocket.message_handler import (
    handle_ping_message,
    handle_query_message,
    handle_unknown_message,
)

__all__ = [
    "accept_connection",
    "handle_disconnect",
    "handle_error",
    "handle_query_message",
    "handle_ping_message",
    "handle_unknown_message",
]
