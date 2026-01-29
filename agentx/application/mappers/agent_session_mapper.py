"""Agent session mapper for Real AgentX v0.1.

Converts between domain entities and DTOs.
Following the mapper pattern from mimicus.
"""

from uuid import UUID

from agentx.application.dtos.agent_dtos import SessionStatusDTO
from agentx.domain.entities.agent_session import AgentSessionEntity


class AgentSessionMapper:
    """Mapper for agent session entities and DTOs."""

    @staticmethod
    def entity_to_dto(entity: AgentSessionEntity) -> SessionStatusDTO:
        """Convert session entity to DTO.

        Args:
            entity: The session entity.

        Returns:
            SessionStatusDTO: The session status DTO.
        """
        return SessionStatusDTO(
            session_id=str(entity.session_id),
            state=entity.state.value,
            created_at=entity.created_at,
            last_activity_at=entity.last_activity_at,
            current_reasoning_step=entity.current_reasoning_step,
            total_tool_calls=entity.total_tool_calls,
        )

    @staticmethod
    def dto_to_entity(dto: SessionStatusDTO) -> AgentSessionEntity:
        """Convert session DTO to entity.

        Note: This is a simplified conversion. In practice, you'd need
        to reconstruct the full entity with all fields.

        Args:
            dto: The session status DTO.

        Returns:
            AgentSessionEntity: The session entity.
        """
        from agentx.domain.entities.agent_session import SHA256Hash
        from agentx.domain.entities.enums import SessionState

        # This is a placeholder - real implementation would need
        # the user_id which isn't in the DTO
        return AgentSessionEntity(
            session_id=UUID(dto.session_id),
            user_id=SHA256Hash.from_string("reconstructed"),  # Placeholder
            state=SessionState(dto.state),
            created_at=dto.created_at,
            modified_at=dto.last_activity_at,
            last_activity_at=dto.last_activity_at,
            current_reasoning_step=dto.current_reasoning_step,
            total_tool_calls=dto.total_tool_calls,
        )
