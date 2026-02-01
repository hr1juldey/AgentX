# Spec: Mem0 Consolidation

**Domain**: agent-runtime
**Generated**: 2026-02-02
**Status**: Draft

---

## 1. Purpose

Define the Mem0AI integration for advanced memory consolidation with quality filtering.

**Problem**: Storing every partial execution bloats memory with low-quality data.

**Success Criteria**:
- Quality filters (confidence >= 0.6, length >= 50)
- Duplicate detection before storing
- Consolidation at 100 memories threshold
- Qdrant as Mem0 backend

---

## 2. Scope

### In Scope

- Mem0MemoryAdapter class
- Quality filtering logic
- Consolidation triggering
- Duplicate detection

### Out of Scope

- Temporal metadata (covered by c005-temporal-metadata spec)
- Store interface (covered by agent-memory-store spec)

---

## 3. Requirements

### 3.1 Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-MC-001 | MUST filter low-confidence results (< 0.6) | Must |
| FR-MC-002 | MUST filter trivial results (< 50 chars) | Must |
| FR-MC-003 | MUST detect duplicates before storing | Must |
| FR-MC-004 | MUST consolidate at 100 memories | Should |
| FR-MC-005 | MUST use Qdrant as backend | Should |

### 3.2 Non-Functional Requirements

| ID | Requirement | Target Metric |
|----|-------------|---------------|
| NFR-MC-001 | Consolidation latency | < 30s |

---

## 4. Data Model

```python
# infrastructure/memory/mem0_adapter.py
from mem0 import Memory
from application.use_cases.manage_memory import ConsolidateMemoryUseCase

class Mem0MemoryAdapter:
    """Mem0AI adapter with safeguards against memory hoarding.

    Problem: Mem0 can store every partial execution, bloating memory.
    Solution: Filter and consolidate before storing.
    """
```

---

## 5. API Contract

```python
class Mem0MemoryAdapter:
    """Mem0AI integration with quality filtering."""

    QUALITY_THRESHOLD = 0.6
    MIN_LENGTH = 50
    CONSOLIDATION_THRESHOLD = 100

    def __init__(self, consolidation_use_case: ConsolidateMemoryUseCase):
        self.client = Memory.from_config({
            "vector_store": {
                "provider": "qdrant",
                "config": {"host": "localhost", "port": 6333},
            },
        })
        self.consolidation = consolidation_use_case

    async def store_execution_result(
        self,
        query: str,
        result: str,
        user_id: str,
        confidence: float,
    ) -> bool:
        """Store result ONLY if it meets quality thresholds.

        Prevents hoarding by:
        1. Filtering low-confidence results (< 0.6)
        2. Filtering trivial results (< 50 chars)
        3. Checking for duplicates before storing

        Args:
            query: Original query
            result: Execution result
            user_id: User ID
            confidence: Confidence score (0.0-1.0)

        Returns:
            bool: True if stored, False if filtered
        """
        # 🔴 CRITICAL: Filter low-quality results
        if confidence < self.QUALITY_THRESHOLD:
            return False  # Don't store uncertain results

        if len(result.strip()) < self.MIN_LENGTH:
            return False  # Don't store trivial results

        # Check for duplicates (Mem0 does this, but we add extra check)
        existing = self.client.search(query, user_id=user_id, limit=3)
        for ex in existing:
            if ex.get("memory", "") == result:
                return False  # Duplicate, don't store

        # Store if passes all filters
        self.client.add(
            result,
            user_id=user_id,
            metadata={
                "query": query,
                "confidence": confidence,
                "stored_at": datetime.now().isoformat(),
            },
        )

        return True

    async def consolidate_if_needed(self, user_id: str) -> int:
        """Consolidate memories if count exceeds threshold.

        Prevents memory hoarding by consolidating old memories.

        Args:
            user_id: User ID

        Returns:
            int: Number of memories consolidated
        """
        # Get all memories for user
        all_memories = self.client.get_all(user_id=user_id)
        memory_count = len(all_memories.get("results", []))

        # Consolidate if > 100 memories
        if memory_count > self.CONSOLIDATION_THRESHOLD:
            # Use consolidation use case
            return await self.consolidation.execute(user_id=user_id)

        return 0
```

---

## 6. Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| BR-MC-001 | Confidence threshold | 0.6 minimum |
| BR-MC-002 | Length threshold | 50 chars minimum |
| BR-MC-003 | Duplicate detection | Exact match check |
| BR-MC-004 | Consolidation trigger | 100 memories |

---

## 7. Acceptance Criteria

- [ ] Mem0MemoryAdapter class created
- [ ] Quality filters enforce thresholds
- [ ] Duplicate detection works
- [ ] Consolidation triggers at 100 memories
- [ ] Qdrant backend configured
- [ ] Ruff and pyrefly checks pass

---

## 8. Test Scenarios

| Input | Confidence | Expected |
|-------|------------|----------|
| "Hi" | 1.0 | False (too short) |
| "AI is helpful" | 0.5 | False (low confidence) |
| "Research findings..." | 0.8 | True |
| Duplicate | 0.9 | False (duplicate) |
| 101st memory | 0.8 | Triggers consolidation |

---

**Next**: See `c005-temporal-metadata/spec.md` for temporal models.
