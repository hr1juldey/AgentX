# =============================================================================
# R003 Pomodoro Timer - Pydantic Models
# =============================================================================
# Request/response schemas for Pomodoro Timer API endpoints
# =============================================================================

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class SessionStatus(str, Enum):
    """Pomodoro session status values."""

    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class SessionCreate(BaseModel):
    """Schema for creating a pomodoro session."""

    title: str = Field(..., description="Session title", min_length=1, max_length=200)
    duration_minutes: int | None = Field(
        None,
        description="Duration in minutes (deprecated, use work_duration)",
        ge=1,
        le=180,
    )
    work_duration: int = Field(
        default=25, description="Work duration in minutes", ge=1, le=180
    )
    break_duration: int = Field(
        default=5, description="Break duration in minutes", ge=1, le=60
    )


class SessionUpdate(BaseModel):
    """Schema for updating a pomodoro session."""

    status: SessionStatus | None = Field(None, description="New session status")
    remaining_seconds: int | None = Field(
        None, description="Remaining time in seconds", ge=0
    )


class SessionResponse(BaseModel):
    """Schema for session response."""

    id: int = Field(..., description="Session ID")
    title: str = Field(..., description="Session title")
    status: SessionStatus = Field(..., description="Current session status")
    remaining_seconds: int = Field(..., description="Remaining time in seconds")
    total_seconds: int = Field(..., description="Total session duration in seconds")
    work_duration: int = Field(..., description="Work duration in minutes")
    break_duration: int = Field(..., description="Break duration in minutes")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class SessionListResponse(BaseModel):
    """Schema for session list response."""

    sessions: list[SessionResponse] = Field(default_factory=list, description="List of sessions")
    total: int = Field(..., description="Total count of sessions")


class TimerUpdate(BaseModel):
    """Schema for WebSocket timer updates."""

    session_id: int = Field(..., description="Session ID")
    remaining_seconds: int = Field(..., description="Remaining time in seconds")
    status: SessionStatus = Field(..., description="Current session status")


class ErrorResponse(BaseModel):
    """Error response schema."""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    detail: str | None = Field(None, description="Detailed error information")
