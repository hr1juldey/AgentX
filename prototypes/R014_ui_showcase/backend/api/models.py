# =============================================================================
# AGENTX R014 - API Models
# =============================================================================
# Pydantic models for API requests and responses
# =============================================================================

from typing import Any, Literal

from pydantic import BaseModel


class UIDescriptor(BaseModel):
    """UI descriptor model."""

    id: str
    type: Literal[
        "markdown",
        "card",
        "form",
        "progress",
        "action",
        "confirmation",
        "voice",
        "image",
        "gallery",
        "chart",
    ]
    timestamp: str
    dismissible: bool = True
    content: str | None = None
    title: str | None = None
    metadata: dict[str, Any] = {}


class GenerateRequest(BaseModel):
    """Request to generate content."""

    prompt: str
    widget_type: (
        Literal[
            "markdown",
            "card",
            "form",
            "progress",
            "action",
            "confirmation",
            "image",
            "gallery",
            "chart",
        ]
        | None
    ) = None


class IntelligentGenerateRequest(BaseModel):
    """Request for intelligent UI generation with device context."""

    prompt: str
    device_context: dict[str, Any] = {
        "type": "desktop",
        "screen_width": 1920,
        "screen_height": 1080,
    }
