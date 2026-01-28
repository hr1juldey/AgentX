# Specs Artifact: c005-memory-rag

**Generated**: 2026-01-28
**Change**: c005-memory-rag
**Schema**: spec-factory v1

---

## Spec Structure

This artifact generates domain-specific specification files in `specs/{domain}/spec.md`.

---

## 1. Spec: memory-consolidation

**File**: `specs/memory-consolidation/spec.md`

### 1.1 Purpose

Define memory consolidation service that moves memories from Tier 2 (session-scoped Qdrant) to Tier 3 (persistent Qdrant + Mem0AI) with merging, invalidation, and summarization.

### 1.2 Scope

**In Scope**:
- Tier 2 → Tier 3 consolidation on trigger
- Duplicate memory merging (same entity/topic)
- Fact invalidation (new supersedes old)
- Duration event summarization
- Three trigger types: SCHEDULED, MANUAL, PRE_QUERY

**Out of Scope**:
- Real-time memory updates (handled by C003)
- Memory visualization UI (future feature)

### 1.3 Requirements

#### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-MC-001 | Service MUST consolidate Tier 2 memories to Tier 3 on trigger | Must |
| FR-MC-002 | Service MUST merge duplicate memories (same entity/topic) | Must |
| FR-MC-003 | Service MUST invalidate outdated facts (new supersedes old) | Must |
| FR-MC-004 | Service MUST summarize duration events into single memories | Must |
| FR-MC-005 | Service MUST support three triggers: SCHEDULED (every 10), MANUAL, PRE_QUERY | Must |
| FR-MC-006 | Service MUST track consolidation status (PENDING → IN_PROGRESS → COMPLETED) | Must |

#### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-MC-001 | Consolidation MUST complete within 30 seconds | Must |
| NFR-MC-002 | Merge rate MUST be >10% (memories_merged / memories_processed) | Should |
| NFR-MC-003 | MemoryRepository MUST be thread-safe for concurrent access | Must |

### 1.4 Data Model

```python
# Locked from LLD: domain_model.md:189-269
from dataclasses import dataclass
from uuid import UUID
from datetime import datetime
from typing import Optional

@dataclass
class MemoryConsolidationEntity:
    """Represents a memory consolidation operation.

    Consolidation moves memories from Tier 2 (Agent's Qdrant) to Tier 3 (User's Qdrant + Mem0AI).
    """
    consolidation_id: UUID
    session_id: UUID
    trigger: ConsolidationTrigger
    status: ConsolidationStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    memories_processed: int = 0
    memories_merged: int = 0
    memories_invalidated: int = 0
    error_message: Optional[str] = None

    def start(self) -> None: ...
    def complete(self, processed: int, merged: int, invalidated: int) -> None: ...
    def fail(self, error: str) -> None: ...
    def duration_seconds(self) -> Optional[int]: ...
    def merge_rate(self) -> float: ...
```

### 1.5 API Contract

#### REST Endpoints

| Method | Path | Request | Response | Status Codes |
|--------|------|---------|----------|--------------|
| POST | `/api/v1/memory/consolidate` | `ConsolidateMemoryCommand` | `ConsolidateMemoryResponse` | 201, 400, 500 |
| GET | `/api/v1/memory/consolidations/{consolidation_id}` | - | `ConsolidationStatusResponse` | 200, 404, 500 |

### 1.6 Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| BR-MC-001 | SCHEDULED trigger fires every 10 interactions | ConsolidationService counter |
| BR-MC-002 | Fact invalidation marks old with superseded_by | ConsolidateMemoryUseCase |
| BR-MC-003 | Duration events summarized as single memory | DurationMemoryService |
| BR-MC-004 | Failed consolidation MUST preserve error message | MemoryConsolidationEntity.fail() |

### 1.7 Acceptance Criteria

- [ ] Consolidation reduces Tier 2 memory count
- [ ] Duplicate memories merged (merge_rate > 0.1)
- [ ] Outdated facts marked with superseded_by
- [ ] Duration events summarized as single memories
- [ ] Consolidation status transitions PENDING → IN_PROGRESS → COMPLETED
- [ ] All three triggers work (SCHEDULED, MANUAL, PRE_QUERY)
- [ ] Consolidation completes within 30 seconds
- [ ] LLD alignment verified (100% field match)

---

## 2. Spec: temporal-rag

**File**: `specs/temporal-rag/spec.md`

### 2.1 Purpose

Define time-aware retrieval-augmented generation with temporal filtering, fact invalidation, and multi-hop search across Tier 2 and Tier 3 memories.

### 2.2 Scope

**In Scope**:
- Temporal metadata enrichment (created_at, valid_from, valid_until)
- Temporal classification (preference, state, event, plan, fact)
- Time-filtered search (recent, historical, all)
- Fact invalidation during retrieval
- Multi-hop retrieval (Tier 2 + Tier 3)

**Out of Scope**:
- Memory storage (covered by consolidation spec)
- UI components (future feature)

### 2.3 Requirements

#### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-TR-001 | Service MUST add temporal metadata to all memories | Must |
| FR-TR-002 | Service MUST classify memory by temporal_type (preference, state, event, plan, fact) | Must |
| FR-TR-003 | Service MUST support time-filtered search (recent, historical, all) | Must |
| FR-TR-004 | Service MUST invalidate outdated facts during retrieval | Must |
| FR-TR-005 | Service MUST search both Tier 2 and Tier 3 (multi-hop) | Must |
| FR-TR-006 | Service MUST weight recent memories higher than historical | Should |

#### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-TR-001 | Temporal classification accuracy MUST be >90% | Must |
| NFR-TR-002 | Time-filtered search MUST complete within 500ms | Must |
| NFR-TR-003 | Multi-hop retrieval MUST be +15% better than Tier 3 alone | Should |

### 2.4 Data Model

```python
# Temporal metadata (added to all memories)
@dataclass
class TemporalMetadata:
    created_at: datetime
    modified_at: datetime
    valid_from: datetime
    valid_until: Optional[datetime]  # None means still valid
    temporal_type: Literal["preference", "state", "event", "plan", "fact"]
    supersedes: list[UUID]  # Memory IDs this one invalidates
    superseded_by: Optional[UUID]  # If this memory is outdated
```

### 2.5 API Contract

#### REST Endpoints

| Method | Path | Request | Response | Status Codes |
|--------|------|---------|----------|--------------|
| POST | `/api/v1/memory/search` | `SearchMemoryCommand` | `SearchMemoryResponse` | 200, 400, 500 |
| POST | `/api/v1/memory/store` | `StoreMemoryCommand` | `StoreMemoryResponse` | 201, 400, 500 |

### 2.6 Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| BR-TR-001 | All memories MUST have temporal metadata | MemoryRepository.store_memory() |
| BR-TR-002 | Recent search = last 30 days | TemporalRAGService._build_time_filter() |
| BR-TR-003 | Historical search = older than 30 days | TemporalRAGService._build_time_filter() |
| BR-TR-004 | Outdated facts filtered at retrieval | TemporalRAGService._invalidate_outdated_facts() |
| BR-TR-005 | Preferences weighted 2x higher than facts | TemporalRAGService._weight_results() |

### 2.7 Acceptance Criteria

- [ ] All memories have temporal metadata
- [ ] Temporal classification accuracy >90%
- [ ] Time-filtered search returns correct time windows
- [ ] Outdated facts filtered or marked with superseded_by
- [ ] Multi-hop search merges Tier 2 and Tier 3 results
- [ ] Time-filtered search completes within 500ms
- [ ] Multi-hop retrieval +15% better than Tier 3 alone

---

## 3. Spec: duration-memory

**File**: `specs/duration-memory/spec.md`

### 3.1 Purpose

Define duration-aware memory for tracking long-term states (e.g., "watched movie for 2 hours") with start/end timestamps and consolidation.

### 3.2 Scope

**In Scope**:
- State tracking (start/end times)
- Duration calculation
- Active states query
- Consolidation of duration events

**Out of Scope**:
- Point events (handled by temporal-rag)
- UI components (future feature)

### 3.3 Requirements

#### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-DM-001 | Service MUST track state start time | Must |
| FR-DM-002 | Service MUST calculate duration on state end | Must |
| FR-DM-003 | Service MUST store duration as consolidated memory | Must |
| FR-DM-004 | Service MUST support multiple concurrent states per user | Must |
| FR-DM-005 | Service MUST auto-end stale states after 24 hours | Should |

#### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-DM-001 | Duration calculation MUST be accurate to within 1 second | Must |
| NFR-DM-002 | Active states query MUST complete within 100ms | Must |

### 3.4 Data Model

```python
# Locked from research:07_temporal_rag.md:271-354
@dataclass
class DurationMemory:
    """Track states with durations."""
    active_states: Dict[str, Dict]  # state_id -> state info

    def start_state(self, state_id: str, state_type: str, attributes: Dict, user_id: str) -> None: ...
    def end_state(self, state_id: str) -> Optional[Dict]: ...
    def get_active_states(self, user_id: str) -> List[Dict]: ...
```

### 3.5 API Contract

#### REST Endpoints

| Method | Path | Request | Response | Status Codes |
|--------|------|---------|----------|--------------|
| POST | `/api/v1/memory/start-state` | `StartStateCommand` | `StartStateResponse` | 201, 400, 500 |
| POST | `/api/v1/memory/end-state/{state_id}` | - | `EndStateResponse` | 200, 404, 500 |
| GET | `/api/v1/memory/active-states/{user_id}` | - | `ActiveStatesResponse` | 200, 404, 500 |

### 3.6 Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| BR-DM-001 | Duration = end_time - start_time (seconds) | DurationMemory.end_state() |
| BR-DM-002 | Stale states auto-end after 24 hours | DurationMemory._cleanup_stale_states() |
| BR-DM-003 | Consolidated duration memory includes "Duration: X for Ys" | DurationMemory._create_consolidated_memory() |

### 3.7 Acceptance Criteria

- [ ] States tracked with start_time
- [ ] Duration calculated correctly (end - start)
- [ ] Duration memory stored to Tier 3 on consolidation
- [ ] Active states queryable by user_id
- [ ] Multiple concurrent states supported
- [ ] Stale states auto-end after 24 hours
- [ ] Duration calculation accurate within 1 second
- [ ] Active states query within 100ms

---

## 4. Cross-Domain Contracts

### 4.1 Shared Types

**ConsolidationTrigger** (used by memory-consolidation):
```python
class ConsolidationTrigger(str, Enum):
    SCHEDULED = "scheduled"  # Every 10 interactions
    MANUAL = "manual"  # User requested
    PRE_QUERY = "pre_query"  # Before query processing
```

**ConsolidationStatus** (used by memory-consolidation):
```python
class ConsolidationStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
```

**TemporalType** (used by temporal-rag):
```python
class TemporalType(str, Enum):
    PREFERENCE = "preference"
    STATE = "state"
    EVENT = "event"
    PLAN = "plan"
    FACT = "fact"
```

### 4.2 Integration Points

| Domain A | Domain B | Interface |
|----------|----------|-----------|
| **memory-consolidation** | **temporal-rag** | TemporalRAGService provides temporal metadata for consolidation |
| **memory-consolidation** | **duration-memory** | DurationMemoryService provides duration events for consolidation |
| **temporal-rag** | **C003-agent-pipeline** | RAGDSPyAgent uses TemporalRAGService for context retrieval |
| **memory-consolidation** | **MemoryRepository** | MemoryRepository.consolidate_memories() |
| **duration-memory** | **MemoryRepository** | MemoryRepository.store_memory() for consolidated durations |

### 4.3 Data Flow

```
User Interaction
    ↓
Memory Creation (with temporal metadata)
    ↓
Tier 2 Storage (Qdrant, session-scoped)
    ↓
[After 10 interactions or trigger]
    ↓
Consolidation Triggered
    ↓
MemoryConsolidationEntity.created(PENDING)
    ↓
Retrieve all Tier 2 memories
    ↓
Merge duplicates (same entity/topic)
    ↓
Invalidate outdated facts (new supersedes old)
    ↓
Summarize duration events
    ↓
Store to Tier 3 (Qdrant + Mem0AI)
    ↓
MemoryConsolidationEntity.complete(COMPLETED)
```

---

## 5. Pydantic → Zod Type Mappings

### 5.1 Shared DTOs

**Backend (Pydantic v2)**:
```python
class StoreMemoryCommand(BaseModel):
    content: str
    user_id: str
    temporal_type: Literal["preference", "state", "event", "plan", "fact"] = "fact"
    metadata: Optional[Dict[str, Any]] = None
```

**Frontend (Zod)**:
```typescript
export const StoreMemoryCommandSchema = z.object({
  content: z.string().min(1),
  user_id: z.string().min(1),
  temporal_type: TemporalTypeSchema.default("fact"),
  metadata: z.record(z.any()).optional(),
});
```

---

**Next Artifact**: design.md
