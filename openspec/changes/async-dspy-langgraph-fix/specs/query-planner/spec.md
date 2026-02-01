# Spec: Query Planner

**Domain**: agent-runtime
**Generated**: 2026-02-02
**Status**: Draft

---

## 1. Purpose

Define the QueryPlannerModule DSPy module that generates execution plans based on query complexity.

**Problem**: Fixed pipelines waste time on simple queries and struggle with complex queries.

**Success Criteria**:
- QueryPlannerModule generates 0-N research tasks
- Simple queries return 0 tasks (direct answer)
- Complex queries return relevant tasks
- Checks Store before generating new plan
- Class-based DSPy signature

---

## 2. Scope

### In Scope

- QueryPlannerModule DSPy class
- Check Store cache before planning
- Generate task dependencies
- Return structured ExecutionPlan

### Out of Scope

- ExecutionPlan model definitions (covered by execution-plan-models spec)
- Store implementation (covered by agent-memory-store spec)

---

## 3. Requirements

### 3.1 Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-QP-001 | QueryPlannerModule MUST check Store before planning | Must |
| FR-QP-002 | MUST return 0 tasks for simple queries | Must |
| FR-QP-003 | MUST return 1-N tasks for complex queries | Must |
| FR-QP-004 | MUST include task dependencies in plan | Should |
| FR-QP-005 | MUST use class-based DSPy signature | Must |

### 3.2 Non-Functional Requirements

| ID | Requirement | Target Metric |
|----|-------------|---------------|
| NFR-QP-001 | Planning latency | < 5s |
| NFR-QP-002 | Cache hit latency | < 1s |

---

## 4. Data Model

```python
# Using ExecutionPlan from execution-plan-models spec
from domain.models.query_plan import ExecutionPlan
```

---

## 5. API Contract

```python
# agent/tools/planner/query_planner.py
import dspy
from dspy import InputField, OutputField, Signature

class QueryPlannerSignature(dspy.Signature):
    """Generate execution plan based on query complexity."""

    query: str = InputField(desc="User's original query")
    conversation_history: str = InputField(desc="Previous messages (optional)")
    available_tasks: str = InputField(desc="Available task types")

    # Structured output
    needs_research: str = OutputField(desc="true or false")
    task_count: str = OutputField(desc="Number of tasks (0-N)")
    task_descriptions: str = OutputField(desc="Description of each task")
    reasoning: str = OutputField(desc="Why this plan")

class QueryPlannerModule(dspy.Module):
    """Generate execution plan for query processing."""

    def __init__(self, store_adapter):
        super().__init__()
        self.plan = dspy.Predict(QueryPlannerSignature)
        self.store = store_adapter

    def forward(self, query: str, conversation_history: str = "") -> dspy.Prediction:
        """Generate execution plan.

        Args:
            query: User's query
            conversation_history: Optional conversation context

        Returns:
            dspy.Prediction: With execution_plan
        """
        # Check Store for cached plan
        cached_plan = await self._check_cache(query)
        if cached_plan:
            return dspy.Prediction(execution_plan=cached_plan)

        # Generate new plan
        result = self.plan(
            query=query,
            conversation_history=conversation_history,
            available_tasks="SEARCH, SUMMARIZE, COMPARE, ANALYZE",
        )

        # Parse into ExecutionPlan
        execution_plan = self._parse_plan(result)

        return dspy.Prediction(execution_plan=execution_plan)

    async def _check_cache(self, query: str) -> ExecutionPlan | None:
        """Check Store for cached execution plan."""
        # Implementation in agent-memory-store spec
        pass

    def _parse_plan(self, result) -> ExecutionPlan:
        """Parse LLM output into ExecutionPlan model."""
        # Implementation uses ExecutionPlan from execution-plan-models
        pass
```

---

## 6. Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| BR-QP-001 | Cache first | Always check Store before LLM call |
| BR-QP-002 | Simple = 0 tasks | Queries like "2+2" get 0 tasks |
| BR-QP-003 | Complex = N tasks | Research queries get 1-10 tasks |

---

## 7. Acceptance Criteria

- [ ] QueryPlannerModule checks Store before planning
- [ ] Simple queries return 0 tasks
- [ ] Complex queries return relevant tasks
- [ ] Tasks have dependencies defined
- [ ] Returns dspy.Prediction (not dict)
- [ ] Class-based signature used
- [ ] Ruff and pyrefly checks pass

---

## 8. Test Scenarios

| Query | Expected Tasks | Reason |
|-------|----------------|--------|
| "What is 2+2?" | 0 tasks | Simple math |
| "Compare iPhone vs Pixel" | 2-3 tasks | Comparison needs research |
| "Summarize climate change" | 1-2 tasks | Single topic |
| "Analyze AI trends in 2024" | 3-5 tasks | Complex analysis |

---

**Next**: See `execution-plan-models/spec.md` for ExecutionPlan data structures.
