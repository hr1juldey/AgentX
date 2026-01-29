"""Agent session repository interface.

Abstract base class defining the contract for session persistence.
Following the repository pattern from mimicus.
"""

from abc import ABC, abstractmethod
from uuid import UUID

from agentx.domain.entities.agent_session import AgentSessionEntity


class AgentSessionRepository(ABC):
    """Repository interface for agent session persistence.

    Defines the contract for session storage operations.
    Implementations are in infrastructure/database/.
    """

    @abstractmethod
    async def save(self, session: AgentSessionEntity) -> None:
        """Save a session to storage.

        Args:
            session: The session entity to save.
        """
        pass

    @abstractmethod
    async def find_by_id(self, session_id: UUID) -> AgentSessionEntity | None:
        """Find a session by its ID.

        Args:
            session_id: The session identifier.

        Returns:
            AgentSessionEntity | None: The session if found, None otherwise.
        """
        pass

    @abstractmethod
    async def find_by_user(self, user_id: str) -> list[AgentSessionEntity]:
        """Find all sessions for a user.

        Args:
            user_id: The user identifier (SHA-256 hash).

        Returns:
            list[AgentSessionEntity]: List of user sessions.
        """
        pass

    @abstractmethod
    async def delete(self, session_id: UUID) -> None:
        """Delete a session from storage.

        Args:
            session_id: The session identifier.
        """
        pass

    @abstractmethod
    async def find_active_sessions(self) -> list[AgentSessionEntity]:
        """Find all currently active sessions.

        Returns:
            list[AgentSessionEntity]: List of active sessions.
        """
        pass
