# =============================================================================
# AGENTX Master Agent - Factory
# =============================================================================
# Factory functions and streaming execution for MasterAgent
# =============================================================================

from typing import TYPE_CHECKING, Callable, Optional

if TYPE_CHECKING:
    from services.master_agent.master_agent import MasterAgent


def create_master_agent(
    widget_callback: Optional[Callable] = None,
    qa_callback: Optional[Callable] = None,
) -> "MasterAgent":
    """Factory function to create a MasterAgent instance.

    Args:
        widget_callback: Async callback for widget delivery
        qa_callback: Async callback for QA progress updates

    Returns:
        Configured MasterAgent instance
    """
    # Import here to avoid circular dependency
    from services.master_agent.master_agent import MasterAgent

    return MasterAgent(
        widget_callback=widget_callback,
        qa_callback=qa_callback,
    )


# Export StreamingExecution for use in master_agent.py
from services.master_agent.factory.streaming import StreamingExecution  # noqa: E402

__all__ = ["create_master_agent", "StreamingExecution"]
