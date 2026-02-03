# Spec: RAG Conflict Resolution

**Domain**: rag_conflict_resolution
**Generated**: 2026-02-03
**Status**: Draft

---

## 1. Purpose

Resolve contradictions between retrieved memories using tiered strategy + LLM fallback. Protect against RAG context contradiction failures.

**Problem Statement**: RAG fails when contradicting facts load into context. Memory A says "X is true", Memory B says "X is false". LLM cannot resolve without explicit strategy.

**Success Criteria**: Memories with contradictions resolved using 4-tier strategy before synthesis.

---

## 2. Scope

### In Scope

- Source attribution (each memory tracks source)
- Confidence-based filtering (highest confidence wins)
- Source authority weighting (academic > general > social)
- Temporal priority (newest memory wins for same topic)
- LLM-mediated resolution (DSPy synthesis) as fallback
- Integration with Real RAG and Multi-Source Synthesis

### Out of Scope

- Memory storage logic (separate concern)

---

## 3. Requirements

### 3.1 Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| RF-CONFLICT-001 | Each memory tracks: source_type, confidence_score, created_at | Must |
| RF-CONFLICT-002 | Tier 1: Temporal priority - newest memory wins for same topic | Must |
| RF-CONFLICT-003 | Tier 2: Confidence score - highest >= threshold wins | Must |
| RF-CONFLICT-004 | Tier 3: Source authority - academic > report > general > social | Must |
| RF-CONFLICT-005 | Tier 4: DSPy synthesis for remaining conflicts | Must |
| RF-CONFLICT-006 | Explicit contradiction handling: "Sources disagree: A says X, B says Y" | Must |

### 3.2 Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-CONFLICT-001 | All files pass Ruff and Pyrefly | Must |
| NFR-CONFLICT-002 | Absolute imports only | Must |

---

## 4. Data Model

```python
# agentx/domain/entities/memory_record.py (EXTENDED)
from enum import Enum

class SourceType(str, Enum):
    """Type of source for memory attribution."""
    ACADEMIC = "academic"      # Peer-reviewed papers, academic journals
    REPORT = "report"          # Industry reports, white papers
    GENERAL = "general"        # General websites, blogs
    SOCIAL = "social"          # Social media, forums
    UNKNOWN = "unknown"        # Source type unknown

@dataclass
class MemoryRecord:
    # ... existing fields ...
    source_type: SourceType
    confidence_score: float  # 0.0 to 1.0
    created_at: datetime

# agentx/application/services/rag_conflict_resolution_service.py
from dataclasses import dataclass
from typing import List

@dataclass
class ConflictResolution:
    """Result of conflict resolution process."""
    resolved_memories: list  # Memories after resolution
    conflicts_detected: int  # How many conflicts found
    conflicts_resolved: int  # How many resolved by tiers 1-3
    llm_fallback_used: bool  # Whether tier 4 was needed
    resolution_summary: str  # Human-readable summary

class RAGConflictResolutionService:
    """Service for resolving conflicts between retrieved memories."""

    def __init__(self):
        self.tier1_threshold_days = 30  # Same topic = within 30 days
        self.tier2_confidence_threshold = 0.7
        self.tier3_authority_priority = {
            SourceType.ACADEMIC: 5,
            SourceType.REPORT: 4,
            SourceType.GENERAL: 3,
            SourceType.SOCIAL: 2,
            SourceType.UNKNOWN: 1,
        }

    async def resolve_conflicts(
        self,
        memories: list[MemoryRecord],
        query: str
    ) -> ConflictResolution:
        """Resolve conflicts using 4-tier strategy.

        Tier 1: Temporal Priority (newest wins same topic)
        Tier 2: Confidence Score (highest >= 0.7 wins)
        Tier 3: Source Authority (academic > general)
        Tier 4: DSPy LLM synthesis (fallback)
        """
        # Implementation follows 4-tier strategy
        pass
```

---

## 5. API Contract

This spec defines domain entities and service. No REST/WebSocket endpoints.

---

## 6. Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| BR-CONFLICT-001 | Same topic (within 30 days): Newest memory wins | Tier 1 logic |
| BR-CONFLICT-002 | Different topics: Highest confidence_score >= 0.7 wins | Tier 2 logic |
| BR-CONFLICT-003 | Equal confidence: Source authority priority | Tier 3 logic |
| BR-CONFLICT-004 | Remaining conflicts: DSPy LLM resolution | Tier 4 fallback |
| BR-CONFLICT-005 | Explicit contradiction reporting in synthesis | MultiSourceSynthesisSignature |

---

## 7. Acceptance Criteria

- [ ] MemoryRecord extended with source_type, confidence_score
- [ ] SourceType enum exists: ACADEMIC, REPORT, GENERAL, SOCIAL, UNKNOWN
- [ ] RAGConflictResolutionService implements 4-tier strategy
- [ ] Tier 1: Temporal priority works (newest wins same topic)
- [ ] Tier 2: Confidence filtering works (highest >= 0.7 wins)
- [ ] Tier 3: Source authority weighting works
- [ ] Tier 4: DSPy synthesis fallback for remaining conflicts
- [ ] ConflictResolution reports: conflicts_detected, conflicts_resolved, llm_fallback_used
- [ ] All files pass: `ruff check` and `pyrefly check`

**Verification**:
```python
from agentx.application.services.rag_conflict_resolution_service import RAGConflictResolutionService
from agentx.domain.entities.memory_record import MemoryRecord, SourceType
from datetime import datetime, timedelta

service = RAGConflictResolutionService()

# Create contradicting memories
memory_old = MemoryRecord(
    memory_id=UUID('11111111-1111-1111-1111-111111111111'),
    user_id='test',
    memory_type=WorkExperienceType.OUTPUT_PRODUCED,
    data_input='Query about blueberries',
    instruction_input='Search and summarize',
    reasoning_done='Searched web',
    output_produced='Blueberries have 5 calories per cup',
    quality_score=0.8,
    source_type=SourceType.GENERAL,
    created_at=datetime.now() - timedelta(days=60),
    # ... other fields ...
)

memory_new = MemoryRecord(
    memory_id=UUID('22222222-2222-2222-2222-222222222222'),
    user_id='test',
    memory_type=WorkExperienceType.OUTPUT_PRODUCED,
    data_input='Query about blueberries',
    instruction_input='Search and summarize',
    reasoning_done='Searched academic source',
    output_produced='Blueberries have 85 calories per cup',
    quality_score=0.9,
    source_type=SourceType.ACADEMIC,
    created_at=datetime.now(),
    # ... other fields ...
)

# Resolve conflicts
resolution = await service.resolve_conflicts([memory_old, memory_new], query="blueberries calories")

# Should pick memory_new because:
# - Different topics (old vs new date), NOT same topic
# - Tier 2: 0.9 > 0.8 (highest confidence wins)
assert resolution.conflicts_detected >= 1
assert resolution.conflicts_resolved >= 1
assert not resolution.llm_fallback_used  # Resolved by tier 2
```

---

## 8. References

- **Related Specs**: `specs/real_rag/spec.md` (enhanced with conflict resolution)
- **Related Specs**: `specs/multi_source_synthesis/spec.md` (uses LLM fallback)

---

**Related Specs**:
- `specs/real_rag/spec.md` - Enhanced with conflict resolution
- `specs/multi_source_synthesis/spec.md` - Uses LLM fallback
