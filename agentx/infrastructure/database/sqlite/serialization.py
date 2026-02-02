"""SQLite serialization utilities.

Converts between session entities and database rows.
"""

import sqlite3
from datetime import datetime
from typing import Any
from uuid import UUID

from agentx.domain.entities.agent_session import (
    AgentSessionEntity,
    SHA256Hash,
)
from agentx.domain.entities.enums import SessionState


def serialize_session(session: AgentSessionEntity) -> tuple[Any, ...]:
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


def deserialize_session(row: sqlite3.Row) -> AgentSessionEntity:
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
