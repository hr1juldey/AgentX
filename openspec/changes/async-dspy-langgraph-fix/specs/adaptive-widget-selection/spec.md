# Spec: Adaptive Widget Selection (Overview)

**Domain**: agent-runtime
**Generated**: 2026-02-02
**Status**: Overview - References granular implementation specs

---

## 1. Purpose

**This is an OVERVIEW spec** that ties together the granular implementation specs for adaptive widget selection.

Define the adaptive widget selection system that dynamically generates UI components based on query complexity and accumulated research findings. This replaces R014's "arbitrary widget dump" with intelligent, content-driven widget selection.

**Problem Statement**: R014 sends maximum types and numbers of widgets no matter what happens, resulting in irrelevant UI clutter and poor user experience. Users see widgets for data that wasn't found or isn't relevant to their query.

**Success Criteria**:
- Only relevant widgets are generated based on actual findings
- Widget selection adapts to query complexity (simple queries get minimal UI)
- Widget types match content types (comparison → table, timeline → chart, etc.)
- No "widget dump" - each widget serves a clear purpose

---

## 2. Granular Implementation Specs

This overview spec references the following granular specs for implementation details:

| Spec | Purpose | Key Components |
|------|---------|----------------|
| [`content-pattern-detection/spec.md`](../content-pattern-detection/spec.md) | Pattern → Widget mapping | comparison → DATA_TABLE, temporal → TIMELINE |
| [`widget-mapping/spec.md`](../widget-mapping/spec.md) | Widget implementations | DataTable, Chart, Timeline, Map components |
| [`progressive-disclosure-ux/spec.md`](../progressive-disclosure-ux/spec.md) | ProgressiveDisclosure component | Show 3 widgets initially, "Show More" button |

---

## 3. Architecture Overview

```
[Evaluator] → finalize
    ↓
[Widget Selector]
    ├─ Analyze accumulated_findings
    ├─ Detect content patterns (content-pattern-detection)
    └─ Select widgets based on patterns
    ↓
[Widget Generator]
    ├─ Generate widget specifications
    ├─ Sort by priority
    └─ Limit count based on task count
    ↓
[Synthesizer]
    ├─ Stream text response
    └─ Include widget specifications
    ↓
[Frontend]
    └─ ProgressiveDisclosure for widgets (progressive-disclosure-ux)
```

---

## 4. Requirements

### 4.1 Functional Requirements

| ID | Requirement | Implementation Spec |
|----|-------------|---------------------|
| FR-AWS-001 | Analyze accumulated findings for widget candidates | content-pattern-detection |
| FR-AWS-002 | Infer widget types from content patterns | content-pattern-detection |
| FR-AWS-003 | Limit widget count based on query complexity | content-pattern-detection |
| FR-AWS-004 | Simple queries (0 tasks) get text-only response | content-pattern-detection |
| FR-AWS-005 | Complex queries get relevant widgets only | content-pattern-detection |
| FR-AWS-006 | Widgets include source attribution | widget-mapping |
| FR-AWS-007 | Widgets support progressive disclosure | progressive-disclosure-ux |

### 4.2 Non-Functional Requirements

| ID | Requirement | Target Metric | Implementation Spec |
|----|-------------|---------------|---------------------|
| NFR-AWS-001 | Widget selection latency | < 500ms | content-pattern-detection |
| NFR-AWS-002 | Max widgets per response | 3-7 widgets | progressive-disclosure-ux |
| NFR-AWS-003 | Simple query widget count | 0-1 widgets | content-pattern-detection |
| NFR-AWS-004 | Widget generation accuracy | >90% relevant | content-pattern-detection |

---

## 5. Business Rules

| Rule | Description | Implementation Spec |
|------|-------------|---------------------|
| BR-AWS-001 | Simple queries (0 tasks) get no widgets | content-pattern-detection |
| BR-AWS-002 | Max widgets based on task count | content-pattern-detection |
| BR-AWS-003 | Widgets sorted by priority | progressive-disclosure-ux |
| BR-AWS-004 | Each widget needs clear purpose | content-pattern-detection |
| BR-AWS-005 | Widgets include source attribution | widget-mapping |
| BR-AWS-006 | No duplicate widget types | content-pattern-detection |

---

## 6. Acceptance Criteria

- [ ] Simple queries (0 tasks) return no widgets
- [ ] Complex queries return relevant widgets only
- [ ] Widget types match content patterns
- [ ] Max widget count enforced based on task count
- [ ] Widgets sorted by priority
- [ ] Each widget includes source attribution
- [ ] No duplicate widget types
- [ ] Widget selection < 500ms
- [ ] Ruff and pyrefly checks pass

---

## 7. Test Scenarios

### 7.1 Simple Query (No Widgets)

| Query | Tasks | Expected Widgets |
|-------|-------|------------------|
| "What is 2+2?" | 0 | None (text-only) |
| "What's the capital of France?" | 0 | None (direct answer) |

### 7.2 Comparison Query (Table Widget)

| Query | Pattern | Expected Widgets |
|-------|---------|-----------------|
| "Compare iPhone 15 vs Pixel 8" | comparison | 1 DATA_TABLE with specs |
| "Top 5 laptops 2024" | ranking | 1 DATA_TABLE or CHART |

### 7.3 Temporal Query (Timeline/Chart)

| Query | Pattern | Expected Widgets |
|-------|---------|-----------------|
| "History of the iPhone" | temporal | 1 TIMELINE or LINE_CHART |
| "Apple stock price 2024" | temporal + numerical | 1 LINE_CHART |

---

## 8. Widget Count Limits

| Task Count | Max Widgets | Rationale |
|------------|-------------|-----------|
| 0 (simple query) | 0 | Direct answer, no research needed |
| 1-2 (light research) | 2-3 | Minimal findings, focused UI |
| 3-5 (moderate research) | 4-5 | Balanced UI |
| 6+ (deep research) | 6-7 | Rich findings, comprehensive UI |

---

## 9. Integration Points

| Spec | Integration Details |
|------|-------------------|
| [`query-complexity-assessment/spec.md`](../query-complexity-assessment/spec.md) | Provides task count for widget limits |
| [`dynamic-routing/spec.md`](../dynamic-routing/spec.md) | Research worker provides findings |
| [`transient-ux/spec.md`](../transient-ux/spec.md) | Progressive disclosure for widget display |

---

## 10. Comparison to R014

| Aspect | R014 | New Design |
|--------|------|------------|
| **Widget count** | Always max (arbitrary dump) | Adaptive (0-7 based on findings) |
| **Widget selection** | Static, predefined | Dynamic, content-driven |
| **Relevance** | Often irrelevant | Only relevant widgets |
| **Simple queries** | Still gets widgets | No widgets (text-only) |
| **Source attribution** | Missing | Included |
| **User control** | None | Progressive disclosure |

---

**Next**: See [`content-pattern-detection/spec.md`](../content-pattern-detection/spec.md) for pattern → widget mapping.
