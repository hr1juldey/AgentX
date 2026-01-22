# =============================================================================
# AGENTX Master Agent - Pipeline Orchestrator
# =============================================================================
# Orchestrates the 10-phase Master Agent pipeline
# =============================================================================

import logging
from typing import TYPE_CHECKING, Any, Callable

from services.master_agent.qa_checkpoints import QACheckpointModule
from services.master_agent.orchestration.logging import (
    log_analysis_result,
    log_design_result,
    log_judgment_result,
    log_research_result,
    log_widget_selection,
)

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from services.pipeline.analyst import AnalystAgent
    from services.pipeline.data_contextualizer import DataContextualizerAgent
    from services.pipeline.designer import DesignerAgent
    from services.pipeline.presenter import PresenterAgent
    from services.pipeline.researcher import ResearcherAgent
    from services.pipeline.sequencer import SequencerAgent
    from services.pipeline.widget_selector import WidgetSelectorAgent


class PipelineOrchestrator:
    """Orchestrates the 10-phase Master Agent pipeline.

    Manages sequential execution with QA checkpoints.
    """

    def __init__(
        self,
        qa: QACheckpointModule,
        qa_callback: Callable | None = None,
    ) -> None:
        """Initialize pipeline orchestrator.

        Args:
            qa: QA checkpoint module
            qa_callback: Optional callback for QA progress
        """
        self.qa = qa
        self.qa_callback = qa_callback

    def execute_pipeline(
        self,
        analyst: "AnalystAgent",
        researcher: "ResearcherAgent",
        data_contextualizer: "DataContextualizerAgent",
        designer: "DesignerAgent",
        widget_selector: "WidgetSelectorAgent",
        sequencer: "SequencerAgent",
        presenter: "PresenterAgent",
        user_query: str,
        device_context: str,
    ) -> dict[str, Any]:
        """Execute the full pipeline.

        Args:
            analyst: Analyst agent instance
            researcher: Researcher agent instance
            data_contextualizer: Data contextualizer instance
            designer: Designer agent instance
            widget_selector: Widget selector instance
            sequencer: Sequencer instance
            presenter: Presenter instance
            user_query: User's query
            device_context: Device context

        Returns:
            Dict with sequence plan, design result, widget selection, etc.
        """
        # Phase 1: ANALYST - Understand query and context
        logger.info("  [ANALYST] Understanding query context...")
        analysis_result = self._run_phase(
            "analysis_qa",
            lambda: analyst(user_query=user_query, device_context=device_context),  # type: ignore[arg-type]
        )
        log_analysis_result(analysis_result)

        # Phase 2: RESEARCHER - Fetch live data
        search_query = analysis_result.get("search_query", user_query)
        logger.info(f"  [RESEARCHER] Searching: '{search_query[:80]}...'")
        research_result = self._run_phase(
            "research_qa",
            lambda: researcher(analysis=analysis_result),  # type: ignore[arg-type]
        )
        log_research_result(research_result)

        # Phase 3: DATA CONTEXTUALIZER - Rerank, filter, contextualize
        logger.info(
            f"  [CONTEXTUALIZER] Processing {len(research_result.get('documents', []))} documents..."
        )
        contextualized_result = self._run_phase(
            "contextualization_qa",
            lambda: data_contextualizer(research_data=research_result),  # type: ignore[arg-type]
        )

        # Phase 4: ANALYST (Pass 2) - Judge data quality
        logger.info("  [ANALYST] Judging data quality...")
        judgment_result = self._run_phase(
            "judgment_qa",
            lambda: analyst(  # type: ignore[arg-type]
                user_query=user_query,
                device_context=device_context,
                contextualized_data=contextualized_result,
                pass_number=2,
            ),
        )
        log_judgment_result(judgment_result)

        # Check if more research is needed
        if judgment_result.get("needs_more_research", False):
            logger.info("  [RESEARCHER] Additional research needed...")
            research_result = self._run_phase(
                "research_qa",
                lambda: researcher(  # type: ignore[arg-type]
                    analysis=judgment_result,
                    previous_data=research_result,
                ),
            )
            contextualized_result = self._run_phase(
                "contextualization_qa",
                lambda: data_contextualizer(research_data=research_result),  # type: ignore[arg-type]
            )

        # Phase 5: DESIGNER - Add POVs, color schemes
        logger.info("  [DESIGNER] Adding design context...")
        design_result = self._run_phase(
            "design_qa",
            lambda: designer(  # type: ignore[arg-type]
                researched_data=contextualized_result,
                analysis=analysis_result,
            ),
        )
        log_design_result(design_result)

        # Phase 6: WIDGET SELECTOR - Choose widgets
        logger.info("  [WIDGET SELECTOR] Choosing widgets...")
        widget_selection = self._run_phase(
            "widget_selection_qa",
            lambda: widget_selector(  # type: ignore[arg-type]
                designed_data=design_result,
                device_context=device_context,
            ),
        )
        log_widget_selection(widget_selection)

        # Phase 7: SEQUENCER - Plan delivery order
        logger.info("  [SEQUENCER] Planning delivery order...")
        sequence_plan = self._run_phase(
            "sequence_qa",
            lambda: sequencer(  # type: ignore[arg-type]
                widgets=widget_selection.get("widgets", []),
                user_query=user_query,
            ),
        )

        # Phase 8: PRESENTER - Final polish and QA
        logger.info("  [PRESENTER] Final polish...")
        presentation_ready = self._run_phase(
            "presentation_qa",
            lambda: presenter(  # type: ignore[arg-type]
                widgets=widget_selection.get("widgets", []),
                sequence=sequence_plan.get("sequence", []),
                design=design_result,
            ),
        )

        return {
            "sequence_plan": sequence_plan,
            "design_result": design_result,
            "widget_selection": widget_selection,
            "presentation_ready": presentation_ready,
        }

    def _run_phase(self, checkpoint_name: str, phase_func: Callable) -> dict:
        """Run a single pipeline phase with QA checkpoint.

        Args:
            checkpoint_name: Name of the QA checkpoint
            phase_func: Function to execute for this phase

        Returns:
            Phase result data
        """
        try:
            result = phase_func()
            self.qa.validate_checkpoint(checkpoint_name, result)
            self._emit_qa_progress(checkpoint_name, "passed", result)
            return result
        except Exception as e:
            self.qa.mark_failed(checkpoint_name, str(e))
            self._emit_qa_progress(checkpoint_name, "failed", {"error": str(e)})
            raise

    def _emit_qa_progress(self, checkpoint: str, status: str, data: dict) -> None:
        """Emit QA progress to frontend via callback.

        Args:
            checkpoint: Checkpoint name
            status: Status (passed, failed, running)
            data: Additional data to send
        """
        if self.qa_callback:
            try:
                import asyncio

                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.create_task(self.qa_callback(checkpoint, status, data))
            except Exception:
                pass  # Silently fail if callback fails
