# Spec: DSPy Signature Replacements

**Domain**: dspy_signatures
**Generated**: 2026-02-03
**Status**: Draft

---

## 1. Purpose

Replace all inline signatures with class-based signatures. Ensure weak LLM compatibility (gemma3:4b).

**Problem Statement**: 12 tool files use inline signatures incompatible with gemma3:4b (Fraud #6-17).

**Success Criteria**: All 5 signature files created; all 24 tool modules updated to use class-based signatures.

---

## 2. Scope

### In Scope

- Create proper signature classes in dspy_signatures/:
  - analyst.py (4 signatures)
  - researcher.py (3 signatures)
  - presenter.py (2 signatures)
  - designer.py (3 signatures)
  - contextualizer.py (3 signatures)
- Update all 24 tool modules to use class-based signatures
- Each signature has explicit field descriptions

### Out of Scope

- Changing module logic (only signature usage)

---

## 3. Requirements

### 3.1 Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| RF-SIG-001 | analyst.py signature file exists with 4 signatures | Must |
| RF-SIG-002 | researcher.py signature file exists with 3 signatures | Must |
| RF-SIG-003 | presenter.py signature file exists with 2 signatures | Must |
| RF-SIG-004 | designer.py signature file exists with 3 signatures | Must |
| RF-SIG-005 | contextualizer.py signature file exists with 3 signatures | Must |
| RF-SIG-006 | All tool modules updated to use class-based signatures | Must |
| RF-SIG-007 | No dspy.Predict(string) calls with inline signatures | Must |
| RF-SIG-008 | All signatures have explicit field descriptions | Must |

### 3.2 Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-SIG-001 | All files pass Ruff and Pyrefly | Must |
| NFR-SIG-002 | Absolute imports only | Must |

---

## 4. Data Model

```python
# agentx/agent/dspy_signatures/analyst.py
import dspy

class QueryAnalysisSignature(dspy.Signature):
    """Analyze query type, domain, and urgency."""
    query: str = dspy.InputField(desc="User's question or request")
    query_type: str = dspy.OutputField(desc="Type: question, task, analysis, or comparison")
    domain: str = dspy.OutputField(desc="Domain: health, finance, tech, travel, general")
    urgency: str = dspy.OutputField(desc="Urgency: routine, urgent, critical")

class GoalDetectionSignature(dspy.Signature):
    """Detect user goal from query."""
    query: str = dspy.InputField(desc="User's question or request")
    insights: str = dspy.InputField(desc="Additional context or insights")
    goal: str = dspy.OutputField(desc="User's underlying goal")
    scope: str = dspy.OutputField(desc="'broad' or 'narrow'")
    depth: str = dspy.OutputField(desc="'shallow' or 'deep'")

# Example module update:
class ContextAnalyzerModule(dspy.Module):
    def __init__(self):
        super().__init__()
        from agentx.agent.dspy_signatures.analyst import QueryAnalysisSignature
        self.analyze = dspy.Predict(QueryAnalysisSignature)  # ✅ Class-based

    def forward(self, query: str) -> dspy.Prediction:
        result = self.analyze(query=query)
        return dspy.Prediction(
            query_type=result.query_type,
            domain=result.domain,
            urgency=result.urgency,
        )
```

---

## 5. API Contract

This spec defines DSPy signatures only. No REST/WebSocket endpoints.

---

## 6. Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| BR-SIG-001 | All signatures are classes inheriting dspy.Signature | Code review |
| BR-SIG-002 | All fields have explicit descriptions | Code review |
| BR-SIG-003 | No inline string signatures (e.g., "query -> answer") | Verification script |

---

## 7. Acceptance Criteria

- [ ] analyst.py signature file exists with 4 signatures
- [ ] researcher.py signature file exists with 3 signatures
- [ ] presenter.py signature file exists with 2 signatures
- [ ] designer.py signature file exists with 3 signatures
- [ ] contextualizer.py signature file exists with 3 signatures
- [ ] All tool modules updated to use class-based signatures
- [ ] No dspy.Predict(string) calls with inline signatures
- [ ] All signatures have explicit field descriptions
- [ ] All files pass: `ruff check` and `pyrefly check`

---

## 8. References

- **Fraud #6-17**: `.claude/fraud/AGENTX_DSPY_FRAUD_ANALYSIS_2026.md` (Inline Signatures)
- **Plan**: `.claude/plans/golden-skipping-hedgehog.md` (Batches 5-9)

---

**Related Specs**:
- `specs/return_types/spec.md` - Also modifies tool modules
