"""API routes for session management."""

import logging
from typing import Optional

from fastapi import APIRouter, Header, HTTPException, status

from models.schemas import (
    SessionCreate,
    SessionListResponse,
    SessionResponse,
    SessionUpdate,
)
from services.service import session_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sessions", tags=["sessions"])


# Mock user ID extraction (in production, this would come from JWT auth)
async def get_current_user_id(
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
) -> str:
    """
    Extract user ID from request header.
    In production, this would decode a JWT token.
    """
    if x_user_id:
        return x_user_id
    # Default mock user ID for testing
    return "user_1234567890"


@router.post(
    "",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new session",
    description="Create a new login session for a device.",
)
async def create_session(
    session_data: SessionCreate,
    user_id: str = Header(
        ..., alias="X-User-Id", description="User ID from authentication"
    ),
) -> SessionResponse:
    """
    Create a new session (login from device).

    Args:
        session_data: Session creation data with device information
        user_id: User ID from authentication header

    Returns:
        Created session with session token
    """
    try:
        logger.info(
            f"Creating session for user {user_id} on {session_data.device_type}"
        )
        session = await session_service.create_session(session_data, user_id)
        return session
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create session: {str(e)}",
        )


@router.get(
    "",
    response_model=SessionListResponse,
    summary="List all sessions",
    description="Get all active sessions for the authenticated user.",
)
async def list_sessions(
    user_id: str = Header(
        ..., alias="X-User-Id", description="User ID from authentication"
    ),
) -> SessionListResponse:
    """
    List all active sessions for the user.

    Args:
        user_id: User ID from authentication header

    Returns:
        List of active sessions with counts
    """
    try:
        sessions = await session_service.list_sessions(user_id)
        active_count = len([s for s in sessions if s.is_active])
        return SessionListResponse(
            sessions=sessions,
            total=len(sessions),
            active=active_count,
        )
    except Exception as e:
        logger.error(f"Error listing sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list sessions: {str(e)}",
        )


@router.get(
    "/{session_id}",
    response_model=SessionResponse,
    summary="Get session details",
    description="Get details of a specific session.",
)
async def get_session(
    session_id: str,
    user_id: str = Header(
        ..., alias="X-User-Id", description="User ID from authentication"
    ),
) -> SessionResponse:
    """
    Get a specific session by ID.

    Args:
        session_id: Session ID
        user_id: User ID from authentication header

    Returns:
        Session details

    Raises:
        HTTPException: If session not found
    """
    session = await session_service.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )
    # Verify session belongs to user
    if session.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Session does not belong to authenticated user",
        )
    return session


@router.put(
    "/{session_id}",
    response_model=SessionResponse,
    summary="Update a session",
    description="Update session status and refresh last_active timestamp.",
)
async def update_session(
    session_id: str,
    session_update: SessionUpdate,
    user_id: str = Header(
        ..., alias="X-User-Id", description="User ID from authentication"
    ),
) -> SessionResponse:
    """
    Update a session (refresh last_active or deactivate).

    Args:
        session_id: Session ID
        session_update: Update data with is_active status
        user_id: User ID from authentication header

    Returns:
        Updated session

    Raises:
        HTTPException: If session not found or doesn't belong to user
    """
    # First verify session exists and belongs to user
    session = await session_service.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )
    if session.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Session does not belong to authenticated user",
        )

    # Update session
    updated_session = await session_service.update_session(
        session_id, session_update.is_active
    )
    if not updated_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found after update",
        )
    return updated_session


@router.delete(
    "/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a session",
    description="Logout and invalidate a specific session.",
)
async def delete_session(
    session_id: str,
    user_id: str = Header(
        ..., alias="X-User-Id", description="User ID from authentication"
    ),
) -> None:
    """
    Delete a session (logout from specific device).

    Args:
        session_id: Session ID
        user_id: User ID from authentication header

    Raises:
        HTTPException: If session not found or doesn't belong to user
    """
    # First verify session exists and belongs to user
    session = await session_service.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )
    if session.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Session does not belong to authenticated user",
        )

    # Delete session
    deleted = await session_service.delete_session(session_id, user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete session {session_id}",
        )


@router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete all sessions",
    description="Logout and invalidate all sessions for the user.",
)
async def delete_all_sessions(
    user_id: str = Header(
        ..., alias="X-User-Id", description="User ID from authentication"
    ),
) -> None:
    """
    Delete all sessions for the user (logout from all devices).

    Args:
        user_id: User ID from authentication header

    Returns:
        Number of sessions deleted
    """
    count = await session_service.delete_all_sessions(user_id)
    logger.info(f"Deleted {count} sessions for user {user_id}")
    return None


@router.get(
    "/status/storage",
    response_model=dict,
    summary="Get storage status",
    description="Get information about the current storage backend (Redis or fallback).",
)
async def get_storage_status() -> dict:
    """
    Get the current storage status.

    Returns:
        Storage status information
    """
    return session_service.get_storage_status()
