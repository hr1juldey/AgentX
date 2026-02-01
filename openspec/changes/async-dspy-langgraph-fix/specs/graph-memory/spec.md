# Spec: Graph Memory / Procedural Routing (Overview)

**Domain**: agent-runtime
**Generated**: 2026-02-02
**Status**: Overview - References granular implementation specs

---

## 1. Purpose

**This is an OVERVIEW spec** that ties together the granular implementation specs for graph memory (procedural routing with LangGraph Checkpointers).

Define the graph memory system using LangGraph Checkpointers for procedural routing. This is "procedural memory" - the graph learns efficient execution paths based on past executions within a thread.

**Problem Statement**: R014 runs a fixed pipeline and forgets why it searched, leading to arbitrary widget dumps. Graph memory enables state-driven routing where the LLM evaluates accumulated state to decide "what do I know vs what do I need."

**Success Criteria**:
- Graph maintains conversation state across iterations
- Evaluator uses accumulated state to decide whether to continue researching
- Routing decisions are based on state (not fragile string parsing)
- Time-travel debugging: inspect and replay past graph states

---

## 2. Granular Implementation Specs

This overview spec references the following granular specs for implementation details:

| Spec | Purpose | Key Components |
|------|---------|----------------|
| [`checkpointers-integration/spec.md`](../checkpointers-integration/spec.md) | PostgresSaver integration | get_state(), get_state_history(), replay |
| [`state-accumulation/spec.md`](../state-accumulation/spec.md) | AgentState with reducers | Annotated[list, add] for accumulation |
| [`evaluator-optimizer/spec.md`](../evaluator-optimizer/spec.md) | Evaluator DSPy module | EvaluateProgressModule, ContinuationDecision |
| [`conditional-routing/spec.md`](../conditional-routing/spec.md) | Routing functions | should_continue_research(), enum-based routing |

---

## 3. Architecture Overview

```
[QueryPlannerModule]
    ↓
[Research Worker] (dynamic via Send API)
    ↓ State accumulation
[AgentState]
    ├─ research_findings: Annotated[list, add]
    ├─ accumulated_confidence: float
    └─ information_gaps: Annotated[list, add]
    ↓
[Evaluator] (evaluator-optimizer)
    ├─ Analyze accumulated state
    └─ Return ContinuationDecision (structured!)
    ↓
[should_continue_research()] (conditional-routing)
    ├─ CONTINUE → assign_workers
    ├─ ADD_TASKS → assign_workers
    └─ FINALIZE → synthesizer
    ↓
[Checkpointers] (checkpointers-integration)
    ├─ Auto-save state after each node
    └─ Enable time-travel debugging
```

---

## 4. Requirements

### 4.1 Functional Requirements

| ID | Requirement | Implementation Spec |
|----|-------------|---------------------|
| FR-GM-001 | Graph state persisted across iterations | checkpointers-integration |
| FR-GM-002 | Accumulate research findings in state | state-accumulation |
| FR-GM-003 | Evaluator uses structured output (not text parsing) | evaluator-optimizer |
| FR-GM-004 | Max iteration limit enforced (safety) | conditional-routing |
| FR-GM-005 | Time-travel: inspect past states | checkpointers-integration |
| FR-GM-006 | State updated with reducers (functional) | state-accumulation |
| FR-GM-007 | thread_id for per-user isolation | checkpointers-integration |

### 4.2 Non-Functional Requirements

| ID | Requirement | Target Metric | Implementation Spec |
|----|-------------|---------------|---------------------|
| NFR-GM-001 | State persistence latency | < 50ms | checkpointers-integration |
| NFR-GM-002 | Checkpoint size | < 10 KB per checkpoint | checkpointers-integration |
| NFR-GM-003 | Max checkpoints per thread | 100-500 | checkpointers-integration |
| NFR-GM-004 | Retention period | 24-72 hours | checkpointers-integration |

---

## 5. Business Rules

| Rule | Description | Implementation Spec |
|------|-------------|---------------------|
| BR-GM-001 | State accumulated with reducers (functional updates) | state-accumulation |
| BR-GM-002 | Evaluator uses structured output only | evaluator-optimizer |
| BR-GM-003 | Max 5 iterations enforced | conditional-routing |
| BR-GM-004 | thread_id isolates conversations | checkpointers-integration |
| BR-GM-005 | State persisted after each node | checkpointers-integration |
| BR-GM-006 | Routing based on accumulated state | evaluator-optimizer |
| BR-GM-007 | Time-travel via get_state_history | checkpointers-integration |

---

## 6. Acceptance Criteria

- [ ] Graph state persisted across iterations
- [ ] Research findings accumulated with reducers
- [ ] Evaluator uses structured output (no text parsing)
- [ ] Max 5 iterations enforced
- [ ] thread_id isolates user conversations
- [ ] Time-travel: can inspect past states
- [ ] Can replay from checkpoint
- [ ] Can modify and replay (alternative paths)
- [ ] Routing decisions based on accumulated state
- [ ] Ruff and pyrefly checks pass

---

## 7. Test Scenarios

### 7.1 State Accumulation

| Iteration | research_findings | accumulated_confidence |
|-----------|-------------------|------------------------|
| 0 | [] | 0.0 |
| 1 | ["Finding 1"] | 0.3 |
| 2 | ["Finding 1", "Finding 2"] | 0.6 |
| 3 | ["Finding 1", "Finding 2", "Finding 3"] | 0.85 |

### 7.2 Evaluator Decision

| Accumulated Confidence | Gaps Remaining | Expected Action |
|------------------------|----------------|-----------------|
| 0.9 | [] | finalize |
| 0.4 | ["key info missing"] | continue_research |
| 0.6 | ["minor detail"] | finalize (good enough) |

### 7.3 Time-Travel

| Operation | Expected Result |
|-----------|-----------------|
| get_state_history(thread_id) | List all checkpoints |
| get(thread_id, checkpoint_id) | Specific state snapshot |
| replay_from_checkpoint | Continue from that point |
| modify_and_replay | Test alternative decisions |

---

## 8. Integration Points

| Spec | Integration Details |
|------|-------------------|
| [`query-complexity-assessment/spec.md`](../query-complexity-assessment/spec.md) | Provides ExecutionPlan |
| [`dynamic-routing/spec.md`](../dynamic-routing/spec.md) | Send API worker creation |
| [`episodic-memory/spec.md`](../episodic-memory/spec.md) | Separate: Graph memory = procedural (Checkpointers), Agent memory = episodic (Store) |

---

## 9. R014 Fixes

| R014 Problem | Design Solution | Implementation Spec |
|--------------|-----------------|---------------------|
| "Forgot why it searched" | State accumulation + evaluator | state-accumulation, evaluator-optimizer |
| Text parsing for routing | Structured `ContinuationDecision` | evaluator-optimizer |
| Fixed pipeline | Dynamic routing based on state | conditional-routing |

---

## 10. Biological Inspiration: Procedural Memory

Graph memory is inspired by biological **procedural memory**:

| Biological | Graph Memory | Implementation Spec |
|------------|--------------|---------------------|
| Corticostriatal circuits (habit) | Checkpointers (routing patterns) | checkpointers-integration |
| Chunking (grouping actions) | State accumulation (findings → decisions) | state-accumulation |
| Model-free RL (stimulus-response) | Evaluator routing (state → action) | evaluator-optimizer |
| Skill learning with practice | Graph improves with more executions | All specs |

**Key insight**: The graph "learns" efficient paths by:
1. Accumulating state (experience)
2. Evaluating progress (dopamine-like quality signals)
3. Routing decisions based on state (habitual responses)

---

## 11. Memory Types Clarification

**THREE TYPES OF MEMORY** (don't confuse them):

| Type | Purpose | Implementation | Duration | Analogy |
|------|---------|----------------|----------|---------|
| **Graph Memory** | Procedural routing, how to navigate | Checkpointers | Per-thread | "Muscle memory" |
| **Agent Memory** | Cached research, what was found | Store | Cross-thread | "Work experience" |
| **Semantic Memory** | Knowledge base, vector search | Qdrant + ColBERT | Long-term | "Knowledge base" |

**This spec** defines Graph Memory (Checkpointers).
**See `episodic-memory/spec.md`** for Agent Memory (Store).
**See `colbert-embedder/spec.md`** for Semantic Memory (Qdrant + ColBERT).

---

**Next**: See [`checkpointers-integration/spec.md`](../checkpointers-integration/spec.md) for PostgresSaver integration.
