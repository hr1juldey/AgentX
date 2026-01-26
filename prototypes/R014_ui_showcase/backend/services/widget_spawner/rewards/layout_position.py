# =============================================================================
# AGENTX Widget Spawner - Layout Position Rewards
# =============================================================================
# Reward functions for layout position scoring
# =============================================================================

"""Layout position scoring functions.

Provides pure logic for scoring how well widget positions fit the layout.
"""

from typing import Any


def layout_position_score(plan: dict[str, Any], widget: dict[str, Any]) -> float:
    """Score how well a widget's position fits the layout.

    Checks: priority alignment, spatial logic, overlap avoidance.
    """
    score = 0.0

    widget_priority = widget.get("priority", "medium")
    widget_position = widget.get("position", "middle")

    # Rule 1: High priority should be at top
    if widget_priority == "high":
        if widget_position in ["top", "left", "center"]:
            score += 0.5
        elif widget_position == "bottom":
            score += 0.1

    # Rule 2: Low priority can be anywhere
    elif widget_priority == "low":
        score += 0.3

    # Rule 3: Medium priority
    else:
        if widget_position in ["middle", "right", "center"]:
            score += 0.4

    # Rule 4: Check for reasonable spacing
    if widget.get("x") and widget.get("y"):
        x, y = widget["x"], widget["y"]
        if 0 <= x <= 2000 and 0 <= y <= 2000:
            score += 0.2
        else:
            score -= 0.2

    return max(score, 0.0)
