"""Domain models for streaming events.

This module defines the models for transient UX streaming events
that keep users engaged during long-running tasks.
"""

from enum import Enum

from pydantic import BaseModel, Field


class StreamingEventType(str, Enum):
    """Types of streaming events."""

    TOKEN = "token"
    PROGRESS = "progress"
    WIDGET_REVEAL = "widget_reveal"
    BACKGROUND_PROMPT = "background_prompt"
    COMPLETE = "complete"
    ERROR = "error"


class TokenEvent(BaseModel):
    """Token streaming event for text responses."""

    event_type: StreamingEventType = Field(
        default=StreamingEventType.TOKEN,
        description="Event type",
    )
    token: str = Field(description="Token text")
    is_first: bool = Field(
        default=False,
        description="True if this is the first token",
    )
    index: int = Field(description="Token index in stream")


class ProgressEvent(BaseModel):
    """Progress update event for long-running tasks."""

    event_type: StreamingEventType = Field(
        default=StreamingEventType.PROGRESS,
        description="Event type",
    )
    progress: float = Field(
        ge=0.0,
        le=1.0,
        description="Progress (0.0-1.0)",
    )
    message: str = Field(description="Progress message")
    current_step: str = Field(description="Current step name")
    total_steps: int = Field(description="Total number of steps")


class BackgroundPromptEvent(BaseModel):
    """Prompt to continue task in background."""

    event_type: StreamingEventType = Field(
        default=StreamingEventType.BACKGROUND_PROMPT,
        description="Event type",
    )
    elapsed_seconds: int = Field(
        ge=0,
        description="Elapsed time in seconds",
    )
    message: str = Field(
        default="Task is taking longer. Continue in background?",
        description="Prompt message",
    )


class WidgetRevealEvent(BaseModel):
    """Widget reveal event for progressive disclosure."""

    event_type: StreamingEventType = Field(
        default=StreamingEventType.WIDGET_REVEAL,
        description="Event type",
    )
    widget: dict = Field(description="Widget specification")
    index: int = Field(description="Widget index (0-based)")
    total: int = Field(description="Total number of widgets")


class CompleteEvent(BaseModel):
    """Task completion event."""

    event_type: StreamingEventType = Field(
        default=StreamingEventType.COMPLETE,
        description="Event type",
    )
    final_response: str = Field(description="Final response text")
    widget_count: int = Field(description="Number of widgets generated")
    total_duration: float = Field(description="Total duration in seconds")
