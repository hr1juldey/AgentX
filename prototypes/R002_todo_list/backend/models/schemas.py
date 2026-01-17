# =============================================================================
# R002 Todo List - Pydantic Models
# =============================================================================
# Request/response schemas for todo API endpoints with enhanced Swagger docs
# =============================================================================

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class Priority(str, Enum):
    """Todo priority levels for organization."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Status(str, Enum):
    """Todo status values tracking progress."""

    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class TodoCreate(BaseModel):
    """Schema for creating a new todo item.

    Create a task with optional description, due date, and priority.
    """

    title: str = Field(
        ...,
        description="Task title (brief description)",
        min_length=1,
        max_length=200,
        examples=["Complete project report", "Buy groceries", "Call client"],
    )
    description: str | None = Field(
        None,
        description="Detailed task description",
        max_length=1000,
        examples=["Include all sections and appendices"],
    )
    due_date: datetime | None = Field(
        None,
        description="When the task is due (ISO 8601 format)",
        examples=["2024-01-20T17:00:00Z"],
    )
    priority: Priority = Field(
        default=Priority.MEDIUM,
        description="Task priority level",
        examples=[Priority.MEDIUM, Priority.HIGH],
    )
    status: Status = Field(
        default=Status.TODO, description="Initial task status", examples=[Status.TODO]
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Complete project report",
                    "description": "Include all sections and appendices",
                    "due_date": "2024-01-20T17:00:00Z",
                    "priority": "high",
                    "status": "todo",
                }
            ]
        }
    }


class TodoUpdate(BaseModel):
    """Schema for updating an existing todo.

    All fields are optional - only include what you want to change.
    """

    title: str | None = Field(
        None,
        description="Updated task title",
        min_length=1,
        max_length=200,
        examples=["Updated: Complete project report"],
    )
    description: str | None = Field(None, description="Updated task description", max_length=1000)
    due_date: datetime | None = Field(
        None, description="Updated due date", examples=["2024-01-21T17:00:00Z"]
    )
    priority: Priority | None = Field(
        None, description="Updated priority level", examples=[Priority.LOW, Priority.HIGH]
    )
    status: Status | None = Field(
        None, description="Updated status", examples=[Status.IN_PROGRESS, Status.DONE]
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"status": "in_progress"},
                {"priority": "high", "due_date": "2024-01-21T17:00:00Z"},
            ]
        }
    }


class TodoResponse(BaseModel):
    """Schema for todo response.

    Returns complete todo with all fields including timestamps.
    """

    id: int = Field(..., description="Unique todo identifier", examples=[1, 42, 100])
    title: str = Field(..., description="Task title", examples=["Complete project report"])
    description: str | None = Field(..., description="Task description or null")
    due_date: datetime | None = Field(..., description="Due date or null")
    priority: Priority = Field(..., description="Priority level", examples=[Priority.HIGH])
    status: Status = Field(..., description="Current status", examples=[Status.IN_PROGRESS])
    created_at: datetime = Field(
        ..., description="When the todo was created", examples=["2024-01-15T10:00:00Z"]
    )
    updated_at: datetime = Field(
        ..., description="When the todo was last updated", examples=["2024-01-15T14:30:00Z"]
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "title": "Complete project report",
                    "description": "Include all sections and appendices",
                    "due_date": "2024-01-20T17:00:00Z",
                    "priority": "high",
                    "status": "in_progress",
                    "created_at": "2024-01-15T10:00:00Z",
                    "updated_at": "2024-01-15T14:30:00Z",
                }
            ]
        }
    }


class TodoListResponse(BaseModel):
    """Schema for paginated todo list response."""

    todos: list[TodoResponse] = Field(
        default_factory=list, description="List of todos (may be empty)"
    )
    total: int = Field(..., description="Total count of all todos", examples=[42])


class ErrorResponse(BaseModel):
    """Error response schema."""

    error: str = Field(..., description="Error type", examples=["ValidationError", "NotFound"])
    message: str = Field(
        ...,
        description="Human-readable error message",
        examples=["Todo not found", "Title is required"],
    )
    detail: str | None = Field(None, description="Additional technical details")
