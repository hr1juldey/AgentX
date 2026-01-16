# =============================================================================
# R001 Personal Notes - Pydantic Models
# =============================================================================
# Request/response schemas for note API endpoints with enhanced Swagger docs
# =============================================================================

from datetime import datetime

from pydantic import BaseModel, Field


class NoteCreate(BaseModel):
    """Schema for creating a new note.

    Use this to create a new personal note with title and content.
    """

    title: str = Field(
        ...,
        description="Note title (brief heading)",
        min_length=1,
        max_length=200,
        examples=["Meeting Notes", "Shopping List", "Project Ideas"]
    )
    content: str = Field(
        ...,
        description="Full note content (can be long-form text)",
        min_length=1,
        examples=["Discussed Q1 goals and action items..."]
    )

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "title": "Meeting Notes",
                "content": "Discussed Q1 goals and action items. Follow up with team next week."
            }]
        }
    }


class NoteUpdate(BaseModel):
    """Schema for updating an existing note.

    All fields are optional - only include fields you want to change.
    """

    title: str | None = Field(
        None,
        description="Updated note title (leave empty to keep current)",
        min_length=1,
        max_length=200,
        examples=["Updated Meeting Notes"]
    )
    content: str | None = Field(
        None,
        description="Updated note content (leave empty to keep current)",
        min_length=1,
        examples=["Updated: Discussed Q1 goals with new timeline..."]
    )

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "title": "Updated Meeting Notes",
                "content": "Updated: Discussed Q1 goals with new timeline"
            }, {
                "content": "Just updating the content, title stays the same"
            }]
        }
    }


class NoteResponse(BaseModel):
    """Schema for note response.

    Returns the complete note with system-generated fields.
    """

    id: int = Field(
        ...,
        description="Unique note identifier (auto-generated)",
        examples=[1, 42, 100]
    )
    title: str = Field(
        ...,
        description="Note title",
        examples=["Meeting Notes"]
    )
    content: str = Field(
        ...,
        description="Note content",
        examples=["Discussed Q1 goals and action items..."]
    )
    created_at: datetime = Field(
        ...,
        description="When the note was first created",
        examples=["2024-01-15T10:30:00Z"]
    )
    updated_at: datetime = Field(
        ...,
        description="When the note was last modified",
        examples=["2024-01-15T14:20:00Z"]
    )

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "id": 1,
                "title": "Meeting Notes",
                "content": "Discussed Q1 goals and action items. Follow up with team next week.",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T14:20:00Z"
            }]
        }
    }


class NoteListResponse(BaseModel):
    """Schema for paginated note list response."""

    notes: list[NoteResponse] = Field(
        default_factory=list,
        description="List of notes (may be empty)"
    )
    total: int = Field(
        ...,
        description="Total count of all notes (not just returned page)",
        examples=[42]
    )

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "notes": [
                    {
                        "id": 1,
                        "title": "Meeting Notes",
                        "content": "Discussed Q1 goals...",
                        "created_at": "2024-01-15T10:30:00Z",
                        "updated_at": "2024-01-15T14:20:00Z"
                    },
                    {
                        "id": 2,
                        "title": "Shopping List",
                        "content": "Milk, eggs, bread...",
                        "created_at": "2024-01-16T09:00:00Z",
                        "updated_at": "2024-01-16T09:00:00Z"
                    }
                ],
                "total": 2
            }]
        }
    }


class ErrorResponse(BaseModel):
    """Error response schema."""

    error: str = Field(
        ...,
        description="Type of error that occurred",
        examples=["ValidationError", "NotFound"]
    )
    message: str = Field(
        ...,
        description="Human-readable error message",
        examples=["Note not found", "Title is required"]
    )
    detail: str | None = Field(
        None,
        description="Additional technical details for debugging"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "error": "NotFound",
                "message": "Note with ID 999 not found",
                "detail": "No note exists with the provided identifier"
            }]
        }
    }
