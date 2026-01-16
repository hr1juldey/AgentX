"""Request and response schemas."""
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime


class ToolCall(BaseModel):
    """Tool call schema."""
    name: str
    arguments: dict


class Message(BaseModel):
    """Chat message schema."""
    role: Literal["user", "assistant", "system"]
    content: str
    tool_calls: Optional[List[ToolCall]] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class ChatRequest(BaseModel):
    """Chat request schema."""
    message: str = Field(..., min_length=1, description="User message")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for context")
    tools: Optional[List[str]] = Field(None, description="Available tools")


class ChatResponse(BaseModel):
    """Chat response schema."""
    response: str
    tool_calls: Optional[List[ToolCall]] = None
    thoughts: Optional[str] = None
    conversation_id: str


class ToolSchema(BaseModel):
    """Tool definition schema."""
    name: str
    description: str
    parameters: dict
