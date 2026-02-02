"""Redis serialization utilities for session data."""

from datetime import datetime
from uuid import UUID

from agentx.domain.entities.agent_session import AgentSessionEntity, SHA256Hash
from agentx.domain.entities.enums import SessionState


class RedisSerialization:
    """Handles serialization and deserialization of session data."""

    @staticmethod
    def session_key(session_id: UUID) -> str:
        """Generate Redis key for session.

        Args:
            session_id: The session identifier.

        Returns:
            str: Redis key string.
        """
        return f"session:{session_id}"

    @staticmethod
    def user_key(user_id: str) -> str:
        """Generate Redis key for user sessions set.

        Args:
            user_id: The user identifier.

        Returns:
            str: Redis key string.
        """
        return f"user_sessions:{user_id}"

    @staticmethod
    def serialize(session: AgentSessionEntity) -> dict:
        """Serialize session entity to dict.

        Args:
            session: The session entity to serialize.

        Returns:
            dict: Serialized session data.
        """
        return {
            "session_id": str(session.session_id),
            "user_id": session.user_id.value,
            "state": session.state.value,
            "created_at": session.created_at.isoformat(),
            "modified_at": session.modified_at.isoformat(),
            "last_activity_at": session.last_activity_at.isoformat(),
            "current_reasoning_step": session.current_reasoning_step,
            "total_tool_calls": session.total_tool_calls,
        }

    @staticmethod
    def deserialize(data: dict) -> AgentSessionEntity:
        """Deserialize dict to AgentSessionEntity.

        Args:
            data: Serialized session data.

        Returns:
            AgentSessionEntity: Deserialized session entity.
        """
        return AgentSessionEntity(
            session_id=UUID(data["session_id"]),
            user_id=SHA256Hash(data["user_id"]),
            state=SessionState(data["state"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            modified_at=datetime.fromisoformat(data["modified_at"]),
            last_activity_at=datetime.fromisoformat(data["last_activity_at"]),
            current_reasoning_step=data["current_reasoning_step"],
            total_tool_calls=data["total_tool_calls"],
        )
