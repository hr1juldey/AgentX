"""Session DTOs for Real AgentX v0.1.

Data Transfer Objects for session management operations.
Follows Pydantic v2 pattern for C002 data contracts alignment.
"""

from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID


class CreateSessionCommand(BaseModel):
    """Command to create a new session.

    Input DTO for session creation.

    Attributes:
        user_id: User identifier (SHA-256 hash).
        initial_context: Optional initial context for the session.
    """

    user_id: str = Field(
        ..., min_length=64, max_length=64, description="SHA-256 hash of user ID"
    )
    initial_context: list[str] = Field(
        default_factory=list, description="Initial context for the session"
    )


class SessionResponseDTO(BaseModel):
    """Response DTO for session operations.

    Represents a session in API responses.

    Attributes:
        session_id: Session identifier.
        user_id: User identifier hash.
        state: Current session state.
        created_at: Session creation timestamp.
        modified_at: Last modification timestamp.
        last_activity_at: Last activity timestamp.
        current_reasoning_step: Current reasoning step number.
        total_tool_calls: Total tool executions in session.
    """

    session_id: UUID = Field(..., description="Session identifier")
    user_id: str = Field(..., description="User identifier hash")
    state: str = Field(..., description="Current session state")
    created_at: datetime = Field(..., description="Session creation timestamp")
    modified_at: datetime = Field(..., description="Last modification timestamp")
    last_activity_at: datetime = Field(..., description="Last activity timestamp")
    current_reasoning_step: int = Field(0, ge=0, description="Current reasoning step")
    total_tool_calls: int = Field(0, ge=0, description="Total tool executions")


class PauseSessionCommand(BaseModel):
    """Command to pause a session.

    Attributes:
        session_id: Session identifier to pause.
        reason: Optional reason for pausing.
    """

    session_id: UUID = Field(..., description="Session identifier to pause")
    reason: str | None = Field(None, description="Optional reason for pausing")


class ResumeSessionCommand(BaseModel):
    """Command to resume a paused session.

    Attributes:
        session_id: Session identifier to resume.
        context: Optional additional context for resumption.
    """

    session_id: UUID = Field(..., description="Session identifier to resume")
    context: list[str] = Field(
        default_factory=list, description="Additional context for resumption"
    )


class CloseSessionCommand(BaseModel):
    """Command to close a session.

    Attributes:
        session_id: Session identifier to close.
        reason: Optional reason for closing.
    """

    session_id: UUID = Field(..., description="Session identifier to close")
    reason: str | None = Field(None, description="Optional reason for closing")
