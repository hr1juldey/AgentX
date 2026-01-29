"""Manage session use case.

Orchestrates session management workflow (pause/resume/close).
Following the use case pattern from mimicus.
"""

from agentx.application.dtos.session_dtos import (
    CloseSessionCommand,
    PauseSessionCommand,
    ResumeSessionCommand,
    SessionResponseDTO,
)
from agentx.application.mappers.agent_session_mapper import AgentSessionMapper
from agentx.core.dependencies import get_agent_session_repository
from agentx.domain.entities.enums import SessionState


class ManageSessionUseCase:
    """Use case for managing sessions.

    Orchestrates session management workflow:
    1. Pause: ACTIVE -> PAUSED
    2. Resume: PAUSED -> ACTIVE
    3. Close: ACTIVE/PAUSED -> CLOSED
    """

    def __init__(self) -> None:
        """Initialize the use case with dependencies."""
        self._session_repository = get_agent_session_repository()
        self._session_mapper = AgentSessionMapper()

    async def pause(self, command: PauseSessionCommand) -> SessionResponseDTO:
        """Pause an active session.

        Args:
            command: The pause session command DTO.

        Returns:
            SessionResponseDTO: The updated session DTO.

        Raises:
            ValueError: If session is not in ACTIVE state.
        """
        # Step 1: Retrieve session
        session = await self._session_repository.find_by_id(command.session_id)
        if session is None:
            msg = f"Session {command.session_id} not found"
            raise ValueError(msg)

        # Step 2: Check state
        if session.state != SessionState.ACTIVE:
            msg = f"Cannot pause session in {session.state} state"
            raise ValueError(msg)

        # Step 3: Transition to PAUSED
        session.pause()
        await self._session_repository.save(session)

        # Step 4: Map to response DTO
        return self._session_mapper.entity_to_dto(session)

    async def resume(self, command: ResumeSessionCommand) -> SessionResponseDTO:
        """Resume a paused session.

        Args:
            command: The resume session command DTO.

        Returns:
            SessionResponseDTO: The updated session DTO.

        Raises:
            ValueError: If session is not in PAUSED state.
        """
        # Step 1: Retrieve session
        session = await self._session_repository.find_by_id(command.session_id)
        if session is None:
            msg = f"Session {command.session_id} not found"
            raise ValueError(msg)

        # Step 2: Check state
        if session.state != SessionState.PAUSED:
            msg = f"Cannot resume session in {session.state} state"
            raise ValueError(msg)

        # Step 3: Transition to ACTIVE
        session.activate()
        await self._session_repository.save(session)

        # Step 4: Map to response DTO
        return self._session_mapper.entity_to_dto(session)

    async def close(self, command: CloseSessionCommand) -> SessionResponseDTO:
        """Close an active or paused session.

        Args:
            command: The close session command DTO.

        Returns:
            SessionResponseDTO: The updated session DTO.

        Raises:
            ValueError: If session is not in ACTIVE or PAUSED state.
        """
        # Step 1: Retrieve session
        session = await self._session_repository.find_by_id(command.session_id)
        if session is None:
            msg = f"Session {command.session_id} not found"
            raise ValueError(msg)

        # Step 2: Check state
        if session.state not in (SessionState.ACTIVE, SessionState.PAUSED):
            msg = f"Cannot close session in {session.state} state"
            raise ValueError(msg)

        # Step 3: Transition to CLOSED
        session.close()
        await self._session_repository.save(session)

        # Step 4: Map to response DTO
        return self._session_mapper.entity_to_dto(session)
