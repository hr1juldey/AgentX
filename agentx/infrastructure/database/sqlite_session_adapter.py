"""SQLite session adapter implementation.

Implements AgentSessionRepository using SQLite for persistent storage.
Provides backup/failover for Redis adapter.

This is a facade for backward compatibility. Actual implementation has been
moved to the sqlite/ subdirectory.
"""

from agentx.infrastructure.database.sqlite import SQLiteSessionAdapter

__all__ = ["SQLiteSessionAdapter"]
