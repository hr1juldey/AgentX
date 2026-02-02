"""UI component extraction from agent responses.

Extracts and formats UI components from LangGraph state.
"""

import logging

from agentx.application.dtos.ui_dtos import UIComponentDTO

logger = logging.getLogger(__name__)


def extract_ui_components(ui_messages: list) -> list[UIComponentDTO]:
    """Extract UI components from LangGraph UI messages.

    Args:
        ui_messages: List of UI messages from LangGraph state.

    Returns:
        list[UIComponentDTO]: List of UI component DTOs.
    """
    components = []

    for msg in ui_messages:
        # Extract UI component data from message
        if hasattr(msg, "content"):
            content = msg.content
            if isinstance(content, dict):
                component_type = content.get("type", "markdown")
                props = content.get("props", {})
                component_id = content.get("id", f"component-{len(components)}")

                components.append(
                    UIComponentDTO(
                        component_id=component_id,
                        component_type=component_type,
                        props=props,
                    )
                )

    logger.debug(f"[UI] Extracted {len(components)} UI components")
    return components
