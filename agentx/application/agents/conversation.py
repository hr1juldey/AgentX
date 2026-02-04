"""Conversation Agent - differentiated stem cell for conversational tasks."""

from agentx.application.agents.stem_cell import StemCellAgent


class ConversationAgent(StemCellAgent):
    """Conversation agent for natural dialogue tasks.

    Uses the default pluripotent signature with conversational instructions.
    """

    def __init__(self, user_id: str) -> None:
        """Initialize the conversation agent.

        Args:
            user_id: User identifier for memory isolation
        """
        # Use default pluripotent signature (from StemCellAgent)
        # with conversational instructions
        super().__init__(user_id=user_id)
