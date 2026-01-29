"""Agent API routes for Real AgentX v0.1.

REST endpoints for agent interaction.
Following FastAPI patterns from CLAUDE.md.
"""

from uuid import UUID

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

from agentx.application.dtos.agent_dtos import (
    ExecuteAgentQueryRequest,
    ExecuteAgentQueryResponse,
    SessionStatusDTO,
)
from agentx.application.use_cases.execute_agent_query import (
    ExecuteAgentQueryUseCase,
)
from agentx.core.dependencies import get_agent_session_repository
from agentx.ui.protocols.websocket_messages import (
    ErrorMessage,
    QueryMessage,
    ResponseMessage,
    StatusMessage,
    WebSocketMessage,
)

router = APIRouter()


# Use case instance
_query_use_case = ExecuteAgentQueryUseCase()


@router.post("/query", response_model=ExecuteAgentQueryResponse)
async def execute_query(request: ExecuteAgentQueryRequest) -> ExecuteAgentQueryResponse:
    """Execute an agent query.

    Args:
        request: The query request.

    Returns:
        ExecuteAgentQueryResponse: Agent response with UI components.

    Raises:
        HTTPException: If query execution fails.
    """
    try:
        response = await _query_use_case.execute(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/session/{session_id}", response_model=SessionStatusDTO)
async def get_session_status(session_id: str) -> SessionStatusDTO:
    """Get session status.

    Args:
        session_id: Session identifier.

    Returns:
        SessionStatusDTO: Session status information.

    Raises:
        HTTPException: If session not found.
    """
    session_repo = get_agent_session_repository()
    session = await session_repo.find_by_id(UUID(session_id))

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    from agentx.application.mappers.agent_session_mapper import AgentSessionMapper

    return AgentSessionMapper.entity_to_dto(session)


@router.get("/sessions")
async def list_sessions(user_id: str | None = None) -> list[SessionStatusDTO]:
    """List sessions.

    Args:
        user_id: Optional user ID to filter by.

    Returns:
        list[SessionStatusDTO]: List of session statuses.
    """
    session_repo = get_agent_session_repository()
    from agentx.application.mappers.agent_session_mapper import AgentSessionMapper

    if user_id:
        sessions = await session_repo.find_by_user(user_id)
    else:
        sessions = await session_repo.find_active_sessions()

    return [AgentSessionMapper.entity_to_dto(s) for s in sessions]


@router.delete("/session/{session_id}")
async def delete_session(session_id: str) -> JSONResponse:
    """Delete a session.

    Args:
        session_id: Session identifier.

    Returns:
        JSONResponse: Deletion confirmation.
    """
    session_repo = get_agent_session_repository()
    await session_repo.delete(UUID(session_id))

    return JSONResponse(content={"message": "Session deleted"})


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
                # Process query
                query_msg = QueryMessage(
                    query=message.data.get("query", ""),
                    session_id=UUID(message.session_id) if message.session_id else None,
                )

                # Execute query
                request = ExecuteAgentQueryRequest(
                    query=query_msg.data["query"],
                    session_id=str(query_msg.session_id)
                    if query_msg.session_id
                    else None,
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
                    from agentx.ui.protocols.websocket_messages import (
                        UIComponentMessage,
                    )

                    ui_msg = UIComponentMessage(
                        component_type=component.component_type,
                        props=component.props,
                        session_id=UUID(response.session_id),
                        merge=component.merge,
                        component_id=UUID(component.component_id)
                        if component.component_id != "placeholder"
                        else None,
                    )
                    await websocket.send_json(ui_msg.to_dict())

            elif message.message_type.value == "ping":
                # Respond with pong

                pong_msg = WebSocketMessage(
                    message_type=WebSocketMessage.message_type.__class__("PONG")
                )
                await websocket.send_json(pong_msg.to_dict())

            else:
                # Unknown message type
                error_msg = ErrorMessage(
                    error_message=f"Unknown message type: {message.message_type.value}"
                )
                await websocket.send_json(error_msg.to_dict())

    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        error_msg = ErrorMessage(error_message=str(e))
        await websocket.send_json(error_msg.to_dict())
