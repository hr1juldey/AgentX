"""RAG specialist agent for context retrieval and injection.

Locked from LLD: agent_runtime.md:582-663

Agentic RAG Pattern:
1. Retrieve relevant memories from vector store (REAL via RealRetriever)
2. Score context quality (high/medium/low based on relevance)
3. Decide whether to inject context
4. Filter and format context for main agent

This is NOT a simple context dump - the agent decides whether to inject.

Phase 3 Fixes:
- Converted async forward() to sync for DSPy compatibility
- Fixed return type from dict[str, Any] to dspy.Prediction
- Split into focused modules (RealRetriever, ContextScorer, ContextInjector)
- Externalized magic numbers (Fraud #5.5)
"""

import dspy
from typing import Any

from agentx.agent.dspy_agents.rag.injector import ContextInjector
from agentx.agent.dspy_agents.rag.retriever import RealRetriever
from agentx.agent.dspy_agents.rag.scorer import ContextScorer


class RAGContextGenerator(dspy.Module):
    """RAG specialist agent for context retrieval and injection.

    Implements agentic RAG pattern (not simple context dump):
    - Retrieves relevant memories (REAL via RealRetriever, not dspy.Predict)
    - Scores context quality
    - Decides whether to inject
    - Filters and formats context

    The agent decides whether retrieved context is relevant enough to inject.

    Phase 3 Fixes:
    - Now uses sync forward() for DSPy compatibility
    - Returns dspy.Prediction instead of dict
    - Uses focused modules for SRP compliance (Fraud #5.4)
    - Externalized magic numbers (Fraud #5.5)
    """

    # Externalized magic numbers (Fraud #5.5)
    DEFAULT_RETRIEVAL_K: int = 10
    DEFAULT_QUALITY_THRESHOLD: float = 0.6
    DEFAULT_MIN_RESULTS: int = 3

    def __init__(
        self,
        k: int = DEFAULT_RETRIEVAL_K,
        quality_threshold: float = DEFAULT_QUALITY_THRESHOLD,
        min_results: int = DEFAULT_MIN_RESULTS,
    ) -> None:
        """Initialize the RAG agent with focused modules.

        Args:
            k: Maximum number of results to retrieve
            quality_threshold: Minimum score threshold (0.0-1.0)
            min_results: Minimum results to return regardless of threshold
        """
        super().__init__()

        # Focused modules for SRP compliance (Phase 3 Fix)
        self._retriever = RealRetriever(
            k=k,
            quality_threshold=quality_threshold,
            min_results=min_results,
        )
        self._scorer = ContextScorer()
        self._injector = ContextInjector()

    def forward(
        self,
        query: str,
        user_id: str = "default_user",
        **kwargs: Any,
    ) -> dspy.Prediction:
        """Execute agentic RAG pipeline with REAL retrieval.

        Phase 3 Fix: Converted from async to sync, returns dspy.Prediction.
        DSPy does not support async forward() methods or dict returns.

        Args:
            query: User query
            user_id: User to retrieve memories for
            **kwargs: Additional arguments

        Returns:
            dspy.Prediction: With retrieval results and injection decision
        """
        # Step 1: REAL retrieval via RealRetriever
        retrieved_memories = self._retriever.retrieve(query=query, user_id=user_id)

        # Step 2: Score context quality
        context_quality = self._scorer.score(retrieved=retrieved_memories)

        # Step 3: Format retrieval summary
        retrieval_summary = "\n".join([f"- {r}" for r in retrieved_memories])

        # Step 4: Decide whether to inject and filter context
        injection_decision = self._injector.decide_and_filter(
            query=query,
            retrieved_context=retrieval_summary,
        )

        # Return dspy.Prediction with all results
        return dspy.Prediction(
            retrieved_memories=retrieved_memories,
            retrieval_summary=retrieval_summary,
            context_quality=context_quality,
            should_inject=injection_decision["should_inject"],
            injection_rationale=injection_decision["injection_rationale"],
            filtered_context=injection_decision["filtered_context"],
        )


# Backward compatibility alias
RAGDSPyAgent = RAGContextGenerator

__all__ = ["RAGContextGenerator", "RAGDSPyAgent"]
