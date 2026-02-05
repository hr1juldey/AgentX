"""Conversation Agent - differentiated stem cell for conversational tasks."""

from __future__ import annotations

import dspy

from agentx.application.agents.stem_cell import StemCellAgent
from agentx.domain.signatures.conversation_signature import ConversationSignature


def create_streaming_agent(agent: ConversationAgent) -> object:
    """Create a streaming wrapper for a ConversationAgent.

    Wraps the agent with dspy.streamify to enable token streaming.

    Args:
        agent: The ConversationAgent to wrap

    Returns:
        Async generator that yields StreamResponse tokens and final Prediction
    """
    # Create StreamListener for the 'answer' field
    stream_listeners = [
        dspy.streaming.StreamListener(signature_field_name="answer", allow_reuse=True)
    ]

    # Wrap agent with streamify
    return dspy.streamify(
        agent,
        stream_listeners=stream_listeners,
        status_message_provider=None,  # No custom status messages for now
    )


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
