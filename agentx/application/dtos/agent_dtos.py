"""Agent DTOs for Real AgentX v0.1.

Data Transfer Objects for agent-related API operations.
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class ExecuteAgentQueryRequest(BaseModel):
    """Request DTO for executing an agent query."""

    query: str = Field(..., description="User's query text", min_length=1)
    session_id: str | None = Field(None, description="Optional session ID for continuation")
    user_id: str | None = Field(None, description="Optional user identifier")
    context: str | None = Field(None, description="Optional context for the query")


class ToolCallDTO(BaseModel):
    """DTO representing a tool execution call."""

    tool_name: str = Field(..., description="Name of the tool")
    parameters: dict[str, Any] = Field(default_factory=dict, description="Tool parameters")
    result: Any = Field(None, description="Tool execution result")
    status: str = Field("pending", description="Tool execution status")
    timestamp: datetime = Field(default_factory=datetime.now)


class UIComponentDTO(BaseModel):
    """DTO representing a UI component for server-driven UI."""

    component_id: str = Field(..., description="Component identifier")
    component_type: str = Field(..., description="Component type (markdown, card, etc.)")
    props: dict[str, Any] = Field(default_factory=dict, description="Component properties")
    merge: bool = Field(False, description="Whether to merge with existing component")


class ExecuteAgentQueryResponse(BaseModel):
    """Response DTO for agent query execution."""

    session_id: str = Field(..., description="Session identifier")
    response: str = Field(..., description="Agent's response text")
    reasoning: str = Field(..., description="Agent's reasoning process")
    ui_components: list[UIComponentDTO] = Field(
        default_factory=list, description="UI components to render"
    )
    tool_calls: list[ToolCallDTO] = Field(
        default_factory=list, description="Tool executions performed"
    )
    sources: list[str] = Field(default_factory=list, description="Source references")
    timestamp: datetime = Field(default_factory=datetime.now)


class SessionStatusDTO(BaseModel):
    """DTO representing session status."""

    session_id: str = Field(..., description="Session identifier")
    state: str = Field(..., description="Session state")
    created_at: datetime = Field(..., description="Session creation time")
    last_activity_at: datetime = Field(..., description="Last activity time")
    current_reasoning_step: int = Field(0, description="Current reasoning step")
    total_tool_calls: int = Field(0, description="Total tool executions")
