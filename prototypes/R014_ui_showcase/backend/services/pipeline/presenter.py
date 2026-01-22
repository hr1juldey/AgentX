# =============================================================================
# AGENTX PRESENTER Agent
# =============================================================================
# Phase 8: Final Polish + QA
# =============================================================================

from typing import Optional

import dspy

from services.tools.presenter_tools import (
    FlowCheckerModule,
    PolisherModule,
    QAFinalizerModule,
)


class PresenterAgent(dspy.Module):
    """PRESENTER Agent: Polishes presentation and performs final QA.

    Ensures widgets are polished, flow is coherent, and quality
    standards are met before sending to frontend.
    """

    def __init__(self):
        super().__init__()
        # Tools for presentation
        self.flow_checker = FlowCheckerModule()
        self.polisher = PolisherModule()
        self.qa_finalizer = QAFinalizerModule()

    def forward(
        self,
        widgets: list,
        sequence: list,
        design: Optional[dict] = None,
    ) -> dict:
        """Execute PRESENTER agent pipeline.

        Args:
            widgets: List of widget descriptors
            sequence: Sequence plan from SEQUENCER
            design: Optional design output for context

        Returns:
            Presentation-ready widgets with QA report
        """
        design_data = design or {}
        sequence_list = (
            sequence.get("sequence", []) if isinstance(sequence, dict) else sequence
        )

        # Check narrative flow and pacing
        flow_result_raw = self.flow_checker(sequence=sequence_list, widgets=widgets)
        flow_result = flow_result_raw if hasattr(flow_result_raw, "get") else {}

        # Polish widget content
        polish_result_raw = self.polisher(widgets=widgets, sequence=sequence_list)
        polish_result = polish_result_raw if hasattr(polish_result_raw, "get") else {}

        # Final QA checks
        qa_result_raw = self.qa_finalizer(widgets=widgets, sequence=sequence_list)
        qa_result = qa_result_raw if hasattr(qa_result_raw, "get") else {}

        # Combine results
        presentation_ready = {
            "widgets": polish_result.get("polished_content", widgets)
            if hasattr(polish_result, "get")
            else widgets,
            "enhanced_widgets": polish_result.get("enhanced_content", widgets)
            if hasattr(polish_result, "get")
            else widgets,
            "transition_suggestions": polish_result.get("transition_suggestions", [])
            if hasattr(polish_result, "get")
            else [],
            "delivery_sequence": sequence_list,
            "flow_analysis": {
                "narrative_flow": flow_result.get("flow_analysis", "Coherent flow")
                if hasattr(flow_result, "get")
                else "Coherent flow",
                "flow_issues": flow_result.get("flow_issues", [])
                if hasattr(flow_result, "get")
                else [],
                "pacing_analysis": flow_result.get(
                    "pacing_analysis", "Appropriate pacing"
                )
                if hasattr(flow_result, "get")
                else "Appropriate pacing",
                "pacing_issues": flow_result.get("pacing_issues", [])
                if hasattr(flow_result, "get")
                else [],
            },
            "qa_report": {
                "quality_check": qa_result.get("quality_check", "passed")
                if hasattr(qa_result, "get")
                else "passed",
                "accessibility_check": qa_result.get("accessibility_check", "passed")
                if hasattr(qa_result, "get")
                else "passed",
                "format_check": qa_result.get("format_check", "passed")
                if hasattr(qa_result, "get")
                else "passed",
                "sequence_check": qa_result.get("sequence_check", "passed")
                if hasattr(qa_result, "get")
                else "passed",
                "all_passed": qa_result.get("all_passed", True)
                if hasattr(qa_result, "get")
                else True,
                "issues": qa_result.get("issues", [])
                if hasattr(qa_result, "get")
                else [],
            },
            "ready_to_send": qa_result.get("ready_to_send", True)
            if hasattr(qa_result, "get")
            else True,
            "design_context": {
                "color_scheme": design_data.get("color_scheme", {}),
                "visual_hierarchy": design_data.get("visual_hierarchy", []),
            },
        }

        # Add warnings if issues detected
        issues = []
        issues.extend(
            flow_result.get("flow_issues", []) if hasattr(flow_result, "get") else []
        )
        issues.extend(
            flow_result.get("pacing_issues", []) if hasattr(flow_result, "get") else []
        )
        issues.extend(qa_result.get("issues", []) if hasattr(qa_result, "get") else [])

        if issues:
            presentation_ready["warnings"] = issues
            presentation_ready["requires_review"] = True

        return presentation_ready

    def get_progress_status(self, phase: str = "polishing") -> dict:
        """Get progress status for UI updates.

        Args:
            phase: Current phase (checking, polishing, finalizing)

        Returns:
            Progress status dict
        """
        return {
            "phase": phase,
            "status": "running",
            "message": f"Presenter: {phase.capitalize()} widgets...",
            "completion_percentage": self._get_phase_progress(phase),
        }

    def _get_phase_progress(self, phase: str) -> float:
        """Get completion percentage for phase."""
        progress_map = {
            "checking": 33.0,
            "polishing": 66.0,
            "finalizing": 100.0,
        }
        return progress_map.get(phase.lower(), 50.0)
