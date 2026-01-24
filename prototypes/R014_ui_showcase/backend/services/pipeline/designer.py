# =============================================================================
# AGENTX DESIGNER Agent
# =============================================================================
# Phase 5: POV + Color Schemes
# =============================================================================

from typing import Optional

import dspy

from services.tools.designer import (
    AccessibilityModule,
    ColorPickerModule,
    HierarchyPlannerModule,
    POVGeneratorModule,
)
from services.tools.designer.widget_insights import WidgetInsightsModule


class DesignerAgent(dspy.Module):
    """DESIGNER Agent: Adds points of view, color schemes, visual hierarchy.

    Works with researched data to create presentation-ready design
    with multiple perspectives and appropriate styling.
    """

    def __init__(self):
        super().__init__()
        # Tools for design
        self.pov_generator = POVGeneratorModule()
        self.color_picker = ColorPickerModule()
        self.hierarchy_planner = HierarchyPlannerModule()
        self.accessibility = AccessibilityModule()
        self.insights_generator = WidgetInsightsModule()

    def forward(
        self,
        researched_data: dict,
        analysis: dict,
        widgets: Optional[list] = None,
    ) -> dict:
        """Execute DESIGNER agent pipeline.

        Args:
            researched_data: Research output from RESEARCHER/CONTEXTUALIZER
            analysis: Analysis result from ANALYST agent
            widgets: Optional widget list for hierarchy planning

        Returns:
            Design plan with POVs, colors, and visual hierarchy
        """
        query = researched_data.get("query", "")
        domain = analysis.get("domain", "general")
        insights = analysis.get("insights", [])

        # Generate balanced POVs
        povs_result_raw = self.pov_generator(
            query=query, researched_data=researched_data
        )
        povs_result = povs_result_raw if hasattr(povs_result_raw, "get") else {}

        # Pick color scheme based on domain
        color_result_raw = self.color_picker(query=query, domain=domain)
        color_result = color_result_raw if hasattr(color_result_raw, "get") else {}

        # Plan visual hierarchy
        widget_list = widgets or analysis.get("suggested_widgets", ["markdown"])
        hierarchy_result_raw = self.hierarchy_planner(widgets=widget_list, query=query)
        hierarchy_result = (
            hierarchy_result_raw if hasattr(hierarchy_result_raw, "get") else {}
        )

        # Check accessibility
        design_for_check = {
            "color_scheme": color_result.get("color_scheme", {})
            if hasattr(color_result, "get")
            else {},
            "widgets": widget_list,
            "layout": hierarchy_result.get("layout", "narrative_focused")
            if hasattr(hierarchy_result, "get")
            else "narrative_focused",
        }
        accessibility_result_raw = self.accessibility(design=design_for_check)
        accessibility_result = (
            accessibility_result_raw if hasattr(accessibility_result_raw, "get") else {}
        )

        # Generate widget-specific insights
        widget_insights = {}
        for widget_type in set(widget_list):  # Unique types only
            insights_result_raw = self.insights_generator(
                query=query,
                data=researched_data,
                widget_type=widget_type,
            )
            insights_result = (
                insights_result_raw if hasattr(insights_result_raw, "get") else {}
            )
            widget_insights[widget_type] = insights_result.get("insights", [])

        return {
            "points_of_view": povs_result.get("points_of_view", [])
            if hasattr(povs_result, "get")
            else [],
            "balanced_povs": povs_result.get("balanced_povs", [])
            if hasattr(povs_result, "get")
            else [],
            "nuanced_analysis": povs_result.get("nuanced_analysis", "")
            if hasattr(povs_result, "get")
            else "",
            "color_scheme": color_result.get(
                "color_scheme",
                {
                    "primary": "blue_500",
                    "accent": "green_400",
                    "background": "slate_900",
                },
            )
            if hasattr(color_result, "get")
            else {
                "primary": "blue_500",
                "accent": "green_400",
                "background": "slate_900",
            },
            "contrast_ratio": color_result.get("contrast_ratio", 7.0)
            if hasattr(color_result, "get")
            else 7.0,
            "visual_hierarchy": hierarchy_result.get(
                "visual_hierarchy", ["hero", "insights", "details"]
            )
            if hasattr(hierarchy_result, "get")
            else ["hero", "insights", "details"],
            "priority_order": hierarchy_result.get("priority_order", widget_list)
            if hasattr(hierarchy_result, "get")
            else widget_list,
            "layout": hierarchy_result.get("layout", "narrative_focused")
            if hasattr(hierarchy_result, "get")
            else "narrative_focused",
            "accessibility": {
                "wcag_compliant": accessibility_result.get("wcag_compliant", True)
                if hasattr(accessibility_result, "get")
                else True,
                "contrast_ratio": accessibility_result.get("contrast_ratio", 7.0)
                if hasattr(accessibility_result, "get")
                else 7.0,
                "contrast_passes": accessibility_result.get("contrast_passes", True)
                if hasattr(accessibility_result, "get")
                else True,
                "size_issues": accessibility_result.get("size_issues", [])
                if hasattr(accessibility_result, "get")
                else [],
            },
            "query": query,
            "domain": domain,
            "insights": insights,  # Original analysis insights
            "widget_insights": widget_insights,  # Widget-specific insights
        }
