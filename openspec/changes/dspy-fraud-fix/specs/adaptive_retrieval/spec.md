# Spec: Adaptive Retrieval

**Domain**: adaptive_retrieval
**Generated**: 2026-02-03
**Status**: Draft

---

## 1. Purpose

Retrieve until quality score drops below threshold (not fixed k=10). Enable quality-based filtering.

**Problem Statement**: Fixed k=10 retrieval may return low-quality results or miss high-quality results beyond position 10.

**Success Criteria**: Mem0DSPyRetriever supports k=20 candidates, filters by quality_threshold=0.6, returns min_results=3.

---

## 2. Scope

### In Scope

- Quality-based retrieval filtering
- k=20 max candidates
- quality_threshold=0.6 (configurable)
- min_results=3 (guaranteed)
- Mem0DSPyRetriever wrapping Mem0MemoryAdapter

### Out of Scope

- Changing embedding model (use existing ColBERTv2)

---

## 3. Requirements

### 3.1 Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| RF-RET-001 | Retrieve k candidates from Mem0 (default k=20) | Must |
| RF-RET-002 | Filter: keep while quality >= threshold OR until min_results | Must |
| RF-RET-003 | Quality threshold configurable (default 0.6) | Must |
| RF-RET-004 | Minimum results guaranteed (default 3) | Must |
| RF-RET-005 | Return filtered list with scores | Must |

### 3.2 Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-RET-001 | File passes Ruff and Pyrefly | Must |
| NFR-RET-002 | Absolute imports only | Must |

---

## 4. Data Model

```python
# agentx/infrastructure/retrieval/mem0_dspy_retriever.py
import dspy
from typing import List, Any

class Mem0DSPyRetriever:
    """DSPy retriever that wraps Mem0 for quality-based retrieval."""

    def __init__(self, k: int = 20, quality_threshold: float = 0.6, min_results: int = 3):
        self.k = k
        self.quality_threshold = quality_threshold
        self.min_results = min_results
        from agentx.infrastructure.memory.mem0_adapter import Mem0MemoryAdapter
        self.mem0_adapter = Mem0MemoryAdapter()

    def __call__(self, query: str, k: int = None, **kwargs) -> List[Any]:
        """Retrieve memories using Mem0 with quality filtering."""
        k = k or self.k
        user_id = kwargs.get('user_id', 'default_user')

        # Call Mem0's search (uses ColBERTv2 via QdrantVectorStore)
        memories = self.mem0_adapter.search_memories(
            query=query,
            user_id=user_id,
            limit=k
        )

        # Filter by quality score, but guarantee min_results
        filtered = []
        for i, m in enumerate(memories):
            score = m.get('score', 0.0)
            # Keep if quality >= threshold OR we haven't reached min_results yet
            if score >= self.quality_threshold or i < self.min_results:
                filtered.append(m)

        return filtered
```

---

## 5. API Contract

This spec defines DSPy retriever only. No REST/WebSocket endpoints.

---

## 6. Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| BR-RET-001 | Always return at least min_results | Code logic |
| BR-RET-002 | Stop filtering after min_results if all below threshold | Code logic |
| BR-RET-003 | Use ColBERTv2 embeddings (via Mem0) | Existing Mem0Adapter |

---

## 7. Acceptance Criteria

- [ ] Mem0DSPyRetriever exists in infrastructure/retrieval/
- [ ] Configurable quality_threshold parameter (default 0.6)
- [ ] Configurable min_results parameter (default 3)
- [ ] Returns at least min_results even if below threshold
- [ ] Returns filtered list with scores
- [ ] File passes: `ruff check` and `pyrefly check`

---

## 8. References

- **Plan**: `.claude/plans/golden-skipping-hedgehog.md` (Batch 0c)
- **Mem0 Integration**: `agentx/infrastructure/memory/mem0_adapter.py`

---

**Related Specs**:
- `specs/work_experience_memory/spec.md` - Quality scoring source
- `specs/context_rotting/spec.md` - TTL and decay
