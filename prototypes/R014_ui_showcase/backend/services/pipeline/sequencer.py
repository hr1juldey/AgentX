# =============================================================================
# AGENTX SEQUENCER Agent
# =============================================================================
# Phase 7: What Order?
# =============================================================================

from typing import Optional

import dspy

from services.tools.sequencing_tools import (
    FlowPlannerModule,
    PacingCalculatorModule,
)


class SequencerAgent(dspy.Module):
    """SEQUENCER Agent: Plans widget order and timing for narrative flow.

    Determines the optimal sequence for widget delivery to create
    a compelling narrative (hook → context → insight → action).
    """

    def __init__(self):
        super().__init__()
        # Tools for sequencing
        self.flow_planner = FlowPlannerModule()
        self.pacing_calculator = PacingCalculatorModule()

    def forward(
        self,
        widgets: list,
        user_query: str = "",
        design: Optional[dict] = None,
    ) -> dict:
        """Execute SEQUENCER agent pipeline.

        Args:
            widgets: List of widgets to sequence
            user_query: Original user query for context
            design: Optional design output for hierarchy hints

        Returns:
            Sequence plan with timing and narrative arc
        """
        design_data = design or {}
        visual_hierarchy = design_data.get(
            "visual_hierarchy", ["hero", "insights", "details"]
        )

        # Plan narrative flow
        flow_result_raw = self.flow_planner(widgets=widgets, query=user_query)
        flow_result = flow_result_raw if hasattr(flow_result_raw, "get") else {}

        sequence = (
            flow_result.get("sequence", widgets)
            if hasattr(flow_result, "get")
            else widgets
        )
        narrative_arc = (
            flow_result.get("narrative_arc", "hook → context → insight → action")
            if hasattr(flow_result, "get")
            else "hook → context → insight → action"
        )
        is_valid = (
            flow_result.get("is_valid", True) if hasattr(flow_result, "get") else True
        )

        # Create sequence items with order
        sequence_items = []
        for i, widget in enumerate(sequence):
            widget_name = (
                widget.get("widget", widget) if isinstance(widget, dict) else widget
            )
            sequence_items.append(
                {
                    "widget": widget_name,
                    "order": i + 1,
                }
            )

        # Calculate pacing for staggered delivery
        pacing_result_raw = self.pacing_calculator(
            widgets=widgets,
            sequence=sequence_items,
        )
        pacing_result = pacing_result_raw if hasattr(pacing_result_raw, "get") else {}

        sequence_for_plan = (
            pacing_result.get("sequence", sequence_items)
            if hasattr(pacing_result, "get")
            else sequence_items
        )

        return {
            "sequence": sequence_for_plan,
            "narrative_arc": narrative_arc,
            "is_valid": is_valid,
            "total_duration": pacing_result.get("total_duration", 0)
            if hasattr(pacing_result, "get")
            else 0,
            "delivery_plan": self._create_delivery_plan(
                sequence_for_plan,
                visual_hierarchy,
            ),
        }

    def _create_delivery_plan(self, sequence: list, visual_hierarchy: list) -> list:
        """Create detailed delivery plan."""
        delivery_plan = []

        for item in sequence:
            widget = item.get("widget", "unknown")
            order = item.get("order", 1)
            delay = item.get("delay_sec", 0.0)

            # Determine visual role based on order and hierarchy
            if len(visual_hierarchy) > 0:
                role_index = min(order - 1, len(visual_hierarchy) - 1)
                visual_role = visual_hierarchy[role_index]
            else:
                visual_role = "standard"

            delivery_plan.append(
                {
                    "widget": widget,
                    "order": order,
                    "delay_sec": delay,
                    "visual_role": visual_role,
                    "delivery_type": "immediate" if delay == 0 else "staggered",
                }
            )

        return delivery_plan
