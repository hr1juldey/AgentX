# Specs Artifact: c005-memory-rag

**Generated**: 2026-01-29 (Updated with LangGraph server-driven UI integration)
**Change**: c005-memory-rag
**Schema**: spec-factory v1

---

## 1. Spec: memory-consolidation

**File**: `specs/memory-consolidation/spec.md`

**Purpose**: Define memory consolidation service that moves memories from Tier 2 (session-scoped Qdrant) to Tier 3 (persistent Qdrant + Mem0AI) with merging, invalidation, and summarization.

**Key Requirements**:
- Tier 2 → Tier 3 consolidation on trigger (SCHEDULED, MANUAL, PRE_QUERY)
- Duplicate memory merging (same entity/topic)
- Fact invalidation (new supersedes old)
- Duration event summarization
- UI updates via `push_ui_message()` for consolidation progress

**Acceptance Criteria**:
- [ ] Consolidation reduces Tier 2 memory count
- [ ] Merge rate > 0.1 (10%)
- [ ] Outdated facts marked with superseded_by
- [ ] Duration events summarized
- [ ] UI progress widget displays consolidation status

---

## 2. Spec: temporal-rag

**File**: `specs/temporal-rag/spec.md`

**Purpose**: Define time-aware retrieval-augmented generation with temporal filtering, fact invalidation, and multi-hop search across Tier 2 and Tier 3 memories.

**Key Requirements**:
- Temporal metadata enrichment (created_at, valid_from, valid_until)
- Temporal classification (preference, state, event, plan, fact)
- Time-filtered search (recent, historical, all)
- Fact invalidation during retrieval
- Multi-hop retrieval (Tier 2 + Tier 3)
- Search results emitted via `push_ui_message()`

**Temporal Types**:
`preference`, `state`, `event`, `plan`, `fact`

**Acceptance Criteria**:
- [ ] All memories have temporal metadata
- [ ] Classification accuracy > 90%
- [ ] Time-filtered search within 500ms
- [ ] Multi-hop retrieval +15% better than Tier 3 alone
- [ ] Search results displayed via server-driven UI

---

## 3. Spec: duration-memory

**File**: `specs/duration-memory/spec.md`

**Purpose**: Define duration-aware memory for tracking long-term states (e.g., "watched movie for 2 hours") with start/end timestamps and consolidation.

**Key Requirements**:
- State tracking (start/end times)
- Duration calculation (accurate to 1 second)
- Active states query (within 100ms)
- Multiple concurrent states per user
- Auto-end stale states after 24 hours
- Active state UI updates via `push_ui_message()`

**Acceptance Criteria**:
- [ ] States tracked with start_time
- [ ] Duration calculated correctly
- [ ] Duration memory stored to Tier 3
- [ ] Multiple concurrent states supported
- [ ] Active states displayed via hop progress widgets

---

## 4. Cross-Domain Contracts

### 4.1 Shared Types

| Type | Values | Used By |
|------|--------|---------|
| `ConsolidationTrigger` | SCHEDULED, MANUAL, PRE_QUERY | memory-consolidation |
| `ConsolidationStatus` | PENDING, IN_PROGRESS, COMPLETED, FAILED | memory-consolidation |
| `TemporalType` | preference, state, event, plan, fact | temporal-rag |

### 4.2 Integration Points

| Domain A | Domain B | Interface |
|----------|----------|-----------|
| **memory-consolidation** | **temporal-rag** | TemporalRAGService provides temporal metadata |
| **memory-consolidation** | **duration-memory** | DurationMemoryService provides duration events |
| **temporal-rag** | **C003-agent-pipeline** | RAGDSPyAgent uses TemporalRAGService for context |
| **memory-consolidation** | **MemoryRepository** | MemoryRepository.consolidate_memories() |

### 4.3 Frontend UI Integration (from C007)

| Widget | Purpose | Emission Pattern |
|--------|---------|-----------------|
| `progress` | Consolidation progress | `push_ui_message("progress", {...})` |
| `searchResult` | RAG search results | `push_ui_message("searchResult", {...})` |
| `hopProgress` | Active state tracking | `push_ui_message("hopProgress", {...})` |
| `card` | Status messages | `push_ui_message("card", {...})` |

### 4.4 Component Registration

```typescript
// src/agent/ui.tsx (colocated with graph.py)
export default {
  progress: ProgressComponent,
  searchResult: SearchResultComponent,
  hopProgress: HopProgressComponent,
  card: CardComponent,
};
```

---

## 5. Data Flow

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
UI Progress Widget Updated (via push_ui_message)
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
UI Completion Card Updated (via push_ui_message)
```

---

## 6. Three-Tier Memory Architecture

```
┌─────────────────────────────────────────┐
│  Tier 1: Session Memory                 │
│  (Redis/In-Memory, hours)               │
└─────────────────────────────────────────┘
              ↓ Consolidation
┌─────────────────────────────────────────┐
│  Tier 2: Agent Memory                   │
│  (Qdrant, session-scoped)               │
└─────────────────────────────────────────┘
              ↓ Consolidation
┌─────────────────────────────────────────┐
│  Tier 3: User Memory                    │
│  (Qdrant + Mem0AI, persistent)          │
└─────────────────────────────────────────┘
```

---

## 7. LangGraph Server-Driven UI Integration

### Consolidation Progress Updates

```python
# Emit progress during consolidation
push_ui_message(
    "progress",
    {
        "title": "Consolidating Memories",
        "status": "in_progress",
        "current": processed,
        "total": total,
        "message": f"Merged {merged} duplicates...",
    },
    message=None,
    id=progress_id,
    merge=True
)
```

### Search Results Display

```python
# Emit search results
for result in search_results:
    push_ui_message(
        "searchResult",
        {
            "title": f"Memory {idx + 1}",
            "content": result.content,
            "metadata": {
                "temporalType": result.temporal_type.value,
                "score": result.score,
                "superseded": result.superseded,
            },
        },
        message=message
    )
```

### Active State Tracking

```python
# Emit active state updates
push_ui_message(
    "hopProgress",
    {
        "label": state_type,
        "status": "active",
        "startedAt": datetime.utcnow().isoformat(),
    },
    message=None
)
```

---

**Next Artifact**: design.md
