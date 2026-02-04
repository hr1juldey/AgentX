"""DSPy signature for conversational interactions."""

import dspy


class ConversationSignature(dspy.Signature):
    """Signature for natural dialogue with conversation history.

    This signature enables the agent to maintain context across multiple
    conversation turns using DSPy's native History field.
    """

    question: str = dspy.InputField(desc="User's question or input")
    history: dspy.History = dspy.InputField(desc="Conversation history for context")
    answer: str = dspy.OutputField(desc="Agent's response")
