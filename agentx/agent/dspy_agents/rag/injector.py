"""RAG context injection decision module.

Phase 3 Fix: Extracted from RAGContextGenerator for SRP compliance.
"""

import dspy

from agentx.agent.dspy_signatures.rag_signatures import ContextInjectionSignature
from agentx.agent.tools.common.dspy_helpers import safe_extract


class ContextInjector:
    """Decides whether to inject retrieved context into the main agent.

    Phase 3 Fix: Extracted from RAGContextGenerator.
    Single Responsibility: Decide and filter context injection.
    """

    def __init__(self) -> None:
        """Initialize the injector with DSPy predictor."""
        self._decider = dspy.Predict(ContextInjectionSignature)

    def decide_and_filter(
        self,
        query: str,
        retrieved_context: str,
    ) -> dict[str, object]:
        """Decide whether to inject retrieved context and filter it.

        Args:
            query: User query
            retrieved_context: Retrieved context from RAG

        Returns:
            dict with should_inject, injection_rationale, filtered_context
        """
        decision = self._decider(
            query=query,
            retrieved_context=retrieved_context,
        )

        should_inject = safe_extract(decision, "should_inject", False)
        injection_rationale = safe_extract(decision, "injection_rationale", "")
        filtered_context = safe_extract(decision, "filtered_context", "")

        return {
            "should_inject": should_inject,
            "injection_rationale": injection_rationale,
            "filtered_context": filtered_context,
        }


__all__ = ["ContextInjector"]
