"""WebSocket message handling.

Handles different types of WebSocket messages from clients.
"""

import logging
from uuid import UUID

from fastapi import WebSocket

from agentx.application.dtos.agent_dtos import ExecuteAgentQueryRequest
from agentx.application.use_cases.execute_agent_query import (
    ExecuteAgentQueryUseCase,
)
from agentx.ui.protocols.websocket_messages import (
    ErrorMessage,
    QueryMessage,
    ResponseMessage,
    UIComponentMessage,
    WebSocketMessage,
)

logger = logging.getLogger(__name__)
_query_use_case = ExecuteAgentQueryUseCase()


async def handle_query_message(websocket: WebSocket, message: WebSocketMessage) -> None:
    """Handle query message from client.

    Args:
        websocket: The WebSocket connection.
        message: Query message from client.
    """
    query_text = message.data.get("query", "")
    logger.info(f"[WebSocketRoutes] Processing query: {query_text[:100]}...")

    # Process query
    query_msg = QueryMessage(
        query=query_text,
        session_id=message.session_id,
    )

    # Execute query
    request = ExecuteAgentQueryRequest(
        query=query_msg.data["query"],
        session_id=str(query_msg.session_id) if query_msg.session_id else None,
    )

    logger.info(
        f"[WebSocketRoutes] Executing agent query for session: {request.session_id}"
    )
    response = await _query_use_case.execute(request)
    logger.info(
        f"[WebSocketRoutes] Agent execution completed for session: {response.session_id}"
    )

    # Send response
    response_msg = ResponseMessage(
        content=response.response,
        session_id=UUID(response.session_id),
        is_complete=True,
    )
    await websocket.send_json(response_msg.to_dict())
    logger.debug(
        f"[WebSocketRoutes] Sent response message: {len(response.response)} chars"
    )

    # Send UI components
    for component in response.ui_components:
        component_uuid = (
            UUID(component.component_id)
            if component.component_id != "placeholder"
            else None
        )
        ui_msg = UIComponentMessage(
            component_type=component.component_type,
            props=component.props,
            session_id=UUID(response.session_id),
            merge=component.merge,
            component_id=component_uuid,
        )
        await websocket.send_json(ui_msg.to_dict())
        logger.debug(f"[WebSocketRoutes] Sent UI component: {component.component_type}")


async def handle_ping_message(websocket: WebSocket) -> None:
    """Handle ping message from client.

    Args:
        websocket: The WebSocket connection.
    """
    pong_msg = WebSocketMessage(
        message_type=WebSocketMessage.message_type.__class__("PONG"),
        session_id=UUID(int=0),  # Nil UUID
    )
    await websocket.send_json(pong_msg.to_dict())


async def handle_unknown_message(
    websocket: WebSocket, message: WebSocketMessage
) -> None:
    """Handle unknown message type from client.

    Args:
        websocket: The WebSocket connection.
        message: Unknown message from client.
    """
    error_msg = ErrorMessage(
        error_message=f"Unknown message type: {message.message_type.value}"
    )
    await websocket.send_json(error_msg.to_dict())
