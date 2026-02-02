"""UI component message for server-driven UI.

Emits UI component descriptors to frontend for rendering.
Pattern from C007: LangGraph server-driven UI.
"""

from dataclasses import dataclass
from typing import Any, override
from uuid import UUID, uuid4

from agentx.ui.protocols.messages.base import WebSocketMessage
from agentx.ui.protocols.messages.enums import MessageType


@dataclass
class UIComponentMessage(WebSocketMessage):
    """UI component message for server-driven UI.

    Emits UI component descriptors to frontend for rendering.
    Pattern from C007: LangGraph server-driven UI.
    """

    @override
    def __init__(
        self,
        component_type: str,
        props: dict[str, Any],
        session_id: UUID,
        merge: bool = False,
        component_id: UUID | None = None,
    ):
        """Initialize UI component message.

        Args:
            component_type: Type of UI component.
            props: Component properties.
            session_id: Session identifier.
            merge: Whether to merge with existing component.
            component_id: Optional component ID for merging.
        """
        super().__init__(
            message_type=MessageType.UI_COMPONENT,
            session_id=session_id,
            data={
                "component_type": component_type,
                "props": props,
                "merge": merge,
                "component_id": str(component_id) if component_id else str(uuid4()),
            },
        )
