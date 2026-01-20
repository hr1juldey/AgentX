# =============================================================================
# AGENTX Widget Spawner Models
# =============================================================================
# Pydantic models for widget descriptors
# =============================================================================

from typing import Any

from pydantic import BaseModel


class WidgetDescriptor(BaseModel):
    """Widget descriptor for frontend rendering."""

    id: str
    type: str
    title: str | None = None
    content: str | None = None
    metadata: dict[str, Any] | None = None
    dismissible: bool = True


class WidgetGenerationRequest(BaseModel):
    """Request for widget generation."""

    prompt: str
    widget_type: str | None = None


class WidgetGenerationResponse(BaseModel):
    """Response from single widget generation (legacy)."""

    widget: WidgetDescriptor
    preview_data: dict[str, Any] | None = None


class MultiWidgetGenerationResponse(BaseModel):
    """Response from multi-widget generation using ReAct agent."""

    widgets: list[WidgetDescriptor]
    tools_used: list[str] | None = None
    reasoning: str | None = None
    preview_data: dict[str, Any] | None = None


# =============================================================================
# Legacy alias for backward compatibility
# =============================================================================

# For API backward compatibility, keep the old response name
WidgetResponse = MultiWidgetGenerationResponse
