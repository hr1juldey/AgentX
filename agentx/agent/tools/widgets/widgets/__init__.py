"""Widget selection module for Real AgentX v0.1.

This module provides adaptive widget selection based on research findings.
"""

from agentx.agent.tools.widgets.widgets.detection import (
    DetectContentPatternModule,
    infer_widgets_from_patterns,
)
from agentx.agent.tools.widgets.widgets.filtering import (
    apply_widget_filters,
    get_max_widget_count,
)
from agentx.agent.tools.widgets.widgets.signatures import (
    DetectContentPatternSignature,
)

__all__ = [
    "DetectContentPatternSignature",
    "DetectContentPatternModule",
    "infer_widgets_from_patterns",
    "apply_widget_filters",
    "get_max_widget_count",
]
