"""SQLite session repository implementation.

Implements AgentSessionRepository using SQLite for persistent storage.
"""

from uuid import UUID

from agentx.core.config import get_settings
from agentx.domain.entities.agent_session import AgentSessionEntity
from agentx.domain.entities.enums import SessionState
from agentx.domain.repositories.agent_session_repository import (
    AgentSessionRepository,
)
from agentx.infrastructure.database.sqlite.connection import (
    SQLiteConnectionManager,
)
from agentx.infrastructure.database.sqlite.serialization import (
    deserialize_session,
    serialize_session,
)


class SQLiteSessionAdapter(AgentSessionRepository):
    """SQLite implementation of session repository.

    Provides persistent, queryable session storage.
    """

    def __init__(self) -> None:
        """Initialize SQLite connection and create schema."""
        settings = get_settings()
        self._conn_manager = SQLiteConnectionManager(settings.database.sqlite_path)

    async def save(self, session: AgentSessionEntity) -> None:
        """Save session to SQLite.

        Args:
            session: The session entity to save.
        """
        conn = self._conn_manager.get_connection()
        conn.execute(
            """
            INSERT OR REPLACE INTO sessions
            (session_id, user_id, state, created_at, modified_at,
             last_activity_at, current_reasoning_step, total_tool_calls)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            serialize_session(session),
        )
        conn.commit()

    async def find_by_id(self, session_id: UUID) -> AgentSessionEntity | None:
        """Find session by ID.

        Args:
            session_id: The session identifier.

        Returns:
            AgentSessionEntity | None: The session if found.
        """
        conn = self._conn_manager.get_connection()
        cursor = conn.execute(
            "SELECT * FROM sessions WHERE session_id = ?", (str(session_id),)
        )
        row = cursor.fetchone()

        if not row:
            return None

        return deserialize_session(row)

    async def find_by_user(self, user_id: str) -> list[AgentSessionEntity]:
        """Find all sessions for user.

        Args:
            user_id: The user identifier.

        Returns:
            list[AgentSessionEntity]: List of user sessions.
        """
        conn = self._conn_manager.get_connection()
        cursor = conn.execute("SELECT * FROM sessions WHERE user_id = ?", (user_id,))
        rows = cursor.fetchall()

        return [deserialize_session(row) for row in rows]

    async def delete(self, session_id: UUID) -> None:
        """Delete session from SQLite.

        Args:
            session_id: The session identifier.
        """
        conn = self._conn_manager.get_connection()
        conn.execute("DELETE FROM sessions WHERE session_id = ?", (str(session_id),))
        conn.commit()

    async def find_active_sessions(self) -> list[AgentSessionEntity]:
        """Find all active sessions.

        Returns:
            list[AgentSessionEntity]: List of active sessions.
        """
        conn = self._conn_manager.get_connection()
        cursor = conn.execute(
            "SELECT * FROM sessions WHERE state = ?", (SessionState.ACTIVE.value,)
        )
        rows = cursor.fetchall()

        return [deserialize_session(row) for row in rows]
