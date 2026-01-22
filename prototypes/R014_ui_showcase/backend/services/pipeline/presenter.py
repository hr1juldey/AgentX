# =============================================================================
# AGENTX PRESENTER Agent
# =============================================================================
# Phase 8: Final Polish + QA
# =============================================================================

from typing import Optional

import dspy

from services.pipeline.presenter import (
    PresenterProgressTracker,
    PresenterResultBuilder,
)
from services.tools.presenter import (
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

        # Helpers
        self._result_builder = PresenterResultBuilder()
        self._progress_tracker = PresenterProgressTracker()

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

        # Build presentation_ready dict
        return self._result_builder.build_presentation_ready(
            widgets=widgets,
            sequence_list=sequence_list,
            design_data=design_data,
            flow_result=flow_result,
            polish_result=polish_result,
            qa_result=qa_result,
        )

    def get_progress_status(self, phase: str = "polishing") -> dict:
        """Get progress status for UI updates.

        Args:
            phase: Current phase (checking, polishing, finalizing)

        Returns:
            Progress status dict
        """
        return self._progress_tracker.get_progress_status(phase)
