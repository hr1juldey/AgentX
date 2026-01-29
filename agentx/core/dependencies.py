"""Dependency injection configuration for Real AgentX v0.1.

Provides singleton instances of core services following the getter pattern
from mimicus. All dependencies are lazy-loaded.
"""

import dspy

from agentx.core.config import get_settings
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agentx.domain.repositories.agent_session_repository import (
        AgentSessionRepository,
    )
    from agentx.infrastructure.database.redis_session_adapter import (
        RedisSessionAdapter,
    )
    from agentx.infrastructure.database.sqlite_session_adapter import (
        SQLiteSessionAdapter,
    )


# Lazy-loaded singletons
_redis_adapter: "RedisSessionAdapter | None" = None
_sqlite_adapter: "SQLiteSessionAdapter | None" = None
_agent_session_repo: "AgentSessionRepository | None" = None
_dspy_configured: bool = False


def _configure_dspy() -> None:
    """Configure DSPy with Ollama LM.

    Uses settings from config.py. Must be called before any DSPy agent usage.
    """
    global _dspy_configured
    if _dspy_configured:
        return

    settings = get_settings()

    # Configure DSPy with Ollama
    # Note: DSPy uses "ollama_chat/" prefix for Ollama chat models
    # Ollama requires api_key="" (empty string)
    lm = dspy.LM(
        model=f"ollama_chat/{settings.llm.model}",
        api_base=settings.llm.api_base,
        api_key="",  # Ollama doesn't require API key, but DSPy needs empty string
        temperature=settings.llm.temperature,
        max_tokens=settings.llm.max_tokens,
    )
    dspy.configure(lm=lm)
    _dspy_configured = True


def ensure_dspy_configured() -> None:
    """Ensure DSPy is configured with Ollama LM.

    This should be called before any DSPy agent usage.
    """
    _configure_dspy()


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
        adapter = get_redis_session_adapter()
        _agent_session_repo = adapter
    return _agent_session_repo


def reset_dependencies() -> None:
    """Reset all dependency singletons.

    Useful for testing or clearing state.
    """
    global _redis_adapter, _sqlite_adapter, _agent_session_repo, _dspy_configured
    _redis_adapter = None
    _sqlite_adapter = None
    _agent_session_repo = None
    _dspy_configured = False
