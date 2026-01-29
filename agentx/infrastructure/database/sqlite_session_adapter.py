"""SQLite session adapter implementation.

Implements AgentSessionRepository using SQLite for persistent storage.
Provides backup/failover for Redis adapter.
"""

import sqlite3
from datetime import datetime
from typing import Any
from uuid import UUID

from agentx.core.config import get_settings
from agentx.domain.entities.agent_session import AgentSessionEntity, SHA256Hash
from agentx.domain.entities.enums import SessionState
from agentx.domain.repositories.agent_session_repository import (
    AgentSessionRepository,
)


class SQLiteSessionAdapter(AgentSessionRepository):
    """SQLite implementation of session repository.

    Provides persistent, queryable session storage.
    """

    def __init__(self) -> None:
        """Initialize SQLite connection and create schema."""
        settings = get_settings()
        self._db_path = settings.database.sqlite_path
        self._conn: sqlite3.Connection | None = None
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database schema."""
        # Ensure data directory exists
        self._db_path.parent.mkdir(parents=True, exist_ok=True)

        conn = self._get_connection()
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                state TEXT NOT NULL,
                created_at TEXT NOT NULL,
                modified_at TEXT NOT NULL,
                last_activity_at TEXT NOT NULL,
                current_reasoning_step INTEGER DEFAULT 0,
                total_tool_calls INTEGER DEFAULT 0
            )
        """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_user_id ON sessions(user_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_state ON sessions(state)")
        conn.commit()

    def _get_connection(self) -> sqlite3.Connection:
        """Get or create SQLite connection.

        Returns:
            sqlite3.Connection: The SQLite connection.
        """
        if self._conn is None:
            self._conn = sqlite3.connect(str(self._db_path))
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def _serialize(self, session: AgentSessionEntity) -> tuple[Any, ...]:
        """Serialize session to database row.

        Args:
            session: The session entity.

        Returns:
            tuple: Database row values.
        """
        return (
            str(session.session_id),
            session.user_id.value,
            session.state.value,
            session.created_at.isoformat(),
            session.modified_at.isoformat(),
            session.last_activity_at.isoformat(),
            session.current_reasoning_step,
            session.total_tool_calls,
        )

    def _deserialize(self, row: sqlite3.Row) -> AgentSessionEntity:
        """Deserialize database row to session.

        Args:
            row: Database row.

        Returns:
            AgentSessionEntity: Deserialized session entity.
        """
        return AgentSessionEntity(
            session_id=UUID(row["session_id"]),
            user_id=SHA256Hash(row["user_id"]),
            state=SessionState(row["state"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            modified_at=datetime.fromisoformat(row["modified_at"]),
            last_activity_at=datetime.fromisoformat(row["last_activity_at"]),
            current_reasoning_step=row["current_reasoning_step"],
            total_tool_calls=row["total_tool_calls"],
        )

    async def save(self, session: AgentSessionEntity) -> None:
        """Save session to SQLite.

        Args:
            session: The session entity to save.
        """
        conn = self._get_connection()
        conn.execute(
            """
            INSERT OR REPLACE INTO sessions
            (session_id, user_id, state, created_at, modified_at,
             last_activity_at, current_reasoning_step, total_tool_calls)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            self._serialize(session),
        )
        conn.commit()

    async def find_by_id(self, session_id: UUID) -> AgentSessionEntity | None:
        """Find session by ID.

        Args:
            session_id: The session identifier.

        Returns:
            AgentSessionEntity | None: The session if found.
        """
        conn = self._get_connection()
        cursor = conn.execute(
            "SELECT * FROM sessions WHERE session_id = ?", (str(session_id),)
        )
        row = cursor.fetchone()

        if not row:
            return None

        return self._deserialize(row)

    async def find_by_user(self, user_id: str) -> list[AgentSessionEntity]:
        """Find all sessions for user.

        Args:
            user_id: The user identifier.

        Returns:
            list[AgentSessionEntity]: List of user sessions.
        """
        conn = self._get_connection()
        cursor = conn.execute("SELECT * FROM sessions WHERE user_id = ?", (user_id,))
        rows = cursor.fetchall()

        return [self._deserialize(row) for row in rows]

    async def delete(self, session_id: UUID) -> None:
        """Delete session from SQLite.

        Args:
            session_id: The session identifier.
        """
        conn = self._get_connection()
        conn.execute("DELETE FROM sessions WHERE session_id = ?", (str(session_id),))
        conn.commit()

    async def find_active_sessions(self) -> list[AgentSessionEntity]:
        """Find all active sessions.

        Returns:
            list[AgentSessionEntity]: List of active sessions.
        """
        conn = self._get_connection()
        cursor = conn.execute(
            "SELECT * FROM sessions WHERE state = ?", (SessionState.ACTIVE.value,)
        )
        rows = cursor.fetchall()

        return [self._deserialize(row) for row in rows]
