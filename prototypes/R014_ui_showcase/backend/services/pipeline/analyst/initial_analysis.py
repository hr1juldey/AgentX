# =============================================================================
# AGENTX ANALYST - Initial Analysis
# =============================================================================
# Pass 1: Initial query analysis logic
# =============================================================================

from typing import Any, Dict

from services.tools.analyst import (
    ContextAnalyzerModule,
    GoalDetectorModule,
    InsightExtractorModule,
)


class InitialAnalysisHandler:
    """Handles Pass 1: Initial query analysis."""

    def __init__(
        self,
        context_analyzer: ContextAnalyzerModule,
        insight_extractor: InsightExtractorModule,
        goal_detector: GoalDetectorModule,
    ):
        """Initialize initial analysis handler.

        Args:
            context_analyzer: Context analyzer module
            insight_extractor: Insight extractor module
            goal_detector: Goal detector module
        """
        self.context_analyzer = context_analyzer
        self.insight_extractor = insight_extractor
        self.goal_detector = goal_detector

    def analyze(self, user_query: str, device_context: str) -> Dict[str, Any]:
        """Perform initial query analysis.

        Args:
            user_query: The user's query
            device_context: Device context

        Returns:
            Analysis result dict
        """
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

        # Ensure context and goals are dicts
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
            "_context": context_dict,
            "_goals": goals_dict,
        }

    def _suggest_widgets(self, context: dict, goals: dict) -> list:
        """Suggest initial widgets based on context and goals.

        Args:
            context: Context analysis result
            goals: Goals analysis result

        Returns:
            List of suggested widget types
        """
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
