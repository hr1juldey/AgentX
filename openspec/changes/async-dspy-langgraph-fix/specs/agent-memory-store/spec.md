# Spec: Agent Memory Store

**Domain**: agent-runtime
**Generated**: 2026-02-02
**Status**: Draft

---

## 1. Purpose

Define the LangGraph Store integration for agent memory (cached research results).

**Success Criteria**:
- PostgresStore configured for agent memory
- aput() for storing research results
- asearch() for retrieving cached research
- Namespace pattern: ("research", query_hash)

---

## 2. Scope

### In Scope

- Store adapter for LangGraph PostgresStore
- Cache lookup before planning
- Storage after research completion
- Namespace organization

### Out of Scope

- Temporal metadata (covered by c005-temporal-metadata spec)
- Semantic search (covered by colbert-embedder spec)

---

## 3. Requirements

### 3.1 Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-AMS-001 | MUST use PostgresStore backend | Must |
| FR-AMS-002 | MUST support aput() for storage | Must |
| FR-AMS-003 | MUST support asearch() for retrieval | Must |
| FR-AMS-004 | MUST use namespace pattern ("research", query_hash) | Must |

### 3.2 Non-Functional Requirements

| ID | Requirement | Target Metric |
|----|-------------|---------------|
| NFR-AMS-001 | Cache hit latency | < 1s |
| NFR-AMS-002 | Storage latency | < 500ms |

---

## 4. API Contract

```python
# infrastructure/memory/langgraph_store_adapter.py
from langgraph.store.postgres import PostgresStore
from domain.models.episodic_memory import EpisodicMemory

class AgentMemoryStore:
    """Agent memory: cached research results (Store).

    Purpose: "What was found?" (episodic)
    Analogy: "Work experience"
    Duration: Cross-thread, medium-term (7-30 days)
    """

    def __init__(self):
        DB_URI = "postgresql://postgres:postgres@localhost:5442/postgres?sslmode=disable"
        self.store = PostgresStore.from_conn_string(DB_URI)

    async def store_research_result(
        self,
        query: str,
        user_id: str,
        summary: str,
        result: str,
    ) -> str:
        """Store research result in Store.

        Args:
            query: Original query
            user_id: User ID
            summary: Result summary
            result: Full result

        Returns:
            str: memory_id
        """
        import uuid
        import hashlib

        memory_id = str(uuid.uuid4())
        query_hash = hashlib.sha256(query.lower().encode()).hexdigest()

        # Namespace pattern: ("research", query_hash)
        namespace = ("research", query_hash)

        # Create memory with C005 temporal metadata
        memory = EpisodicMemory(
            memory_id=memory_id,
            query=query,
            summary=summary,
            result=result,
            # ... temporal fields ...
        )

        await self.store.aput(namespace, memory_id, memory.model_dump())
        return memory_id

    async def search_research_memories(
        self,
        query: str,
        user_id: str,
        limit: int = 5,
    ) -> list[EpisodicMemory]:
        """Search for relevant cached research.

        Args:
            query: Search query
            user_id: User ID
            limit: Max results

        Returns:
            list[EpisodicMemory]: Cached research results
        """
        import hashlib

        query_hash = hashlib.sha256(query.lower().encode()).hexdigest()
        namespace = ("research", query_hash)

        # Search by query
        items = await self.store.asearch(
            namespace,
            query=query,
            limit=limit,
        )

        return [EpisodicMemory(**item.value) for item in items]
```

---

## 5. Graph Integration

```python
# In QueryPlannerModule
async def _check_cache(self, query: str) -> ExecutionPlan | None:
    """Check Store for cached execution plan."""
    memories = await self.store.search_research_memories(query, self.user_id)

    if memories:
        # Return cached plan
        return ExecutionPlan(
            query=query,
            needs_research=False,
            research_tasks=[],  # Empty (all cached)
            reasoning="Using cached research results",
        )

    return None

# In research_worker_node
async def research_worker_node(state: AgentState) -> dict:
    """Execute research and store result."""
    task = state["task"]
    result = await execute_task(task)

    # Store result in agent memory
    await self.store.store_research_result(
        query=task.query,
        user_id=state["user_id"],
        summary=result.summary,
        result=result.full_text,
    )

    return {"task_results": {task.task_id: result}}
```

---

## 6. Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| BR-AMS-001 | Namespace pattern | ("research", query_hash) |
| BR-AMS-002 | User isolation | Separate stores per user |
| BR-AMS-003 | Cache before plan | QueryPlanner checks first |

---

## 7. Acceptance Criteria

- [ ] PostgresStore configured
- [ ] aput() stores research results
- [ ] asearch() retrieves cached results
- [ ] Namespace pattern used
- [ ] User isolation enforced
- [ ] Ruff and pyrefly checks pass

---

## 8. Test Scenarios

| Scenario | Expected Result |
|----------|-----------------|
| Second query (same) | Cache hit, < 1s |
| Different query | Cache miss, new research |
| Different user | No cross-user leakage |

---

**Next**: See `c005-temporal-metadata/spec.md` for temporal models.
