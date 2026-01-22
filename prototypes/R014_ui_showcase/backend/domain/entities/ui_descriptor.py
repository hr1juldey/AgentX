# =============================================================================
# AGENTX R014 - Domain Layer - UI Descriptor Entity
# =============================================================================
# Core domain entity for UI widgets
# =============================================================================

from typing import Any, Literal

from pydantic import BaseModel


class UIDescriptor(BaseModel):
    """UI descriptor domain entity.

    Represents a UI widget in the domain layer, independent of API concerns.
    This is the core entity that exists at the heart of the system.

    Widget types include multi-hop search widgets:
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
