"""SQLite session adapter components.

Provides persistent session storage using SQLite.
"""

from agentx.infrastructure.database.sqlite.repository import (
    SQLiteSessionAdapter,
)

__all__ = ["SQLiteSessionAdapter"]
