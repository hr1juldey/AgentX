# =============================================================================
# AGENTX SEQUENCER Agent
# =============================================================================
# Phase 7: What Order?
# =============================================================================

import logging
from typing import Optional

import dspy
from services.pipeline.sequencer_logging import (
    log_narrative_flow_result,
    log_pacing_result,
)
from services.pipeline.sequencer_utils import create_delivery_plan
from services.tools.sequencing_tools import (
    FlowPlannerModule,
    PacingCalculatorModule,
)

logger = logging.getLogger(__name__)


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
        logger.info("  [SEQUENCER] Planning narrative flow...")
        flow_result_raw = self.flow_planner(widgets=widgets, user_query=user_query)
        flow_result: dict = (
            flow_result_raw if hasattr(flow_result_raw, "get") else {}  # type: ignore[bad-assignment]
        )

        sequence = (
            flow_result.get("sequence", widgets)
            if hasattr(flow_result, "get")
            else widgets
        )
        narrative_arc, is_valid = log_narrative_flow_result(flow_result)
        logger.info(
            f"    → Sequence length: {len(sequence)} widgets, valid: {is_valid}"
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
        logger.info("  [SEQUENCER] Calculating pacing...")
        pacing_result_raw = self.pacing_calculator(
            widgets=widgets,
            sequence=sequence_items,
        )
        pacing_result: dict = (
            pacing_result_raw if hasattr(pacing_result_raw, "get") else {}  # type: ignore[bad-assignment]
        )

        sequence_for_plan = (
            pacing_result.get("sequence", sequence_items)
            if hasattr(pacing_result, "get")
            else sequence_items
        )

        total_duration = log_pacing_result(pacing_result, sequence)

        return {
            "sequence": sequence_for_plan,
            "narrative_arc": narrative_arc,
            "is_valid": is_valid,
            "total_duration": total_duration,
            "delivery_plan": create_delivery_plan(
                sequence_for_plan,
                visual_hierarchy,
            ),
        }
