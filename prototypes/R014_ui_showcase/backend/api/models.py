# =============================================================================
# AGENTX R014 - API Models
# =============================================================================
# Pydantic models for API requests and responses
# =============================================================================

from typing import Any, Literal

from pydantic import BaseModel


class UIDescriptor(BaseModel):
    """UI descriptor model.

    Extended with multi-hop search widget types:
    - search-result: Final answer with citations
    - hop-progress: Real-time hop progress with expandable details
    - citation-card: Expandable citation cards
    """

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
        "search-result",
        "hop-progress",
        "citation-card",
    ]
    timestamp: str
    dismissible: bool = True
    content: str | None = None
    title: str | None = None
    metadata: dict[str, Any] = {}
    # Multi-hop search optional fields
    progress: float | None = None
    hops_completed: int | None = None
    total_hops: int | None = None
    reflection_reasoning: str | None = None
    citations: list[dict[str, Any]] | None = None
    hop_events: list[dict[str, Any]] | None = None
    eta_seconds: float | None = None


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
