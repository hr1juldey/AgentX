"""Create session use case.

Orchestrates session creation workflow.
Following the use case pattern from mimicus.
"""

from agentx.application.dtos.agent_dtos import SessionStatusDTO
from agentx.application.dtos.session_dtos import CreateSessionCommand
from agentx.application.mappers.agent_session_mapper import AgentSessionMapper
from agentx.core.dependencies import get_agent_session_repository
from agentx.domain.entities.agent_session import AgentSessionEntity, SHA256Hash


class CreateSessionUseCase:
    """Use case for creating new sessions.

    Orchestrates session creation workflow:
    1. Hash user_id to SHA256Hash
    2. Create new AgentSessionEntity
    3. Persist to repository
    4. Return SessionResponseDTO
    """

    def __init__(self) -> None:
        """Initialize the use case with dependencies."""
        self._session_repository = get_agent_session_repository()
        self._session_mapper = AgentSessionMapper()

    async def execute(self, command: CreateSessionCommand) -> SessionStatusDTO:
        """Create a new session.

        Args:
            command: The create session command DTO.

        Returns:
            SessionStatusDTO: The created session DTO.
        """
        # Step 1: Hash user_id to SHA256Hash
        user_hash = SHA256Hash.from_string(command.user_id)

        # Step 2: Create new AgentSessionEntity
        session = AgentSessionEntity.create(user_hash)

        # Step 3: Persist to repository
        await self._session_repository.save(session)

        # Step 4: Map to response DTO
        return self._session_mapper.entity_to_dto(session)
