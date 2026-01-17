# =============================================================================
# R003 Pomodoro Timer - Pydantic Models
# =============================================================================
# Request/response schemas for Pomodoro Timer API endpoints with enhanced Swagger docs
# =============================================================================

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class SessionStatus(str, Enum):
    """Pomodoro session status values.

    Tracks the state of a focus session throughout its lifecycle.
    """

    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class SessionCreate(BaseModel):
    """Schema for creating a new Pomodoro session.

    Start a focus session with customizable work and break durations.
    """

    title: str = Field(
        ...,
        description="Session title or task description",
        min_length=1,
        max_length=200,
        examples=["Deep work: Project proposal", "Code review session"],
    )
    duration_minutes: int | None = Field(
        None,
        description="Duration in minutes (deprecated: use work_duration instead)",
        ge=1,
        le=180,
        deprecated=True,
    )
    work_duration: int = Field(
        default=25,
        description="Work/focus duration in minutes (default: 25)",
        ge=1,
        le=180,
        examples=[25, 45, 60],
    )
    break_duration: int = Field(
        default=5,
        description="Break duration in minutes (default: 5)",
        ge=1,
        le=60,
        examples=[5, 10, 15],
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Deep work: Project proposal",
                    "work_duration": 25,
                    "break_duration": 5,
                }
            ]
        }
    }


class SessionUpdate(BaseModel):
    """Schema for updating a Pomodoro session.

    Change status or manually adjust remaining time.
    """

    status: SessionStatus | None = Field(
        None,
        description="New session status",
        examples=[SessionStatus.PAUSED, SessionStatus.COMPLETED],
    )
    remaining_seconds: int | None = Field(
        None,
        description="Manually set remaining time in seconds",
        ge=0,
        examples=[600, 1200],
    )

    model_config = {
        "json_schema_extra": {
            "examples": [{"status": "paused"}, {"remaining_seconds": 1200}]
        }
    }


class SessionResponse(BaseModel):
    """Schema for session response.

    Returns complete session with timing information.
    """

    id: int = Field(..., description="Unique session identifier", examples=[1, 42])
    title: str = Field(
        ..., description="Session title", examples=["Deep work: Project proposal"]
    )
    status: SessionStatus = Field(
        ..., description="Current session status", examples=[SessionStatus.RUNNING]
    )
    remaining_seconds: int = Field(
        ..., description="Remaining time in seconds", examples=[600], ge=0
    )
    total_seconds: int = Field(
        ..., description="Total session duration in seconds", examples=[1500], ge=0
    )
    work_duration: int = Field(
        ..., description="Work duration in minutes", examples=[25]
    )
    break_duration: int = Field(
        ..., description="Break duration in minutes", examples=[5]
    )
    created_at: datetime = Field(
        ...,
        description="When the session was created",
        examples=["2024-01-15T10:00:00Z"],
    )
    updated_at: datetime = Field(
        ...,
        description="When the session was last updated",
        examples=["2024-01-15T10:25:00Z"],
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "title": "Deep work: Project proposal",
                    "status": "running",
                    "remaining_seconds": 600,
                    "total_seconds": 1500,
                    "work_duration": 25,
                    "break_duration": 5,
                    "created_at": "2024-01-15T10:00:00Z",
                    "updated_at": "2024-01-15T10:25:00Z",
                }
            ]
        }
    }


class SessionListResponse(BaseModel):
    """Schema for session list response."""

    sessions: list[SessionResponse] = Field(
        default_factory=list, description="List of sessions (may be empty)"
    )
    total: int = Field(..., description="Total count of sessions", examples=[42])


class TimerUpdate(BaseModel):
    """Schema for WebSocket timer updates.

    Real-time timer state pushed to connected clients.
    """

    session_id: int = Field(
        ..., description="Session ID this update belongs to", examples=[1]
    )
    remaining_seconds: int = Field(
        ..., description="Current remaining time in seconds", examples=[600], ge=0
    )
    status: SessionStatus = Field(
        ..., description="Current session status", examples=[SessionStatus.RUNNING]
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"session_id": 1, "remaining_seconds": 600, "status": "running"}
            ]
        }
    }


class ErrorResponse(BaseModel):
    """Error response schema."""

    error: str = Field(
        ..., description="Error type", examples=["ValidationError", "NotFound"]
    )
    message: str = Field(
        ...,
        description="Human-readable error message",
        examples=["Session not found", "Invalid status transition"],
    )
    detail: str | None = Field(None, description="Additional technical details")
