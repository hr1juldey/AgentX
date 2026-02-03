# Design Artifact: dspy-fraud-fix

**Generated**: 2026-02-03
**Change**: dspy-fraud-fix
**Schema**: spec-factory v1.0.0

---

## 1. Architecture

### 1.1 Component Diagram

```bash
┌─────────────────────────────────────────────────────────────────────────┐
│                         DSPy Fraud Fix Architecture                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    LangGraph Agent Graph                        │    │
│  │  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │    │
│  │  │ QueryPlanner │───▶│ HybridSearch │───▶│ CacheLookup  │       │    │
│  │  │  (Enhanced)  │    │  Decision    │    │  (Preserved) │       │    │
│  │  └──────────────┘    │   (NEW)      │    └──────────────┘       │    │
│  │                      └──────────────┘                           │    │
│  │                                                                 │    │
│  │  ┌────────────────────────────────────────────────────────┐     │    │
│  │  │              Research Workers (Dynamic)                │     │    │
│  │  │  ┌────────────┐  ┌────────────┐  ┌────────────┐        │     │    │
│  │  │  │ RAGContext │  │  Analyst   │  │ Researcher │        │     │    │
│  │  │  │ Generator  │  │   Agent    │  │   Agent    │        │     │    │
│  │  │  │ (Real RAG) │  │ (Enhanced) │  │ (Enhanced) │        │     │    │
│  │  │  └────────────┘  └────────────┘  └────────────┘        │     │    │
│  │  └────────────────────────────────────────────────────────┘     │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                   │                                     │
│                                   ▼                                     │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │              Conflict Resolution & Synthesis Layer              │    │
│  │  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │    │
│  │  │ RAGConflict  │    │   Hybrid     │    │ Synthesis    │       │    │
│  │  │  Resolution  │───▶│   Search     │───▶│  Service     │       │    │
│  │  │   (NEW)      │    │   Service    │    │  (Enhanced)  │       │    │
│  │  └──────────────┘    └──────────────┘    └──────────────┘       │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                   │                                     │
│                                   ▼                                     │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    Memory & Retrieval Layer                     │    │
│  │  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │    │
│  │  │ MemoryRecord │    │    Mem0      │    │   Qdrant     │       │    │
│  │  │   (NEW)      │◀──▶│   Adapter    │◀──▶│ VectorStore  │       │    │
│  │  │              │    │  (Enhanced)  │    │(ColBERTv2)   │       │    │
│  │  └──────────────┘    └──────────────┘    └──────────────┘       │    │
│  │                                                                 │    │
│  │  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │    │
│  │  │ContextRotMgr │    │Reinforcement │    │ Mem0DSPy     │       │    │
│  │  │   (NEW)      │    │   Tracker    │    │  Retriever   │       │    │
│  │  │              │    │    (NEW)     │    │    (NEW)     │       │    │
│  │  └──────────────┘    └──────────────┘    └──────────────┘       │    │
│  │                                                                 │    │
│  │  ┌──────────────┐    ┌──────────────┐                          │    │
│  │  │  SearchTerm  │    │  TermPattern │                          │    │
│  │  │   Pattern    │───▶│   Service    │                          │    │
│  │  │   (NEW)      │    │    (NEW)     │                          │    │
│  │  └──────────────┘    └──────────────┘                          │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                   │                                     │
│                                   ▼                                     │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                   Session Performance Layer                     │    │
│  │  ┌──────────────┐    ┌──────────────┐                           │    │
│  │  │SessionPerf   │    │ RoutingDecis │                           │    │
│  │  │  Entity      │───▶│   ionService │                           │    │
│  │  │   (NEW)      │    │    (NEW)     │                           │    │
│  │  └──────────────┘    └──────────────┘                           │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Layer Structure (Clean Architecture - PRESERVED)

```bash
agentx/
├── core/                         # Configuration, dependencies (PRESERVED)
│   ├── config.py
│   └── dependency_facades/
│       └── dspy.py               # ✏️ EDIT: cache=False → cache=True
│
├── domain/                       # Business logic (PRESERVED + EXTENDED)
│   ├── entities/                 # ✏️ ADD: memory_record.py, session_performance.py, search_term_pattern.py
│   │   ├── agent_session.py      # ✅ PRESERVED (locked from LLD)
│   │   ├── ui_component.py       # ✅ PRESERVED (locked from LLD)
│   │   ├── memory_record.py      # ✨ NEW: Work-experience memory + SourceType, confidence_score
│   │   ├── session_performance.py # ✨ NEW: Routing performance
│   │   └── search_term_pattern.py # ✨ NEW: Search term patterns for learning
│   ├── repositories/             # ✅ PRESERVED (ABC interfaces)
│   └── services/                 # ✏️ ADD: routing_decision_service.py
│
├── application/                  # Use case orchestration (PRESERVED + EXTENDED)
│   ├── use_cases/
│   └── services/                 # ✏️ ADD: synthesis_service.py, hybrid_search_service.py,
│                               #       rag_conflict_resolution_service.py, search_term_pattern_service.py
│
├── infrastructure/               # External concerns (PRESERVED + EXTENDED)
│   ├── retrieval/                # ✨ NEW: mem0_dspy_retriever.py
│   ├── memory/                   # ✏️ ADD: context_rot_manager.py, reinforcement_tracker.py
│   │   └── mem0_adapter.py       # ✏️ EDIT: Enhance with work-experience support
│   └── database/qdrant/
│       └── qdrant_vector_store.py # ✅ PRESERVED (ColBERTv2)
│
├── agent/                        # DSPy agents (✏️ HEAVY EDITS)
│   ├── dspy_signatures/          # ✨ NEW: Class-based signatures
│   │   ├── analyst.py            # ✨ NEW: 4 signatures
│   │   ├── researcher.py         # ✨ NEW: 3 signatures
│   │   ├── presenter.py          # ✨ NEW: 2 signatures
│   │   ├── designer.py           # ✨ NEW: 3 signatures
│   │   ├── contextualizer.py     # ✨ NEW: 3 signatures
│   │   ├── decision_signatures.py # ✨ NEW: Search guidance
│   │   └── synthesis_signatures.py # ✨ NEW: Multi-source synthesis
│   │
│   ├── dspy_agents/              # ✏️ EDIT: Fix fraud issues
│   │   ├── rag_agent.py          # ✏️ EDIT: Real RAG (was fake)
│   │   ├── agents/
│   │   │   ├── main.py           # ✏️ EDIT: Mem0 integration
│   │   │   ├── analyst.py        # ✏️ EDIT: Mem0 integration
│   │   │   ├── designer.py       # ✏️ EDIT: Mem0 integration
│   │   │   └── memory.py         # ✏️ EDIT: Real memory (was fake)
│   │
│   ├── tools/                    # ✏️ EDIT ALL 24 modules
│   │   ├── analyst/              # ✏️ EDIT: Class signatures + dspy.Prediction
│   │   ├── researcher/           # ✏️ EDIT: Class signatures + dspy.Prediction
│   │   ├── presenter/            # ✏️ EDIT: Class signatures + dspy.Prediction
│   │   ├── contextualizer/       # ✏️ EDIT: Class signatures + dspy.Prediction
│   │   │   └── reranker.py       # ✏️ EDIT: Add actual filtering
│   │   └── designer/             # ✏️ EDIT: Class signatures + dspy.Prediction
│   │
│   └── nodes/                    # ✅ PRESERVED (enhance query_planner only)
│       ├── query_planner.py      # ✏️ ENHANCE: Add memory guidance
│       └── routing_performance.py # ✨ NEW: Performance-based routing
│
└── graph/                        # ✅ PRESERVED (LangGraph compilation)
    └── dynamic_agent_graph.py    # ✅ PRESERVED
```

---

## 2. Data Flow

### 2.1 Query Flow with Memory-Guided Search

```bash
┌─────────────┐
│ User Query  │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│  QueryPlannerNode (ENHANCED, not replaced)                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 1. Retrieve Memory Context (NEW)                     │   │
│  │    └─▶ SearchGuidanceModule.get_user_preferences()   │   │
│  │       Returns: search_depth, terms, sources, format  │   │
│  │                                                      │   │
│  │ 2. Generate ExecutionPlan (PRESERVED)                │   │
│  │    └─▶ QueryPlannerModule.forward()                  │   │
│  │       Returns: ExecutionPlan (0 to N tasks)          │   │
│  │       0 tasks → Direct Answer                        │   │
│  │       N tasks → Research Workers                     │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│  CacheLookupNode (PRESERVED)                                │
│  └─▶ Check agent memory for cached results                  │
└─────────────────────────────────────────────────────────────┘
       │
       ▼ (if cache miss and N > 0 tasks)
┌─────────────────────────────────────────────────────────────┐
│  SendAPI: Create Dynamic Workers (PRESERVED)                │
└─────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│  Research Workers with Real RAG (FIXED)                     │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ RAGContextGenerator (was RAGDSPyAgent)               │   │
│  │  └─▶ Mem0DSPyRetriever(query, user_id)               │   │
│  │      └─▶ Mem0MemoryAdapter.search_memories()         │   │
│  │         └─▶ QdrantVectorStore (ColBERTv2)            │   │
│  │            └─▶ Returns: RetrievedMemory[]            │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Tool Modules (ALL 24 FIXED)                          │   │
│  │  └─▶ Class-based signatures (was inline)             │   │
│  │  └─▶ Return dspy.Prediction (was dict)               │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│  EvaluatorNode (PRESERVED)                                  │
│  └─▶ Continue, Add Tasks, or Finalize                       │
└─────────────────────────────────────────────────────────────┘
       │
       ▼ (if finalize)
┌─────────────────────────────────────────────────────────────┐
│  SynthesizerNode (ENHANCED)                                 │
│  └─▶ RAGConflictResolutionService.resolve_conflicts() (NEW) │
│      └─▶ 4-tier strategy: temporal → confidence → source → LLM│
│  └─▶ HybridSearchService.decide_strategy() (NEW)           │
│      └─▶ RAG vs SearXNG vs both decision                    │
│  └─▶ SynthesisService.synthesize() (NEW)                   │
│      └─▶ Returns: unified_answer, consensus, conflicts      │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Memory Lifecycle Flow

```bash
┌─────────────────────────────────────────────────────────────┐
│  Work-Experience Memory Storage                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Agent completes task                                 │   │
│  │  └─▶ Store MemoryRecord:                             │   │
│  │      • data_input: What agent received               │   │
│  │      • instruction_input: What instructions followed │   │
│  │      • reasoning_done: What reasoning performed      │   │
│  │      • output_produced: What output generated        │   │
│  │      • quality_score: 0.0-1.0                        │   │
│  │      • ttl_days: 30 (default)                        │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│  Memory Retrieval (Adaptive)                                │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Mem0DSPyRetriever.__call__(query, k=20)              │   │
│  │  1. Get k candidates from Mem0                       │   │
│  │  2. Filter: quality >= threshold OR i < min_results  │   │
│  │  3. Return filtered list                             │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│  Context Rotting Prevention                                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ ContextRotManager.check_ttl(memory)                  │   │
│  │  └─▶ Returns: is_expired (boolean)                   │   │
│  │                                                      │   │
│  │ ContextRotManager.apply_decay(memory)                │   │
│  │  └─▶ Reduces quality_score over time                 │   │
│  │                                                      │   │
│  │ ReinforcementTracker.log_outcome(memory_id, success) │   │
│  │  └─▶ Good: extend_ttl(), Bad: shorten_ttl()          │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Technical Decisions

| Decision | Option Chosen | Alternatives | Rationale |
|----------|---------------|--------------|-----------|
| **Retrieval Architecture** | DSPy wraps Mem0, Mem0 wraps Qdrant | Direct dspy-qdrant | Single embedding source (ColBERTv2), avoids duplication |
| **Memory Schema** | Work-experience only (not facts) | Fact/knowledge storage | User requirement: "AGENTS REMEMBER WHAT THEY DID" |
| **Search Planning** | ENHANCE QueryPlanner (not replace) | Replace with memory-driven | PRESERVES existing ExecutionPlan 0-to-N pattern |
| **Signature Style** | Class-based (not inline) | Keep inline strings | Weak LLM compatible (gemma3:4b) |
| **Return Types** | dspy.Prediction (not dict) | Keep dict returns | DSPy standard, enables DSPy features |
| **Quality Filtering** | Actual filtering (not just scoring) | Keep scores only | Fraud #5: scores computed but ignored |
| **Caching** | Enable cache=True | Keep disabled | Fraud #53: performance issue |
| **Implementation Batches** | 2-3 modules per batch | All at once | QA/QC manageable, easier rollback |

---

## 4. Tradeoff Analysis

### 4.1 Approach A: Direct dspy-qdrant Integration

| Aspect | Rating | Notes |
|--------|--------|-------|
| Simplicity | ⭐⭐⭐ | Direct integration, fewer layers |
| Performance | ⭐⭐⭐ | Fewer indirections |
| Maintainability | ⭐ | Duplicate embedding logic |
| Consistency | ⭐ | Different embeddings for Mem0 vs DSPy |

**Pros**:

- Simpler architecture
- Direct Qdrant access

**Cons**:

- **Duplicate embeddings**: DSPy and Mem0 would use separate ColBERT instances
- **Inconsistent search**: Same query returns different results from DSPy vs Mem0
- **Memory fragmentation**: Work-experience memories separate from RAG memories

### 4.2 Approach B: Mem0DSPyRetriever (CHOSEN)

| Aspect | Rating | Notes |
|--------|--------|-------|
| Simplicity | ⭐⭐ | Additional wrapper layer |
| Performance | ⭐⭐ | One indirection via Mem0 |
| Maintainability | ⭐⭐⭐ | Single embedding source |
| Consistency | ⭐⭐⭐ | Same embeddings everywhere |

**Pros**:

- **Single embedding source**: ColBERTv2 used consistently
- **Unified memory**: All memories in one place (Mem0)
- **DSPy-compatible**: Returns format DSPy expects (long_text attribute)
- **Work-experience tracking**: Mem0 can store work patterns

**Cons**:

- Additional layer (Mem0DSPyRetriever)
- Dependent on Mem0 adapter

### 4.3 Decision: Approach B (Mem0DSPyRetriever)

**Rationale**:

1. **User requirement**: "AGENTS REMEMBER WHAT THEY DID" - unified memory is essential
2. **Architecture consistency**: Single ColBERTv2 source prevents fragmentation
3. **DSPy compatibility**: Wrapper returns format DSPy expects
4. **Preserves existing**: Mem0 adapter already working, just wrap it

---

## 5. Implementation Details

### 5.1 Key Classes/Modules

| Module | Responsibility | Dependencies |
|--------|----------------|--------------|
| `MemoryRecord` | Work-experience storage (data, instructions, reasoning, output) + SourceType, confidence_score | dataclasses, UUID, datetime |
| `SessionPerformance` | Route tracking for LangGraph decisions | dataclasses, UUID, RouteOutcome enum |
| `RoutingDecisionService` | Suggest routing strategies based on history | SessionPerformance, Mem0 |
| `SearchGuidanceModule` | Retrieve user preferences for search guidance | DSPy, Mem0 |
| `Mem0DSPyRetriever` | DSPy-compatible retriever wrapping Mem0 | Mem0MemoryAdapter, QdrantVectorStore |
| `ContextRotManager` | TTL, decay, supersede management | MemoryRecord, datetime |
| `ReinforcementTracker` | Retrieval outcome tracking for TTL adjustment | UUID, bool outcomes |
| `SynthesisService` | Combine multiple research sources | DSPy ChainOfThought |
| `RAGConflictResolutionService` | 4-tier conflict resolution: temporal → confidence → source → LLM | MemoryRecord, DSPy |
| `HybridSearchService` | Decision logic: RAG vs SearXNG vs both | DSPy, SearchTermPatternService |
| `SearchTermPatternService` | Learn from past searches, predict terms for new queries | SearchTermPattern, Mem0 |
| `SearchTermPattern` | Pattern entity: topic_type, search_terms, success_count, avg_quality_score | dataclasses, UUID, datetime |
| RAGContextGenerator | Real RAG using Mem0 (was fake) | Mem0DSPyRetriever |
| All 24 tool modules | Fixed: class signatures + dspy.Prediction returns | DSPy signatures |

### 5.2 Port Assignments

| Service | Port | Protocol | Purpose |
|---------|------|----------|---------|
| (No new services - uses existing infrastructure) |

### 5.3 Storage Schema

```python
# Work-Experience Memory (NEW - Extended for Conflict Resolution)
@dataclass
class MemoryRecord:
    memory_id: UUID
    user_id: str
    session_id: str
    memory_type: WorkExperienceType
    data_input: str          # What data agent received
    instruction_input: str   # What instructions agent followed
    reasoning_done: str      # What reasoning agent performed
    output_produced: str     # What output agent generated
    quality_score: float     # 0.0 to 1.0
    source_type: SourceType  # ACADEMIC, REPORT, GENERAL, SOCIAL, UNKNOWN
    access_count: int = 0
    ttl_days: int = 30
    superseded_by: UUID | None = None
    created_at: datetime
    last_accessed_at: datetime | None = None

# Session Performance (NEW)
@dataclass
class SessionPerformance:
    performance_id: UUID
    session_id: str
    user_id: str
    query: str
    route_taken: list[AgentStep]
    overall_outcome: RouteOutcome
    created_at: datetime

@dataclass
class AgentStep:
    agent_name: str
    duration_ms: int
    success: bool
    quality_score: float

# Search Term Pattern (NEW - for Search Term Pattern Memory)
@dataclass
class SearchTermPattern:
    pattern_id: UUID
    user_id: str
    topic_type: TopicType
    search_terms: list[str]
    success_count: int
    fail_count: int
    avg_quality_score: float
    last_used_at: datetime
    created_at: datetime

# Source Type (NEW - for Conflict Resolution)
class SourceType(str, Enum):
    ACADEMIC = "academic"
    REPORT = "report"
    GENERAL = "general"
    SOCIAL = "social"
    UNKNOWN = "unknown"
```

---

## 6. Security Considerations

| Concern | Mitigation |
|---------|------------|
| **Memory Isolation** | user_id enforced in all memory operations |
| **Quality Score Injection** | Validation: 0.0 <= score <= 1.0 |
| **TTL Bypass** | ContextRotManager enforces expiration |
| **Supersede Loop** | Validation: superseded_by must be different UUID |
| **DSPy Cache Poisoning** | Cache key includes query context (user-specific) |

---

## 7. Performance Considerations

| Concern | Mitigation |
|---------|------------|
| **Mem0 Latency** | Configurable k=20 max, quality_threshold=0.6 early exit |
| **Memory Decay Overhead** | Applied on access (lazy), not batch |
| **TTL Check Overhead** | Simple datetime comparison (negligible) |
| **DSPy Cache Size** | Bounded by DSPy internal LRU |
| **Signature Class Loading** | One-time import cost (negligible) |
| **Return Type Wrapping** | dspy.Prediction is lightweight wrapper |

---

## 8. Migration Strategy

### 8.1 Phase 0: Foundation (5 NEW files, 0 breaking changes)

```
Batch 0a: MemoryRecord + enums
Batch 0b: SessionPerformance + RoutingDecisionService
Batch 0b-a: SearchGuidanceModule (enhances QueryPlanner)
Batch 0c: Adaptive Retrieval (Mem0DSPyRetriever)
Batch 0d: ContextRotManager + ReinforcementTracker
```

**Risk**: None (NEW files, no existing code changed)

### 8.2 Phase 1: Critical Content Quality (3 files modified)

```
Batch 1: rag_agent.py (dspy.Predict → Mem0DSPyRetriever)
Batch 2: agents/memory.py (dspy.Predict → Mem0MemoryAdapter)
Batch 3: Specialist agents Mem0 integration
Batch 4: SynthesisService (NEW)
```

**Risk**: Medium (changes core DSPy agents)

### 8.3 Phase 2: Advanced Search Features (6 NEW files for conflict resolution, hybrid search, term patterns)

```
Batch 5: RAG Conflict Resolution
  - MemoryRecord extended with source_type, confidence_score
  - RAGConflictResolutionService (4-tier strategy)
  - SourceType enum (ACADEMIC, REPORT, GENERAL, SOCIAL, UNKNOWN)

Batch 6: SearXNG Hybrid Search
  - HybridSearchService (decision logic: RAG vs SearXNG vs both)
  - QueryCharacteristics enum (CURRENT_EVENTS, PREDICTIONS, WELL_ESTABLISHED, NICHE, CONTRADICTING)
  - SearchStrategy enum (RAG_ONLY, SEARXNG_ONLY, HYBRID)

Batch 7: Search Term Pattern Memory
  - SearchTermPattern entity (topic_type, search_terms, success_count, avg_quality_score)
  - SearchTermPatternService (learn from past searches, predict terms)
  - TopicType enum (HEALTH, FINANCE, TECHNOLOGY, SCIENCE, TRAVEL, GENERAL)
  - Integration with SearchTermExtractorModule (R014 - preserved)
```

**Risk**: Low (NEW services, no breaking changes)

### 8.4 Phase 3: DSPy Anti-Patterns (29 files modified)

```
Batch 8: analyst.py signatures (3 files)
Batch 9: researcher.py signatures (3 files)
Batch 10: presenter.py signatures (2 files)
Batch 11: designer.py signatures (2 files)
Batch 12: contextualizer.py signatures (2 files)
Batch 13: Return types (24 files)
```

**Risk**: Low (mechanical changes, well-defined pattern)

### 8.5 Phase 4: Architecture & Naming (4 files modified)

```
Batch 14: dspy.py (cache=True)
Batch 15: reranker.py (add filtering)
Batch 16: Dead code removal
Batch 17: Module renaming (optional)
```

**Risk**: Very Low (single-line changes, deletions)

---

## 9. Rollback Strategy

Each batch is independently mergeable:

1. **Foundation (Phase 0)**: Can be deployed independently, adds NEW entities
2. **Content Quality (Phase 1)**: If RAG breaks, revert to old rag_agent.py
3. **Advanced Search Features (Phase 2)**: NEW services, can be disabled via config
4. **Anti-Patterns (Phase 3)**: If signature break, revert specific tool module
5. **Architecture (Phase 4)**: Single-line changes, trivial to revert

**Rollback Command** (per batch):

```bash
git revert <commit-hash> --no-edit
```

---

**Next Artifact**: tasks.md
