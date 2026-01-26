# =============================================================================
# AGENTX Widget Spawner - Widget Rewards
# =============================================================================
# Reward functions for widget appropriateness and positioning
# =============================================================================

"""Widget reward functions for scoring widget selection and positioning.

This module exports all reward functions for widget spawner.
"""

from services.widget_spawner.rewards.layout_position import layout_position_score
from services.widget_spawner.rewards.widget_appropriateness import (
    form_appropriateness_penalty,
    widget_appropriateness_score,
)

__all__ = [
    "widget_appropriateness_score",
    "form_appropriateness_penalty",
    "layout_position_score",
]
