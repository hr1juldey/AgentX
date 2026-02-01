# Spec: Episodic Memory (Agent Memory with LangGraph Store)

**Domain**: agent-runtime
**Generated**: 2026-02-01
**Status**: Draft

---

## 1. Purpose

Define the episodic memory system using LangGraph Store for cross-thread, long-term storage of research results. This is "agent memory" (work experience) - cached research that can be retrieved across sessions via semantic search.

**Problem Statement**: Without episodic memory, every query repeats expensive research operations. Users asking the same question get slow responses and wasted compute.

**Success Criteria**:
- Repeated queries return cached results (< 1s vs 20-60s)
- Cache hits reduce research task count dynamically
- Memory is managed to avoid context rot (no overfilling with detail)
- Semantic search finds relevant past research even with different phrasing

---

## 2. Scope

### In Scope

- LangGraph Store for long-term memory (InMemoryStore, PostgresStore, RedisStore)
- Semantic search with embedding models
- Cached research result storage and retrieval
- Namespace organization: ("research", query_hash)
- Consolidation and forgetting policies
- Metadata indexing (timestamp, user_id, outcome)

### Out of Scope

- Graph memory (Checkpointers) - see graph-memory spec for procedural routing
- STT preprocessing - see stt-preprocessing spec
- Transient UX patterns - see transient-ux spec

---

## 3. Requirements

### 3.1 Functional Requirements

| ID | Requirement | Priority | Source |
|----|-------------|----------|--------|
| FR-EM-001 | Store research results in LangGraph Store after execution | Must | Cache hit |
| FR-EM-002 | Query planner checks Store before planning | Must | Cache-first |
| FR-EM-003 | Semantic search by query similarity | Must | LangGraph Store |
| FR-EM-004 | Namespace organization: ("research", query_hash) | Must | Organization |
| FR-EM-005 | Metadata: timestamp, user_id, outcome, tags | Should | Filtering |
| FR-EM-006 | Consolidation: summarize old memories | Should | Space control |
| FR-EM-007 | Forgetting: delete low-value memories | Should | Space control |
| FR-EM-008 | User can delete their memories (privacy) | Must | GDPR/compliance |

### 3.2 Non-Functional Requirements

| ID | Requirement | Priority | Target Metric |
|----|-------------|----------|---------------|
| NFR-EM-001 | Search latency | Must | < 100ms |
| NFR-EM-002 | Storage per memory | Should | < 1 KB average |
| NFR-EM-003 | Max memories per user | Should | 1000-5000 items |
| NFR-EM-004 | Retention period | Should | 30-90 days default |

---

## 4. Data Model

### 4.1 Memory Entry Schema

```python
# domain/models/episodic_memory.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal, Optional
from enum import Enum

class OutcomeQuality(str, Enum):
    """Quality of research outcome."""
    HIGH = "high"           # Direct answer, confident
    MEDIUM = "medium"       # Partial answer, some ambiguity
    LOW = "low"            # Incomplete, needs more research

class RetentionPolicy(str, Enum):
    """How long to keep this memory."""
    SHORT = "short"         # 7 days
    DEFAULT = "default"     # 30 days
    LONG = "long"          # 90 days

# From C005: temporal-rag spec - Temporal types and metadata
class TemporalType(str, Enum):
    """Type of memory for temporal classification (from C005)."""
    PREFERENCE = "preference"   # User preferences (e.g., "likes Italian food")
    STATE = "state"            # Current state (e.g., "planning trip")
    EVENT = "event"            # One-time event (e.g., "went to Paris 2024")
    PLAN = "plan"              # Future plans (e.g., "visiting Japan next month")
    FACT = "fact"              # Factual information (can be superseded)
    RESEARCH = "research"      # Research result (this spec's primary type)

class TemporalMetadata(BaseModel):
    """Temporal metadata for time-aware RAG (aligned with C005)."""
    created_at: datetime = Field(description="When memory was created")
    modified_at: datetime = Field(description="Last modification time")
    valid_from: datetime = Field(description="When this memory becomes valid")
    valid_until: Optional[datetime] = Field(default=None, description="None means still valid")
    temporal_type: TemporalType = Field(default=TemporalType.RESEARCH, description="Memory type")
    supersedes: list[str] = Field(default_factory=list, description="Memory IDs this invalidates")
    superseded_by: Optional[str] = Field(default=None, description="If this memory is outdated")

class EpisodicMemory(BaseModel):
    """A single episodic memory entry in Store (aligned with C005 temporal patterns)."""
    # Primary key (Store key)
    memory_id: str = Field(description="Unique memory identifier (UUID)")

    # Core content
    query: str = Field(description="Original query that led to this memory")
    query_hash: str = Field(description="SHA256 hash of normalized query (for namespace)")
    summary: str = Field(description="Concise summary of research findings (1-2 sentences)")
    result: str = Field(description="Full research result for detailed retrieval")

    # Temporal metadata (from C005 temporal-rag)
    temporal: TemporalMetadata = Field(description="Temporal metadata for RAG")

    # Research-specific quality (this spec's addition)
    outcome_quality: OutcomeQuality = Field(description="Quality of the outcome")
    retention_policy: RetentionPolicy = Field(default=RetentionPolicy.DEFAULT)

    # User and session
    user_id: str = Field(description="User who created this memory")
    session_id: str = Field(description="Session where this was created")

    # Statistics (for consolidation decisions)
    access_count: int = Field(default=0, description="Times this memory was retrieved")
    last_accessed: Optional[datetime] = Field(default=None, description="Last retrieval time")
    success_score: float = Field(default=0.5, ge=0.0, le=1.0, description="How useful this was (0-1)")

    # Tags and entities (for semantic filtering)
    tags: list[str] = Field(default_factory=list, description="Extracted entities/topics")
    domain: Optional[str] = Field(default=None, description="Domain (e.g., 'science', 'history')")

class MemorySearchQuery(BaseModel):
    """Query for searching episodic memories."""
    query: str = Field(description="Search query (semantic)")
    user_id: Optional[str] = Field(default=None, description="Filter by user")
    time_window: Optional[tuple[datetime, datetime]] = Field(default=None, description="Date range")
    min_quality: Optional[OutcomeQuality] = Field(default=None, description="Minimum quality")
    tags: list[str] = Field(default_factory=list, description="Filter by tags")
    limit: int = Field(default=5, ge=1, le=20, description="Max results")
```

### 4.2 LangGraph Store Integration

```python
# infrastructure/memory/langgraph_store_adapter.py
from langgraph.store.base import BaseStore
from langgraph.store.memory import InMemoryStore
from langgraph.store.postgres import PostgresStore
from langgraph.store.redis import RedisStore
from typing import Optional
import hashlib
import uuid

class EpisodicMemoryStore:
    """Adapter for LangGraph Store with episodic memory operations."""

    def __init__(self, store: Optional[BaseStore] = None):
        # Use InMemoryStore for testing, PostgresStore/RedisStore for production
        self.store = store or InMemoryStore()

    def _get_namespace(self, query_hash: str, user_id: str) -> tuple[str, str]:
        """Generate Store namespace for this query."""
        return ("research", query_hash)

    def _normalize_query(self, query: str) -> str:
        """Normalize query for hashing."""
        return query.lower().strip()

    def _hash_query(self, query: str) -> str:
        """Generate SHA256 hash of normalized query."""
        normalized = self._normalize_query(query)
        return hashlib.sha256(normalized.encode()).hexdigest()

    async def store_research_result(
        self,
        query: str,
        user_id: str,
        session_id: str,
        summary: str,
        result: str,
        outcome_quality: OutcomeQuality,
        tags: list[str] = None,
        domain: str = None,
        valid_until: datetime = None,  # Optional expiration
    ) -> str:
        """Store a research result in episodic memory (with C005 temporal metadata)."""
        memory_id = str(uuid.uuid4())
        query_hash = self._hash_query(query)
        namespace = self._get_namespace(query_hash, user_id)

        now = datetime.now()

        memory = EpisodicMemory(
            memory_id=memory_id,
            query=query,
            query_hash=query_hash,
            summary=summary,
            result=result,
            temporal=TemporalMetadata(
                created_at=now,
                modified_at=now,
                valid_from=now,
                valid_until=valid_until,  # None = still valid
                temporal_type=TemporalType.RESEARCH,
                supersedes=[],
                superseded_by=None,
            ),
            outcome_quality=outcome_quality,
            retention_policy=RetentionPolicy.DEFAULT,
            user_id=user_id,
            session_id=session_id,
            tags=tags or [],
            domain=domain,
        )

        # Store in LangGraph Store
        await self.store.aput(namespace, memory_id, memory.model_dump())

        return memory_id

    async def search_research_memories(
        self,
        query: str,
        user_id: str = None,
        limit: int = 5,
    ) -> list[EpisodicMemory]:
        """Search for relevant past research by semantic similarity."""
        query_hash = self._hash_query(query)
        namespace = self._get_namespace(query_hash, user_id or "default")

        # Semantic search in Store (if enabled)
        items = await self.store.asearch(
            namespace,
            query=query,
            limit=limit,
        )

        # Convert to EpisodicMemory objects
        memories = []
        for item in items:
            memory_dict = item.value
            memory_dict["access_count"] = memory_dict.get("access_count", 0) + 1
            memory_dict["last_accessed"] = datetime.now().isoformat()
            memories.append(EpisodicMemory(**memory_dict))

        return memories

    async def get_memory_by_id(self, memory_id: str, user_id: str) -> Optional[EpisodicMemory]:
        """Retrieve a specific memory by ID."""
        # This requires storing inverse mapping (memory_id -> namespace)
        # For now, return None (can be added with secondary index)
        return None

    async def delete_memory(self, memory_id: str, user_id: str) -> bool:
        """Delete a specific memory (for privacy/compliance)."""
        # Requires memory_id -> namespace mapping
        # TODO: Implement with secondary index
        return False

    async def consolidate_old_memories(
        self,
        user_id: str,
        older_than_days: int = 30,
    ) -> int:
        """Consolidate old memories into summaries to save space."""
        # Find memories older than threshold
        # Group by topic/domain
        # Generate summaries
        # Replace old memories with summaries
        # Return count of consolidated memories
        return 0
```

---

## 5. API Contract

### 5.1 Store Operations in Query Planner

```python
# agent/tools/planner/query_planner.py
from infrastructure.memory.langgraph_store_adapter import EpisodicMemoryStore

class QueryPlannerModule(dspy.Module):
    """Generate dynamic execution plan with episodic memory integration."""

    def __init__(self, memory_store: EpisodicMemoryStore = None):
        super().__init__()
        self.plan = dspy.Predict(ExecutionPlanSignature)
        self.memory_store = memory_store

    async def aforward(
        self,
        query: str,
        input_path: str,
        user_id: str,
        available_knowledge: str = "",
    ) -> dspy.Prediction:
        """Generate execution plan with cache lookup."""

        # 1. Search episodic memory for relevant past research
        cached_research = {}
        if self.memory_store:
            memories = await self.memory_store.search_research_memories(
                query=query,
                user_id=user_id,
                limit=5,
            )

            cached_research = {
                m.memory_id: m.summary
                for m in memories
            }

        previous_queries = list(cached_research.keys()) if cached_research else []

        # 2. Include cached research in available knowledge
        enhanced_knowledge = available_knowledge
        if cached_research:
            cache_text = "\n".join(f"- [{k}]: {v}" for k, v in cached_research.items())
            enhanced_knowledge = f"{available_knowledge}\n\nRelevant cached research:\n{cache_text}"

        # 3. Generate plan considering cached research
        return await self.plan.acall(
            query=query,
            input_path=input_path,
            cached_research=str(cached_research),
            previous_queries=str(previous_queries),
            available_knowledge=enhanced_knowledge,
        )
```

### 5.2 Storing Results After Execution

```python
# agent/nodes/research_worker.py
from infrastructure.memory.langgraph_store_adapter import EpisodicMemoryStore

async def research_worker_node(
    state: AgentState,
    *,
    store: BaseStore,  # LangGraph Store from runtime
) -> dict:
    """Execute a single research task and cache result."""

    task: ResearchTask = state["task"]
    memory_store = EpisodicMemoryStore(store)

    # Execute task
    if task.task_type == TaskType.SEARCH:
        module = SearchExecutorModule()
        result = await module.aforward(query=task.query)

    # Store result in episodic memory
    user_id = state.get("user_id", "anonymous")
    session_id = state.get("session_id", "unknown")

    await memory_store.store_research_result(
        query=task.query,
        user_id=user_id,
        session_id=session_id,
        summary=result.text[:200],  # First 200 chars as summary
        result=result.text,
        outcome_quality=OutcomeQuality.HIGH if result.confidence > 0.8 else OutcomeQuality.MEDIUM,
        tags=state.get("current_tags", []),
        domain=state.get("current_domain"),
    )

    return {
        "task_results": {task.task_id: result.text},
        "visited_tasks": [task.task_id],
    }
```

---

## 6. Business Rules

| Rule | Description | Enforcement | Source |
|------|-------------|-------------|--------|
| BR-EM-001 | Check Store before planning | Query planner always searches first | Cache-first |
| BR-EM-002 | Mark tasks as cached if found | Planner sets cached=True on ResearchTask | Skip execution |
| BR-EM-003 | Store results after execution | Worker nodes call store.put() | Future cache |
| BR-EM-004 | Namespace by query hash | ("research", sha256(query)) | Organization |
| BR-EM-005 | Track access statistics | Increment access_count on retrieval | Consolidation |
| BR-EM-006 | Delete on user request | Support GDPR right to erasure | Privacy |
| BR-EM-007 | Consolidate old memories | Summarize memories older than 30 days | Space control |
| BR-EM-008 | No context rot | Limit max memories per user | Performance |

---

## 7. Acceptance Criteria

- [ ] Repeated query returns cached result in < 1s
- [ ] Planner marks tasks as cached when memory found
- [ ] Semantic search finds relevant research with different phrasing
- [ ] Stored results include summary, full result, metadata
- [ ] Namespace pattern: ("research", query_hash)
- [ ] Access statistics tracked (access_count, last_accessed)
- [ ] User can delete their memories
- [ ] Consolidation summarizes old memories
- [ ] Max memories enforced (1000-5000 per user)
- [ ] Ruff and pyrefly checks pass

---

## 8. Test Scenarios

### 8.1 Cache Hit (Repeated Query)

| Query | First Run | Second Run |
|-------|-----------|------------|
| "Compare iPhone 15 vs Pixel 8" | Executes research (10s) | Returns cached (0.1s) |

### 8.2 Semantic Search (Different Phrasing)

| Query 1 | Query 2 | Expected |
|---------|---------|----------|
| "What's the capital of France?" | "France capital city" | Cache hit on query 2 |

### 8.3 Consolidation

| Scenario | Expected Behavior |
|----------|-------------------|
| 1000+ memories, 30+ days old | Summarize into 100-200 consolidated memories |

---

## 9. Memory Management Strategies

### 9.1 Forgetting Policy

```python
# application/memory/forgetting_policy.py
from datetime import datetime, timedelta

class ForgettingPolicy:
    """Decide which memories to keep or forget."""

    async def should_forget(self, memory: EpisodicMemory) -> bool:
        """Decide if a memory should be deleted."""

        # Keep high-quality, frequently accessed memories
        if memory.outcome_quality == OutcomeQuality.HIGH and memory.access_count > 5:
            return False

        # Forget old, low-quality memories
        age = datetime.now() - memory.timestamp
        if age > timedelta(days=90):
            return True

        # Forget low-success memories after 30 days
        if memory.success_score < 0.3 and age > timedelta(days=30):
            return True

        return False

    async def get_retention_days(self, memory: EpisodicMemory) -> int:
        """Get retention period in days."""
        if memory.retention_policy != RetentionPolicy.DEFAULT:
            return {
                RetentionPolicy.SHORT: 7,
                RetentionPolicy.DEFAULT: 30,
                RetentionPolicy.LONG: 90,
            }[memory.retention_policy]

        # Dynamic retention based on quality and access
        if memory.outcome_quality == OutcomeQuality.HIGH and memory.access_count > 10:
            return 90
        elif memory.success_score < 0.3:
            return 7
        else:
            return 30
```

### 9.2 Consolidation Strategy

```python
# application/memory/consolidation.py
class MemoryConsolidation:
    """Consolidate multiple memories into summaries."""

    async def consolidate_by_domain(
        self,
        memories: list[EpisodicMemory],
    ) -> EpisodicMemory:
        """Combine memories in same domain into summary."""

        # Group by domain
        by_domain = {}
        for m in memories:
            by_domain.setdefault(m.domain or "general", []).append(m)

        # For each domain, generate summary using LLM
        summaries = []
        for domain, domain_memories in by_domain.items():
            summary_text = f"{len(domain_memories)} {domain} queries: "
            summary_text += ", ".join([m.query for m in domain_memories[:3]])
            if len(domain_memories) > 3:
                summary_text += f" and {len(domain_memories) - 3} more"

            summaries.append(summary_text)

        # Create consolidated memory
        return EpisodicMemory(
            memory_id=str(uuid.uuid4()),
            query=f"[Consolidated] {len(memories)} queries from {memories[0].timestamp}",
            query_hash="",
            summary="; ".join(summaries),
            result="Consolidated from multiple research results",
            timestamp=datetime.now(),
            user_id=memories[0].user_id,
            session_id="consolidation",
            outcome_quality=OutcomeQuality.MEDIUM,
            access_count=sum(m.access_count for m in memories) // len(memories),
        )
```

---

## 10. References

- **LangGraph Store**: `tests/langgraph_memory.md` (lines 384-824)
- **C005 Memory Specs**:
  - `openspec/changes/c005-memory-rag/specs/temporal-rag/spec.md` - Temporal metadata, fact invalidation
  - `openspec/changes/c005-memory-rag/specs/memory-consolidation/spec.md` - Consolidation patterns
  - `openspec/changes/c005-memory-rag/specs/duration-memory/spec.md` - Duration event handling
- **ColBERTv2 + Qdrant**: Research from tavily_research on episodic memory architecture
- **Neuroscience**: Biological procedural vs episodic memory research
- **DSPy Mem0 ReAct**: `/home/riju279/Downloads/dspy-main/dspy-main/docs/docs/tutorials/mem0_react_agent/`
- **Time Travel**: `tests/langgraph_memory.md` - Checkpointers for graph memory (separate from agent memory)

---

## 11. Memory Types Clarification

**TWO TYPES OF MEMORY** (don't confuse them):

| Type | Purpose | Implementation | Duration |
|------|---------|----------------|----------|
| **Graph Memory** | Procedural routing, short-term state | Checkpointers (InMemorySaver, PostgresSaver) | Per-thread, time-travel enabled |
| **Agent Memory** | Cached research, work experience | Store (InMemoryStore, PostgresStore) | Cross-thread, long-term |

**This spec** defines Agent Memory (Store).
**See `graph-memory/spec.md`** for Graph Memory (Checkpointers).

---

**Next**: See `graph-memory/spec.md` for procedural routing memory.
