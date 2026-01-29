"""RAG signatures for agentic retrieval-augmented generation.

Locked from LLD: agent_runtime.md:111-137

These signatures enable the RAGDSPyAgent to implement agentic RAG:
- RetrievalSignature: Retrieve relevant context for a query
- ContextInjectionSignature: Decide whether to inject retrieved context

Agentic RAG Pattern (not simple context dump):
1. Retrieve memories from vector store
2. Score context quality
3. Decide whether to inject
4. Filter and format context
"""

import dspy
from typing import List, Dict, Any


class RetrievalSignature(dspy.Signature):
    """Retrieve relevant context for a user query.

    Uses semantic search to find relevant memories from the vector store.
    Returns retrieved memories and a summary for the main agent.
    """

    query: str = dspy.InputField(
        desc="User query to retrieve context for",
        prefix="Query: ",
    )
    user_context: str = dspy.InputField(
        desc="Additional user context (conversation history, preferences)",
        prefix="Context: ",
    )
    retrieved_memories: List[Dict[str, Any]] = dspy.OutputField(
        desc="Retrieved memories from vector store (max 10)",
        prefix="Memories: ",
    )
    retrieval_summary: str = dspy.OutputField(
        desc="Summary of retrieved information for main agent",
        prefix="Summary: ",
    )


class ContextInjectionSignature(dspy.Signature):
    """Decide whether to inject retrieved context into the main agent.

    Agentic decision: NOT all retrieved context should be injected.
    The agent decides based on query relevance and context quality.
    """

    query: str = dspy.InputField(
        desc="User query",
        prefix="Query: ",
    )
    retrieved_context: str = dspy.InputField(
        desc="Retrieved context from RAG system",
        prefix="Context: ",
    )
    should_inject: bool = dspy.OutputField(
        desc="Whether to inject context into main agent response",
        prefix="Inject: ",
    )
    injection_rationale: str = dspy.OutputField(
        desc="Reasoning for injection decision",
        prefix="Rationale: ",
    )
    filtered_context: str = dspy.OutputField(
        desc="Filtered and formatted context to inject (if should_inject=True)",
        prefix="Filtered: ",
    )
