"""Core configuration and dependency injection.

This module contains the foundational configuration and DI setup
for Real AgentX v0.1.
"""

from agentx.core.config import Settings, get_settings, settings
from agentx.core.dependencies import (
    get_agent_session_repository,
    get_redis_session_adapter,
    get_sqlite_session_adapter,
    reset_dependencies,
)

__all__ = [
    "Settings",
    "get_settings",
    "settings",
    "get_agent_session_repository",
    "get_redis_session_adapter",
    "get_sqlite_session_adapter",
    "reset_dependencies",
]
