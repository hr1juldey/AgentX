"""RAG specialist agent for context retrieval and injection.

Locked from LLD: agent_runtime.md:582-663

Agentic RAG Pattern:
1. Retrieve relevant memories from vector store
2. Score context quality (high/low based on relevance)
3. Decide whether to inject context
4. Filter and format context for main agent

This is NOT a simple context dump - the agent decides whether to inject.
"""

import dspy
from typing import List, Dict, Any

from agentx.agent.dspy_signatures.rag_signatures import (
    ContextInjectionSignature,
    RetrievalSignature,
)
from agentx.agent.tools.common.dspy_helpers import safe_extract


class RAGDSPyAgent(dspy.Module):
    """RAG specialist agent for context retrieval and injection.

    Implements agentic RAG pattern (not simple context dump):
    - Retrieves relevant memories
    - Scores context quality
    - Decides whether to inject
    - Filters and formats context

    The agent decides whether retrieved context is relevant enough to inject.
    """

    def __init__(self) -> None:
        """Initialize the RAG agent with DSPy signatures."""
        super().__init__()

        self.context_retriever = dspy.Predict(RetrievalSignature)
        self.injection_decider = dspy.Predict(ContextInjectionSignature)

    def retrieve_context(
        self,
        query: str,
        user_context: str,
        memories: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Retrieve and format context from memories.

        Args:
            query: User query to retrieve context for
            user_context: Additional user context
            memories: Retrieved memories from vector store (max 10)

        Returns:
            dict with retrieved_memories, retrieval_summary, context_quality
        """
        # Format memories for DSPy
        memory_summaries = [f"- {m.get('content', '')}" for m in memories[:10]]
        memories_text = "\n".join(memory_summaries)

        # Use DSPy to summarize
        retrieval = self.context_retriever(
            query=query,
            user_context=f"{user_context}\n\nMemories:\n{memories_text}",
        )

        retrieved_memories = safe_extract(retrieval, "retrieved_memories", memories)
        retrieval_summary = safe_extract(retrieval, "retrieval_summary", "")
        context_quality = "high" if len(retrieved_memories) > 3 else "low"

        return {
            "retrieved_memories": retrieved_memories,
            "retrieval_summary": retrieval_summary,
            "context_quality": context_quality,
        }

    def should_inject_context(
        self,
        query: str,
        retrieved_context: str,
    ) -> Dict[str, Any]:
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

    def forward(
        self,
        query: str,
        user_context: str,
        memories: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Execute agentic RAG pipeline.

        Args:
            query: User query
            user_context: Additional user context
            memories: Retrieved memories from vector store

        Returns:
            dict with retrieval results and injection decision
        """
        # Step 1: Retrieve and format context
        retrieval = self.retrieve_context(
            query=query,
            user_context=user_context,
            memories=memories,
        )

        # Step 2: Decide whether to inject
        injection = self.should_inject_context(
            query=query,
            retrieved_context=retrieval["retrieval_summary"],
        )

        return {
            **retrieval,
            **injection,
        }
