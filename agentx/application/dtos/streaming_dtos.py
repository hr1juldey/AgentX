"""Streaming DTOs for Real AgentX v0.1.

Data Transfer Objects for streaming agent operations.
Follows Pydantic v2 pattern for C002 data contracts alignment.
"""

from datetime import datetime
from pydantic import BaseModel, Field
from typing import Any, Literal


class StreamChunk(BaseModel):
    """A chunk of streamed agent response.

    Represents a single piece of data in a streaming response.

    Attributes:
        chunk_type: Type of chunk (text, reasoning, tool_call, ui_component, error).
        content: Chunk content (varies by type).
        sequence_id: Sequence number for ordering.
        timestamp: When this chunk was generated.
    """

    chunk_type: Literal["text", "reasoning", "tool_call", "ui_component", "error"] = (
        Field(..., description="Type of streamed chunk")
    )
    content: dict[str, Any] = Field(..., description="Chunk content (varies by type)")
    sequence_id: int = Field(..., ge=0, description="Sequence number for ordering")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Chunk timestamp"
    )


class ReasoningStep(BaseModel):
    """A single reasoning step in agent execution.

    Represents one step in the agent's multi-step reasoning process.

    Attributes:
        step_number: Step sequence number.
        thought: Agent's thought at this step.
        action: Action taken (tool call or final answer).
        observation: Result of the action.
        confidence: Confidence score (0-1).
    """

    step_number: int = Field(..., ge=1, description="Step sequence number")
    thought: str = Field(..., description="Agent's thought at this step")
    action: str = Field(..., description="Action taken (tool call or final answer)")
    observation: str = Field("", description="Result of the action")
    confidence: float = Field(default=0.5, ge=0, le=1, description="Confidence score")


class ToolCall(BaseModel):
    """Represents a tool execution call.

    Attributes:
        tool_name: Name of the tool being called.
        parameters: Parameters passed to the tool.
        result: Result returned by the tool.
        status: Execution status (pending, running, success, error).
        error_message: Error message if status is error.
        duration_ms: Execution duration in milliseconds.
        timestamp: When the tool was called.
    """

    tool_name: str = Field(..., description="Name of the tool being called")
    parameters: dict[str, Any] = Field(
        default_factory=dict, description="Parameters passed to the tool"
    )
    result: Any = Field(None, description="Result returned by the tool")
    status: Literal["pending", "running", "success", "error"] = Field(
        "pending", description="Execution status"
    )
    error_message: str = Field("", description="Error message if status is error")
    duration_ms: int | None = Field(None, ge=0, description="Execution duration in ms")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Tool call timestamp"
    )


class StreamingMetadata(BaseModel):
    """Metadata for a streaming response.

    Attributes:
        session_id: Session identifier.
        total_chunks: Total number of chunks expected.
        current_chunk: Current chunk number.
        is_complete: Whether streaming is complete.
        total_tool_calls: Total tool calls made.
        total_reasoning_steps: Total reasoning steps taken.
    """

    session_id: str = Field(..., description="Session identifier")
    total_chunks: int | None = Field(None, ge=0, description="Total chunks expected")
    current_chunk: int = Field(0, ge=0, description="Current chunk number")
    is_complete: bool = Field(False, description="Whether streaming is complete")
    total_tool_calls: int = Field(0, ge=0, description="Total tool calls made")
    total_reasoning_steps: int = Field(0, ge=0, description="Total reasoning steps")
