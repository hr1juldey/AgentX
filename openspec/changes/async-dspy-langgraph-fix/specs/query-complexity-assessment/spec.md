# Spec: Dynamic Query Planning (Overview)

**Domain**: agent-runtime
**Generated**: 2026-02-02
**Status**: Overview - References granular implementation specs

---

## 1. Purpose

**This is an OVERVIEW spec** that ties together the granular implementation specs for dynamic query planning.

Define the dynamic query planning system where the LLM generates an execution plan based on query complexity, available knowledge, and information gaps. The plan DYNAMICALLY determines which workers to create via Send API.

**Problem Statement**: R014 uses a fixed 8-phase pipeline regardless of query complexity. Even "What's 2+2?" goes through multi-hop research, widget selection, and sequencing.

**Success Criteria**:
- Simple queries: Plan returns zero research tasks → direct answer (< 5s)
- Moderate queries: Plan returns 1-3 research tasks → single pass (< 20s)
- Complex queries: Plan returns multi-stage research → iterative execution (< 60s)

---

## 2. Granular Implementation Specs

This overview spec references the following granular specs for implementation details:

| Spec | Purpose | Key Components |
|------|---------|----------------|
| [`query-planner/spec.md`](../query-planner/spec.md) | QueryPlannerModule DSPy class | ExecutionPlanSignature, _check_cache(), aforward() |
| [`execution-plan-models/spec.md`](../execution-plan-models/spec.md) | Pydantic data models | ExecutionPlan, ResearchTask, TaskType, InputPath |
| [`agent-memory-store/spec.md`](../agent-memory-store/spec.md) | LangGraph Store integration | Cache lookup before planning, aput() for storage |
| [`conditional-routing/spec.md`](../conditional-routing/spec.md) | route_by_plan() function | Zero tasks → direct_answer routing |

---

## 3. Architecture Overview

```
Query Input
    ↓
[QueryPlannerModule] (query-planner/spec.md)
    ├─ Check Store for cached research (agent-memory-store/spec.md)
    ├─ Generate ExecutionPlan (execution-plan-models/spec.md)
    └─ Return 0-N ResearchTask objects
    ↓
[route_by_plan()] (conditional-routing/spec.md)
    ├─ 0 uncached tasks → direct_answer
    └─ N uncached tasks → assign_workers
```

---

## 4. Requirements

### 4.1 Functional Requirements

| ID | Requirement | Implementation Spec |
|----|-------------|---------------------|
| FR-QP-001 | System must generate execution plan at graph entry | query-planner |
| FR-QP-002 | Plan must use LLM with structured output | execution-plan-models |
| FR-QP-003 | Plan includes: research tasks, information gaps, expected depth | execution-plan-models |
| FR-QP-004 | Research task count is dynamic (0 to N) | query-planner |
| FR-QP-005 | Input path (text/STT) affects plan complexity | execution-plan-models |
| FR-QP-006 | Plan completes in < 1 second | query-planner |
| FR-QP-007 | Check Store before planning | agent-memory-store |

### 4.2 Non-Functional Requirements

| ID | Requirement | Target Metric | Implementation Spec |
|----|-------------|---------------|---------------------|
| NFR-QP-001 | Plan generation latency | < 1s | query-planner |
| NFR-QP-002 | Task count accuracy | > 85% match actual needs | execution-plan-models |
| NFR-QP-003 | Type safety | Pydantic models | execution-plan-models |

---

## 5. Business Rules

| Rule | Description | Implementation Spec |
|------|-------------|---------------------|
| BR-QP-001 | Zero research tasks → direct answer | conditional-routing |
| BR-QP-002 | STT input → requires_preprocessing=true | execution-plan-models |
| BR-QP-003 | High confidence (> 0.8) → fewer tasks | query-planner |
| BR-QP-004 | Complex queries → staged execution via dependencies | execution-plan-models |
| BR-QP-005 | LangGraph Store checked FIRST before planning | agent-memory-store |
| BR-QP-006 | Cached tasks marked with cached=True + memory_id | execution-plan-models |
| BR-QP-007 | Task results stored in Store after execution | agent-memory-store |

---

## 6. Acceptance Criteria

- [ ] Plan generation completes in < 1s
- [ ] Simple query "What's 2+2?" returns 0 research tasks
- [ ] Complex query returns multiple tasks with dependencies
- [ ] STT input sets requires_preprocessing=true
- [ ] Research tasks include task_type, query, dependencies, priority
- [ ] Store searched before planning (cache-first)
- [ ] Repeated queries mark tasks as cached=True with memory_id
- [ ] Ruff and pyrefly checks pass

---

## 7. Test Scenarios

### 7.1 Simple Queries

| Query | Expected Tasks | Expected Reasoning |
|-------|----------------|-------------------|
| "What's 2+2?" | 0 | "Can answer directly from math knowledge" |
| "What time is it?" | 1 (search current time) | "Needs current time lookup" |
| "Define 'epistemology'" | 0 | "Can answer from vocabulary knowledge" |

### 7.2 Moderate Queries

| Query | Expected Tasks | Expected Pattern |
|-------|----------------|------------------|
| "Compare iPhone 15 vs Pixel 8" | 2-3 (search specs, compare) | Parallel searches |
| "Latest news on AI regulation" | 1-2 (search recent news) | Temporal search |
| "Python fastapi vs flask" | 2-3 (search each, compare) | Parallel + synthesis |

### 7.3 Complex Queries

| Query | Expected Tasks | Expected Pattern |
|-------|----------------|------------------|
| "Analyze AI adoption in healthcare vs finance 2020-2024" | 5-8 (staged) | Domain searches → trends → compare → synthesize |
| "What caused the 2008 financial crisis and what lessons apply today?" | 4-6 (staged) | History search → causes → current relevance → synthesis |
| "Compare climate policies of US, EU, China with economic impact analysis" | 6-10 (staged) | Multiple country searches → economic analysis → comparison |

### 7.4 STT Input

| Input | Expected Behavior |
|-------|-------------------|
| "whats two plus two" | requires_preprocessing=true, then 0 tasks |
| "tell me about the latest iphone" | requires_preprocessing=true, then 1-2 tasks |

---

## 8. Example Plan Output

See [`execution-plan-models/spec.md`](../execution-plan-models/spec.md) for complete ExecutionPlan model definition.

```python
# Example: "Analyze AI adoption in healthcare vs finance 2020-2024"
ExecutionPlan(
    input_path=InputPath.TEXT,
    original_query="Analyze AI adoption in healthcare vs finance 2020-2024",
    requires_preprocessing=False,
    research_tasks=[
        ResearchTask(
            task_id="search_healthcare_ai",
            task_type=TaskType.SEARCH,
            query="AI adoption in healthcare industry 2020-2024 statistics trends",
            dependencies=[],
            priority=1,
            expected_duration=3.0
        ),
        ResearchTask(
            task_id="search_finance_ai",
            task_type=TaskType.SEARCH,
            query="AI adoption in finance banking industry 2020-2024 statistics trends",
            dependencies=[],
            priority=1,
            expected_duration=3.0
        ),
        ResearchTask(
            task_id="compare_sectors",
            task_type=TaskType.SYNTHESIZE,
            query="Compare AI adoption trends between healthcare and finance sectors",
            dependencies=["search_healthcare_ai", "search_finance_ai"],
            priority=2,
            expected_duration=2.0
        ),
    ],
    estimated_depth="deep",
    expected_duration=8.0,
    confidence_can_answer=0.1,
    information_gaps=[
        "Current adoption statistics in healthcare",
        "Current adoption statistics in finance",
        "Comparative analysis between sectors"
    ],
    reasoning="Query requires sector-specific research with temporal focus (2020-2024) and comparative synthesis."
)
```

---

## 9. Integration Points

| Spec | Integration Details |
|------|-------------------|
| [`send-api-workers/spec.md`](../send-api-workers/spec.md) | Consumes ExecutionPlan.research_tasks to create Send objects |
| [`stt-preprocessing/spec.md`](../stt-preprocessing/spec.md) | Provides preprocessed query when InputPath.STT |
| [`conditional-routing/spec.md`](../conditional-routing/spec.md) | route_by_plan() routes based on task count |
| [`evaluator-optimizer/spec.md`](../evaluator-optimizer/spec.md) | Adds new tasks if research is insufficient |

---

**Next**: See [`query-planner/spec.md`](../query-planner/spec.md) for QueryPlannerModule implementation.
