# Spec: Memory-Guided Search Planning

**Domain**: memory_guided_search
**Generated**: 2026-02-03
**Status**: Draft

---

## 1. Purpose

Memory guides HOW to search (ALWAYS search happens, memory determines depth/terms/sources/format). ENHANCE existing QueryPlannerModule without breaking it.

**Problem Statement**: Search always happens with fixed parameters, ignoring user preferences and past successful patterns stored in memory.

**Success Criteria**: SearchGuidanceModule retrieves user preferences; QueryPlannerModule ENHANCED (not replaced) with memory guidance.

---

## 2. Scope

### In Scope

- ENHANCE existing QueryPlannerModule with memory guidance
- SearchGuidanceModule for retrieving user preferences from memory
- Memory provides: search_depth, prioritized_terms, source_preferences, answer_format
- Preserves ExecutionPlan with 0 to N tasks pattern
- Preserves cache lookup logic
- Integration with SearchTermPatternMemory (NEW - see spec 2.12)

### Out of Scope

- Replacing ExecutionPlan generation (MUST PRESERVE 0 to N tasks pattern)
- Cache lookup logic (MUST PRESERVE)
- Changing search execution (SearXNG integration preserved)

---

## 3. Requirements

### 3.1 Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| RF-SEARCH-001 | SearchGuidanceModule retrieves user preferences from memory | Must |
| RF-SEARCH-002 | Returns: search_depth, prioritized_terms, source_preferences, answer_format | Must |
| RF-SEARCH-003 | QueryPlannerModule still generates ExecutionPlan with 0 to N tasks | Must |
| RF-SEARCH-004 | QueryPlannerModule preserves cache lookup logic | Must |
| RF-SEARCH-005 | Direct answer path still works (0 tasks) | Must |
| RF-SEARCH-006 | Memory guidance is optional enhancement | Must |

### 3.2 Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-SEARCH-001 | All files pass Ruff and Pyrefly | Must |
| NFR-SEARCH-002 | Absolute imports only | Must |
| NFR-SEARCH-003 | Preserves existing ExecutionPlan format | Must |

---

## 4. Data Model

```python
# agentx/agent/dspy_signatures/decision_signatures.py
import dspy

class SearchGuidanceSignature(dspy.Signature):
    """Memory provides guidance for search execution."""
    query: str = dspy.InputField(desc="User's question or request")
    user_id: str = dspy.InputField(desc="User identifier for memory lookup")
    search_depth: str = dspy.OutputField(desc="Depth: shallow, medium, deep")
    prioritized_terms: str = dspy.OutputField(desc="Comma-separated search terms")
    source_preferences: str = dspy.OutputField(desc="Preferred sources: academic, general, news")
    answer_format: str = dspy.OutputField(desc="Format: concise, detailed, bullet_points")

# EXISTING pattern to PRESERVE from query_planner.py
class QueryPlannerModule(dspy.Module):
    def forward(self, query: str, **kwargs) -> dspy.Prediction:
        # Generates ExecutionPlan with 0 to N research tasks
        # 0 tasks = direct answer (cache hit or simple query)
        # N tasks = research needed
```

---

## 5. API Contract

This spec defines DSPy modules only. No REST/WebSocket endpoints.

---

## 6. Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| BR-SEARCH-001 | Search ALWAYS happens (memory guides HOW) | QueryPlannerModule |
| BR-SEARCH-002 | Memory does NOT store facts/knowledge | SearchGuidanceModule |
| BR-SEARCH-003 | 0 tasks = direct answer preserved | QueryPlannerModule |
| BR-SEARCH-004 | Cache lookup happens before tasks | Preserved in node |

---

## 7. Acceptance Criteria

- [ ] SearchGuidanceModule exists and retrieves from memory
- [ ] SearchGuidance returns: search_depth, prioritized_terms, source_preferences, answer_format
- [ ] QueryPlannerModule still generates ExecutionPlan with 0 to N tasks
- [ ] QueryPlannerModule preserves cache lookup logic
- [ ] Direct answer path still works (0 tasks)
- [ ] Memory guidance is optional enhancement
- [ ] All files pass: `ruff check` and `pyrefly check`

---

## 8. References

- **Plan**: `.claude/plans/golden-skipping-hedgehog.md` (Batch 0b-a)
- **Existing Node**: `agentx/agent/nodes/query_planner.py` (PRESERVE)

---

**Related Specs**:
- `specs/session_performance/spec.md` - Provides routing history
- `specs/adaptive_retrieval/spec.md` - Quality-based retrieval
- `specs/search_term_pattern_memory/spec.md` - Provides term prediction based on past patterns
- `specs/searxng_hybrid_search/spec.md` - Uses search term patterns for guidance
