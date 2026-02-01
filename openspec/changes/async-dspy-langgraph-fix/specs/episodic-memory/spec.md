# Spec: Episodic Memory / Agent Memory (Overview)

**Domain**: agent-runtime
**Generated**: 2026-02-02
**Status**: Overview - References granular implementation specs

---

## 1. Purpose

**This is an OVERVIEW spec** that ties together the granular implementation specs for agent memory (episodic memory with LangGraph Store).

Define the episodic memory system using LangGraph Store for cross-thread, long-term storage of research results. This is "agent memory" (work experience) - cached research that can be retrieved across sessions via semantic search.

**Problem Statement**: Without episodic memory, every query repeats expensive research operations. Users asking the same question get slow responses and wasted compute.

**Success Criteria**:
- Repeated queries return cached results (< 1s vs 20-60s)
- Cache hits reduce research task count dynamically
- Memory is managed to avoid context rot (no overfilling with detail)
- Semantic search finds relevant past research even with different phrasing

---

## 2. Granular Implementation Specs

This overview spec references the following granular specs for implementation details:

| Spec | Purpose | Key Components |
|------|---------|----------------|
| [`agent-memory-store/spec.md`](../agent-memory-store/spec.md) | PostgresStore integration | aput(), asearch(), namespace pattern |
| [`mem0-consolidation/spec.md`](../mem0-consolidation/spec.md) | Mem0AI integration | Consolidation, quality filtering |
| [`c005-temporal-metadata/spec.md`](../c005-temporal-metadata/spec.md) | Temporal metadata | TemporalMetadata, TemporalType, supersedes |
| [`colbert-embedder/spec.md`](../colbert-embedder/spec.md) | ColBERTv2 embeddings | Semantic search in Store |

---

## 3. Architecture Overview

```
Query Input
    ↓
[QueryPlannerModule]
    ├─ Check Store for cached research (agent-memory-store)
    ├─ Use ColBERT embeddings for semantic search (colbert-embedder)
    └─ Return ExecutionPlan with cached=True for hits
    ↓
[Research Worker]
    ├─ Execute task
    └─ Store result in Store (agent-memory-store)
        ├─ With C005 temporal metadata (c005-temporal-metadata)
        └─ With ColBERT embeddings (colbert-embedder)
    ↓
[Consolidation] (background job)
    ├─ Quality filtering (mem0-consolidation)
    └─ Summarize old memories
```

---

## 4. Requirements

### 4.1 Functional Requirements

| ID | Requirement | Implementation Spec |
|----|-------------|---------------------|
| FR-EM-001 | Store research results in LangGraph Store | agent-memory-store |
| FR-EM-002 | Query planner checks Store before planning | agent-memory-store |
| FR-EM-003 | Semantic search by query similarity | colbert-embedder |
| FR-EM-004 | Namespace organization: ("research", query_hash) | agent-memory-store |
| FR-EM-005 | C005 temporal metadata integration | c005-temporal-metadata |
| FR-EM-006 | Consolidation: summarize old memories | mem0-consolidation |
| FR-EM-007 | Forgetting: delete low-value memories | mem0-consolidation |
| FR-EM-008 | User can delete their memories (privacy) | agent-memory-store |

### 4.2 Non-Functional Requirements

| ID | Requirement | Target Metric | Implementation Spec |
|----|-------------|---------------|---------------------|
| NFR-EM-001 | Search latency | < 100ms | agent-memory-store |
| NFR-EM-002 | Storage per memory | < 1 KB average | agent-memory-store |
| NFR-EM-003 | Max memories per user | 1000-5000 items | mem0-consolidation |
| NFR-EM-004 | Retention period | 30-90 days default | c005-temporal-metadata |

---

## 5. Business Rules

| Rule | Description | Implementation Spec |
|------|-------------|---------------------|
| BR-EM-001 | Check Store before planning | agent-memory-store |
| BR-EM-002 | Mark tasks as cached if found | agent-memory-store |
| BR-EM-003 | Store results after execution | agent-memory-store |
| BR-EM-004 | Namespace by query hash | agent-memory-store |
| BR-EM-005 | Track access statistics | agent-memory-store |
| BR-EM-006 | Delete on user request | agent-memory-store |
| BR-EM-007 | Consolidate old memories | mem0-consolidation |
| BR-EM-008 | C005 temporal types used | c005-temporal-metadata |

---

## 6. Acceptance Criteria

- [ ] Repeated query returns cached result in < 1s
- [ ] Planner marks tasks as cached when memory found
- [ ] Semantic search finds relevant research with different phrasing
- [ ] Stored results include summary, full result, metadata
- [ ] Namespace pattern: ("research", query_hash)
- [ ] C005 temporal metadata attached
- [ ] Access statistics tracked (access_count, last_accessed)
- [ ] User can delete their memories
- [ ] Consolidation summarizes old memories
- [ ] Max memories enforced (1000-5000 per user)
- [ ] Ruff and pyrefly checks pass

---

## 7. Test Scenarios

### 7.1 Cache Hit (Repeated Query)

| Query | First Run | Second Run |
|-------|-----------|------------|
| "Compare iPhone 15 vs Pixel 8" | Executes research (10s) | Returns cached (0.1s) |

### 7.2 Semantic Search (Different Phrasing)

| Query 1 | Query 2 | Expected |
|---------|---------|----------|
| "What's the capital of France?" | "France capital city" | Cache hit on query 2 |

### 7.3 Consolidation

| Scenario | Expected Behavior |
|----------|-------------------|
| 1000+ memories, 30+ days old | Summarize into 100-200 consolidated memories |

---

## 8. Integration Points

| Spec | Integration Details |
|------|-------------------|
| [`query-complexity-assessment/spec.md`](../query-complexity-assessment/spec.md) | Planner checks Store before generating plan |
| [`dynamic-routing/spec.md`](../dynamic-routing/spec.md) | Workers store results after execution |
| [`graph-memory/spec.md`](../graph-memory/spec.md) | Separate: Graph memory = procedural (Checkpointers), Agent memory = episodic (Store) |

---

## 9. Memory Types Clarification

**THREE TYPES OF MEMORY** (don't confuse them):

| Type | Purpose | Implementation | Duration | Analogy |
|------|---------|----------------|----------|---------|
| **Graph Memory** | Procedural routing, how to navigate | Checkpointers | Per-thread | "Muscle memory" |
| **Agent Memory** | Cached research, what was found | Store | Cross-thread | "Work experience" |
| **Semantic Memory** | Knowledge base, vector search | Qdrant + ColBERT | Long-term | "Knowledge base" |

**This spec** defines Agent Memory (Store).
**See `graph-memory/spec.md`** for Graph Memory (Checkpointers).
**See `colbert-embedder/spec.md`** for Semantic Memory (Qdrant + ColBERT).

---

**Next**: See [`agent-memory-store/spec.md`](../agent-memory-store/spec.md) for PostgresStore integration.
