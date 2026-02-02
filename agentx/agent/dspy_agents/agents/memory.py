"""Memory agent for RAG operations.

Retrieves relevant context from memory stores.
"""

import dspy

from agentx.agent.dspy_signatures.main_signatures import MemorySignature


class MemoryAgent(dspy.Module):
    """Memory agent for RAG operations.

    Retrieves relevant context from episodic, semantic, and procedural memory.
    """

    def __init__(self) -> None:
        """Initialize the memory agent."""
        super().__init__()
        self.retrieve = dspy.Predict(MemorySignature)

    def forward(self, query: str, session_id: str) -> dspy.Prediction:
        """Retrieve relevant context from memory.

        Args:
            query: User's question or request.
            session_id: Current session identifier.

        Returns:
            dspy.Prediction: Retrieved context with source references.
        """
        result = self.retrieve(query=query, session_id=session_id)
        return dspy.Prediction(
            context=result.context,  # type: ignore[attr-defined]
            sources=result.sources,  # type: ignore[attr-defined]
        )
