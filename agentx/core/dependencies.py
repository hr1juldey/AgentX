"""Dependency injection configuration for Real AgentX v0.1.

This facade maintains backward compatibility with existing imports.
Actual implementation has been moved to the dependency_facades/ subdirectory.

All getter functions are preserved as re-exports for zero breaking changes.
"""

# Re-export all dependency functions for backward compatibility
# 26 downstream files depend on these getters
from agentx.core.dependency_facades import (
    get_agent_session_repository,
    get_conversation_state_manager,
    get_redis_session_adapter,
    get_sqlite_session_adapter,
    get_text_stream_handler,
    get_vector_store,
    get_voice_gateway_service,
)
from agentx.core.dependency_facades.dspy import (
    configure_dspy as _configure_dspy_impl,
    ensure_dspy_configured,
)


# Legacy function name for backward compatibility
def _configure_dspy() -> None:
    """Configure DSPy with Ollama LM (legacy wrapper)."""
    _configure_dspy_impl()


__all__ = [
    "get_redis_session_adapter",
    "get_sqlite_session_adapter",
    "get_agent_session_repository",
    "get_vector_store",
    "ensure_dspy_configured",
    "get_voice_gateway_service",
    "get_conversation_state_manager",
    "get_text_stream_handler",
    "reset_dependencies",
]


def reset_dependencies() -> None:
    """Reset all dependency singletons.

    Useful for testing to ensure clean state between tests.
    """
    from agentx.core.dependency_facades import reset_all_dependencies

    reset_all_dependencies()
