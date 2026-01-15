# =============================================================================
# R001 Personal Notes - Pydantic Models
# =============================================================================
# Request/response schemas for note API endpoints
# =============================================================================

from datetime import datetime
from pydantic import BaseModel, Field


class NoteCreate(BaseModel):
    """Schema for creating a note."""

    title: str = Field(..., description="Note title", min_length=1, max_length=200)
    content: str = Field(..., description="Note content", min_length=1)


class NoteUpdate(BaseModel):
    """Schema for updating a note."""

    title: str | None = Field(None, description="Note title", min_length=1, max_length=200)
    content: str | None = Field(None, description="Note content", min_length=1)


class NoteResponse(BaseModel):
    """Schema for note response."""

    id: int = Field(..., description="Note ID")
    title: str = Field(..., description="Note title")
    content: str = Field(..., description="Note content")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class NoteListResponse(BaseModel):
    """Schema for note list response."""

    notes: list[NoteResponse] = Field(default_factory=list, description="List of notes")
    total: int = Field(..., description="Total count of notes")


class ErrorResponse(BaseModel):
    """Error response schema."""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    detail: str | None = Field(None, description="Detailed error information")
