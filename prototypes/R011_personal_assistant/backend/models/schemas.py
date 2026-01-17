"""
Request and response schemas for Personal Assistant API with enhanced Swagger documentation.

This module provides schemas for AI chat assistant with tool calling capabilities.
"""

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class ToolCall(BaseModel):
    """Schema for a tool/function call.

    Represents a single tool invocation by the AI assistant.
    """

    name: str = Field(
        ...,
        description="Tool/function name to call",
        examples=["search_web", "get_weather", "calculate"],
    )
    arguments: dict = Field(
        ...,
        description="Arguments to pass to the tool",
        examples=[{"query": "machine learning", "limit": 5}],
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "search_web",
                    "arguments": {"query": "latest AI news", "limit": 5},
                }
            ]
        }
    }


class Message(BaseModel):
    """Schema for a chat message.

    Represents a single message in the conversation.
    """

    role: Literal["user", "assistant", "system"] = Field(
        ..., description="Message sender role", examples=["user", "assistant"]
    )
    content: str = Field(
        ...,
        description="Message text content",
        examples=["Hello, how can you help me?"],
    )
    tool_calls: Optional[List[ToolCall]] = Field(
        None,
        description="Tool calls made by the assistant (for assistant messages only)",
    )
    timestamp: datetime = Field(
        default_factory=datetime.now, description="When the message was sent"
    )


class ChatRequest(BaseModel):
    """Schema for chat request.

    Send a message to the AI assistant and receive a response.
    """

    message: str = Field(
        ...,
        description="User message to the assistant",
        min_length=1,
        examples=["What's the weather like?", "Help me write a poem"],
    )
    conversation_id: Optional[str] = Field(
        None,
        description="Conversation ID for context (optional for new chats)",
        examples=["conv_abc123"],
    )
    tools: Optional[List[str]] = Field(
        None,
        description="List of available tool names the assistant can use",
        examples=[["search_web", "get_weather"], ["calculator"]],
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "message": "What's the weather like in San Francisco?",
                    "conversation_id": "conv_abc123",
                    "tools": ["get_weather"],
                }
            ]
        }
    }


class ChatResponse(BaseModel):
    """Schema for chat response.

    Returns the assistant's response with optional tool calls.
    """

    response: str = Field(
        ...,
        description="Assistant's text response",
        examples=["The weather in San Francisco is currently..."],
    )
    tool_calls: Optional[List[ToolCall]] = Field(
        None, description="Tool calls the assistant wants to make"
    )
    thoughts: Optional[str] = Field(
        None, description="Assistant's reasoning/thought process (if enabled)"
    )
    conversation_id: str = Field(
        ..., description="Conversation ID for context", examples=["conv_abc123"]
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "response": "The weather in San Francisco is currently 65°F and sunny.",
                    "tool_calls": None,
                    "thoughts": None,
                    "conversation_id": "conv_abc123",
                }
            ]
        }
    }


class ToolSchema(BaseModel):
    """Schema for tool/function definition.

    Describes a tool that the assistant can use.
    """

    name: str = Field(
        ..., description="Tool/function name", examples=["search_web", "get_weather"]
    )
    description: str = Field(
        ...,
        description="What the tool does and when to use it",
        examples=["Search the web for current information"],
    )
    parameters: dict = Field(
        ...,
        description="JSON schema for tool parameters",
        examples=[
            {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"}
                },
                "required": ["query"],
            }
        ],
    )


class ErrorResponse(BaseModel):
    """Schema for error response."""

    error: str = Field(
        ..., description="Error type", examples=["ValidationError", "AssistantError"]
    )
    message: str = Field(
        ...,
        description="Error message",
        examples=["Message is required", "Assistant unavailable"],
    )
    detail: Optional[str] = Field(None, description="Additional technical details")


class ConversationListResponse(BaseModel):
    """Schema for conversation list response."""

    conversations: List[dict] = Field(
        default_factory=list, description="List of conversations"
    )
    total: int = Field(..., description="Total count of conversations", examples=[10])
