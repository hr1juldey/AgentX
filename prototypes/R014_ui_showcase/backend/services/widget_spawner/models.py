# =============================================================================
# AGENTX Widget Spawner Models (DEPRECATED)
# =============================================================================
# ⚠️  DEPRECATED: Import from domain/entities/ and application/dtos/
# =============================================================================

from typing import Any

from pydantic import BaseModel

# Import domain entity for use in services
from domain.entities.ui_descriptor import UIDescriptor

# Deprecated aliases for backward compatibility
WidgetDescriptor = UIDescriptor


class WidgetGenerationRequest(BaseModel):
    """Request for widget generation."""

    prompt: str
    widget_type: str | None = None


class MultiWidgetGenerationResponse(BaseModel):
    """Response from multi-widget generation using ReAct agent."""

    widgets: list[UIDescriptor]
    tools_used: list[str] | None = None
    reasoning: str | None = None
    preview_data: dict[str, Any] | None = None


# =============================================================================
# Legacy aliases for backward compatibility
# =============================================================================

# For API backward compatibility, keep the old response name
WidgetGenerationResponse = MultiWidgetGenerationResponse

# Legacy alias
WidgetResponse = MultiWidgetGenerationResponse
