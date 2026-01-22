# =============================================================================
# AGENTX Widget Spawner - Tools Package
# =============================================================================
# Widget generation tools for ReAct agent
# =============================================================================

from services.widget_spawner.tools.content_widgets import (
    create_card_widget,
    create_chart_widget,
    create_form_widget,
    create_markdown_widget,
    create_progress_widget,
)
from services.widget_spawner.tools.interactive_widgets import (
    create_action_widget,
    create_confirmation_widget,
    create_gallery_widget,
    create_image_widget,
)

# Tool registry for ReAct agent
WIDGET_TOOLS = [
    create_markdown_widget,
    create_card_widget,
    create_form_widget,
    create_progress_widget,
    create_chart_widget,
    create_action_widget,
    create_confirmation_widget,
    create_image_widget,
    create_gallery_widget,
]

__all__ = [
    "WIDGET_TOOLS",
    "create_markdown_widget",
    "create_card_widget",
    "create_form_widget",
    "create_progress_widget",
    "create_chart_widget",
    "create_action_widget",
    "create_confirmation_widget",
    "create_image_widget",
    "create_gallery_widget",
]
