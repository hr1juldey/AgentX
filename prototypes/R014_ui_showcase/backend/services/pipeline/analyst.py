# =============================================================================
# AGENTX ANALYST Agent
# =============================================================================
# Phase 1 & 4: Reasoning + Judgment (CoT modules)
# =============================================================================

from typing import Optional

import dspy

from services.pipeline.analyst import (
    DataJudgmentHandler,
    InitialAnalysisHandler,
)
from services.tools.analyst import (
    ContextAnalyzerModule,
    DataQualityCheckerModule,
    GoalDetectorModule,
    InsightExtractorModule,
)


class AnalystAgent(dspy.Module):
    """ANALYST Agent: Makes sense of queries and judges data quality.

    Runs twice in the pipeline:
    - Pass 1: Understand query and context (before research)
    - Pass 2: Judge data quality and completeness (after contextualization)
    """

    def __init__(self):
        super().__init__()
        # Tools for Pass 1 (Initial Analysis)
        self.context_analyzer = ContextAnalyzerModule()
        self.insight_extractor = InsightExtractorModule()
        self.goal_detector = GoalDetectorModule()

        # Tools for Pass 2 (Data Judgment)
        self.data_quality_checker = DataQualityCheckerModule()

        # Handlers
        self._initial_analysis_handler = InitialAnalysisHandler(
            self.context_analyzer,
            self.insight_extractor,
            self.goal_detector,
        )
        self._data_judgment_handler = DataJudgmentHandler(
            self.data_quality_checker,
        )

    def forward(
        self,
        user_query: str,
        device_context: str = "desktop",
        contextualized_data: Optional[dict] = None,
        pass_number: int = 1,
    ) -> dict:
        """Execute ANALYST agent based on pass number.

        Args:
            user_query: The user's query
            device_context: Device context (desktop, mobile, etc.)
            contextualized_data: Data from contextualizer (Pass 2 only)
            pass_number: 1 for initial analysis, 2 for judgment

        Returns:
            Analysis or judgment result
        """
        if pass_number == 1:
            result = self._initial_analysis_handler.analyze(user_query, device_context)
            # Remove internal keys from result
            result.pop("_context", None)
            result.pop("_goals", None)
            return result
        else:
            # Ensure we have a dict for contextualized_data
            data = contextualized_data if contextualized_data is not None else {}
            return self._data_judgment_handler.judge(user_query, data)
