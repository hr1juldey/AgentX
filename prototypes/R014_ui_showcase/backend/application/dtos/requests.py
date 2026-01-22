# =============================================================================
# AGENTX R014 - Application Layer - Request DTOs
# =============================================================================
# Data Transfer Objects for API requests (Clean Architecture)
# =============================================================================

from typing import Any, Literal

from pydantic import BaseModel


class GenerateWidgetRequest(BaseModel):
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


class SearchRequest(BaseModel):
    """Request for multi-hop search."""

    query: str
