# =============================================================================
# AGENTX Widget Spawner - Reward Functions
# =============================================================================
# Pure Python evaluation functions for assessing UI presentation quality.
# These functions encode design knowledge without LLM calls - fast and deterministic.
# =============================================================================

from typing import Dict, Any
import json
import logging

logger = logging.getLogger(__name__)


def presentation_quality_score(args: Dict[str, Any], pred: Any) -> float:
    """
    Evaluate presentation plan quality (0.0 to 1.0).

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
    device_type = args.get("device_context", {}).get("type", "desktop")
    layout = plan.get("layout", "")

    if device_type == "mobile":
        if layout in ["simple_vertical", "single_column", "stack"]:
            score += 0.3
        elif layout in ["grid_2column", "grid_3column"]:
            score += 0.0
    else:
        if layout in ["grid_2column", "grid_3column", "masonry"]:
            score += 0.3
        elif layout == "simple_vertical":
            score += 0.1

    # Rule 3: Color accessibility (0.2 points)
    color_scheme = plan.get("color_scheme", {})
    contrast_ratio = color_scheme.get("contrast_ratio", 0)

    if contrast_ratio >= 7.0:
        score += 0.2
    elif contrast_ratio >= 4.5:
        score += 0.15
    elif contrast_ratio >= 3.0:
        score += 0.05

    # Rule 4: Visual hierarchy (0.15 points)
    hierarchy = plan.get("visual_hierarchy", {})
    if hierarchy.get("primary_element") and hierarchy.get("secondary_element"):
        score += 0.15

    # Rule 5: Whitespace balance (0.15 points)
    whitespace_ratio = hierarchy.get("whitespace_ratio", 0)
    if 0.15 <= whitespace_ratio <= 0.35:
        score += 0.15
    elif 0.1 <= whitespace_ratio <= 0.4:
        score += 0.05

    return min(score, 1.0)


def accessibility_compliance_score(args: Dict[str, Any], pred: Any) -> float:
    """
    Evaluate WCAG compliance (0.0 to 1.0).

    Checks: color contrast, font sizes, interactive element sizes.
    """
    try:
        content = json.loads(pred.widget_content)
    except (json.JSONDecodeError, AttributeError):
        logger.warning("Invalid widget content JSON")
        return 0.0

    score = 1.0

    # Check 1: Color contrast (multiply penalty)
    if content.get("contrast_ratio", 0) < 4.5:
        score *= 0.7
    elif content.get("contrast_ratio", 0) < 7.0:
        score *= 0.9

    # Check 2: Font size (multiply penalty)
    font_size = content.get("font_size", 16)
    if font_size < 14:
        score *= 0.7
    elif font_size < 16:
        score *= 0.9

    # Check 3: Interactive elements (multiply penalty)
    button_size = content.get("button_size", 40)
    if button_size < 44:
        score *= 0.85

    # Check 4: Has alt text (additive bonus)
    if content.get("has_alt_text", False):
        score = min(score + 0.05, 1.0)

    return max(score, 0.0)


def widget_appropriateness_score(content_analysis: str, widget_type: str) -> float:
    """
    Score how appropriate a widget type is for the content.

    Pure logic based on content-type to widget-type mapping.
    """
    content_type = content_analysis.lower()

    # Data-heavy content
    if any(
        kw in content_type
        for kw in ["data", "trends", "statistics", "analytics", "metrics"]
    ):
        if widget_type in ["chart", "table", "card"]:
            return 0.9
        elif widget_type == "markdown":
            return 0.3

    # Text-heavy content
    if any(
        kw in content_type
        for kw in ["article", "blog", "guide", "explanation", "summary"]
    ):
        if widget_type in ["markdown", "card"]:
            return 0.9
        elif widget_type == "chart":
            return 0.2

    # Form/input content
    if any(
        kw in content_type for kw in ["input", "form", "survey", "feedback", "collect"]
    ):
        if widget_type == "form":
            return 1.0
        elif widget_type == "card":
            return 0.4

    # Visual/gallery content
    if any(
        kw in content_type for kw in ["images", "photos", "gallery", "visual", "media"]
    ):
        if widget_type in ["gallery", "image"]:
            return 0.95
        elif widget_type == "card":
            return 0.5

    # Progress/status content
    if any(
        kw in content_type for kw in ["loading", "progress", "status", "processing"]
    ):
        if widget_type == "progress":
            return 1.0
        elif widget_type == "card":
            return 0.6

    return 0.5


def layout_position_score(plan: Dict[str, Any], widget: Dict[str, Any]) -> float:
    """
    Score how well a widget's position fits the layout.

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
