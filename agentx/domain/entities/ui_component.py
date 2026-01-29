"""UI component domain entity.

Represents a UI component/descriptor emitted by the agent
for rendering in the frontend.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from agentx.domain.entities.enums import UIComponentType


@dataclass
class UIComponentEntity:
    """Represents a UI component emitted by the agent.

    Mapped to frontend React components via LangGraph server-driven UI.

    Attributes:
        component_id: Unique component identifier.
        component_type: Type of UI component.
        props: Component properties (serialized dict).
        session_id: Associated session identifier.
        created_at: Component creation timestamp.
        merge: Whether to merge with existing component (for streaming).
    """

    component_id: UUID
    component_type: UIComponentType
    props: dict[str, Any]
    session_id: UUID
    created_at: datetime
    merge: bool = False

    @classmethod
    def create(
        cls,
        component_type: UIComponentType,
        props: dict[str, Any],
        session_id: UUID,
        merge: bool = False,
    ) -> "UIComponentEntity":
        """Create a new UI component.

        Args:
            component_type: Type of UI component.
            props: Component properties.
            session_id: Associated session ID.
            merge: Whether to merge with existing component.

        Returns:
            UIComponentEntity: New UI component entity.
        """
        return cls(
            component_id=uuid4(),
            component_type=component_type,
            props=props,
            session_id=session_id,
            created_at=datetime.now(),
            merge=merge,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for WebSocket serialization.

        Returns:
            dict: Serializable component representation.
        """
        return {
            "component_id": str(self.component_id),
            "component_type": self.component_type.value,
            "props": self.props,
            "session_id": str(self.session_id),
            "created_at": self.created_at.isoformat(),
            "merge": self.merge,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "UIComponentEntity":
        """Create from dictionary (WebSocket deserialization).

        Args:
            data: Serialized component data.

        Returns:
            UIComponentEntity: Deserialized component entity.
        """
        return cls(
            component_id=UUID(data["component_id"]),
            component_type=UIComponentType(data["component_type"]),
            props=data["props"],
            session_id=UUID(data["session_id"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            merge=data.get("merge", False),
        )


@dataclass
class ToolCallEntity:
    """Represents a tool execution call.

    Attributes:
        call_id: Unique call identifier.
        tool_name: Name of the tool called.
        arguments: Tool arguments.
        result: Tool execution result (if complete).
        created_at: Call creation timestamp.
    """

    call_id: UUID
    tool_name: str
    arguments: dict[str, Any]
    result: Any = None
    created_at: datetime = field(default_factory=datetime.now)

    @classmethod
    def create(
        cls, tool_name: str, arguments: dict[str, Any]
    ) -> "ToolCallEntity":
        """Create a new tool call.

        Args:
            tool_name: Name of the tool.
            arguments: Tool arguments.

        Returns:
            ToolCallEntity: New tool call entity.
        """
        return cls(
            call_id=uuid4(),
            tool_name=tool_name,
            arguments=arguments,
        )

    def complete(self, result: Any) -> None:
        """Mark the tool call as complete with result.

        Args:
            result: Tool execution result.
        """
        self.result = result
