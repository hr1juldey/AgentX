"""Base UI descriptor for Real AgentX v0.1.

Defines the base descriptor class for all UI components.
Server-driven UI pattern from C007.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any
from uuid import UUID, uuid4

from agentx.domain.entities.enums import UIComponentType


@dataclass
class BaseUIDescriptor(ABC):
    """Base class for all UI descriptors.

    UI descriptors are Python objects that map to React components
    via LangGraph server-driven UI (from C007).
    """

    descriptor_id: UUID = field(default_factory=uuid4)
    component_type: UIComponentType = field(init=False)
    props: dict[str, Any] = field(default_factory=dict)

    @abstractmethod
    def validate(self) -> bool:
        """Validate descriptor properties.

        Returns:
            bool: True if descriptor is valid.
        """
        pass

    def to_dict(self) -> dict[str, Any]:
        """Convert descriptor to dictionary for serialization.

        Returns:
            dict: Serializable descriptor representation.
        """
        return {
            "descriptor_id": str(self.descriptor_id),
            "component_type": self.component_type.value,
            "props": self.props,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BaseUIDescriptor":
        """Create descriptor from dictionary.

        Args:
            data: Serialized descriptor data.

        Returns:
            BaseUIDescriptor: Deserialized descriptor.
        """
        return cls(
            descriptor_id=UUID(data.get("descriptor_id", str(uuid4()))),
            props=data.get("props", {}),
        )


@dataclass
class MarkdownDescriptor(BaseUIDescriptor):
    """Markdown content descriptor.

    Renders formatted markdown text in the frontend.
    """

    component_type: UIComponentType = field(default=UIComponentType.MARKDOWN, init=False)
    props: dict[str, Any] = field(default_factory=lambda: {"content": "", "format": "markdown"})

    def __init__(self, content: str, format: str = "markdown"):
        """Initialize markdown descriptor.

        Args:
            content: Markdown content to render.
            format: Content format (markdown, plain text).
        """
        super().__init__()
        self.props = {"content": content, "format": format}

    def validate(self) -> bool:
        """Validate markdown descriptor.

        Returns:
            bool: True if content is non-empty string.
        """
        return isinstance(self.props.get("content"), str) and len(
            self.props.get("content", "")
        ) > 0


@dataclass
class CardDescriptor(BaseUIDescriptor):
    """Card component descriptor.

    Displays content in a card with title and optional actions.
    """

    component_type: UIComponentType = field(default=UIComponentType.CARD, init=False)
    props: dict[str, Any] = field(default_factory=dict)

    def __init__(
        self, title: str, content: str, actions: list[dict[str, Any]] | None = None
    ):
        """Initialize card descriptor.

        Args:
            title: Card title.
            content: Card content (can be markdown).
            actions: Optional list of action buttons.
        """
        super().__init__()
        self.props = {
            "title": title,
            "content": content,
            "actions": actions or [],
        }

    def validate(self) -> bool:
        """Validate card descriptor.

        Returns:
            bool: True if title and content are non-empty.
        """
        return (
            isinstance(self.props.get("title"), str)
            and len(self.props.get("title", "")) > 0
            and isinstance(self.props.get("content"), str)
        )
