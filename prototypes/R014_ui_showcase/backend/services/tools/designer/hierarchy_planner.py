# =============================================================================
# AGENTX Designer - Hierarchy Planner Module
# =============================================================================
# Plans visual hierarchy and flow
# =============================================================================

import dspy


class HierarchyPlannerModule(dspy.Module):
    """Plans visual hierarchy and flow.

    Has 2 signatures:
    - PlanVisualFlow: Plan how information flows visually
    - AssignPriority: Assign priority levels to elements
    """

    def __init__(self):
        super().__init__()
        self.plan_flow = dspy.Predict("widgets, query -> visual_flow")
        self.assign_priority = dspy.Predict("widgets -> priority_order")

    def forward(self, widgets: list, query: str = "") -> dict:
        """Plan visual hierarchy."""
        widgets_str = str(widgets)
        flow_result = self.plan_flow(widgets=widgets_str, query=query)
        priority_result = self.assign_priority(widgets=widgets_str)

        return {
            "visual_hierarchy": [
                item.strip()
                for item in str(flow_result.visual_flow).split(",")
                if item.strip()
            ]
            if hasattr(flow_result, "visual_flow")
            else ["hero", "insights", "details"],
            "priority_order": [
                item.strip()
                for item in str(priority_result.priority_order).split(",")
                if item.strip()
            ]
            if hasattr(priority_result, "priority_order")
            else widgets,
            "layout": "narrative_focused",
        }
