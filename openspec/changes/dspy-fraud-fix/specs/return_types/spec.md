# Spec: Return Type Fixes

**Domain**: return_types
**Generated**: 2026-02-03
**Status**: Draft

---

## 1. Purpose

Fix all modules returning dict instead of dspy.Prediction. Ensure proper DSPy return types.

**Problem Statement**: 24 tool modules return dict instead of dspy.Prediction (Fraud #18-41).

**Success Criteria**: All 24 tool modules return dspy.Prediction; no modules return dict.

---

## 2. Scope

### In Scope

- All 24 tool modules in agentx/agent/tools/
- Wrap all dict returns in dspy.Prediction
- Update type hints to -> dspy.Prediction

### Out of Scope

- Changing module logic (only return type)

**Affected Modules** (24 total):
- analyst/: context_analyzer.py, goal_detector.py, search_terms.py, insight_extractor.py, data_quality_checker.py
- researcher/: citation_builder.py, data_structurer.py, findings_beautifier.py
- presenter/: quality_check.py, presentation.py
- contextualizer/: reranker.py, contextualizer.py, filter.py
- designer/: color_scheme.py, hierarchy.py, pov_generator.py
- (all remaining tool modules)

---

## 3. Requirements

### 3.1 Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| RF-RET-001 | All 24 tool modules return dspy.Prediction | Must |
| RF-RET-002 | No modules return dict | Must |
| RF-RET-003 | Dict values wrapped in dspy.Prediction constructor | Must |
| RF-RET-004 | Type hints updated to -> dspy.Prediction | Must |

### 3.2 Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-RET-001 | All files pass Ruff and Pyrefly | Must |
| NFR-RET-002 | Absolute imports only | Must |

---

## 4. Data Model

```python
# WRONG - Returns dict (before fix)
def forward(self, query: str) -> dict:
    result = self.analyzer(query=query)
    return {"query_type": result.query_type, "domain": result.domain}

# CORRECT - Returns dspy.Prediction (after fix)
def forward(self, query: str) -> dspy.Prediction:
    result = self.analyzer(query=query)
    return dspy.Prediction(
        query_type=result.query_type,
        domain=result.domain
    )
```

---

## 5. API Contract

This spec modifies DSPy modules only. No REST/WebSocket endpoints.

---

## 6. Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| BR-RET-001 | All forward() methods return dspy.Prediction | Code review |
| BR-RET-002 | No dict literals in return statements | Verification script |

---

## 7. Acceptance Criteria

- [ ] All 24 tool modules return dspy.Prediction
- [ ] No modules return dict
- [ ] Type hints updated to -> dspy.Prediction
- [ ] All files pass: `ruff check` and `pyrefly check`
- [ ] Verification script passes:
```python
import ast
import os
violations = []
for root, dirs, files in os.walk('agentx/agent/tools'):
    for file in files:
        if file.endswith('.py'):
            path = os.path.join(root, file)
            with open(path) as f:
                tree = ast.parse(f.read())
            for node in ast.walk(tree):
                if isinstance(node, ast.Return) and isinstance(node.value, ast.Dict):
                    violations.append(path)
if violations:
    print('❌ Dict returns found:')
    for v in violations:
        print(f'  {v}')
    exit(1)
else:
    print('✅ No dict returns')
```

---

## 8. References

- **Fraud #18-41**: `.claude/fraud/AGENTX_DSPY_FRAUD_ANALYSIS_2026.md` (Wrong Return Types)
- **Plan**: `.claude/plans/golden-skipping-hedgehog.md` (Batch 10)

---

**Related Specs**:
- `specs/dspy_signatures/spec.md` - Also modifies tool modules
