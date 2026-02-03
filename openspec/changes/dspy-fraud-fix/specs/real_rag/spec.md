# Spec: Real RAG Implementation

**Domain**: real_rag
**Generated**: 2026-02-03
**Status**: Draft

---

## 1. Purpose

Replace fake RAG (dspy.Predict) with real Mem0-powered retrieval. All components use SAME ColBERTv2 embeddings.

**Problem Statement**: `rag_agent.py` uses `dspy.Predict` instead of real retrieval (Fraud #1). No actual memories are retrieved.

**Success Criteria**: Mem0DSPyRetriever wraps Mem0MemoryAdapter; RAGDSPyAgent uses real retrieval (not dspy.Predict).

---

## 2. Scope

### In Scope

- Replace dspy.Predict with real Mem0 retrieval
- Mem0DSPyRetriever wrapping Mem0MemoryAdapter
- All components use SAME ColBERTv2 embeddings (colbert-ir/colbertv2.0)
- RAGDSPyAgent (rename to RAGContextGenerator)
- Integration with RAGConflictResolutionService (NEW - see spec 2.13)

### Out of Scope

- Changing embedding model (ColBERTv2 is standard)
- Mem0MemoryAdapter changes (existing, working)

---

## 3. Requirements

### 3.1 Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| RF-RAG-001 | Create Mem0DSPyRetriever class | Must |
| RF-RAG-002 | Mem0DSPyRetriever wraps Mem0MemoryAdapter.search_memories() | Must |
| RF-RAG-003 | Retrieval uses ColBERTv2 via QdrantVectorStore | Must |
| RF-RAG-004 | Returns list of objects with long_text attribute | Must |
| RF-RAG-005 | RAGDSPyAgent uses Mem0DSPyRetriever (not dspy.Predict) | Must |
| RF-RAG-006 | No dspy.Predict used for retrieval | Must |

### 3.2 Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-RAG-001 | All files pass Ruff and Pyrefly | Must |
| NFR-RAG-002 | Absolute imports only | Must |

---

## 4. Data Model

```python
# agentx/infrastructure/retrieval/mem0_dspy_retriever.py
import dspy
from typing import List, Any

class Mem0DSPyRetriever:
    """DSPy retriever that wraps Mem0 for consistent embeddings.

    Uses Mem0's search which already uses ColBERTv2 via QdrantVectorStore.
    This ensures DSPy, Mem0, and Qdrant all use the SAME embeddings.
    """

    def __init__(self, k: int = 10):
        self.k = k
        from agentx.infrastructure.memory.mem0_adapter import Mem0MemoryAdapter
        self.mem0_adapter = Mem0MemoryAdapter()

    def __call__(self, query: str, k: int = None, **kwargs) -> List[Any]:
        """Retrieve memories using Mem0's ColBERTv2-powered search."""
        k = k or self.k
        user_id = kwargs.get('user_id', 'default_user')

        # Call Mem0's search (uses ColBERTv2 via QdrantVectorStore)
        memories = self.mem0_adapter.search_memories(
            query=query,
            user_id=user_id,
            limit=k
        )

        # Format for DSPy (expects objects with long_text attribute)
        class RetrievedMemory:
            def __init__(self, content, score, metadata):
                self.long_text = content
                self.score = score
                self.metadata = metadata

        return [
            RetrievedMemory(
                content=m.get('content', ''),
                score=m.get('score', 0.0),
                metadata=m.get('metadata', {})
            )
            for m in memories
        ]

# agentx/agent/dspy_agents/rag_agent.py
import dspy

class RAGContextGenerator(dspy.Module):
    """RAG specialist using Mem0-powered retrieval (ColBERTv2 embeddings)."""

    def __init__(self) -> None:
        super().__init__()
        from agentx.infrastructure.retrieval.mem0_dspy_retriever import Mem0DSPyRetriever

        # REAL retrieval using Mem0 wrapper (ColBERTv2-powered)
        self.retrieve = Mem0DSPyRetriever(k=10)

    def retrieve_context(self, query: str, user_id: str) -> dspy.Prediction:
        # REAL retrieval via Mem0 (uses ColBERTv2)
        retrieved = self.retrieve(query=query, k=10, user_id=user_id)

        # Format for DSPy
        memory_summaries = [f"- {r.long_text}" for r in retrieved]
        memories_text = "\n".join(memory_summaries)

        return dspy.Prediction(
            retrieved_memories=retrieved,
            retrieval_summary=memories_text,
            context_quality="high" if len(retrieved) > 3 else "low"
        )

    def forward(self, query: str, user_id: str) -> dspy.Prediction:
        # Step 1: REAL retrieval via Mem0
        retrieval = self.retrieve_context(query=query, user_id=user_id)

        return dspy.Prediction(
            **retrieval
        )
```

---

## 5. API Contract

This spec defines DSPy modules only. No REST/WebSocket endpoints.

---

## 6. Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| BR-RAG-001 | All components use ColBERTv2 (colbert-ir/colbertv2.0) | Documentation |
| BR-RAG-002 | No dspy.Predict for retrieval | Code review |
| BR-RAG-003 | RetrievedMemory has long_text attribute | DSPy requirement |

---

## 7. Acceptance Criteria

- [ ] Mem0DSPyRetriever class exists in infrastructure/retrieval/
- [ ] RAGDSPyAgent uses Mem0DSPyRetriever (not dspy.Predict)
- [ ] Mem0DSPyRetriever returns list of objects with long_text attribute
- [ ] Retrieval uses Mem0MemoryAdapter.search_memories()
- [ ] All components use ColBERTv2 (colbert-ir/colbertv2.0)
- [ ] No dspy.Predict used for retrieval
- [ ] All files pass: `ruff check` and `pyrefly check`

---

## 8. References

- **Fraud #1**: `.claude/fraud/AGENTX_DSPY_FRAUD_ANALYSIS_2026.md` (Fake RAG)
- **Plan**: `.claude/plans/golden-skipping-hedgehog.md` (Batch 1)
- **Mem0 Integration**: `agentx/infrastructure/memory/mem0_adapter.py`

---

**Related Specs**:
- `specs/adaptive_retrieval/spec.md` - Quality-based retrieval
- `specs/rag_conflict_resolution/spec.md` - Conflict resolution for retrieved memories
