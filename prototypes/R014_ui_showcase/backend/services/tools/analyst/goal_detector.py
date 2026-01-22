# =============================================================================
# AGENTX Analyst - Goal Detector Module
# =============================================================================
# Detects the goal and scope of the query
# =============================================================================

import dspy


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
