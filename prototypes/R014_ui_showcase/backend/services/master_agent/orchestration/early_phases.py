# =============================================================================
# AGENTX Master Agent - Early Pipeline Phases
# =============================================================================
# Phases 1-4: Analyst, Researcher, Contextualizer, Analyst Judgment
# =============================================================================

import logging
from typing import TYPE_CHECKING, Any

from services.master_agent.orchestration.logging import (
    log_analysis_result,
    log_judgment_result,
    log_research_result,
)
from services.master_agent.orchestration.phase_executor import PhaseExecutor

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from services.pipeline.analyst import AnalystAgent
    from services.pipeline.data_contextualizer import DataContextualizerAgent
    from services.pipeline.researcher import ResearcherAgent


class EarlyPhases:
    """Early pipeline phases (1-4): Data gathering and analysis."""

    def __init__(self, executor: PhaseExecutor) -> None:
        """Initialize early phases.

        Args:
            executor: Phase executor instance
        """
        self.executor = executor

    def run_analyst_phase(
        self,
        analyst: "AnalystAgent",
        user_query: str,
        device_context: str,
    ) -> dict[str, Any]:
        """Phase 1: ANALYST - Understand query and context.

        Args:
            analyst: Analyst agent instance
            user_query: User's query
            device_context: Device context

        Returns:
            Analysis result dict
        """
        logger.info("  [ANALYST] Understanding query context...")
        result = self.executor.execute_phase(
            "analysis_qa",
            lambda: analyst(user_query=user_query, device_context=device_context),  # type: ignore[arg-type]
        )
        log_analysis_result(result)
        return result

    def run_researcher_phase(
        self,
        researcher: "ResearcherAgent",
        analysis_result: dict,
    ) -> dict[str, Any]:
        """Phase 2: RESEARCHER - Fetch live data.

        Args:
            researcher: Researcher agent instance
            analysis_result: Result from analyst phase

        Returns:
            Research result dict
        """
        # Check for search_terms from analyst
        search_terms = analysis_result.get("search_terms", [])
        if search_terms:
            logger.info(f"  [RESEARCHER] Search terms: {search_terms[:5]}")
        else:
            search_query = analysis_result.get("goal", analysis_result.get("query", ""))
            logger.info(
                f"  [RESEARCHER] No search terms, using: '{search_query[:80]}...'"
            )
        result = self.executor.execute_phase(
            "research_qa",
            lambda: researcher(analysis=analysis_result),  # type: ignore[arg-type]
        )
        log_research_result(result)
        return result

    def run_contextualizer_phase(
        self,
        data_contextualizer: "DataContextualizerAgent",
        research_result: dict,
    ) -> dict[str, Any]:
        """Phase 3: DATA CONTEXTUALIZER - Rerank, filter, contextualize.

        Args:
            data_contextualizer: Data contextualizer instance
            research_result: Result from researcher phase

        Returns:
            Contextualized result dict
        """
        doc_count = len(research_result.get("documents", []))
        logger.info(f"  [CONTEXTUALIZER] Processing {doc_count} documents...")
        result = self.executor.execute_phase(
            "contextualization_qa",
            lambda: data_contextualizer(research_data=research_result),  # type: ignore[arg-type]
        )
        return result

    def run_analyst_judgment_phase(
        self,
        analyst: "AnalystAgent",
        user_query: str,
        device_context: str,
        contextualized_result: dict,
    ) -> dict[str, Any]:
        """Phase 4: ANALYST (Pass 2) - Judge data quality.

        Args:
            analyst: Analyst agent instance
            user_query: User's query
            device_context: Device context
            contextualized_result: Result from contextualizer phase

        Returns:
            Judgment result dict
        """
        logger.info("  [ANALYST] Judging data quality...")
        result = self.executor.execute_phase(
            "judgment_qa",
            lambda: analyst(  # type: ignore[arg-type]
                user_query=user_query,
                device_context=device_context,
                contextualized_data=contextualized_result,
                pass_number=2,
            ),
        )
        log_judgment_result(result)
        return result
