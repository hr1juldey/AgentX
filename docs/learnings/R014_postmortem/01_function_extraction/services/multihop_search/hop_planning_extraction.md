# hop_planning.py - Function Extraction

## File: services/multihop_search/execution/hop_planning.py

### Primary Purpose
Plans the next hop based on assessment results - uses HopPlanner to decide strategy and next query.

### Key Classes

#### `HopPlanning`
**Purpose**: Plans the next hop based on assessment.

**SRP**: Plan next hop only.

**Init parameters**:
- `planner`: HopPlanner module
- `time_estimator`: Time estimator service
- `progress_callback`: Progress callback function
- `max_hops`: Maximum hops for progress calculation

---

### Key Methods

#### `plan_next(question: str, assessment: dspy.Prediction, hop_queries: list[str], hop_num: int) -> dspy.Prediction`
**Purpose**: Plan the next hop based on assessment.

**Progress events**:
1. "Planning next hop..." at `(hop_num - 0.2) / max_hops`
2. "Continuing: {strategy}" at `hop_num / max_hops` with ETA

**Calls**: `self.planner(question, gap_description, previous_queries)`

**Returns**: Plan result with next_query and strategy.

**Logging**: Logs strategy for each hop.

---

### Architectural Patterns

1. **Progress tracking**: Sends events at key stages
2. **Strategy delegation**: Uses HopPlanner module for decision
3. **ETA calculation**: Uses time_estimator for remaining time

---

### Dependencies

**Internal**:
- `services.multihop_search.execution.hop_helpers`: send_progress_event
- `services.multihop_search.reflection`: HopPlanner (TYPE_CHECKING import)

**External**:
- `dspy`: DSPy framework
- `logging`: Standard logging
- `typing`: Type hints

---

### Lessons Learned

1. **Progress updates need context**: Show strategy and reasoning in events
2. **ETA improves UX**: Time estimator gives users expected completion
3. **Delegation to planner**: HopPlanning delegates strategy to HopPlanner module
4. **Progress calculation**: Use hop_num/max_hops for percentage
