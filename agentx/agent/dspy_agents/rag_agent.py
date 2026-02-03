"""RAG specialist agent for context retrieval and injection.

Locked from LLD: agent_runtime.md:582-663

Agentic RAG Pattern:
1. Retrieve relevant memories from vector store (REAL via Mem0DSPyRetriever)
2. Score context quality (high/low based on relevance)
3. Decide whether to inject context
4. Filter and format context for main agent

This is NOT a simple context dump - the agent decides whether to inject.
"""

import dspy
from typing import Any

from agentx.agent.dspy_signatures.rag_signatures import ContextInjectionSignature
from agentx.agent.tools.common.dspy_helpers import safe_extract
from agentx.infrastructure.retrieval.mem0_dspy_retriever import Mem0DSPyRetriever


class RAGContextGenerator(dspy.Module):
    """RAG specialist agent for context retrieval and injection.

    Implements agentic RAG pattern (not simple context dump):
    - Retrieves relevant memories (REAL via Mem0DSPyRetriever, not dspy.Predict)
    - Scores context quality
    - Decides whether to inject
    - Filters and formats context

    The agent decides whether retrieved context is relevant enough to inject.

    Renamed from RAGDSPyAgent to RAGContextGenerator for clarity.
    """

    def __init__(self) -> None:
        """Initialize the RAG agent with real Mem0 retriever."""
        super().__init__()

        # REAL retrieval using Mem0 (ColBERTv2-powered)
        self.retrieve = Mem0DSPyRetriever(k=10, quality_threshold=0.6, min_results=3)
        self.injection_decider = dspy.Predict(ContextInjectionSignature)

    async def retrieve_context(
        self,
        query: str,
        user_id: str = "default_user",
    ) -> dict[str, Any]:
        """Retrieve and format context from memories using REAL Mem0 retrieval.

        Args:
            query: User query to retrieve context for
            user_id: User to retrieve memories for

        Returns:
            dict with retrieved_memories, retrieval_summary, context_quality
        """
        # REAL retrieval via Mem0 (uses ColBERTv2)
        retrieved = await self.retrieve(query=query, k=10, user_id=user_id)

        # Format for DSPy
        memory_summaries = [f"- {r.long_text}" for r in retrieved]
        memories_text = "\n".join(memory_summaries)

        return {
            "retrieved_memories": retrieved,
            "retrieval_summary": memories_text,
            "context_quality": "high" if len(retrieved) > 3 else "low",
        }

    def should_inject_context(
        self,
        query: str,
        retrieved_context: str,
    ) -> dict[str, Any]:
        """Decide whether to inject retrieved context.

        Args:
            query: User query
            retrieved_context: Retrieved context from RAG

        Returns:
            dict with should_inject, injection_rationale, filtered_context
        """
        decision = self.injection_decider(
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

    async def forward(
        self,
        query: str,
        user_id: str = "default_user",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Execute agentic RAG pipeline with REAL retrieval.

        Args:
            query: User query
            user_id: User to retrieve memories for
            **kwargs: Additional arguments

        Returns:
            dict with retrieval results and injection decision
        """
        # Step 1: REAL retrieval via Mem0
        retrieval = await self.retrieve_context(query=query, user_id=user_id)

        # Step 2: Decide whether to inject
        injection = self.should_inject_context(
            query=query,
            retrieved_context=retrieval["retrieval_summary"],
        )

        return {
            **retrieval,
            **injection,
        }


# Backward compatibility alias
RAGDSPyAgent = RAGContextGenerator
