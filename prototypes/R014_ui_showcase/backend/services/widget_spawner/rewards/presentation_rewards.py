# =============================================================================
# AGENTX Widget Spawner - Presentation Quality Rewards
# =============================================================================
# Reward functions for presentation plan quality evaluation
# =============================================================================

import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


def presentation_quality_score(args: Any, pred: Any) -> float:
    """Evaluate presentation plan quality (0.0 to 1.0).

    Pure Python logic - no LLM calls. Deterministic and fast.

    Scoring:
    - Widget variety (0.2 points)
    - Device-appropriate layout (0.3 points)
    - Color accessibility (0.2 points)
    - Visual hierarchy (0.15 points)
    - Whitespace balance (0.15 points)
    """
    try:
        plan = json.loads(pred.presentation_plan)
    except (json.JSONDecodeError, AttributeError):
        logger.warning("Invalid presentation plan JSON")
        return 0.0

    score = 0.0

    # Rule 1: Widget variety (0.2 points)
    widget_types = set(w.get("type", "") for w in plan.get("widgets", []))
    if len(widget_types) > 1:
        score += 0.2
    elif len(widget_types) == 1 and "markdown" in widget_types:
        score += 0.05

    # Rule 2: Device-appropriate layout (0.3 points)
    score += _device_layout_score(
        args.get("device_context", {}).get("type", "desktop"),
        plan.get("layout", ""),
    )

    # Rule 3: Color accessibility (0.2 points)
    score += _color_accessibility_score(plan.get("color_scheme", {}))

    # Rule 4: Visual hierarchy (0.15 points)
    score += _visual_hierarchy_score(plan.get("visual_hierarchy", {}))

    # Rule 5: Whitespace balance (0.15 points)
    score += _whitespace_balance_score(plan.get("visual_hierarchy", {}))

    return min(score, 1.0)


def _device_layout_score(device_type: str, layout: str) -> float:
    """Score device-appropriate layout choice."""
    if device_type == "mobile":
        if layout in ["simple_vertical", "single_column", "stack"]:
            return 0.3
        return 0.0
    else:
        if layout in ["grid_2column", "grid_3column", "masonry"]:
            return 0.3
        elif layout == "simple_vertical":
            return 0.1
    return 0.0


def _color_accessibility_score(color_scheme: dict) -> float:
    """Score color accessibility based on contrast ratio."""
    contrast_ratio = color_scheme.get("contrast_ratio", 0)

    if contrast_ratio >= 7.0:
        return 0.2
    elif contrast_ratio >= 4.5:
        return 0.15
    elif contrast_ratio >= 3.0:
        return 0.05
    return 0.0


def _visual_hierarchy_score(hierarchy: dict) -> float:
    """Score visual hierarchy presence."""
    if hierarchy.get("primary_element") and hierarchy.get("secondary_element"):
        return 0.15
    return 0.0


def _whitespace_balance_score(hierarchy: dict) -> float:
    """Score whitespace balance."""
    whitespace_ratio = hierarchy.get("whitespace_ratio", 0)
    if 0.15 <= whitespace_ratio <= 0.35:
        return 0.15
    elif 0.1 <= whitespace_ratio <= 0.4:
        return 0.05
    return 0.0
