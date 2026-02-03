# Spec: Work-Experience Memory Schema

**Domain**: work_experience_memory
**Generated**: 2026-02-03
**Status**: Draft

---

## 1. Purpose

Define the memory schema for work-experience based storage. Agents remember their WORK (data received, instructions followed, reasoning performed, output produced), NOT arbitrary facts or knowledge.

**Problem Statement**: Current memory system has no schema for work-experience tracking, preventing agents from learning from past performance.

**Success Criteria**: MemoryRecord entity stores work-experience with quality scoring and TTL.

---

## 2. Scope

### In Scope

- MemoryRecord entity with work-experience fields
- WorkExperienceType enum (DATA_RECEIVED, INSTRUCTION_FOLLOWED, REASONING_DONE, OUTPUT_PRODUCED)
- Quality scoring (0.0-1.0)
- Access count tracking for reinforcement
- TTL (time-to-live) in days
- Supersede mechanism (better memory replaces older)

### Out of Scope

- Fact/knowledge storage (memory stores WORK EXPERIENCE only)
- Memory retrieval logic (handled by Adaptive Retrieval spec)
- Memory consolidation logic (handled by existing MemoryConsolidationEntity)

---

## 3. Requirements

### 3.1 Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-MEM-001 | MemoryRecord stores data_input, instruction_input, reasoning_done, output_produced | Must |
| FR-MEM-002 | Quality score is required float between 0.0 and 1.0 | Must |
| FR-MEM-003 | Access count increments on each retrieval | Must |
| FR-MEM-004 | TTL days is positive integer | Must |
| FR-MEM-005 | Superseded_by field references better memory ID | Must |
| FR-MEM-006 | WorkExperienceType enum has 4 values | Must |

### 3.2 Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-MEM-001 | Entity passes Ruff and Pyrefly checks | Must |
| NFR-MEM-002 | Entity uses @dataclass decorator | Must |
| NFR-MEM-003 | Entity uses absolute imports only | Must |
| NFR-MEM-004 | Entity is under 100 lines executable | Must |

---

## 4. Data Model

```python
# agentx/domain/entities/memory_record.py
from dataclasses import dataclass
from uuid import UUID
from datetime import datetime
from enum import Enum

class WorkExperienceType(str, Enum):
    """Types of work experience memories."""
    DATA_RECEIVED = "data_received"
    INSTRUCTION_FOLLOWED = "instruction_followed"
    REASONING_DONE = "reasoning_done"
    OUTPUT_PRODUCED = "output_produced"

@dataclass
class MemoryRecord:
    """Work-experience memory record.

    Agents remember WHAT THEY DID, not arbitrary facts.
    Each record captures: data received, instructions followed,
    reasoning performed, and output produced.
    """
    memory_id: UUID
    user_id: str
    session_id: str
    memory_type: WorkExperienceType
    data_input: str
    instruction_input: str
    reasoning_done: str
    output_produced: str
    quality_score: float  # 0.0 to 1.0
    access_count: int = 0
    ttl_days: int = 30
    superseded_by: UUID | None = None
    created_at: datetime
    last_accessed_at: datetime | None = None

    def is_expired(self) -> bool:
        """Check if memory has expired based on TTL."""
        if self.last_accessed_at is None:
            return False
        elapsed_days = (datetime.now() - self.last_accessed_at).days
        return elapsed_days > self.ttl_days

    def record_access(self) -> None:
        """Record a retrieval access for reinforcement."""
        self.access_count += 1
        self.last_accessed_at = datetime.now()
```

---

## 5. API Contract

This spec defines domain entities only. No REST/WebSocket endpoints.

---

## 6. Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| BR-MEM-001 | Quality score must be between 0.0 and 1.0 | Code validation |
| BR-MEM-002 | TTL days must be positive integer | Code validation |
| BR-MEM-003 | Superseded_by must be valid UUID or None | Code validation |
| BR-MEM-004 | Memory stores work experience only, not facts | Documentation + validation |

---

## 7. Acceptance Criteria

- [ ] MemoryRecord entity exists in `agentx/domain/entities/memory_record.py`
- [ ] WorkExperienceType enum exists with 4 values
- [ ] MemoryRecord has all required fields
- [ ] Quality score validated as float between 0.0 and 1.0
- [ ] is_expired() method works correctly
- [ ] record_access() method increments access_count
- [ ] File uses absolute imports only
- [ ] File passes: `ruff check` and `pyrefly check`
- [ ] Verification passes:
```python
from agentx.domain.entities.memory_record import MemoryRecord, WorkExperienceType
record = MemoryRecord(
    memory_id=UUID('12345678-1234-5678-1234-567812345678'),
    user_id='test',
    session_id='session123',
    memory_type=WorkExperienceType.OUTPUT_PRODUCED,
    data_input='user query',
    instruction_input='search and summarize',
    reasoning_done='queried vector store',
    output_produced='Summary text',
    quality_score=0.85,
    created_at=datetime.now()
)
assert 0.0 <= record.quality_score <= 1.0
```

---

## 8. References

- **Fraud Analysis**: `.claude/fraud/AGENTX_DSPY_FRAUD_ANALYSIS_2026.md`
- **Domain Model LLD**: `docs/engineering/lld/domain_model.md`
- **Plan**: `.claude/plans/golden-skipping-hedgehog.md` (Batch 0a)

---

**Related Specs**:
- `specs/adaptive_retrieval/spec.md` - Quality-based retrieval
- `specs/context_rotting/spec.md` - TTL and decay mechanisms
