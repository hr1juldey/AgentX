# =============================================================================
# AGENTX Designer - Widget Insights Generator Module
# =============================================================================
# Generates insights specific to widget types
# =============================================================================

import dspy
import json
import logging

from services.tools.hydrators.signatures import WidgetInsights

logger = logging.getLogger(__name__)


class WidgetInsightsModule(dspy.Module):
    """Generates insights specific to widget types.

    Uses DSPy signature to generate widget-specific insights:
    - Cards: Key metrics and statistics
    - Forms: Data collection points
    - Charts: Trends and patterns
    - Markdown: Narrative themes
    """

    def __init__(self):
        super().__init__()
        self.generate_insights = dspy.Predict(WidgetInsights)

    def forward(self, query: str, data: dict, widget_type: str) -> dict:
        """Generate widget-specific insights."""
        try:
            result = self.generate_insights(
                query=query,
                data=str(data),
                widget_type=widget_type,
            )

            # Extract structured output
            insights_str = getattr(result, "insights", "[]")

            # Parse insights
            try:
                if isinstance(insights_str, str):
                    insights = json.loads(insights_str)
                elif isinstance(insights_str, list):
                    insights = insights_str
                else:
                    insights = []
            except (json.JSONDecodeError, TypeError):
                insights = []

            return {
                "insights": insights[:5],  # Max 5 insights
                "insight_count": len(insights[:5]),
            }

        except Exception as e:
            logger.error(f"Widget insights generator error: {e}")
            return {
                "insights": [],
                "insight_count": 0,
                "error": str(e),
            }
