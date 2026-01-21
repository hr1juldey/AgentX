# =============================================================================
# AGENTX Widget Spawner - Context Analyzer Agent
# =============================================================================
# Analyzes user queries to understand content type, user intent, and context.
# Uses DSPy ReAct pattern for automatic tool selection.
# =============================================================================

import json
import logging
from typing import Dict, Any

import dspy

logger = logging.getLogger(__name__)


def detect_content_type(query: str) -> str:
    """Detect content type from keywords."""
    query_lower = query.lower()

    if any(kw in query_lower for kw in ["data", "trends", "sales", "chart", "graph", "statistics", "analytics", "metrics"]):
        return "data-heavy"
    elif any(kw in query_lower for kw in ["explain", "guide", "article", "summary", "blog", "description"]):
        return "text-heavy"
    elif any(kw in query_lower for kw in ["image", "photo", "gallery", "picture", "visual"]):
        return "visual-heavy"
    return "mixed"


def infer_user_goal(query: str) -> str:
    """Infer user intent from query."""
    query_lower = query.lower()

    if any(kw in query_lower for kw in ["compare", "vs", "versus", "difference", "better", "between"]):
        return "comparison"
    elif any(kw in query_lower for kw in ["show", "display", "what", "list", "all"]):
        return "exploration"
    elif any(kw in query_lower for kw in ["should", "recommend", "best", "choose", "decision"]):
        return "decision"
    elif any(kw in query_lower for kw in ["monitor", "track", "status", "progress"]):
        return "monitor"
    return "general"


def check_device_capabilities(device_context_str: str) -> str:
    """Check device capabilities for responsive design."""
    try:
        device_context = json.loads(device_context_str)
    except (json.JSONDecodeError, TypeError):
        return "desktop"

    device_type = device_context.get("type", "desktop")

    if device_type == "mobile":
        return "mobile"
    elif device_type == "tablet":
        return "tablet"
    return "desktop"


class AnalyzeContextSignature(dspy.Signature):
    """Analyze user query and context to understand requirements."""
    user_query: str = dspy.InputField(desc="User's natural language request")
    device_context: str = dspy.InputField(desc="Device type, screen size")
    content_analysis: str = dspy.OutputField(desc="Content type, complexity, structure")
    user_intent: str = dspy.OutputField(desc="Goal: explore/compare/decide/monitor")
    presentation_constraints: str = dspy.OutputField(desc="Layout limits, accessibility needs")


class ContextAnalyzerAgent(dspy.Module):
    """
    Context analyzer using ReAct for automatic tool selection.

    This agent uses DSPy's ReAct pattern to automatically decide which tools
    to call based on the user's query - no explicit instruction needed.
    """

    def __init__(self):
        super().__init__()
        # Use ReAct to analyze context with tools
        self.analyzer = dspy.ReAct(
            AnalyzeContextSignature,
            tools=[
                detect_content_type,
                infer_user_goal,
                check_device_capabilities,
            ],
            max_iters=3,
        )

    def forward(self, user_query: str, device_context: Dict[str, Any]) -> dspy.Prediction:
        """
        Analyze the user's query to understand context.

        Args:
            user_query: The user's natural language request
            device_context: Device information (type, screen_width, screen_height)

        Returns:
            dspy.Prediction with content_analysis, user_intent, presentation_constraints
        """
        logger.debug(f"🔍 ContextAnalyzer analyzing: {user_query[:100]}")

        result = self.analyzer(
            user_query=user_query,
            device_context=json.dumps(device_context)
        )

        logger.debug(f"🔍 Context analysis: {result.content_analysis}, intent: {result.user_intent}")

        return result
