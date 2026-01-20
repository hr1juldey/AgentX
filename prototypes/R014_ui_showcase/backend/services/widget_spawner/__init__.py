# =============================================================================
# AGENTX Widget Spawner Package
# =============================================================================
# DSPy-based widget generation service
# =============================================================================

from services.widget_spawner.service import get_widget_spawner_service
from services.widget_spawner.models import (
    WidgetDescriptor,
    WidgetGenerationRequest,
    WidgetGenerationResponse,
)

__all__ = [
    "get_widget_spawner_service",
    "WidgetDescriptor",
    "WidgetGenerationRequest",
    "WidgetGenerationResponse",
]
