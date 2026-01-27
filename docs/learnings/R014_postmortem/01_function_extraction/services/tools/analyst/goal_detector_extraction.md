# Function Postmortem: services/tools/analyst/goal_detector.py

## Metadata
- **File**: services/tools/analyst/goal_detector.py
- **Lines of Code**: 36
- **Purpose**: Detects the goal and scope of the query
- **Dependencies**: dspy

---

## Analysis

**File Status**: PRODUCTION DSPy MODULE

**Purpose**: Multi-stage detection module that identifies goal, scope, and depth of user queries.

---

## Classes Extracted

### GoalDetectorModule

**Purpose**: DSPy Module that detects goal, scope, and depth of user queries using 3 separate signatures.

**Lines**: 10-35

**Key Code**:
```python
class GoalDetectorModule(dspy.Module):
    """Detects the goal and scope of the query.

    Has 3 signatures:
    - DetectGoal: Detect primary goal
    - DetectScope: Detect scope (broad, specific, comparison)
    - DetectDepth: Detect required depth (shallow, deep, comprehensive)
    """

    def __init__(self):
        super().__init__()
        self.detect_goal = dspy.Predict("query, insights -> goal")
        self.detect_scope = dspy.Predict("query -> scope")
        self.detect_depth = dspy.Predict("query, goal -> depth")

    def forward(self, query: str, insights: list) -> dict:
        """Detect goal and scope."""
        goal_result = self.detect_goal(query=query, insights=str(insights))
        scope_result = self.detect_scope(query=query)
        depth_result = self.detect_depth(query=query, goal=goal_result.goal)  # type: ignore[attr-defined]

        return {
            "goal": goal_result.goal,  # type: ignore[attr-defined]
            "scope": scope_result.scope,  # type: ignore[attr-defined]
            "depth": depth_result.depth,  # type: ignore[attr-defined]
        }
```

**What Works**:
- ✅ 3-stage detection: goal → scope → depth
- ✅ Sequential dependency: depth uses goal output
- ✅ Inline signatures: Simple "input -> output" format
- ✅ Clean dict return: Structured output for downstream use
- ✅ Type ignores: Handles dynamic Prediction attributes

**Mistakes Found**: None - clean multi-stage detection

**Behavioral Notes**:
- detect_goal uses insights (from previous analysis)
- detect_scope only uses query (independent)
- detect_depth uses both query AND goal (sequential dependency)
- All use dspy.Predict (not ChainOfThought) for speed
- Returns dict with 3 keys: goal, scope, depth

**Dependencies**:
- **Imports**: dspy
- **Uses**: dspy.Predict (3 instances)

**Reusability**: HIGH - Multi-stage detection pattern is reusable for any query understanding task.

---

## File Summary

**Total Classes**: 1
**Lines of Code**: 36

**Overall Assessment**: Clean multi-stage detection module. Sequential dependency (depth uses goal) is a key pattern.

**Key Learnings for Real AgentX**:
1. ✅ Multi-stage detection: Detect goal → scope → depth in sequence
2. ✅ Sequential dependencies: Later stages use earlier outputs (depth uses goal)
3. ✅ Inline signatures: Simple "input -> output" format for fast detection
4. ✅ dspy.Predict vs ChainOfThought: Use Predict for simple classification, ChainOfThought for reasoning
5. ✅ Structured output: Return dict for downstream consumption
6. ✅ Type ignores: Handle dynamic Prediction attributes gracefully

**Reuse for Real AgentX**: ✅ DIRECT - Use this multi-stage detection pattern for any query understanding system.
