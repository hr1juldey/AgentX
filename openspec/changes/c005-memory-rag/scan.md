# Scan Artifact: c005-memory-rag

**Generated**: 2026-01-28
**Change**: c005-memory-rag
**Schema**: spec-factory v1

---

## 1. LLD Synthesis

### 1.1 Relevant LLD Documents

| Document | Path | Relevance |
|----------|------|-----------|
| Temporal RAG Research | `docs/research/07_temporal_rag.md` | **PRIMARY** - Temporal metadata, fact invalidation, consolidation patterns |
| Domain Model LLD | `docs/engineering/lld/domain_model.md` | **PRIMARY** - MemoryConsolidationEntity, MemoryRepository interface (LOCKED) |
| Incremental Release Plan | `docs/engineering/lld/incremental_release_plan.md` | **SECONDARY** - Memory consolidation service placement |

### 1.2 Locked Definitions from LLD

**MemoryConsolidationEntity** (domain_model.md:189-269):

```python
@dataclass
class MemoryConsolidationEntity:
    """Represents a memory consolidation operation.

    Consolidation moves memories from Tier 2 (Agent's Qdrant) to Tier 3 (User's Qdrant + Mem0AI).
    """

    # Identity
    consolidation_id: UUID
    session_id: UUID

    # Consolidation control
    trigger: ConsolidationTrigger
    status: ConsolidationStatus

    # Timestamps
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Results
    memories_processed: int = 0
    memories_merged: int = 0
    memories_invalidated: int = 0
    error_message: Optional[str] = None

    # Business methods
    def start(self) -> None
    def complete(self, processed: int, merged: int, invalidated: int) -> None
    def fail(self, error: str) -> None
    def duration_seconds(self) -> Optional[int]
    def merge_rate(self) -> float
```

**ConsolidationTrigger Enum** (domain_model.md:379-385):

```python
class ConsolidationTrigger(str, Enum):
    """Memory consolidation triggers."""
    SCHEDULED = "scheduled"  # Every 10 interactions
    MANUAL = "manual"  # User requested
    PRE_QUERY = "pre_query"  # Before query processing
```

**ConsolidationStatus Enum** (domain_model.md:387-393):

```python
class ConsolidationStatus(str, Enum):
    """Memory consolidation status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
```

**MemoryRepository Interface** (domain_model.md:531-592):

```python
class MemoryRepository(ABC):
    """Repository for memory operations.

    Implementations: QdrantVectorStoreAdapter, Mem0MemoryAdapter
    """

    @abstractmethod
    async def store_memory(self, content: str, user_id: str, metadata: Optional[Dict[str, Any]] = None) -> UUID: ...

    @abstractmethod
    async def search_memories(self, query: str, user_id: str, limit: int = 10) -> List[Dict[str, Any]]: ...

    @abstractmethod
    async def get_all_memories(self, user_id: str) -> List[Dict[str, Any]]: ...

    @abstractmethod
    async def update_memory(self, memory_id: UUID, new_content: str) -> bool: ...

    @abstractmethod
    async def delete_memory(self, memory_id: UUID) -> bool: ...

    @abstractmethod
    async def consolidate_memories(self, session_id: UUID, user_id: str) -> MemoryConsolidationEntity: ...
```

### 1.3 Temporal RAG Patterns (from Research)

**Key Concepts**:
- **Temporal decay** - Old information becomes less relevant
- **Fact invalidation** - New facts override old ones
- **Event sequencing** - Understanding "what happened before X"
- **Duration tracking** - Long-term states vs point events
- **Memory consolidation** - Summarizing over time periods

**Temporal Metadata**:
```python
{
    "text": content,
    "user_id": user_id,
    "created_at": now.isoformat(),
    "modified_at": now.isoformat(),
    "valid_from": now.isoformat(),
    "valid_until": None,  # None means still valid
    "temporal_type": classify_temporal_type(content),
    "supersedes": find_superseded_memories(content, user_id),
    "related_events": find_related_events(content, user_id),
}
```

**Temporal Types**:
- `preference` - "I prefer X"
- `state` - "Currently doing X"
- `event` - "Happened, occurred, did"
- `plan` - "Will, going to"
- `fact` - Default

---

## 2. Codebase Exploration (opsx:explore)

### 2.1 Exploration Topics

```
Forced Topics:
1. Temporal RAG (fact invalidation, time-aware retrieval)
2. Memory consolidation (Tier 2 → Tier 3 migration)
3. Multi-hop RAG (agentic retrieval)
4. Duration-aware memory (state tracking)
5. Integration with C003 agent pipeline
```

### 2.2 File Inventory

#### Backend Files (Existing Patterns)

| File | Lines | Purpose |
|------|-------|---------|
| `prototypes/R011_personal_assistant/backend/service.py` | 216 | DSPy + Mem0AI integration reference |

#### Frontend Files

| File | Lines | Purpose |
|------|-------|---------|
| (None specific for memory) | - | New feature |

---

## 3. Patterns Discovered

### 3.1 Architectural Patterns

**Three-Tier Memory Architecture**:
```
┌─────────────────────────────────────────────────────────┐
│                    Memory Architecture                   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Tier 1: Session Memory (Redis/In-Memory)               │
│    - Active session context                             │
│    - Conversation history (current session)              │
│    - Temporary state                                    │
│                                                         │
│  Tier 2: Agent Memory (Qdrant - Session-Scoped)         │
│    - Vector embeddings for RAG                          │
│    - Session-specific memories                          │
│    - Short-term retention (hours)                       │
│                                                         │
│  Tier 3: User Memory (Qdrant + Mem0AI - Persistent)     │
│    - Consolidated long-term memories                    │
│    - Cross-session persistence                          │
│    - Temporal metadata (created_at, valid_until)        │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Consolidation Flow**:
```
Session End (or trigger)
    ↓
MemoryConsolidationEntity.created(PENDING)
    ↓
retrieve all session memories (Tier 2)
    ↓
merge duplicates (same entity/topic)
    ↓
invalidate outdated facts (newer overrides older)
    ↓
summarize long sequences (duration events)
    ↓
store to Tier 3 (Qdrant + Mem0AI)
    ↓
MemoryConsolidationEntity.complete(COMPLETED)
```

### 3.2 Code Patterns

**Temporal Classification**:
```python
def classify_temporal_type(content: str) -> str:
    keywords = {
        "preference": ["prefer", "like", "love", "favorite"],
        "state": ["currently", "now", "right now"],
        "event": ["happened", "occurred", "did", "went"],
        "plan": ["will", "going to", "planning to"],
    }
```

**Fact Invalidation**:
```python
def invalidate_outdated_facts(results: list) -> list:
    # Group by entity/topic
    # Sort by timestamp (newest first)
    # Keep only latest, mark others as superseded
```

**Duration Tracking**:
```python
class DurationMemory:
    def start_state(state_id, state_type, attributes, user_id)
    def end_state(state_id) -> duration_dict
```

### 3.3 Anti-Patterns to Avoid

| Anti-Pattern | Why Avoid | Alternative |
|--------------|-----------|-------------|
| **Time-blind retrieval** | Returns outdated facts | Use temporal filtering + invalidation |
| **No consolidation** | Tier 2 grows unbounded | Periodic Tier 2 → Tier 3 migration |
| **All memories equal** | Preferences ≠ events ≠ states | Classify by temporal_type |
| **No fact invalidation** | Contradictory memories | Track supersedes relationships |
| **Point events only** | Misses long-term states | DurationMemory for state tracking |

---

## 4. Reference Analysis

### 4.1 Research Extracted Patterns

**Best Practices**:
1. **Always add temporal metadata** - created_at, valid_from, valid_until
2. **Classify memory type** - preference, state, event, plan, fact
3. **Invalidate outdated facts** - New supersedes old
4. **Consolidate periodically** - Every 10 interactions or session end
5. **Filter by time** - Recent vs historical search
6. **Track durations** - State events have start/end

### 4.2 Multi-Hop Agentic RAG Pattern

```
User Query
    ↓
RAGDSPyAgent.retrieve_context()
    ↓
Search Tier 3 (User Memory) - Top 10 results
    ↓
Search Tier 2 (Session Memory) - Top 5 results
    ↓
Merge + Deduplicate
    ↓
Filter by temporal_type (preferences weighted higher)
    ↓
Invalidate outdated facts (keep newest per entity)
    ↓
RAGDSPyAgent.should_inject_context()
    ↓
Filter + Format for MainDSPyReActAgent
```

---

## 5. Key Files for This Change

```
# Research Documents (PRIMARY)
/home/riju279/Documents/Code/XRIG/AgentX/docs/research/07_temporal_rag.md

# LLD Documents (LOCKED)
/home/riju279/Documents/Code/XRIG/AgentX/docs/engineering/lld/domain_model.md

# Dependency Artifacts
/home/riju279/Documents/Code/XRIG/AgentX/openspec/changes/c001-folder-structure/ (Clean Architecture)
/home/riju279/Documents/Code/XRIG/AgentX/openspec/changes/c002-data-contracts/ (Memory DTOs)
/home/riju279/Documents/Code/XRIG/AgentX/openspec/changes/c003-agent-pipeline/ (RAGDSPyAgent extension)
```

---

**Next Artifact**: extract.md
