"""Application service dependencies.

Provides conversation state manager and other application services.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agentx.application.use_cases.conversation_state_manager import (
        ConversationStateManager,
    )


# Global singleton states (type: ignore needed for string forward refs)
_conversation_state_manager: "ConversationStateManager | None" = None  # type: ignore[name-defined]


def get_conversation_state_manager() -> "ConversationStateManager":
    """Get the conversation state manager singleton.

    Returns:
        ConversationStateManager: The conversation state manager instance.
    """
    global _conversation_state_manager
    if _conversation_state_manager is None:
        from agentx.application.use_cases.conversation_state_manager import (
            ConversationStateManager,
        )

        _conversation_state_manager = ConversationStateManager()
    return _conversation_state_manager


def reset_application_dependencies() -> None:
    """Reset application dependency singletons.

    Useful for testing or clearing state.
    """
    global _conversation_state_manager
    _conversation_state_manager = None
