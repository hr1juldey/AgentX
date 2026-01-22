# =============================================================================
# AGENTX ANALYST Agent
# =============================================================================
# Phase 1 & 4: Reasoning + Judgment (CoT modules)
# =============================================================================

from typing import Optional

import dspy

from services.tools.analyst_tools import (
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
            return self._initial_analysis(user_query, device_context)
        else:
            # Ensure we have a dict for contextualized_data
            data = contextualized_data if contextualized_data is not None else {}
            return self._data_judgment(user_query, data)

    def _initial_analysis(self, user_query: str, device_context: str) -> dict:
        """Pass 1: Initial query analysis."""
        # Analyze context
        context_result = self.context_analyzer(query=user_query)
        context = context_result if hasattr(context_result, "get") else {}

        # Extract insights
        insights_result = self.insight_extractor(query=user_query)
        insights = insights_result if hasattr(insights_result, "get") else {}

        # Detect goals
        goals_result = self.goal_detector(
            query=user_query,
            insights=insights.get("insights", []) if hasattr(insights, "get") else [],
        )
        goals = goals_result if hasattr(goals_result, "get") else {}

        # Ensure context and goals are dicts before passing to _suggest_widgets
        context_dict = context if isinstance(context, dict) else {}
        goals_dict = goals if isinstance(goals, dict) else {}

        return {
            "query_type": context.get("query_type", "general")
            if hasattr(context, "get")
            else "general",
            "domain": context.get("domain", "general")
            if hasattr(context, "get")
            else "general",
            "urgency": context.get("urgency", "normal")
            if hasattr(context, "get")
            else "normal",
            "insights": insights.get("insights", [])
            if hasattr(insights, "get")
            else [],
            "key_questions": insights.get("key_questions", [])
            if hasattr(insights, "get")
            else [],
            "goal": goals.get("goal", "") if hasattr(goals, "get") else "",
            "scope": goals.get("scope", "general")
            if hasattr(goals, "get")
            else "general",
            "depth": goals.get("depth", "medium")
            if hasattr(goals, "get")
            else "medium",
            "suggested_widgets": self._suggest_widgets(context_dict, goals_dict),
        }

    def _data_judgment(self, user_query: str, contextualized_data: dict) -> dict:
        """Pass 2: Judge data quality and completeness."""
        judgment_result = self.data_quality_checker(
            query=user_query,
            data=contextualized_data.get("contextualized_data", contextualized_data),
        )
        judgment = judgment_result if hasattr(judgment_result, "get") else {}

        return {
            "data_quality": judgment.get("data_quality", "medium")
            if hasattr(judgment, "get")
            else "medium",
            "data_completeness": judgment.get("data_completeness", 0.5)
            if hasattr(judgment, "get")
            else 0.5,
            "query_relevance": judgment.get("query_relevance", "medium")
            if hasattr(judgment, "get")
            else "medium",
            "needs_more_research": judgment.get("needs_more_research", False)
            if hasattr(judgment, "get")
            else False,
            "judgment": judgment.get("reason", "") if hasattr(judgment, "get") else "",
        }

    def _suggest_widgets(self, context: dict, goals: dict) -> list:
        """Suggest initial widgets based on context and goals."""
        # This is a simplified suggestion - Widget Selector will make final decision
        suggestions = []

        query_type = context.get("query_type", "") if hasattr(context, "get") else ""
        domain = context.get("domain", "") if hasattr(context, "get") else ""
        depth = goals.get("depth", "") if hasattr(goals, "get") else ""

        # Default widgets for most queries
        suggestions.extend(["markdown"])

        if "comparison" in query_type.lower() or "finance" in domain.lower():
            suggestions.extend(["chart", "card"])

        if depth == "deep" or depth == "comprehensive":
            suggestions.extend(["form"])

        # Remove duplicates while preserving order
        seen = set()
        unique_suggestions = []
        for s in suggestions:
            if s not in seen:
                seen.add(s)
                unique_suggestions.append(s)

        return unique_suggestions
