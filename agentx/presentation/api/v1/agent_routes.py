"""Agent API routes for Real AgentX v0.1.

REST endpoints for agent interaction.
Following FastAPI patterns from CLAUDE.md.
"""

from uuid import UUID

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from agentx.application.dtos.agent_dtos import (
    ExecuteAgentQueryRequest,
    ExecuteAgentQueryResponse,
    SessionStatusDTO,
)
from agentx.application.use_cases.execute_agent_query import (
    ExecuteAgentQueryUseCase,
)
from agentx.application.mappers.agent_session_mapper import AgentSessionMapper
from agentx.core.dependencies import get_agent_session_repository

router = APIRouter()
_query_use_case = ExecuteAgentQueryUseCase()


@router.post("/query", response_model=ExecuteAgentQueryResponse)
async def execute_query(
    request: ExecuteAgentQueryRequest,
) -> ExecuteAgentQueryResponse:
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

    return AgentSessionMapper.entity_to_dto(session)


@router.get("/sessions")
async def list_sessions(
    user_id: str | None = None,
) -> list[SessionStatusDTO]:
    """List sessions.

    Args:
        user_id: Optional user ID to filter by.

    Returns:
        list[SessionStatusDTO]: List of session statuses.
    """
    session_repo = get_agent_session_repository()

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
