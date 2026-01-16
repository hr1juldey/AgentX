# =============================================================================
# R002 Todo List - Pydantic Models
# =============================================================================
# Request/response schemas for todo API endpoints
# =============================================================================

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class Priority(str, Enum):
    """Todo priority levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Status(str, Enum):
    """Todo status values."""

    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class TodoCreate(BaseModel):
    """Schema for creating a todo."""

    title: str = Field(..., description="Todo title", min_length=1, max_length=200)
    description: str | None = Field(None, description="Todo description", max_length=1000)
    due_date: datetime | None = Field(None, description="Todo due date")
    priority: Priority = Field(default=Priority.MEDIUM, description="Todo priority")
    status: Status = Field(default=Status.TODO, description="Todo status")


class TodoUpdate(BaseModel):
    """Schema for updating a todo."""

    title: str | None = Field(None, description="Todo title", min_length=1, max_length=200)
    description: str | None = Field(None, description="Todo description", max_length=1000)
    due_date: datetime | None = Field(None, description="Todo due date")
    priority: Priority | None = Field(None, description="Todo priority")
    status: Status | None = Field(None, description="Todo status")


class TodoResponse(BaseModel):
    """Schema for todo response."""

    id: int = Field(..., description="Todo ID")
    title: str = Field(..., description="Todo title")
    description: str | None = Field(..., description="Todo description")
    due_date: datetime | None = Field(..., description="Todo due date")
    priority: Priority = Field(..., description="Todo priority")
    status: Status = Field(..., description="Todo status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class TodoListResponse(BaseModel):
    """Schema for todo list response."""

    todos: list[TodoResponse] = Field(default_factory=list, description="List of todos")
    total: int = Field(..., description="Total count of todos")


class ErrorResponse(BaseModel):
    """Error response schema."""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    detail: str | None = Field(None, description="Detailed error information")
