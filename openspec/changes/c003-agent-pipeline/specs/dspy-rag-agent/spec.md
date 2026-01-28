# Spec: dspy-rag-agent

**File**: `specs/dspy-rag-agent/spec.md`

**Generated**: 2026-01-28
**Change**: c003-agent-pipeline

---

## 1.1 Purpose

Define the RAG specialist agent that implements agentic retrieval-augmented generation. The RAGDSPyAgent is responsible for retrieving relevant memories, scoring context quality, deciding whether to inject context, and filtering/formatting context for the main agent.

---

## 1.2 Scope

**In Scope**:
- RAGDSPyAgent class with retrieval and injection signatures
- Agentic RAG pattern: retrieve → score → decide → filter
- Memory search with limit enforcement (max 10 memories)
- Context quality scoring before injection
- Integration with Qdrant vector store and Mem0AI

**Out of Scope**:
- Memory consolidation logic (covered by C005-memory-rag)
- Three-tier memory architecture (covered by C005-memory-rag)
- Main agent orchestration (covered by dspy-main-agent spec)

---

## 1.3 Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-RAG-001 | Agent MUST retrieve memories from vector store using semantic search | Must |
| FR-RAG-002 | Agent MUST limit retrieved memories to 10 items | Must |
| FR-RAG-003 | Agent MUST score context quality (high/low) based on relevance | Must |
| FR-RAG-004 | Agent MUST decide whether to inject context based on query relevance | Must |
| FR-RAG-005 | Agent MUST filter and format context before returning | Must |
| FR-RAG-006 | Agent MUST implement agentic RAG (not simple context dump) | Must |

### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-RAG-001 | Agent file MUST NOT exceed 80 lines | Must |
| NFR-RAG-002 | Agent MUST use absolute imports only | Must |
| NFR-RAG-003 | Agent MUST pass ruff check and ruff format | Must |
| NFR-RAG-004 | Memory retrieval MUST complete within 5 seconds | Should |

---

## 1.4 Data Model

**Locked from LLD: agent_runtime.md:582-663**

```python
# File: agent/dspy_agents/rag_agent.py
import dspy
from typing import List, Dict, Any

from agent.dspy_signatures.rag_signatures import (
    RetrievalSignature,
    ContextInjectionSignature
)


class RAGDSPyAgent(dspy.Module):
    """RAG specialist agent for context retrieval and injection.

    Agentic RAG Pattern:
    - Retrieves relevant memories
    - Scores context quality
    - Decides whether to inject
    - Filters and formats context
    """

    def __init__(self, vector_store, memory_repository):
        super().__init__()

        self._vector_store = vector_store
        self._memory_repository = memory_repository

        self.context_retriever = dspy.Predict(RetrievalSignature)
        self.injection_decider = dspy.Predict(ContextInjectionSignature)

    def retrieve_context(
        self,
        query: str,
        user_id: str,
        limit: int = 10
    ) -> dspy.Prediction:
        """Retrieve and format context."""
        # Search memories
        memories = await self._memory_repository.search_memories(
            query=query,
            user_id=user_id,
            limit=limit
        )

        # Format for DSPy
        memory_summaries = [
            f"- {m.get('content', '')}" for m in memories
        ]
        memories_text = "\n".join(memory_summaries)

        # Use DSPy to summarize
        retrieval = self.context_retriever(
            query=query,
            user_context=memories_text
        )

        return dspy.Prediction(
            retrieved_memories=memories,
            retrieval_summary=retrieval.retrieval_summary,
            context_quality="high" if len(memories) > 3 else "low"
        )

    def should_inject_context(
        self,
        query: str,
        retrieved_context: str
    ) -> dspy.Prediction:
        """Decide whether to inject retrieved context."""
        decision = self.injection_decider(
            query=query,
            retrieved_context=retrieved_context
        )

        return dspy.Prediction(
            should_inject=decision.should_inject,
            injection_rationale=decision.injection_rationale,
            filtered_context=decision.filtered_context
        )
```

**Locked from LLD: agent_runtime.md:111-137**

```python
# File: agent/dspy_signatures/rag_signatures.py
import dspy
from typing import List, Dict, Any


class RetrievalSignature(dspy.Signature):
    """Retrieve relevant context for a query."""

    query: str = dspy.InputField(desc="User query")
    user_context: str = dspy.InputField(desc="Additional user context")
    retrieved_memories: List[Dict[str, Any]] = dspy.OutputField(desc="Retrieved memories")
    retrieval_summary: str = dspy.OutputField(desc="Summary of retrieved information")


class ContextInjectionSignature(dspy.Signature):
    """Decide whether to inject retrieved context."""

    query: str = dspy.InputField(desc="User query")
    retrieved_context: str = dspy.InputField(desc="Retrieved context from RAG")
    should_inject: bool = dspy.OutputField(desc="Whether to inject context")
    injection_rationale: str = dspy.OutputField(desc="Reasoning for injection decision")
    filtered_context: str = dspy.OutputField(desc="Filtered context to inject")
```

**Locked from LLD: domain_model.md:543-592**

```python
# File: domain/repositories/memory_repository.py
from abc import ABC, abstractmethod
from uuid import UUID
from typing import List, Optional, Dict, Any

from domain.entities.memory_consolidation import MemoryConsolidationEntity


class MemoryRepository(ABC):
    """Repository for memory operations.

    Implementations: QdrantVectorStoreAdapter, Mem0MemoryAdapter
    """

    @abstractmethod
    async def store_memory(
        self,
        content: str,
        user_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> UUID:
        """Store a memory. Returns memory ID."""
        pass

    @abstractmethod
    async def search_memories(
        self,
        query: str,
        user_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search memories by semantic similarity."""
        pass

    @abstractmethod
    async def get_all_memories(self, user_id: str) -> List[Dict[str, Any]]:
        """Retrieve all memories for a user."""
        pass

    @abstractmethod
    async def update_memory(self, memory_id: UUID, new_content: str) -> bool:
        """Update a memory by ID."""
        pass

    @abstractmethod
    async def delete_memory(self, memory_id: UUID) -> bool:
        """Delete a memory by ID."""
        pass

    @abstractmethod
    async def consolidate_memories(
        self,
        session_id: UUID,
        user_id: str
    ) -> MemoryConsolidationEntity:
        """Consolidate session memories to long-term storage."""
        pass
```

---

## 1.5 API Contract

### Integration with Main Agent

The RAGDSPyAgent is called by the main agent before processing the query:

```python
# In ExecuteAgentQueryUseCase
rag_agent = RAGDSPyAgent(vector_store, memory_repository)

# Step 1: Retrieve context
retrieval = await rag_agent.retrieve_context(
    query=user_query,
    user_id=user_id,
    limit=10
)

# Step 2: Decide whether to inject
injection = rag_agent.should_inject_context(
    query=user_query,
    retrieved_context=retrieval.retrieval_summary
)

# Step 3: Pass to main agent
context_to_use = injection.filtered_context if injection.should_inject else ""
result = await main_agent.execute(
    user_query=user_query,
    conversation_history=conversation_history,
    retrieved_context=context_to_use
)
```

### Agentic RAG Flow

```
User Query
    ↓
RAGDSPyAgent.retrieve_context()
    ↓
Search Memories (Qdrant/Mem0AI)
    ↓
Format Results (memory_summaries)
    ↓
DSPy Summarize (RetrievalSignature)
    ↓
RAGDSPyAgent.should_inject_context()
    ↓
DSPy Decide (ContextInjectionSignature)
    ↓
Filter & Format (filtered_context)
    ↓
MainDSPyReActAgent (with context)
```

---

## 1.6 Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| **BR-RAG-001** | Memory limit MUST NOT exceed 10 items | Parameter validation |
| **BR-RAG-002** | Context quality MUST be "high" if > 3 memories found | Code logic |
| **BR-RAG-003** | Agent MUST NOT dump all retrieved context | Injection decision required |
| **BR-RAG-004** | User isolation MUST be enforced (no cross-user leaks) | user_id parameter required |
| **BR-RAG-005** | Injection decision MUST include rationale | Audit trail |

---

## 1.7 Acceptance Criteria

- [ ] RAGDSPyAgent compiles without errors
- [ ] Both signatures implemented (Retrieval, ContextInjection)
- [ ] Memory limit enforced (max 10)
- [ ] Context quality scoring works (high/low)
- [ ] Injection decision returns boolean + rationale
- [ ] Agentic RAG pattern (not simple dump)
- [ ] File under 80 lines
- [ ] Integration test with Qdrant passes
- [ ] Integration test with Mem0AI passes
- [ ] User isolation enforced (no cross-user results)

---

**Related Specs**:
- `specs/dspy-main-agent/spec.md` - Main agent orchestration
- `specs/dspy-ui-agent/spec.md` - UI specialist agent
- C005-memory-rag - Three-tier memory architecture

---

**Agentic RAG Example**:

```python
# Simple RAG (WRONG - anti-pattern):
def simple_rag(query: str) -> str:
    memories = search(query, limit=10)
    context = "\n".join(m["content"] for m in memories)
    return llm.generate(f"Context: {context}\nQuery: {query}")

# Agentic RAG (CORRECT):
def agentic_rag(query: str, user_id: str) -> str:
    # Step 1: Retrieve
    retrieval = rag_agent.retrieve_context(query, user_id, limit=10)

    # Step 2: Score quality
    quality = "high" if len(retrieval.retrieved_memories) > 3 else "low"

    # Step 3: Decide injection
    injection = rag_agent.should_inject_context(query, retrieval.retrieval_summary)

    # Step 4: Use filtered context
    context = injection.filtered_context if injection.should_inject else ""

    return llm.generate(f"Context: {context}\nQuery: {query}")
```
