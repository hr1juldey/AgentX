# =============================================================================
# R003 Pomodoro Timer - API Routes
# =============================================================================
# FastAPI routes for Pomodoro timer CRUD operations
# =============================================================================

import asyncio
import json
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

from models.schemas import (
    SessionCreate,
    SessionListResponse,
    SessionResponse,
    SessionStatus,
    SessionUpdate,
)
from services.service import get_pomodoro_service


router = APIRouter(prefix="/sessions", tags=["sessions"])

# Service instance
pomodoro_service = get_pomodoro_service()


# -----------------------------------------------------------------------------
# Session Endpoints
# -----------------------------------------------------------------------------
@router.post("", response_model=SessionResponse, status_code=201)
async def create_session(session: SessionCreate) -> SessionResponse:
    """Create a new Pomodoro session.

    Args:
        session: Session creation data

    Returns:
        Created session with ID and timestamps

    """
    return await pomodoro_service.create(session)


@router.get("", response_model=dict)
async def list_sessions(
    status: Annotated[SessionStatus | None, Query(description="Filter by status")] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> dict[str, object]:
    """List all Pomodoro sessions with optional filtering.

    Args:
        status: Filter by status (running, paused, completed, cancelled)
        limit: Maximum number of sessions to return (default: 50)

    Returns:
        Dictionary with sessions list and total count

    """
    sessions = await pomodoro_service.list_all(status=status)
    return {
        "sessions": sessions[:limit],
        "total": len(sessions),
    }


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: int) -> SessionResponse:
    """Get a Pomodoro session by ID.

    Args:
        session_id: Session ID

    Returns:
        Session data

    Raises:
        HTTPException: If session not found (404)

    """
    result = await pomodoro_service.get(session_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return result


@router.put("/{session_id}", response_model=SessionResponse)
async def update_session(session_id: int, session_update: SessionUpdate) -> SessionResponse:
    """Update an existing Pomodoro session.

    Args:
        session_id: Session ID
        session_update: Session update data (all fields optional)

    Returns:
        Updated session

    Raises:
        HTTPException: If session not found (404)

    """
    result = await pomodoro_service.update(session_id, session_update)
    if result is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return result


@router.delete("/{session_id}", status_code=204)
async def delete_session(session_id: int) -> None:
    """Delete a Pomodoro session by ID.

    Args:
        session_id: Session ID

    Raises:
        HTTPException: If session not found (404)

    """
    success = await pomodoro_service.delete(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")


# -----------------------------------------------------------------------------
# WebSocket Endpoint
# -----------------------------------------------------------------------------
@router.websocket("/ws/timer/{session_id}")
async def websocket_timer(websocket: WebSocket, session_id: int) -> None:
    """WebSocket endpoint for real-time timer updates.

    Args:
        websocket: WebSocket connection
        session_id: Session ID to monitor

    """
    # Verify session exists
    session = await pomodoro_service.get(session_id)
    if session is None:
        await websocket.close(code=1008, reason="Session not found")
        return

    await websocket.accept()

    # Register WebSocket connection
    queue = await pomodoro_service.register_websocket(session_id)
    if queue is None:
        await websocket.close(code=1008, reason="Failed to register connection")
        return

    try:
        # Send initial state
        await websocket.send_json(
            {
                "session_id": session.id,
                "remaining_seconds": session.remaining_seconds,
                "status": session.status,
            }
        )

        # Listen for client messages (optional heartbeat)
        receive_task = asyncio.create_task(_receive_client_messages(websocket))

        # Send updates as they arrive
        while True:
            session_update = await queue.get()

            # None signals connection close
            if session_update is None:
                break

            # Send update to client
            await websocket.send_json(
                {
                    "session_id": session_update.id,
                    "remaining_seconds": session_update.remaining_seconds,
                    "status": session_update.status,
                }
            )

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.close(code=1011, reason=str(e))
        except Exception:
            pass
    finally:
        # Cancel receive task
        if "receive_task" in locals():
            receive_task.cancel()

        # Unregister WebSocket connection
        if queue is not None:
            await pomodoro_service.unregister_websocket(session_id, queue)


async def _receive_client_messages(websocket: WebSocket) -> None:
    """Receive and handle client messages (for heartbeat/keepalive).

    Args:
        websocket: WebSocket connection

    """
    try:
        while True:
            # Wait for client messages (could be heartbeat)
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
