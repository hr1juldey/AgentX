"""UI component repository interface.

Abstract base class for UI component persistence.
"""

from abc import ABC, abstractmethod
from uuid import UUID

from agentx.domain.entities.ui_component import UIComponentEntity


class UIComponentRepository(ABC):
    """Repository interface for UI component persistence.

    Defines the contract for UI component storage operations.
    """

    @abstractmethod
    async def save(self, component: UIComponentEntity) -> None:
        """Save a UI component to storage.

        Args:
            component: The UI component entity to save.
        """
        pass

    @abstractmethod
    async def find_by_session(self, session_id: UUID) -> list[UIComponentEntity]:
        """Find all UI components for a session.

        Args:
            session_id: The session identifier.

        Returns:
            list[UIComponentEntity]: List of UI components.
        """
        pass

    @abstractmethod
    async def find_recent(
        self, session_id: UUID, limit: int = 10
    ) -> list[UIComponentEntity]:
        """Find recent UI components for a session.

        Args:
            session_id: The session identifier.
            limit: Maximum number of components to return.

        Returns:
            list[UIComponentEntity]: List of recent UI components.
        """
        pass

    @abstractmethod
    async def delete_by_session(self, session_id: UUID) -> None:
        """Delete all UI components for a session.

        Args:
            session_id: The session identifier.
        """
        pass
