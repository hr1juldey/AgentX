# =============================================================================
# AGENTX Master Agent - Late Pipeline Phases
# =============================================================================
# Phases 5-8: Designer, Widget Selector, Sequencer, Presenter
# =============================================================================

import logging
from typing import TYPE_CHECKING, Any

from services.master_agent.orchestration.logging import (
    log_design_result,
    log_widget_selection,
)
from services.master_agent.orchestration.phase_executor import PhaseExecutor

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from services.pipeline.designer import DesignerAgent
    from services.pipeline.presenter import PresenterAgent
    from services.pipeline.sequencer import SequencerAgent
    from services.pipeline.widget_selector import WidgetSelectorAgent


class LatePhases:
    """Late pipeline phases (5-8): Design and presentation."""

    def __init__(self, executor: PhaseExecutor) -> None:
        """Initialize late phases.

        Args:
            executor: Phase executor instance
        """
        self.executor = executor

    def run_designer_phase(
        self,
        designer: "DesignerAgent",
        contextualized_result: dict,
        analysis_result: dict,
    ) -> dict[str, Any]:
        """Phase 5: DESIGNER - Add POVs, color schemes.

        Args:
            designer: Designer agent instance
            contextualized_result: Result from contextualizer
            analysis_result: Result from initial analyst phase

        Returns:
            Design result dict
        """
        logger.info("  [DESIGNER] Adding design context...")
        result = self.executor.execute_phase(
            "design_qa",
            lambda: designer(  # type: ignore[arg-type]
                researched_data=contextualized_result,
                analysis=analysis_result,
            ),
        )
        log_design_result(result)
        return result

    def run_widget_selector_phase(
        self,
        widget_selector: "WidgetSelectorAgent",
        design_result: dict,
        device_context: str,
    ) -> dict[str, Any]:
        """Phase 6: WIDGET SELECTOR - Choose widgets.

        Args:
            widget_selector: Widget selector instance
            design_result: Result from designer phase
            device_context: Device context

        Returns:
            Widget selection dict
        """
        logger.info("  [WIDGET SELECTOR] Choosing widgets...")
        result = self.executor.execute_phase(
            "widget_selection_qa",
            lambda: widget_selector(  # type: ignore[arg-type]
                designed_data=design_result,
                device_context=device_context,
            ),
        )
        log_widget_selection(result)
        return result

    def run_sequencer_phase(
        self,
        sequencer: "SequencerAgent",
        widget_selection: dict,
        user_query: str,
    ) -> dict[str, Any]:
        """Phase 7: SEQUENCER - Plan delivery order.

        Args:
            sequencer: Sequencer instance
            widget_selection: Result from widget selector phase
            user_query: User's query

        Returns:
            Sequence plan dict
        """
        logger.info("  [SEQUENCER] Planning delivery order...")
        result = self.executor.execute_phase(
            "sequence_qa",
            lambda: sequencer(  # type: ignore[arg-type]
                widgets=widget_selection.get("widgets", []),
                user_query=user_query,
            ),
        )
        return result

    def run_presenter_phase(
        self,
        presenter: "PresenterAgent",
        widget_selection: dict,
        sequence_plan: dict,
        design_result: dict,
        researched_data: dict,
    ) -> dict[str, Any]:
        """Phase 8: PRESENTER - Final polish and QA.

        Args:
            presenter: Presenter instance
            widget_selection: Result from widget selector
            sequence_plan: Result from sequencer
            design_result: Result from designer
            researched_data: Research data from contextualizer

        Returns:
            Presentation ready dict
        """
        logger.info("  [PRESENTER] Final polish...")
        result = self.executor.execute_phase(
            "presentation_qa",
            lambda: presenter(  # type: ignore[arg-type]
                widgets=widget_selection.get("widgets", []),
                sequence=sequence_plan.get("sequence", []),
                design=design_result,
                researched_data=researched_data,
            ),
        )
        return result
