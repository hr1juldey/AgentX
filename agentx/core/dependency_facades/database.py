"""Database-related dependencies.

Provides session adapters, repositories, and vector store.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agentx.domain.repositories.agent_session_repository import (
        AgentSessionRepository,
    )
    from agentx.infrastructure.database.qdrant.qdrant_vector_store import (
        QdrantVectorStore,
    )
    from agentx.infrastructure.database.redis_session_adapter import (
        RedisSessionAdapter,
    )
    from agentx.infrastructure.database.sqlite_session_adapter import (
        SQLiteSessionAdapter,
    )


# Global singleton states
_redis_adapter: "RedisSessionAdapter | None" = None
_sqlite_adapter: "SQLiteSessionAdapter | None" = None
_agent_session_repo: "AgentSessionRepository | None" = None
_vector_store: "QdrantVectorStore | None" = None


def get_redis_session_adapter() -> "RedisSessionAdapter":
    """Get the Redis session adapter singleton.

    Returns:
        RedisSessionAdapter: The Redis adapter instance.
    """
    global _redis_adapter
    if _redis_adapter is None:
        from agentx.infrastructure.database.redis_session_adapter import (
            RedisSessionAdapter,
        )

        _redis_adapter = RedisSessionAdapter()
    return _redis_adapter


def get_sqlite_session_adapter() -> "SQLiteSessionAdapter":
    """Get the SQLite session adapter singleton.

    Returns:
        SQLiteSessionAdapter: The SQLite adapter instance.
    """
    global _sqlite_adapter
    if _sqlite_adapter is None:
        from agentx.infrastructure.database.sqlite_session_adapter import (
            SQLiteSessionAdapter,
        )

        _sqlite_adapter = SQLiteSessionAdapter()
    return _sqlite_adapter


def get_agent_session_repository() -> "AgentSessionRepository":
    """Get the agent session repository singleton.

    Returns:
        AgentSessionRepository: The session repository instance.
    """
    global _agent_session_repo
    if _agent_session_repo is None:
        adapter = get_redis_session_adapter()  # type: ignore[valid-type]
        _agent_session_repo = adapter
    return _agent_session_repo


def get_vector_store() -> "QdrantVectorStore":
    """Get the Qdrant vector store singleton.

    Returns:
        QdrantVectorStore: The vector store instance.
    """
    global _vector_store
    if _vector_store is None:
        from agentx.infrastructure.database.qdrant.qdrant_vector_store import (
            QdrantVectorStore,
        )

        _vector_store = QdrantVectorStore()
    return _vector_store


def reset_database_dependencies() -> None:
    """Reset database dependency singletons.

    Useful for testing or clearing state.
    """
    global _redis_adapter, _sqlite_adapter, _agent_session_repo, _vector_store
    _redis_adapter = None
    _sqlite_adapter = None
    _agent_session_repo = None
    _vector_store = None
