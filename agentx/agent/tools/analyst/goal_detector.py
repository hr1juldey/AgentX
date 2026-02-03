"""Goal Detector Module for Analyst agent.

Ported from R014: services/tools/analyst/goal_detector.py

Detects the goal and scope of the query using 3 parallel Predict calls.

Fraud #6 fix: Returns dspy.Prediction instead of dict.
"""

import dspy

from agentx.agent.dspy_signatures.analyst import (
    DetectDepth,
    DetectGoal,
    DetectScope,
)
from agentx.agent.tools.common.dspy_helpers import safe_extract


class GoalDetectorModule(dspy.Module):
    """Detects the goal and scope of the query.

    Has 3 signatures:
    - DetectGoal: Detect primary goal
    - DetectScope: Detect scope (broad, specific, comparison)
    - DetectDepth: Detect required depth (shallow, deep, comprehensive)

    Fraud #6 fix: Returns dspy.Prediction instead of dict.
    """

    def __init__(self) -> None:
        """Initialize the goal detector."""
        super().__init__()
        self.detect_goal = dspy.Predict(DetectGoal)
        self.detect_scope = dspy.Predict(DetectScope)
        self.detect_depth = dspy.Predict(DetectDepth)

    def forward(self, query: str, insights: list) -> dspy.Prediction:
        """Detect goal and scope.

        Args:
            query: User's question or request
            insights: Context from query analysis

        Returns:
            dspy.Prediction with 'goal', 'scope', and 'depth'
        """
        goal_result = self.detect_goal(query=query, insights=str(insights))
        scope_result = self.detect_scope(query=query)
        depth_result = self.detect_depth(
            query=query, goal=safe_extract(goal_result, "goal", "unknown")
        )

        return dspy.Prediction(
            goal=safe_extract(goal_result, "goal", "unknown"),
            scope=safe_extract(scope_result, "scope", "unknown"),
            depth=safe_extract(depth_result, "depth", "unknown"),
        )
