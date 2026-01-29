# Extract Artifact: c005-memory-rag

**Generated**: 2026-01-28
**Change**: c005-memory-rag
**Schema**: spec-factory v1

---

## 1. Pattern Catalog

### 1.1 Architectural Patterns

| Pattern | Source | Description | Apply? |
|---------|--------|-------------|--------|
| **Three-Tier Memory** | research:07_temporal_rag.md | Session → Agent (Qdrant) → User (Qdrant+Mem0AI) | ✅ |
| **Temporal Metadata** | research:07_temporal_rag.md | All memories have created_at, valid_from, valid_until | ✅ |
| **Fact Invalidation** | research:07_temporal_rag.md | New facts supersede old ones (supersedes relationship) | ✅ |
| **Consolidation** | research:07_temporal_rag.md + LLD | Periodic Tier 2 → Tier 3 migration | ✅ |
| **Duration Tracking** | research:07_temporal_rag.md | State events have start/end times | ✅ |
| **Multi-Hop RAG** | research:07_temporal_rag.md | Search both Tier 2 and Tier 3, merge results | ✅ |
| **mem0 Agent Memory** | dspy-compounding-engineering | Per-agent persistent memory with conversation history | ✅ NEW |
| **KBPredict Auto-Injection** | dspy-compounding-engineering | Auto-inject KB context before DSPy prediction | ✅ NEW |
| **Hybrid Search (RRF)** | dspy-compounding-engineering | Dense + Sparse retrieval with Reciprocal Rank Fusion | ✅ NEW |
| **Reflection-Based Multi-Hop** | R014 (no NetworkX!) | Completeness assessment, hop planning, iterative search | ✅ NEW |
| **MemoryPredict Wrapper** | dspy-compounding-engineering | Auto-inject agent memory + auto-store interactions | ✅ NEW |
| Clean Architecture | mimicus | Layered separation with domain independence | ✅ |
| Repository Pattern | mimicus | ABC base + implementations | ✅ |

### 1.2 Code Structure Patterns

| Pattern | Example | Apply? |
|---------|---------|--------|
| @dataclass entities | `class MemoryConsolidationEntity:` | ✅ |
| ABC repositories | `class MemoryRepository(ABC):` | ✅ |
| Static mappers | `@staticmethod def to_dto()` | ✅ |
| Use case classes | `class ConsolidateMemoryUseCase:` | ✅ |
| Enum for status | `ConsolidationStatus(str, Enum)` | ✅ |
| Business methods on entity | `entity.start()`, `entity.complete()` | ✅ |

### 1.3 Naming Patterns (to Avoid from Prototypes)

| Pattern | Why Avoid | Alternative |
|-----------|-----------|-------------|
| **Time-blind memory storage** | Returns outdated facts | Add temporal metadata (created_at, valid_until) |
| **No consolidation** | Tier 2 grows unbounded | Periodic Tier 2 → Tier 3 migration |
| **All memories equal** | Preferences ≠ events ≠ states | Classify by temporal_type |
| **No fact invalidation** | Contradictory memories | Track supersedes relationships |
| **Point events only** | Misses long-term states | DurationMemory for state tracking |

### 1.4 RAG Patterns from dspy-compounding-engineering (CRITICAL - R014 doesn't have memory!)

**Memory Architecture** (NEW for AgentX):
```
┌─────────────────────────────────────────────────────────────┐
│                  mem0 Agent Memory                        │
├─────────────────────────────────────────────────────────────┤
│  Collection: mem_{agent_name}_{project_hash}              │
│  Storage: Qdrant + OpenAI LLM (for fact extraction)        │
│  ├── Conversation history (query → result)                │
│  ├── Learned reasoning patterns                            │
│  └── Entity relationship cache (3-hop limit, 7-day TTL)     │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                  MemoryPredict Wrapper                      │
├─────────────────────────────────────────────────────────────┤
│  1. Auto-injects past interactions as context              │
│  2. Calls predictor with augmented kwargs                  │
│  3. Auto-stores interaction after prediction               │
└─────────────────────────────────────────────────────────────┘
```

**KBPredict Auto-Injection Pattern**:
```python
# From dspy-compounding-engineering/utils/knowledge/module.py
class KBPredict(dspy.Module):
    """DSPy Module that wraps dspy.Predict with automatic KB injection."""

    def forward(self, **kwargs):
        # 1. Generate query from kwargs (combine all string inputs)
        query = " ".join([str(v)[:500] for v in kwargs.values() if isinstance(v, str)])

        # 2. Retrieve learnings (hybrid: dense + sparse + RRF)
        kb_context = kb.get_context_string(query=query, tags=self.kb_tags)

        # 3. Inject into largest string field
        if kb_context:
            target_key = max((k for k, v in kwargs.items() if isinstance(v, str)), key=lambda k: len(kwargs[k]))
            kwargs[target_key] = f"{kb_context}\n\n---\n\n{kwargs[target_key]}"

        # 4. Call predictor
        return self.predictor(**kwargs)
```

**Hybrid Search with RRF** (Dense + Sparse):
```python
# From dspy-compounding-engineering/utils/knowledge/learning/learning_retrieval.py
def retrieve_relevant(self, query: str = "", tags: list = None, limit: int = 5):
    """Hybrid search with tag filtering, falls back to disk."""
    # Dense: Vector embeddings (semantic similarity)
    dense = self.embedding_provider.get_embedding(query)

    # Sparse: BM25 keyword matching (exact term overlap)
    sparse = self.embedding_provider.get_sparse_embedding(query)

    # Combined: Reciprocal Rank Fusion (RRF)
    result = self.client.query_points(
        collection_name=self.collection_name,
        prefetch=[
            Prefetch(query=dense, using=None, limit=limit * 2),
            Prefetch(query=sparse, using="text-sparse", limit=limit * 2),
        ],
        query=FusionQuery(fusion=Fusion.RRF),
        limit=limit,
    ).points

    # Fallback: Disk-based keyword matching if Qdrant unavailable
    if not result:
        return self._legacy_search(query, tags, limit)
```

**Key Learnings**:
- mem0 requires OpenAI API key for fact extraction
- Per-agent memory isolation (collection_name includes agent_name)
- Auto-injection: no manual context needed, wrapper handles it
- Fallback pattern: disk-based search if Qdrant unavailable
- Tag-based filtering: `kb_tags=["knowledge-gardening", "patterns"]`

### 1.5 Multi-Hop Search Patterns from R014 (NO NetworkX/PageRank!)

**R014 Reflection-Based Multi-Hop** (Simpler than NetworkX approach):
```
┌──────────────┐
│ User Question│
└──────┬───────┘
       ▼
┌──────────────────────────────────────────────┐
│  HOP LOOP (max_hops=5, stop_threshold=0.85) │
│  ┌────────────────────────────────────────┐  │
│  │ 1. GenerateSearchQuery                 │  │
│  │    (context-aware query refinement)    │  │
│  │ 2. SearXNG Search (privacy-focused)     │  │
│  │ 3. AnswerWithSources (ChainOfThought)  │  │
│  │ 4. CompletenessAssessor                │  │ ← STOP if ≥0.85
│  │ 5. GenerateNextQuery                   │  │    (avoid unnecessary hops)
│  │    (strategy: REFINE_TOPIC/            │  │
│  │     DISCOVER_NEW/VALIDATE_EXPAND)      │  │
│  └────────────────────────────────────────┘  │
└──────────────────────────────────────────────┘
       ▼
┌──────────────────┐
│ SynthesizeFinalAnswer │ Combine all hop results
└──────────────────┘
```

**DSPy Signatures** (from R014 services/multihop_search/signatures.py):
- `GenerateSearchQuery`: context-aware query generation
- `AnswerWithSources`: CoT with inline citations [1], [2]
- `CheckCompleteness`: is_sufficient (bool), confidence (0.0-1.0), gap_description
- `GenerateNextQuery`: outputs strategy (REFINE_TOPIC/DISCOVER_NEW/VALIDATE_EXPAND)
- `SynthesizeFinalAnswer`: combines all_hop_answers, all_context

**Key Components** (from R014):
- `HopOrchestrator`: manages multi-hop loop logic
- `CompletenessAssessor`: stop_threshold (0.85) determines when answer is complete enough
- `ProgressCallback`: real-time UI updates during long-running tasks
- `SearXNGClient`: privacy-focused metasearch at http://192.168.1.4:8080

**Key Differences from NetworkX Approach**:
| Aspect | NetworkX (dspy-compounding) | R014 Reflection |
|--------|----------------------------|-----------------|
| **Graph** | Explicit NetworkX DiGraph | Implicit (reflection-based) |
| **Path Finding** | shortest_path() | GenerateNextQuery with strategy |
| **Stopping** | Fixed hops | CompletenessAssessor (0.85 threshold) |
| **Complexity** | High (graph maintenance) | Low (iterative refinement) |

**AgentX Decision**: Use R014's reflection-based approach (simpler, no NetworkX dependency)

### 1.6 Knowledge Consolidation Patterns

**From dspy-compounding-engineering agents/knowledge_gardener/**:

```
┌─────────────────────────────────────────┐
│     Knowledge Gardener Orchestrator    │
├─────────────────────────────────────────┤
│  1. KBConsolidatorSignature            │
│     ├── Merge duplicate learnings       │
│     ├── Remove noise                    │
│     ├── Categorize entries              │
│     └── Assess confidence               │
│  2. MemoryCompressorSignature          │
│     ├── Deduplicate conversations       │
│     ├── Compress reasoning chains       │
│     └── Track compression metrics       │
│  3. PatternExtractorSignature          │
│     └── Extract reusable patterns        │
└─────────────────────────────────────────┘
```

**Auto-Codification Pattern** (from dspy-compounding-engineering docs):
```python
# After every `work` command execution:
learnings = LearningExtractor.extract_from_todo(
    todo_path=completed_todo,
    changes_made=git_diff
)
for learning in learnings:
    kb.save_learning(learning)  # Auto-stores with tags, category
```

**Knowledge Base Structure**:
```
.knowledge/
├── learnings/
│   ├── 2025-12-01_security_bcrypt.json
│   ├── 2025-12-02_architecture_factory.json
│   └── ...
├── index.json  # Fast lookup by tags/categories
└── AI.md       # Human-readable consolidated learnings
```

**Learning Entry Format**:
```json
{
  "id": "uuid",
  "timestamp": "2025-12-07T10:00:00Z",
  "source": "work|review|triage|manual",
  "context": "When working on authentication",
  "action": "Use bcrypt for password hashing",
  "rationale": "MD5 is cryptographically broken",
  "tags": ["security", "authentication", "hashing"],
  "category": "best_practice"
}
```

---

## 2. Specification Drafts

### 2.1 Draft: memory-consolidation Spec

**Purpose**: Define memory consolidation service that moves memories from Tier 2 (session-scoped Qdrant) to Tier 3 (persistent Qdrant + Mem0AI) with merging, invalidation, and summarization.

**Scope**:
- In scope: Tier 2 → Tier 3 consolidation, duplicate merging, fact invalidation, duration summarization
- Out of scope: Real-time memory updates (handled by C003), UI components

**Locked from LLD**:

```python
# domain_model.md:189-269 (LOCKED)
@dataclass
class MemoryConsolidationEntity:
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

    def start(self) -> None
    def complete(self, processed: int, merged: int, invalidated: int) -> None
    def fail(self, error: str) -> None
    def duration_seconds(self) -> Optional[int]
    def merge_rate(self) -> float
```

**Requirements**:
1. **FR-MC-001**: Service MUST consolidate Tier 2 memories to Tier 3 on trigger
2. **FR-MC-002**: Service MUST merge duplicate memories (same entity/topic)
3. **FR-MC-003**: Service MUST invalidate outdated facts (new supersedes old)
4. **FR-MC-004**: Service MUST summarize duration events into single memories
5. **FR-MC-005**: Service MUST support three triggers: SCHEDULED, MANUAL, PRE_QUERY

**Acceptance Criteria**:
- [ ] Consolidation reduces Tier 2 memory count
- [ ] Duplicate memories merged (merge_rate > 0.1)
- [ ] Outdated facts marked with superseded_by
- [ ] Duration events summarized as single memories
- [ ] ConsolidationEntity status transitions PENDING → IN_PROGRESS → COMPLETED
- [ ] All three triggers work (SCHEDULED, MANUAL, PRE_QUERY)

---

### 2.2 Draft: temporal-rag Spec

**Purpose**: Define time-aware retrieval-augmented generation with temporal filtering, fact invalidation, and multi-hop search across Tier 2 and Tier 3 memories.

**Scope**:
- In scope: Time-aware search, fact invalidation, temporal classification, multi-hop retrieval
- Out of scope: Memory storage (covered by consolidation spec), UI components

**Locked from LLD**:

```python
# domain_model.md:531-592 (LOCKED)
class MemoryRepository(ABC):
    @abstractmethod
    async def search_memories(self, query: str, user_id: str, limit: int = 10) -> List[Dict[str, Any]]: ...

    @abstractmethod
    async def consolidate_memories(self, session_id: UUID, user_id: str) -> MemoryConsolidationEntity: ...
```

**Requirements**:
1. **FR-TR-001**: Service MUST add temporal metadata to all memories (created_at, valid_from, valid_until)
2. **FR-TR-002**: Service MUST classify memory by temporal_type (preference, state, event, plan, fact)
3. **FR-TR-003**: Service MUST support time-filtered search (recent, historical, all)
4. **FR-TR-004**: Service MUST invalidate outdated facts during retrieval
5. **FR-TR-005**: Service MUST search both Tier 2 and Tier 3 (multi-hop)

**Acceptance Criteria**:
- [ ] All memories have temporal metadata
- [ ] Temporal classification accuracy >90%
- [ ] Time-filtered search returns correct time windows
- [ ] Outdated facts filtered or marked with superseded_by
- [ ] Multi-hop search merges Tier 2 and Tier 3 results

---

### 2.3 Draft: duration-memory Spec

**Purpose**: Define duration-aware memory for tracking long-term states (e.g., "watched movie for 2 hours") with start/end timestamps.

**Scope**:
- In scope: State tracking, duration calculation, consolidation of duration events
- Out of scope: Point events (handled by temporal-rag), UI components

**Locked from Research**:

```python
# research:07_temporal_rag.md:271-354
class DurationMemory:
    def start_state(self, state_id, state_type, attributes, user_id)
    def end_state(self, state_id) -> duration_dict
    def get_active_states(self, user_id) -> List[Dict]
```

**Requirements**:
1. **FR-DM-001**: Service MUST track state start time
2. **FR-DM-002**: Service MUST calculate duration on state end
3. **FR-DM-003**: Service MUST store duration as consolidated memory
4. **FR-DM-004**: Service MUST support multiple concurrent states per user

**Acceptance Criteria**:
- [ ] States tracked with start_time
- [ ] Duration calculated correctly (end - start)
- [ ] Duration memory stored to Tier 3 on consolidation
- [ ] Active states queryable by user_id
- [ ] Multiple concurrent states supported

---

## 3. API Contracts

### 3.1 REST Endpoints

| Method | Path | Request | Response |
|--------|------|---------|----------|
| POST | `/api/v1/memory/store` | `StoreMemoryCommand` | `StoreMemoryResponse` |
| POST | `/api/v1/memory/search` | `SearchMemoryCommand` | `SearchMemoryResponse` |
| POST | `/api/v1/memory/consolidate` | `ConsolidateMemoryCommand` | `ConsolidateMemoryResponse` |
| GET | `/api/v1/memory/consolidations/{consolidation_id}` | - | `ConsolidationStatusResponse` |
| GET | `/api/v1/memory/active-states/{user_id}` | - | `ActiveStatesResponse` |
| POST | `/api/v1/memory/start-state` | `StartStateCommand` | `StartStateResponse` |
| POST | `/api/v1/memory/end-state/{state_id}` | - | `EndStateResponse` |

### 3.2 WebSocket Channels

| Channel | Message Type | Schema |
|---------|--------------|--------|
| (None specific) | - | Memory operations use REST only |

### 3.3 Port Assignments

| Service | Port | Purpose |
|---------|------|---------|
| Memory API | 8021 | REST endpoints for memory operations |
| Memory Health | 8022 | Health check endpoint |

**Note**: Ports 8018-8020 reserved for C004-voice-streaming. Using 8021-8022 for memory services.

---

## 4. Data Model Mappings

### 4.1 Pydantic → Zod Mappings

| Pydantic Model | Zod Type | Notes |
|----------------|----------|-------|
| `StoreMemoryCommand` | `StoreMemoryCommandSchema` | Memory storage request |
| `SearchMemoryCommand` | `SearchMemoryCommandSchema` | Memory search request |
| `SearchMemoryResponse` | `SearchMemoryResponseSchema` | Search results with temporal metadata |
| `ConsolidateMemoryCommand` | `ConsolidateMemoryCommandSchema` | Consolidation trigger |
| `ConsolidationStatusResponse` | `ConsolidationStatusResponseSchema` | Consolidation status |

### 4.2 Shared Types

```python
# Backend (Pydantic v2)
# File: application/dtos/memory_dtos.py
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, Dict, Any, Literal

class StoreMemoryCommand(BaseModel):
    """Command to store a memory."""
    content: str = Field(..., min_length=1, description="Memory content")
    user_id: str = Field(..., min_length=1, description="User identifier")
    temporal_type: Literal["preference", "state", "event", "plan", "fact"] = Field(
        default="fact", description="Temporal classification"
    )
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")

class StoreMemoryResponse(BaseModel):
    """Response from memory storage."""
    memory_id: UUID
    created_at: datetime
    temporal_type: str

class SearchMemoryCommand(BaseModel):
    """Command to search memories."""
    query: str = Field(..., min_length=1, description="Search query")
    user_id: str = Field(..., min_length=1, description="User identifier")
    time_filter: Literal["recent", "historical", "all"] = Field(
        default="all", description="Temporal filter"
    )
    limit: int = Field(default=10, ge=1, le=50, description="Max results")

class MemoryResult(BaseModel):
    """Single memory result."""
    memory_id: UUID
    content: str
    temporal_type: str
    created_at: datetime
    valid_from: datetime
    valid_until: Optional[datetime]
    score: float
    superseded_by: Optional[UUID] = None

class SearchMemoryResponse(BaseModel):
    """Response from memory search."""
    results: list[MemoryResult]
    total_found: int

class ConsolidateMemoryCommand(BaseModel):
    """Command to trigger consolidation."""
    session_id: UUID
    user_id: str
    trigger: Literal["scheduled", "manual", "pre_query"]

class ConsolidationStatusResponse(BaseModel):
    """Response with consolidation status."""
    consolidation_id: UUID
    status: Literal["pending", "in_progress", "completed", "failed"]
    memories_processed: int
    memories_merged: int
    memories_invalidated: int
    created_at: datetime
    completed_at: Optional[datetime]
    error_message: Optional[str]
```

```typescript
// Frontend (Zod)
// File: frontend/types/memory.ts
import { z } from "zod";

export const TemporalTypeSchema = z.enum(["preference", "state", "event", "plan", "fact"]);

export const StoreMemoryCommandSchema = z.object({
  content: z.string().min(1),
  user_id: z.string().min(1),
  temporal_type: TemporalTypeSchema.default("fact"),
  metadata: z.record(z.any()).optional(),
});

export const StoreMemoryResponseSchema = z.object({
  memory_id: z.string().uuid(),
  created_at: z.string().datetime(),
  temporal_type: TemporalTypeSchema,
});

export const TimeFilterSchema = z.enum(["recent", "historical", "all"]);

export const SearchMemoryCommandSchema = z.object({
  query: z.string().min(1),
  user_id: z.string().min(1),
  time_filter: TimeFilterSchema.default("all"),
  limit: z.number().min(1).max(50).default(10),
});

export const MemoryResultSchema = z.object({
  memory_id: z.string().uuid(),
  content: z.string(),
  temporal_type: TemporalTypeSchema,
  created_at: z.string().datetime(),
  valid_from: z.string().datetime(),
  valid_until: z.string().datetime().optional(),
  score: z.number(),
  superseded_by: z.string().uuid().optional(),
});

export const SearchMemoryResponseSchema = z.object({
  results: z.array(MemoryResultSchema),
  total_found: z.number(),
});

export const ConsolidationTriggerSchema = z.enum(["scheduled", "manual", "pre_query"]);

export const ConsolidateMemoryCommandSchema = z.object({
  session_id: z.string().uuid(),
  user_id: z.string().min(1),
  trigger: ConsolidationTriggerSchema,
});

export const ConsolidationStatusSchema = z.enum(["pending", "in_progress", "completed", "failed"]);

export const ConsolidationStatusResponseSchema = z.object({
  consolidation_id: z.string().uuid(),
  status: ConsolidationStatusSchema,
  memories_processed: z.number(),
  memories_merged: z.number(),
  memories_invalidated: z.number(),
  created_at: z.string().datetime(),
  completed_at: z.string().datetime().optional(),
  error_message: z.string().optional(),
});
```

---

## 5. Dependencies on Other Specs

| Spec | Dependency Type | Rationale |
|------|-----------------|-----------|
| **C001-folder-structure** | Structural | Provides Clean Architecture layers for memory services |
| **C002-data-contracts** | Contract | Defines base DTO patterns for memory operations |
| **C003-agent-pipeline** | Functional | RAGDSPyAgent uses memory search for context retrieval |
| **domain_model.md LLD** | Locked | MemoryConsolidationEntity, MemoryRepository interface |

---

**Next Artifact**: validate.md
