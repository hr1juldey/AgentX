# Spec: Transient UX for Long-Running Tasks (Overview)

**Domain**: agent-runtime
**Generated**: 2026-02-02
**Status**: Overview - References granular implementation specs

---

## 1. Purpose

**This is an OVERVIEW spec** that ties together the granular implementation specs for transient UX patterns during long-running AI tasks.

Define the transient UX patterns that keep users engaged during long-running AI tasks (15+ seconds). Users abandon sessions when tasks take too long without feedback.

**Problem Statement**: Even if a task takes 15 minutes, humans won't wait and will leave. We need transient UX to keep them engaged and provide feedback during execution.

**Success Criteria**:
- Users stay engaged during 15-60s tasks
- Progress feedback appears within 300ms
- Streaming responses reduce perceived latency
- "Continue in background" option after 15s

---

## 2. Granular Implementation Specs

This overview spec references the following granular specs for implementation details:

| Spec | Purpose | Key Components |
|------|---------|----------------|
| [`streaming-events/spec.md`](../streaming-events/spec.md) | Streaming event models | TokenEvent, ProgressEvent, BackgroundPromptEvent |
| [`progress-tracking/spec.md`](../progress-tracking/spec.md) | ProgressTracker class | Track progress, emit events every 1-2s |
| [`skeleton-screens/spec.md`](../skeleton-screens/spec.md) | Skeleton screen pattern | Show UI structure within 300ms |
| [`progressive-disclosure-ux/spec.md`](../progressive-disclosure-ux/spec.md) | ProgressiveDisclosure component | Show 3 widgets initially, "Show More" button |

---

## 3. Architecture Overview

```
User Query
    ↓
[Skeleton Screen] (skeleton-screens)
    ├─ Show within 300ms
    └─ Display UI structure
    ↓
[Progress Tracker] (progress-tracking)
    ├─ Track task completion
    ├─ Emit ProgressEvent every 1-2s
    └─ Emit BackgroundPromptEvent after 15s
    ↓
[Synthesizer Node]
    ├─ Stream tokens (streaming-events)
    └─ Emit TokenEvent for each token
    ↓
[Widget Display]
    └─ ProgressiveDisclosure for widgets (progressive-disclosure-ux)
```

---

## 4. Requirements

### 4.1 Functional Requirements

| ID | Requirement | Implementation Spec |
|----|-------------|---------------------|
| FR-UX-001 | Show skeleton within 300ms of user action | skeleton-screens |
| FR-UX-002 | Stream LLM responses token-by-token | streaming-events |
| FR-UX-003 | Progressive disclosure: summary first | progressive-disclosure-ux |
| FR-UX-004 | "Continue in background?" after 15s | progress-tracking |
| FR-UX-005 | Determinate progress for ≥10s tasks | progress-tracking |
| FR-UX-006 | Graceful degradation when streaming unavailable | streaming-events |

### 4.2 Non-Functional Requirements

| ID | Requirement | Target Metric | Implementation Spec |
|----|-------------|---------------|---------------------|
| NFR-UX-001 | Time-to-first-token < 1s | Fast startup | streaming-events |
| NFR-UX-005 | Skeleton appear < 300ms | Immediate feedback | skeleton-screens |
| NFR-UX-006 | Progress update every 1-2s | Regular updates | progress-tracking |

---

## 5. Business Rules

| Rule | Description | Implementation Spec |
|------|-------------|---------------------|
| BR-UX-001 | Skeleton appears < 300ms | skeleton-screens |
| BR-UX-002 | First token < 1s | streaming-events |
| BR-UX-003 | Background prompt at 15s | progress-tracking |
| BR-UX-004 | Progressive disclosure for complex results | progressive-disclosure-ux |
| BR-UX-005 | Fallback to spinner if streaming unavailable | streaming-events |

---

## 6. Acceptance Criteria

- [ ] Skeleton appears within 300ms
- [ ] First token arrives < 1s
- [ ] Progress updates every 1-2s
- [ ] Background prompt appears after 15s
- [ ] Progressive disclosure shows summary first
- [ ] Graceful degradation when streaming fails
- [ ] Ruff and pyrefly checks pass

---

## 7. Test Scenarios

### 7.1 Streaming Response

| Task | Duration | Expected Behavior |
|------|----------|-------------------|
| Simple query | < 5s | Stream tokens, no skeleton needed |
| Moderate query | 15-30s | Skeleton → tokens → complete |
| Complex query | 30-60s | Skeleton → progress → tokens → background prompt? |

### 7.2 Background Prompt

| Elapsed Time | User Action | Expected |
|--------------|-------------|----------|
| < 15s | None | Continue waiting |
| 15s | User clicks "Continue" | Task continues in background, notify when complete |
| 15s | User waits | Task continues normally |

---

## 8. Integration Points

| Spec | Integration Details |
|------|-------------------|
| [`query-complexity-assessment/spec.md`](../query-complexity-assessment/spec.md) | Query planning determines task duration |
| [`adaptive-widget-selection/spec.md`](../adaptive-widget-selection/spec.md) | Widget count affects progressive disclosure |
| [`dynamic-routing/spec.md`](../dynamic-routing/spec.md) | Research worker execution drives progress |

---

## 9. UX Guidelines Summary

| Wait Time | Pattern | Implementation Spec |
|-----------|--------|---------------------|
| < 2s | No indicator needed | Direct response |
| 2-9s | Indeterminate loop | Spinner with "Working..." |
| ≥ 10s | Determinate progress | progress-tracking |
| ≥ 15s | Background continuation | progress-tracking (BackgroundPromptEvent) |
| Any | Skeleton | skeleton-screens (300ms target) |

---

**Next**: See [`streaming-events/spec.md`](../streaming-events/spec.md) for streaming event models.
