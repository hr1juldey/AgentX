# Spec: Dynamic State-Driven Routing (Overview)

**Domain**: agent-runtime
**Generated**: 2026-02-02
**Status**: Overview - References granular implementation specs

---

## 1. Purpose

**This is an OVERVIEW spec** that ties together the granular implementation specs for dynamic routing with Send API.

Define the dynamic routing system where the LLM uses accumulated state to decide execution paths via Send API. Workers are created DYNAMICALLY based on the execution plan, not pre-defined static nodes.

**Problem Statement**: R014 uses fragile text parsing (`"needs more research: true"`) for routing decisions and has a fixed 8-node pipeline regardless of query complexity.

**Success Criteria**:
- Zero tasks → direct answer (no workers created)
- Cached tasks → skipped (memory_id used directly)
- Parallel independent tasks → executed concurrently via Send
- Staged dependent tasks → executed in dependency order

---

## 2. Granular Implementation Specs

This overview spec references the following granular specs for implementation details:

| Spec | Purpose | Key Components |
|------|---------|----------------|
| [`send-api-workers/spec.md`](../send-api-workers/spec.md) | assign_workers() node | Send API worker creation, dependency resolution |
| [`evaluator-optimizer/spec.md`](../evaluator-optimizer/spec.md) | Evaluator-optimizer DSPy module | EvaluateProgressModule, ContinuationDecision |
| [`conditional-routing/spec.md`](../conditional-routing/spec.md) | Routing functions | route_by_plan(), should_continue_research() |
| [`state-accumulation/spec.md`](../state-accumulation/spec.md) | AgentState with reducers | Annotated[list, add] for accumulation |

---

## 3. Architecture Overview

```
[QueryPlannerModule]
    ↓ ExecutionPlan with 0-N tasks
    ↓
[route_by_plan()] (conditional-routing)
    ├─ 0 uncached tasks → direct_answer
    └─ N uncached tasks → assign_workers
        ↓
[assign_workers()] (send-api-workers)
    ├─ Filter ready tasks (dependencies satisfied)
    ├─ Create Send objects
    └─ Return list[Send]
        ↓
[research_worker] (dynamic worker nodes)
    ├─ Execute task
    ├─ Store result in state
    └─ Accumulate findings
        ↓
[Evaluator] (evaluator-optimizer)
    ├─ Analyze accumulated state
    └─ Return ContinuationDecision
        ↓
[should_continue_research()] (conditional-routing)
    ├─ CONTINUE → assign_workers
    ├─ ADD_TASKS → assign_workers (with new tasks)
    └─ FINALIZE → synthesizer
```

---

## 4. Requirements

### 4.1 Functional Requirements

| ID | Requirement | Implementation Spec |
|----|-------------|---------------------|
| FR-DR-001 | Workers created dynamically via Send API | send-api-workers |
| FR-DR-002 | Cached tasks skipped (memory_id used) | send-api-workers |
| FR-DR-003 | Independent tasks executed in parallel | send-api-workers |
| FR-DR-004 | Dependent tasks executed in order | send-api-workers |
| FR-DR-005 | Evaluator uses structured output (not text parsing) | evaluator-optimizer |
| FR-DR-006 | State accumulated during execution for decisions | state-accumulation |
| FR-DR-007 | Max iteration limit enforced (safety) | conditional-routing |
| FR-DR-008 | Zero tasks routes to direct_answer | conditional-routing |

### 4.2 Non-Functional Requirements

| ID | Requirement | Target Metric | Implementation Spec |
|----|-------------|---------------|---------------------|
| NFR-DR-001 | Routing decision latency | < 100ms | conditional-routing |
| NFR-DR-002 | No fragile string parsing | Structured output only | evaluator-optimizer |
| NFR-DR-003 | State immutability | Functional updates | state-accumulation |

---

## 5. Business Rules

| Rule | Description | Implementation Spec |
|------|-------------|---------------------|
| BR-DR-001 | Zero tasks → skip workers, direct answer | conditional-routing |
| BR-DR-002 | Cached tasks → load from Store, skip execution | send-api-workers |
| BR-DR-003 | Dependencies must be satisfied before execution | send-api-workers |
| BR-DR-004 | Max 5 research iterations (safety) | conditional-routing |
| BR-DR-005 | Decisions use structured output only | evaluator-optimizer |
| BR-DR-006 | State accumulated across iterations | state-accumulation |
| BR-DR-007 | Task results stored in Store after execution | agent-memory-store |

---

## 6. Acceptance Criteria

- [ ] Workers created dynamically via Send API (not fixed nodes)
- [ ] Cached tasks skipped with memory_id lookup
- [ ] Independent tasks executed in parallel
- [ ] Dependent tasks wait for dependencies
- [ ] Evaluator uses structured output (no text parsing)
- [ ] Max 5 iterations enforced
- [ ] Task results stored in Store
- [ ] Ruff and pyrefly checks pass

---

## 7. Test Scenarios

### 7.1 Simple Query (Zero Tasks)

| Query | Plan | Expected Execution |
|-------|------|-------------------|
| "What's 2+2?" | 0 tasks | direct_answer node, no workers |

### 7.2 Cached Query (Memory Hit)

| Query | Memory State | Expected Execution |
|-------|-------------|-------------------|
| "Compare iPhone 15 vs Pixel 8" (repeated) | Previous result in Store | Tasks marked cached=True, workers skipped |

### 7.3 Parallel Independent Tasks

| Query | Plan | Expected Execution |
|-------|------|-------------------|
| "Compare iPhone 15 vs Pixel 8" | 2 independent tasks | 2 workers created, execute concurrently |

### 7.4 Staged Dependent Tasks

| Query | Plan | Expected Execution |
|-------|------|-------------------|
| "Analyze AI adoption in healthcare vs finance" | 3 tasks with dependencies | Task 1,2 parallel → Task 3 waits → executes |

### 7.5 Dynamic Task Addition

| Query | Scenario | Expected Behavior |
|-------|----------|-------------------|
| Complex query | After 2 iterations, quality still low | Evaluator adds new tasks to plan |

---

## 8. Integration Points

| Spec | Integration Details |
|------|-------------------|
| [`query-complexity-assessment/spec.md`](../query-complexity-assessment/spec.md) | Provides ExecutionPlan for worker creation |
| [`agent-memory-store/spec.md`](../agent-memory-store/spec.md) | Stores/retrieves cached research results |
| [`checkpointers-integration/spec.md`](../checkpointers-integration/spec.md) | Persists state across iterations |
| [`stt-preprocessing/spec.md`](../stt-preprocessing/spec.md) | Preprocesses STT input before planning |

---

## 9. R014 Fixes

| R014 Problem | Design Solution | Implementation Spec |
|--------------|-----------------|---------------------|
| Fixed 8-phase pipeline | Dynamic worker creation (0-N tasks) | send-api-workers |
| "Forgot why it searched" | State accumulation + evaluator | state-accumulation, evaluator-optimizer |
| Text parsing for routing | Structured `ContinuationDecision` | evaluator-optimizer |
| No memory integration | Store for cached research | agent-memory-store |

---

**Next**: See [`send-api-workers/spec.md`](../send-api-workers/spec.md) for Send API implementation.
