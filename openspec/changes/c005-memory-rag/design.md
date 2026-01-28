# Design Artifact: c005-memory-rag

**Generated**: 2026-01-28
**Change**: c005-memory-rag
**Schema**: spec-factory v1

---

## 1. Architecture

### 1.1 Component Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      Temporal RAG System Architecture                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Client (Browser/Mobile)                                                │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  Memory UI (Future)                                               │  │
│  │    - Store memory request                                         │  │
│  │    - Search memories                                              │  │
│  │    - Trigger consolidation                                        │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                              ↓ REST (port 8021)                       │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  Memory Routes (FastAPI)                                         │  │
│  │    - POST /api/v1/memory/store                                   │  │
│  │    - POST /api/v1/memory/search                                  │  │
│  │    - POST /api/v1/memory/consolidate                             │  │
│  │    - GET /api/v1/memory/active-states/{user_id}                  │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                              ↓                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  Application Layer (Use Cases)                                   │  │
│  │                                                                  │  │
│  │  ┌──────────────────────┐  ┌──────────────────────┐            │  │
│  │  │ StoreMemoryUseCase   │  │ SearchMemoryUseCase  │            │  │
│  │  └──────────────────────┘  └──────────────────────┘            │  │
│  │                                                                  │  │
│  │  ┌────────────────────────────────────────────────────────┐     │  │
│  │  │  ConsolidateMemoryUseCase                                │     │  │
│  │  │    1. Retrieve Tier 2 memories                          │     │  │
│  │  │    2. Merge duplicates                                   │     │  │
│  │  │    3. Invalidate outdated facts                          │     │  │
│  │  │    4. Summarize durations                                │     │  │
│  │  │    5. Store to Tier 3                                    │     │  │
│  │  └────────────────────────────────────────────────────────┘     │  │
│  │                                                                  │  │
│  │  ┌──────────────────────┐  ┌──────────────────────┐            │  │
│  │  │ TemporalRAGService    │  │ DurationMemoryService│            │  │
│  │  └──────────────────────┘  └──────────────────────┘            │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                              ↓                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  Infrastructure Layer (Adapters)                                │  │
│  │                                                                  │  │
│  │  ┌──────────────────────┐  ┌──────────────────────┐            │  │
│  │  │ QdrantVectorStore    │  │ Mem0MemoryAdapter    │            │  │
│  │  │ (Tier 2 + Tier 3)     │  │ (Tier 3 consolidation)│            │  │
│  │  └──────────────────────┘  └──────────────────────┘            │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Three-Tier Memory Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Three-Tier Memory Architecture                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Tier 1: Session Memory (Redis/In-Memory)                         │   │
│  │    - Active session context                                       │   │
│  │    - Conversation history (current session)                       │   │
│  │    - Temporary state                                              │   │
│  │    - Duration: Session lifetime (hours)                           │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                              ↓ Consolidation                           │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Tier 2: Agent Memory (Qdrant - Session-Scoped)                 │   │
│  │    - Vector embeddings for RAG                                   │   │
│  │    - Session-specific memories                                   │   │
│  │    - Short-term retention (hours)                                │   │
│  │    - Collection: agentx_session_{session_id}                     │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                              ↓ Consolidation                           │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Tier 3: User Memory (Qdrant + Mem0AI - Persistent)             │   │
│  │    - Consolidated long-term memories                             │   │
│  │    - Cross-session persistence                                   │   │
│  │    - Temporal metadata (created_at, valid_until)                │   │
│  │    - Qdrant Collection: agentx_user_{user_id}                   │   │
│  │    - Mem0AI: Advanced summarization                              │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 1.3 Layer Structure (Clean Architecture)

```
agentx/
├── core/                           # Configuration
│   └── memory_config.py            # Memory service settings
├── domain/                         # Business entities
│   ├── entities/
│   │   └── memory_consolidation.py # MemoryConsolidationEntity (@dataclass)
│   └── repositories/
│       └── memory_repository.py    # MemoryRepository (ABC)
├── application/                    # Use case orchestration
│   ├── use_cases/
│   │   ├── store_memory_use_case.py
│   │   ├── search_memory_use_case.py
│   │   └── consolidate_memory_use_case.py
│   ├── services/
│   │   ├── temporal_rag_service.py     # Time-aware RAG
│   │   └── duration_memory_service.py  # State tracking
│   └── dtos/
│       └── memory_dtos.py            # Pydantic DTOs
├── infrastructure/                 # External services
│   └── database/
│       ├── qdrant_vector_store.py  # Qdrant adapter (Tier 2 + 3)
│       └── mem0_memory.py          # Mem0AI adapter (Tier 3)
└── presentation/                   # FastAPI routes
    └── api/v1/
        └── memory_routes.py         # REST endpoints
```

---

## 2. Data Flow

### 2.1 Memory Storage Flow

```
Client sends memory
    ↓
StoreMemoryUseCase.execute()
    ↓
TemporalRAGService.add_temporal_metadata()
    ↓
TemporalRAGService.classify_temporal_type()
    ↓
QdrantVectorStore.store_memory(Tier 2)
    ↓
Returns memory_id with created_at, temporal_type
```

### 2.2 Memory Search Flow (Multi-Hop RAG)

```
Client searches memories
    ↓
SearchMemoryUseCase.execute()
    ↓
TemporalRAGService.build_time_filter() (recent/historical/all)
    ↓
QdrantVectorStore.search_memories(Tier 3, user_id) - Persistent memories
    ↓
QdrantVectorStore.search_memories(Tier 2, session_id) - Session memories
    ↓
Merge + Deduplicate results
    ↓
TemporalRAGService.invalidate_outdated_facts() - Filter superseded
    ↓
TemporalRAGService.weight_results() - Preferences > facts > events
    ↓
Return sorted results with temporal metadata
```

### 2.3 Consolidation Flow

```
Trigger fires (SCHEDULED/MANUAL/PRE_QUERY)
    ↓
ConsolidateMemoryUseCase.execute()
    ↓
MemoryConsolidationEntity.created(PENDING)
    ↓
QdrantVectorStore.get_all_memories(Tier 2, session_id)
    ↓
Group by entity/topic
    ↓
Merge duplicates (keep newest per entity)
    ↓
Invalidate outdated facts (set superseded_by)
    ↓
Summarize duration events (start_state → end_state → duration)
    ↓
Mem0MemoryAdapter.consolidate() - Advanced summarization
    ↓
QdrantVectorStore.store_memory(Tier 3, user_id)
    ↓
QdrantVectorStore.delete_memories(Tier 2, session_id)
    ↓
MemoryConsolidationEntity.complete(COMPLETED)
```

---

## 3. Technical Decisions

| Decision | Option Chosen | Alternatives | Rationale |
|----------|---------------|--------------|-----------|
| **Three-tier memory** | Session → Agent → User | Single-tier, Two-tier | Clear separation, natural consolidation flow |
| **Qdrant for both tiers** | Same API, different collections | Separate DBs | Easier migration, unified API |
| **Mem0AI for Tier 3** | Advanced consolidation | Qdrant-only, Custom LLM | Proven DSPy integration, less work |
| **Temporal types (5)** | preference, state, event, plan, fact | Binary, Free-form | Research-validated, covers all cases |
| **Supersedes tracking** | Mark with superseded_by | Delete old facts, Ignore | Transparent, preserves history |
| **Duration as separate service** | Clean separation from point events | Merge into main memory | Avoids conflating types |
| **Ports 8021-8022** | Memory API + Health | 8000-8014, 8080 | Avoids conflicts (C004 uses 8018-8020) |
| **Consolidation triggers** | SCHEDULED (10), MANUAL, PRE_QUERY | Time-based only, Manual only | Flexible, user-controlled |

---

## 4. Tradeoff Analysis

### 4.1 Approach A: Time-Blind RAG (Standard)

| Aspect | Rating | Notes |
|--------|--------|-------|
| Simplicity | ⭐⭐⭐ | Simple vector search |
| Accuracy | ⭐ | Returns outdated facts |
| User Experience | ⭐ | Contradictions confuse users |

**Pros**:
- Simple implementation (single vector search)
- Fast (no filtering logic)
- Low storage overhead

**Cons**:
- Returns outdated facts (e.g., old preferences)
- No fact invalidation
- Poor UX with contradictory information

### 4.2 Approach B: Temporal RAG (Chosen)

| Aspect | Rating | Notes |
|--------|--------|-------|
| Simplicity | ⭐⭐ | Requires temporal metadata |
| Accuracy | ⭐⭐⭐ | Filters outdated facts |
| User Experience | ⭐⭐⭐ | Consistent with current state |

**Pros**:
- Time-aware retrieval (recent vs historical)
- Fact invalidation (new supersedes old)
- Duration tracking (long-term states)
- Consolidation (prevents unbounded growth)

**Cons**:
- More complex (temporal metadata, filtering)
- Higher storage overhead (additional fields)
- Slower (filtering + merging)

### 4.3 Decision: Temporal RAG

**Rationale**: The accuracy and UX benefits far outweigh complexity. Time-blind RAG causes critical user-facing issues (contradictory information, outdated preferences). Research document provides validated patterns.

---

## 5. Implementation Details

### 5.1 Key Classes/Modules

| Module | Responsibility | Dependencies |
|--------|----------------|--------------|
| **MemoryConsolidationEntity** | Track consolidation state | domain.entities |
| **MemoryRepository** | Abstract interface for memory operations | domain.repositories |
| **ConsolidateMemoryUseCase** | Orchestrate Tier 2 → Tier 3 migration | application.use_cases |
| **TemporalRAGService** | Time-aware search + classification | application.services |
| **DurationMemoryService** | State tracking with durations | application.services |
| **QdrantVectorStoreAdapter** | Qdrant storage (Tier 2 + Tier 3) | infrastructure.database |
| **Mem0MemoryAdapter** | Advanced consolidation | infrastructure.external |

### 5.2 Port Assignments

| Service | Port | Protocol | Purpose |
|---------|------|----------|---------|
| Memory API | 8021 | HTTP | REST endpoints for memory operations |
| Memory Health | 8022 | HTTP | Health check endpoint |

**Note**: Ports 8018-8020 reserved for C004-voice-streaming.

### 5.3 Storage Schema

```python
# Qdrant Collections
# Tier 2: agentx_session_{session_id}
# Tier 3: agentx_user_{user_id}

from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class MemoryPayload(BaseModel):
    """Qdrant payload for stored memories."""
    text: str
    user_id: str
    session_id: Optional[str] = None  # None for Tier 3
    created_at: datetime
    modified_at: datetime
    valid_from: datetime
    valid_until: Optional[datetime] = None
    temporal_type: str  # "preference", "state", "event", "plan", "fact"
    supersedes: list[str] = []  # Memory IDs this one invalidates
    superseded_by: Optional[str] = None  # If this memory is outdated
    embedding: list[float]  # Vector embedding
```

### 5.4 File Structure

```
agentx/
├── domain/entities/
│   └── memory_consolidation.py     # MemoryConsolidationEntity (80 lines)
├── domain/repositories/
│   └── memory_repository.py        # MemoryRepository (ABC, 60 lines)
├── application/use_cases/
│   ├── store_memory_use_case.py    # (80 lines)
│   ├── search_memory_use_case.py   # (100 lines)
│   └── consolidate_memory_use_case.py  # (120 lines)
├── application/services/
│   ├── temporal_rag_service.py     # (150 lines)
│   └── duration_memory_service.py  # (100 lines)
├── application/dtos/
│   └── memory_dtos.py              # (120 lines)
├── infrastructure/database/
│   ├── qdrant_vector_store.py      # (100 lines)
│   └── mem0_memory.py              # (80 lines)
└── presentation/api/v1/
    └── memory_routes.py            # (100 lines)
```

---

## 6. Security Considerations

| Concern | Mitigation |
|---------|------------|
| **Memory injection** | User ID validation, content sanitization |
| **Cross-user access** | User ID filtering on all queries |
| **PII in memories** | No logging of memory content, encrypted storage |
| **DoS (excessive memories)** | Rate limiting, consolidation triggers |
| **Qdrant access** | Internal network only, no public exposure |

---

## 7. Performance Considerations

| Concern | Mitigation |
|---------|------------|
| **Consolidation latency** | Async consolidation, background jobs |
| **Multi-hop search speed** | Parallel Tier 2/3 search, cache Tier 3 |
| **Qdrant capacity** | Consolidation triggers (10 interactions), TTL |
| **Duration state leaks** | Auto-end after 24h, cleanup job |
| **Temporal classification** | Keyword-based initially, DSPy enhancement later |

### 7.1 Consolidation Performance

| Metric | Target | Mitigation |
|--------|--------|------------|
| **Consolidation time** | <30s | Async processing |
| **Merge rate** | >10% | Group by entity/topic |
| **Tier 2 growth** | <1000 memories/session | Trigger at 10 interactions |

### 7.2 Search Performance

| Metric | Target | Mitigation |
|--------|--------|------------|
| **Tier 3 search** | <300ms | Vector indexing |
| **Tier 2 search** | <100ms | Smaller collection |
| **Multi-hop merge** | <100ms | In-memory merge |
| **Total latency** | <500ms | Parallel search |

---

## 8. Integration Points

### 8.1 C003 Agent Pipeline

```python
# Extend RAGDSPyAgent for temporal RAG
from application.services.temporal_rag_service import TemporalRAGService

class RAGDSPyAgent(dspy.Module):
    def retrieve_context(self, query: str, user_id: str) -> dspy.Prediction:
        # Use TemporalRAGService for time-aware search
        memories = temporal_rag_service.search_memories(query, user_id)
        return dspy.Prediction(context=memories)
```

### 8.2 C002 Data Contracts

```python
# Memory DTOs follow C002 patterns
from application.dtos.memory_dtos import StoreMemoryCommand, SearchMemoryResponse
```

---

**Next Artifact**: tasks.md
