"""WebSocket routes for Real AgentX v0.1.

WebSocket endpoint for real-time agent interaction.
Supports query streaming, voice, UI components, and tool updates.
"""

from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from agentx.application.dtos.agent_dtos import ExecuteAgentQueryRequest
from agentx.application.use_cases.execute_agent_query import (
    ExecuteAgentQueryUseCase,
)
from agentx.ui.protocols.websocket_messages import (
    ErrorMessage,
    QueryMessage,
    ResponseMessage,
    StatusMessage,
    UIComponentMessage,
    WebSocketMessage,
)

router = APIRouter()
_query_use_case = ExecuteAgentQueryUseCase()


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
    await websocket.accept()

    try:
        # Send connection established message
        status_msg = StatusMessage(
            status="connected", details="WebSocket connection established"
        )
        await websocket.send_json(status_msg.to_dict())

        while True:
            # Receive message from client
            data = await websocket.receive_json()
            message = WebSocketMessage.from_dict(data)

            # Handle message types
            if message.message_type.value == "query":
                await _handle_query_message(websocket, message)
            elif message.message_type.value == "ping":
                await _handle_ping_message(websocket)
            else:
                await _handle_unknown_message(websocket, message)

    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        error_msg = ErrorMessage(error_message=str(e))
        await websocket.send_json(error_msg.to_dict())


async def _handle_query_message(
    websocket: WebSocket, message: WebSocketMessage
) -> None:
    """Handle query message from client.

    Args:
        websocket: The WebSocket connection.
        message: Query message from client.
    """
    # Process query
    query_msg = QueryMessage(
        query=message.data.get("query", ""),
        session_id=message.session_id,
    )

    # Execute query
    request = ExecuteAgentQueryRequest(
        query=query_msg.data["query"],
        session_id=str(query_msg.session_id) if query_msg.session_id else None,
    )

    response = await _query_use_case.execute(request)

    # Send response
    response_msg = ResponseMessage(
        content=response.response,
        session_id=UUID(response.session_id),
        is_complete=True,
    )
    await websocket.send_json(response_msg.to_dict())

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


async def _handle_ping_message(websocket: WebSocket) -> None:
    """Handle ping message from client.

    Args:
        websocket: The WebSocket connection.
    """
    from uuid import UUID

    pong_msg = WebSocketMessage(
        message_type=WebSocketMessage.message_type.__class__("PONG"),
        session_id=UUID(int=0),  # Nil UUID
    )
    await websocket.send_json(pong_msg.to_dict())


async def _handle_unknown_message(
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
