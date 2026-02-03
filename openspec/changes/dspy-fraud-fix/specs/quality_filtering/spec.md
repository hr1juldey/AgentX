# Spec: Quality Filtering

**Domain**: quality_filtering
**Generated**: 2026-02-03
**Status**: Draft

---

## 1. Purpose

Enable actual quality-based filtering in reranker. Add threshold parameter.

**Problem Statement**: reranker.py computes scores but doesn't filter (Fraud #5). All results returned regardless of quality.

**Success Criteria**: reranker.py filters results by threshold; returns filtered list with counts.

---

## 2. Scope

### In Scope

- Add quality threshold parameter (default 0.6)
- Filter results by quality_score >= threshold
- Return filtered list with counts
- Return type is dspy.Prediction

### Out of Scope

- Changing scoring logic (only filtering)

---

## 3. Requirements

### 3.1 Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| RF-QF-001 | reranker.py filters results by threshold | Must |
| RF-QF-002 | Default threshold is 0.6 | Must |
| RF-QF-003 | Returns dspy.Prediction with filtered_results, original_count, filtered_count | Must |

### 3.2 Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-QF-001 | File passes Ruff and Pyrefly | Must |

---

## 4. Data Model

```python
# BEFORE - No filtering (wrong)
def forward(self, context: List[str], query: str) -> dict:
    results = []
    for ctx in context:
        result = self.scorer(context=ctx, query=query)
        results.append({'context': ctx, 'quality_score': result.quality_score})
    return {'results': results}  # ❌ Returns all, no filtering

# AFTER - Actual filtering (correct)
def forward(self, context: List[str], query: str, threshold: float = 0.6) -> dspy.Prediction:
    results = []
    for ctx in context:
        result = self.scorer(context=ctx, query=query)
        if result.quality_score >= threshold:  # ✅ Filter by threshold
            results.append({'context': ctx, 'quality_score': result.quality_score})

    return dspy.Prediction(
        filtered_results=results,
        original_count=len(context),
        filtered_count=len(results)
    )
```

---

## 5. API Contract

This spec modifies DSPy module only. No REST/WebSocket endpoints.

---

## 6. Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| BR-QF-001 | Quality score >= threshold to include | Code logic |
| BR-QF-001 | Default threshold 0.6 | Configuration |

---

## 7. Acceptance Criteria

- [ ] reranker.py filters results by threshold
- [ ] Default threshold is 0.6
- [ ] Returns dspy.Prediction with filtered_results, original_count, filtered_count
- [ ] File passes: `ruff check` and `pyrefly check`

---

## 8. References

- **Fraud #5**: `.claude/fraud/AGENTX_DSPY_FRAUD_ANALYSIS_2026.md` (Ignored Quality Scores)
- **Plan**: `.claude/plans/golden-skipping-hedgehog.md` (Batch 12)

---

**Related Specs**:
- `specs/adaptive_retrieval/spec.md` - Also uses quality thresholds
