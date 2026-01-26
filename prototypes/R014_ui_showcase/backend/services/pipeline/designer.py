# =============================================================================
# AGENTX DESIGNER Agent
# =============================================================================
# Phase 5: POV + Color Schemes
# =============================================================================

from typing import Optional

import dspy

from services.pipeline.designer_helpers import (
    build_designer_output,
    safe_get,
)
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
            "color_scheme": safe_get(color_result, "color_scheme", {}),
            "widgets": widget_list,
            "layout": safe_get(hierarchy_result, "layout", "narrative_focused"),
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
            widget_insights[widget_type] = safe_get(insights_result, "insights", [])

        return build_designer_output(
            povs_result=povs_result,
            color_result=color_result,
            hierarchy_result=hierarchy_result,
            accessibility_result=accessibility_result,
            widget_insights=widget_insights,
            widget_list=widget_list,
            query=query,
            domain=domain,
            insights=insights,
        )
