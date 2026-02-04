"""Conversation Agent - differentiated stem cell for conversational tasks."""

import dspy

from agentx.application.agents.stem_cell import StemCellAgent
from agentx.domain.signatures.conversation_signature import ConversationSignature


class ConversationAgent(StemCellAgent):
    """Conversation agent for natural dialogue tasks.

    Differentiated from StemCellAgent via ConversationSignature,
    which includes DSPy History field for conversation context.
    """

    def __init__(self, user_id: str) -> None:
        """Initialize the conversation agent.

        Args:
            user_id: User identifier for memory isolation
        """
        super().__init__(user_id=user_id, signature=ConversationSignature)  # type: ignore[arg-type]

    def get_history(self) -> dspy.History:
        """Get the conversation history.

        Returns:
            dspy.History instance containing conversation turns
        """
        return self._history

    def set_history(self, history: dspy.History) -> None:
        """Set the conversation history.

        Args:
            history: New dspy.History instance to use
        """
        self._history = history
