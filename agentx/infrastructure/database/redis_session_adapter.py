"""Redis session adapter implementation.

Implements AgentSessionRepository using Redis for fast session storage.
"""

from datetime import datetime
import json
from uuid import UUID

import redis.asyncio as redis

from agentx.core.config import get_settings
from agentx.domain.entities.agent_session import AgentSessionEntity
from agentx.domain.entities.enums import SessionState
from agentx.domain.repositories.agent_session_repository import (
    AgentSessionRepository,
)


class RedisSessionAdapter(AgentSessionRepository):
    """Redis implementation of session repository.

    Provides fast, persistent session storage with TTL support.
    """

    def __init__(self) -> None:
        """Initialize Redis connection."""
        settings = get_settings()
        self._client: redis.Redis | None = None
        self._url = settings.database.redis_url
        self._ttl = 86400  # 24 hours default

    async def _get_client(self) -> redis.Redis:
        """Get or create Redis client.

        Returns:
            redis.Redis: The Redis client instance.
        """
        if self._client is None:
            self._client = await redis.from_url(
                self._url, encoding="utf-8", decode_responses=True
            )
        return self._client

    def _session_key(self, session_id: UUID) -> str:
        """Generate Redis key for session.

        Args:
            session_id: The session identifier.

        Returns:
            str: Redis key string.
        """
        return f"session:{session_id}"

    def _user_key(self, user_id: str) -> str:
        """Generate Redis key for user sessions set.

        Args:
            user_id: The user identifier.

        Returns:
            str: Redis key string.
        """
        return f"user_sessions:{user_id}"

    async def save(self, session: AgentSessionEntity) -> None:
        """Save session to Redis.

        Args:
            session: The session entity to save.
        """
        client = await self._get_client()
        key = self._session_key(session.session_id)

        # Serialize session to dict
        data = {
            "session_id": str(session.session_id),
            "user_id": session.user_id.value,
            "state": session.state.value,
            "created_at": session.created_at.isoformat(),
            "modified_at": session.modified_at.isoformat(),
            "last_activity_at": session.last_activity_at.isoformat(),
            "current_reasoning_step": session.current_reasoning_step,
            "total_tool_calls": session.total_tool_calls,
        }

        # Save session data with TTL
        await client.setex(key, self._ttl, json.dumps(data))

        # Add to user's session set
        user_key = self._user_key(data["user_id"])
        await client.sadd(user_key, str(session.session_id))

    async def find_by_id(self, session_id: UUID) -> AgentSessionEntity | None:
        """Find session by ID.

        Args:
            session_id: The session identifier.

        Returns:
            AgentSessionEntity | None: The session if found.
        """
        client = await self._get_client()
        key = self._session_key(session_id)

        data = await client.get(key)
        if not data:
            return None

        return self._deserialize(json.loads(data))

    async def find_by_user(self, user_id: str) -> list[AgentSessionEntity]:
        """Find all sessions for user.

        Args:
            user_id: The user identifier.

        Returns:
            list[AgentSessionEntity]: List of user sessions.
        """
        client = await self._get_client()
        user_key = self._user_key(user_id)

        session_ids = await client.smembers(user_key)
        sessions = []

        for session_id in session_ids:
            session = await self.find_by_id(UUID(session_id))
            if session:
                sessions.append(session)

        return sessions

    async def delete(self, session_id: UUID) -> None:
        """Delete session from Redis.

        Args:
            session_id: The session identifier.
        """
        client = await self._get_client()
        key = self._session_key(session_id)

        # Get session data for cleanup
        session = await self.find_by_id(session_id)
        if session:
            user_key = self._session_key(session.user_id.value)
            await client.srem(user_key, str(session_id))

        await client.delete(key)

    async def find_active_sessions(self) -> list[AgentSessionEntity]:
        """Find all active sessions.

        Returns:
            list[AgentSessionEntity]: List of active sessions.
        """
        # Scan all session keys
        client = await self._get_client()
        pattern = "session:*"
        sessions = []

        async for key in client.scan_iter(match=pattern):
            data = await client.get(key)
            if data:
                session = self._deserialize(json.loads(data))
                if session and session.state == SessionState.ACTIVE:
                    sessions.append(session)

        return sessions

    def _deserialize(self, data: dict) -> AgentSessionEntity:
        """Deserialize dict to AgentSessionEntity.

        Args:
            data: Serialized session data.

        Returns:
            AgentSessionEntity: Deserialized session entity.
        """
        from agentx.domain.entities.agent_session import SHA256Hash

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
