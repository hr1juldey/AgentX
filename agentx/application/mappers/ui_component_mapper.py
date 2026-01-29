"""UI component mapper for Real AgentX v0.1.

Converts between UI component entities and DTOs.
"""

from uuid import UUID

from agentx.application.dtos.ui_dtos import (
    CardComponentDTO,
    MarkdownComponentDTO,
    UIComponentDTO,
)
from agentx.domain.entities.ui_component import UIComponentEntity
from agentx.ui.descriptors.base import (
    BaseUIDescriptor,
)


class UIComponentMapper:
    """Mapper for UI component entities and DTOs."""

    @staticmethod
    def entity_to_dto(entity: UIComponentEntity) -> UIComponentDTO:
        """Convert UI component entity to DTO.

        Args:
            entity: The UI component entity.

        Returns:
            UIComponentDTO: The UI component DTO.
        """
        return UIComponentDTO(
            component_id=str(entity.component_id),
            component_type=entity.component_type.value,
            props=entity.props,
            merge=entity.merge,
        )

    @staticmethod
    def dto_to_entity(dto: UIComponentDTO) -> UIComponentEntity:
        """Convert UI component DTO to entity.

        Args:
            dto: The UI component DTO.

        Returns:
            UIComponentEntity: The UI component entity.
        """
        from agentx.domain.entities.enums import UIComponentType

        return UIComponentEntity(
            component_id=UUID(dto.component_id),
            component_type=UIComponentType(dto.component_type),
            props=dto.props,
            session_id=UUID("00000000-0000-0000-0000-000000000000"),  # Placeholder
            merge=dto.merge,
        )

    @staticmethod
    def descriptor_to_entity(
        descriptor: BaseUIDescriptor, session_id: UUID
    ) -> UIComponentEntity:
        """Convert UI descriptor to entity.

        Args:
            descriptor: The UI descriptor.
            session_id: The session identifier.

        Returns:
            UIComponentEntity: The UI component entity.
        """
        return UIComponentEntity(
            component_id=descriptor.descriptor_id,
            component_type=descriptor.component_type,
            props=descriptor.props,
            session_id=session_id,
            merge=False,
        )

    @staticmethod
    def descriptor_to_dto(descriptor: BaseUIDescriptor) -> UIComponentDTO:
        """Convert UI descriptor directly to DTO.

        Args:
            descriptor: The UI descriptor.

        Returns:
            UIComponentDTO: The UI component DTO.
        """
        return UIComponentDTO(
            component_id=str(descriptor.descriptor_id),
            component_type=descriptor.component_type.value,
            props=descriptor.props,
            merge=False,
        )

    @staticmethod
    def create_markdown_dto(content: str) -> MarkdownComponentDTO:
        """Create a markdown component DTO.

        Args:
            content: Markdown content.

        Returns:
            MarkdownComponentDTO: The markdown component DTO.
        """
        return MarkdownComponentDTO(
            component_id="generated",
            component_type="markdown",
            props={"content": content, "format": "markdown"},
            merge=False,
        )

    @staticmethod
    def create_card_dto(title: str, content: str) -> CardComponentDTO:
        """Create a card component DTO.

        Args:
            title: Card title.
            content: Card content.

        Returns:
            CardComponentDTO: The card component DTO.
        """
        return CardComponentDTO(
            component_id="generated",
            component_type="card",
            props={"title": title, "content": content, "actions": []},
            merge=False,
        )
