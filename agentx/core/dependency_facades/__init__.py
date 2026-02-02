"""Dependency injection facades for Real AgentX v0.1.

This module provides singleton instances of core services.
All dependencies are lazy-loaded and split by domain.
"""

# Re-export all dependency functions for backward compatibility
from agentx.core.dependency_facades.application import (
    get_conversation_state_manager,
    reset_application_dependencies,
)
from agentx.core.dependency_facades.database import (
    get_agent_session_repository,
    get_redis_session_adapter,
    get_sqlite_session_adapter,
    reset_database_dependencies,
)
from agentx.core.dependency_facades.dspy import (
    configure_dspy,
    ensure_dspy_configured,
    reset_dspy,
)
from agentx.core.dependency_facades.voice import (
    get_text_stream_handler,
    get_voice_gateway_service,
    reset_voice_dependencies,
)

__all__ = [
    # DSPy
    "configure_dspy",
    "ensure_dspy_configured",
    "reset_dspy",
    # Database
    "get_redis_session_adapter",
    "get_sqlite_session_adapter",
    "get_agent_session_repository",
    "reset_database_dependencies",
    # Application
    "get_conversation_state_manager",
    "reset_application_dependencies",
    # Voice
    "get_text_stream_handler",
    "get_voice_gateway_service",
    "reset_voice_dependencies",
]
