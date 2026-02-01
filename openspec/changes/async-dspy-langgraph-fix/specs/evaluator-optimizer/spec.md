# Spec: Evaluator Optimizer

**Domain**: agent-runtime
**Generated**: 2026-02-02
**Status**: Draft

---

## 1. Purpose

Define the evaluator-optimizer pattern that decides "Do I have enough to answer?"

**Problem**: R014 searches more if quality is low, then forgets why it searched.

**Success Criteria**:
- Evaluator uses accumulated state
- Structured output (no text parsing)
- original_query always passed
- Max iterations enforced

---

## 2. Scope

### In Scope

- EvaluateProgressSignature DSPy class
- EvaluateProgressModule DSPy module
- ContinuationDecision Pydantic model
- should_continue_research() routing function

### Out of Scope

- State accumulation (covered by state-accumulation spec)
- Routing implementation (covered by conditional-routing spec)

---

## 3. Requirements

### 3.1 Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-EO-001 | Evaluator MUST read accumulated_findings | Must |
| FR-EO-002 | Evaluator MUST read original_query | Must |
| FR-EO-003 | MUST return structured ContinuationDecision | Must |
| FR-EO-004 | MUST enforce max_iterations limit | Must |
| FR-EO-005 | Class-based DSPy signature | Must |

### 3.2 Non-Functional Requirements

| ID | Requirement | Target Metric |
|----|-------------|---------------|
| NFR-EO-001 | Evaluator latency | < 2s |

---

## 4. Data Model

```python
# domain/models/routing.py
from pydantic import BaseModel, Field
from enum import Enum

class ActionType(str, Enum):
    """Evaluator action types."""
    CONTINUE_RESEARCH = "continue_research"
    ADD_TASKS = "add_tasks"
    FINALIZE = "finalize"

class ContinuationDecision(BaseModel):
    """Structured decision from evaluator."""

    action: ActionType = Field(description="What to do next")
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="Confidence in current information (0.0-1.0)"
    )
    missing_information: list[str] = Field(
        default_factory=list,
        description="What information is still missing"
    )
    reasoning: str = Field(description="Why this action")
```

---

## 5. API Contract

```python
# agent/tools/evaluator/evaluate_progress.py
import dspy
from dspy import InputField, OutputField, Signature

class EvaluateProgressSignature(dspy.Signature):
    """LLM evaluates: "Do I have enough to answer the ORIGINAL query?""""

    # ALWAYS PASSED - prevents topic drift
    original_query: str = InputField(desc="User's original query")

    # Accumulated state
    accumulated_findings: str = InputField(desc="All research gathered so far")
    accumulated_confidence: str = InputField(desc="Current confidence (0.0-1.0)")
    information_gaps: str = InputField(desc="What's still missing")
    current_iteration: str = InputField(desc="Iteration number")

    # Structured output (NOT text parsing!)
    action: str = OutputField(desc="continue_research, finalize, or add_tasks")
    confidence: str = OutputField(desc="LLM's confidence (0.0-1.0)")
    missing_information: str = OutputField(desc="What's still needed")
    reasoning: str = OutputField(desc="Why this action")

class EvaluateProgressModule(dspy.Module):
    """Evaluate accumulated state to decide next action."""

    def __init__(self):
        super().__init__()
        self.evaluate = dspy.Predict(EvaluateProgressSignature)

    def forward(
        self,
        original_query: str,
        accumulated_findings: list[str],
        accumulated_confidence: float,
        information_gaps: list[str],
        current_iteration: int,
    ) -> dspy.Prediction:
        """Evaluate progress with STRUCTURED output.

        Args:
            original_query: User's original query (prevents drift!)
            accumulated_findings: All research so far
            accumulated_confidence: Current confidence level
            information_gaps: What's missing
            current_iteration: Current iteration number

        Returns:
            dspy.Prediction: With ContinuationDecision
        """
        # Format accumulated state
        findings_text = "\n".join(accumulated_findings)
        gaps_text = "\n".join(information_gaps)

        # LLM evaluates (STRUCTURED OUTPUT!)
        result = self.evaluate(
            original_query=original_query,  # ← ALWAYS PASSED
            accumulated_findings=findings_text,
            accumulated_confidence=str(accumulated_confidence),
            information_gaps=gaps_text,
            current_iteration=str(current_iteration),
        )

        # Parse structured output
        decision = ContinuationDecision(
            action=ActionType(result.action),
            confidence=float(result.confidence),
            missing_information=result.missing_information.split("\n"),
            reasoning=result.reasoning,
        )

        return dspy.Prediction(decision=decision)

# Routing function
def should_continue_research(state: AgentState) -> str:
    """Route based on evaluator's STRUCTURED decision.

    NO TEXT PARSING - uses enum values directly.
    """
    decision = state.get("continuation_decision")
    iteration = state.get("current_iteration", 0)
    max_iterations = 5

    # Hard limit
    if iteration >= max_iterations:
        return "finalize"

    # Structured decision routing
    if decision.action == ActionType.CONTINUE_RESEARCH:
        return "continue"
    elif decision.action == ActionType.ADD_TASKS:
        return "add_tasks"
    else:  # FINALIZE
        return "finalize"
```

---

## 6. Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| BR-EO-001 | original_query ALWAYS passed | Function signature |
| BR-EO-002 | Max 5 iterations | Hard limit in routing |
| BR-EO-003 | Structured output only | ContinuationDecision model |
| BR-EO-004 | No text parsing | Enum-based routing |

---

## 7. Acceptance Criteria

- [ ] EvaluateProgressSignature is class-based
- [ ] original_query always passed to evaluator
- [ ] Returns ContinuationDecision (not dict)
- [ ] Routing uses enum values (no parsing)
- [ ] Max 5 iterations enforced
- [ ] Ruff and pyrefly checks pass

---

## 8. Test Scenarios

| Scenario | Expected Action |
|----------|-----------------|
| High confidence (>= 0.8) | finalize |
| Low confidence (< 0.6), iteration < 5 | continue_research |
| Any confidence, iteration >= 5 | finalize (max limit) |
| Specific gaps identified | add_tasks |

---

**Next**: See `conditional-routing/spec.md` for routing integration.
