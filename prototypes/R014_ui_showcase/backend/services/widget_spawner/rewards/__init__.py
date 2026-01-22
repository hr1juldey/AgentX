# =============================================================================
# AGENTX Widget Spawner - Reward Functions Package
# =============================================================================
# Pure Python evaluation functions for UI presentation quality
# =============================================================================

from services.widget_spawner.rewards.accessibility_rewards import (
    accessibility_compliance_score,
)
from services.widget_spawner.rewards.presentation_rewards import (
    presentation_quality_score,
)
from services.widget_spawner.rewards.widget_rewards import (
    layout_position_score,
    widget_appropriateness_score,
)

__all__ = [
    "presentation_quality_score",
    "accessibility_compliance_score",
    "widget_appropriateness_score",
    "layout_position_score",
]
