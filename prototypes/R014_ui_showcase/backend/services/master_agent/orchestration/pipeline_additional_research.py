# =============================================================================
# AGENTX Master Agent - Additional Research Execution
# =============================================================================
# Conditional additional research logic
# =============================================================================

import logging

from services.master_agent.orchestration.early_phases import EarlyPhases
from services.master_agent.orchestration.research_merger import merge_research_results
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.pipeline.data_contextualizer import DataContextualizerAgent
    from services.pipeline.researcher import ResearcherAgent

logger = logging.getLogger(__name__)


def execute_additional_research(
    early: EarlyPhases,
    researcher: "ResearcherAgent",
    data_contextualizer: "DataContextualizerAgent",
    judgment_result: dict,
    contextualized_result: dict,
) -> dict:
    """Execute additional research if needed.

    Args:
        early: Early phases executor
        researcher: Research agent instance
        data_contextualizer: Data contextualizer instance
        judgment_result: Judgment result from analyst
        contextualized_result: Current contextualized result

    Returns:
        Merged contextualized result
    """
    logger.info("  [RESEARCHER] Additional research needed...")
    research_result = early.run_researcher_phase(
        researcher,
        judgment_result,
    )
    additional_context = early.run_contextualizer_phase(
        data_contextualizer,
        research_result,
    )
    # Merge additional research with first research instead of replacing
    return merge_research_results(contextualized_result, additional_context)
