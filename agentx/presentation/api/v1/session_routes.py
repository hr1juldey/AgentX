"""Session API routes for Real AgentX v0.1.

REST endpoints for session management.
"""

from uuid import UUID

from fastapi import APIRouter, HTTPException

from agentx.application.dtos.agent_dtos import SessionStatusDTO
from agentx.application.dtos.session_dtos import (
    CloseSessionCommand,
    CreateSessionCommand,
    PauseSessionCommand,
    ResumeSessionCommand,
)
from agentx.application.use_cases.create_session import CreateSessionUseCase
from agentx.application.use_cases.manage_session import ManageSessionUseCase
from agentx.application.mappers.agent_session_mapper import AgentSessionMapper
from agentx.core.dependencies import get_agent_session_repository

router = APIRouter()
_create_use_case = CreateSessionUseCase()
_manage_use_case = ManageSessionUseCase()


@router.post("/", response_model=SessionStatusDTO)
async def create_session(command: CreateSessionCommand) -> SessionStatusDTO:
    """Create a new session."""
    try:
        return await _create_use_case.execute(command)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/{session_id}", response_model=SessionStatusDTO)
async def get_session(session_id: UUID) -> SessionStatusDTO:
    """Get session by ID."""
    session_repo = get_agent_session_repository()
    session = await session_repo.find_by_id(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return AgentSessionMapper.entity_to_dto(session)


async def _handle_session_operation(
    operation_name: str, command_factory, **kwargs
) -> SessionStatusDTO:
    """Helper to handle session operations with consistent error handling."""
    try:
        command = command_factory(**kwargs)
        if operation_name == "pause":
            return await _manage_use_case.pause(command)
        elif operation_name == "resume":
            return await _manage_use_case.resume(command)
        elif operation_name == "close":
            return await _manage_use_case.close(command)
        else:
            msg = f"Unknown operation: {operation_name}"
            raise ValueError(msg)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/{session_id}/pause", response_model=SessionStatusDTO)
async def pause_session(
    session_id: UUID, reason: str | None = None
) -> SessionStatusDTO:
    """Pause an active session."""
    return await _handle_session_operation(
        "pause", PauseSessionCommand, session_id=session_id, reason=reason
    )


@router.post("/{session_id}/resume", response_model=SessionStatusDTO)
async def resume_session(
    session_id: UUID, context: list[str] | None = None
) -> SessionStatusDTO:
    """Resume a paused session."""
    return await _handle_session_operation(
        "resume", ResumeSessionCommand, session_id=session_id, context=context or []
    )


@router.post("/{session_id}/close", response_model=SessionStatusDTO)
async def close_session(
    session_id: UUID, reason: str | None = None
) -> SessionStatusDTO:
    """Close a session."""
    return await _handle_session_operation(
        "close", CloseSessionCommand, session_id=session_id, reason=reason
    )


@router.delete("/{session_id}")
async def delete_session(session_id: UUID) -> dict[str, str]:
    """Delete a session."""
    try:
        session_repo = get_agent_session_repository()
        await session_repo.delete(session_id)
        return {"message": "Session deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
