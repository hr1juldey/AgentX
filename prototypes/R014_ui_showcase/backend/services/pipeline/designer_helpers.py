# =============================================================================
# AGENTX DESIGNER Agent Helpers
# =============================================================================
# Helper functions for result processing and safe_get operations
# =============================================================================

"""Helper functions for processing designer agent results.

Provides safe_get utilities and result processing helpers.
"""

from typing import Any


def safe_get(result: Any, key: str, default: Any = None) -> Any:
    """Safely get a value from a result object.

    Args:
        result: Result object (may or may not have get method)
        key: Key to retrieve
        default: Default value if key not found

    Returns:
        Value or default
    """
    if hasattr(result, "get"):
        return result.get(key, default)
    return default


def get_povs_data(povs_result: dict) -> dict[str, Any]:
    """Extract POV data from result.

    Args:
        povs_result: POV generator result

    Returns:
        Dict with points_of_view, balanced_povs, nuanced_analysis
    """
    return {
        "points_of_view": safe_get(povs_result, "points_of_view", []),
        "balanced_povs": safe_get(povs_result, "balanced_povs", []),
        "nuanced_analysis": safe_get(povs_result, "nuanced_analysis", ""),
    }


def get_color_data(color_result: dict) -> dict[str, Any]:
    """Extract color scheme data from result.

    Args:
        color_result: Color picker result

    Returns:
        Dict with color_scheme, contrast_ratio
    """
    default_color_scheme = {
        "primary": "blue_500",
        "accent": "green_400",
        "background": "slate_900",
    }

    return {
        "color_scheme": safe_get(color_result, "color_scheme", default_color_scheme),
        "contrast_ratio": safe_get(color_result, "contrast_ratio", 7.0),
    }


def get_hierarchy_data(hierarchy_result: dict, widget_list: list) -> dict[str, Any]:
    """Extract visual hierarchy data from result.

    Args:
        hierarchy_result: Hierarchy planner result
        widget_list: List of widgets

    Returns:
        Dict with visual_hierarchy, priority_order, layout
    """
    return {
        "visual_hierarchy": safe_get(
            hierarchy_result, "visual_hierarchy", ["hero", "insights", "details"]
        ),
        "priority_order": safe_get(hierarchy_result, "priority_order", widget_list),
        "layout": safe_get(hierarchy_result, "layout", "narrative_focused"),
    }


def get_accessibility_data(accessibility_result: dict) -> dict[str, Any]:
    """Extract accessibility data from result.

    Args:
        accessibility_result: Accessibility checker result

    Returns:
        Dict with wcag_compliant, contrast_ratio, contrast_passes, size_issues
    """
    return {
        "wcag_compliant": safe_get(accessibility_result, "wcag_compliant", True),
        "contrast_ratio": safe_get(accessibility_result, "contrast_ratio", 7.0),
        "contrast_passes": safe_get(accessibility_result, "contrast_passes", True),
        "size_issues": safe_get(accessibility_result, "size_issues", []),
    }


def build_designer_output(
    povs_result: dict,
    color_result: dict,
    hierarchy_result: dict,
    accessibility_result: dict,
    widget_insights: dict,
    widget_list: list,
    query: str,
    domain: str,
    insights: list,
) -> dict[str, Any]:
    """Build final designer output from all module results.

    Args:
        povs_result: POV generator result
        color_result: Color picker result
        hierarchy_result: Hierarchy planner result
        accessibility_result: Accessibility checker result
        widget_insights: Widget-specific insights
        widget_list: List of widgets
        query: Original query
        domain: Domain
        insights: Original analysis insights

    Returns:
        Complete designer output dict
    """
    povs_data = get_povs_data(povs_result)
    color_data = get_color_data(color_result)
    hierarchy_data = get_hierarchy_data(hierarchy_result, widget_list)
    accessibility_data = get_accessibility_data(accessibility_result)

    return {
        **povs_data,
        **color_data,
        **hierarchy_data,
        "accessibility": accessibility_data,
        "query": query,
        "domain": domain,
        "insights": insights,
        "widget_insights": widget_insights,
    }
