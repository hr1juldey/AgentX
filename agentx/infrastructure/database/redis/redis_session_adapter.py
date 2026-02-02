"""Redis session adapter implementation.

Implements AgentSessionRepository using Redis for fast session storage.
"""

from uuid import UUID


from agentx.domain.entities.agent_session import AgentSessionEntity
from agentx.domain.entities.enums import SessionState
from agentx.domain.repositories.agent_session_repository import (
    AgentSessionRepository,
)
from agentx.infrastructure.database.redis.connection import RedisConnectionManager
from agentx.infrastructure.database.redis.serialization import RedisSerialization


class RedisSessionAdapter(AgentSessionRepository):
    """Redis implementation of session repository.

    Provides fast, persistent session storage with TTL support.
    """

    def __init__(self) -> None:
        """Initialize Redis connection."""
        self._conn = RedisConnectionManager()
        self._serial = RedisSerialization()

    async def save(self, session: AgentSessionEntity) -> None:
        """Save session to Redis.

        Args:
            session: The session entity to save.
        """
        client = await self._conn.get_client()
        key = self._serial.session_key(session.session_id)
        data = self._serial.serialize(session)

        # Save session data with TTL
        await client.setex(key, self._conn.ttl, __import__("json").dumps(data))

        # Add to user's session set
        user_key = self._serial.user_key(data["user_id"])
        await client.sadd(user_key, str(session.session_id))

    async def find_by_id(self, session_id: UUID) -> AgentSessionEntity | None:
        """Find session by ID.

        Args:
            session_id: The session identifier.

        Returns:
            AgentSessionEntity | None: The session if found.
        """
        client = await self._conn.get_client()
        key = self._serial.session_key(session_id)

        data = await client.get(key)
        if not data:
            return None

        return self._serial.deserialize(__import__("json").loads(data))

    async def find_by_user(self, user_id: str) -> list[AgentSessionEntity]:
        """Find all sessions for user.

        Args:
            user_id: The user identifier.

        Returns:
            list[AgentSessionEntity]: List of user sessions.
        """
        client = await self._conn.get_client()
        user_key = self._serial.user_key(user_id)

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
        client = await self._conn.get_client()
        key = self._serial.session_key(session_id)

        # Get session data for cleanup
        session = await self.find_by_id(session_id)
        if session:
            user_key = self._serial.user_key(session.user_id.value)
            await client.srem(user_key, str(session_id))

        await client.delete(key)

    async def find_active_sessions(self) -> list[AgentSessionEntity]:
        """Find all active sessions.

        Returns:
            list[AgentSessionEntity]: List of active sessions.
        """
        # Scan all session keys
        client = await self._conn.get_client()
        pattern = "session:*"
        sessions = []

        async for key in client.scan_iter(match=pattern):
            data = await client.get(key)
            if data:
                session = self._serial.deserialize(__import__("json").loads(data))
                if session and session.state == SessionState.ACTIVE:
                    sessions.append(session)

        return sessions
