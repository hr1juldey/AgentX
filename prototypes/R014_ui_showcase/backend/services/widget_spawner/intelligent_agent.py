# =============================================================================
# AGENTX Widget Spawner - Intelligent UI Generator
# =============================================================================
# Three-tier orchestration for intelligent, automatic UI generation.
# No Mem0AI - simple, direct, effective.
# =============================================================================

import json
import logging
import uuid
from typing import Dict, Any

import dspy

from services.widget_spawner.context_analyzer import ContextAnalyzerAgent
from services.widget_spawner.presentation_planner import PresentationPlannerAgent
from services.widget_spawner.enhanced_executor import EnhancedExecutorAgent

logger = logging.getLogger(__name__)


class IntelligentUIGenerator(dspy.Module):
    """
    Intelligent UI generator using three-tier architecture.

    Tier 1: Context Analyzer - Understand the situation
    Tier 2: Presentation Planner - Decide HOW to present
    Tier 3: Content Generators - Create actual widgets

    No memory complexity - pure intelligence from DSPy patterns.
    """

    def __init__(self):
        super().__init__()
        self.context_analyzer = ContextAnalyzerAgent()
        self.presentation_planner = PresentationPlannerAgent()
        self.content_generator = EnhancedExecutorAgent()

    def forward(
        self, user_query: str, device_context: Dict[str, Any], user_id: str = None
    ) -> dspy.Prediction:
        """
        Generate intelligent UI based on user query.

        Args:
            user_query: User's natural language request
            device_context: Device info (type, screen_width, screen_height)
            user_id: Optional user ID (not used in this simple version)

        Returns:
            dspy.Prediction with widgets, layout, design_system, reasoning
        """
        logger.info(f"🤖 IntelligentUIGenerator processing: {user_query[:100]}")

        # Tier 1: Analyze context
        context = self.context_analyzer(
            user_query=user_query, device_context=device_context
        )
        logger.info(
            f"🔍 Tier 1 - Context: {getattr(context, 'content_analysis', 'N/A')}, Intent: {getattr(context, 'user_intent', 'N/A')}"
        )

        # Tier 2: Plan presentation
        presentation = self.presentation_planner(
            content_analysis=getattr(context, "content_analysis", "mixed"),
            user_intent=getattr(context, "user_intent", "general"),
            device_context=device_context,
        )

        # Parse the presentation plan
        try:
            plan = json.loads(getattr(presentation, "presentation_plan", "{}"))
            logger.info(f"📋 Tier 2 - Layout: {plan.get('layout', 'unknown')}")
        except (json.JSONDecodeError, TypeError) as e:
            logger.error(f"📋 Failed to parse presentation plan: {e}")
            # Fallback plan
            plan = {
                "layout": "simple_vertical",
                "color_scheme": {},
                "widgets": [
                    {
                        "type": "markdown",
                        "context": user_query[:100],
                        "priority": "medium",
                        "x": None,
                        "y": None,
                    }
                ],
            }
        widgets = []

        for widget_spec in plan.get("widgets", []):
            widget = self.content_generator(
                widget_spec=widget_spec, design_system=plan.get("color_scheme", {})
            )

            # Create widget with optional positions
            widgets.append(
                {
                    "id": str(uuid.uuid4()),
                    "type": widget_spec.get("type"),
                    "title": widget_spec.get("context", "")[:50],
                    "content": widget.widget_content,
                    "x": widget_spec.get("x"),  # Optional: backend suggestion
                    "y": widget_spec.get("y"),  # Optional: backend suggestion
                    "dismissible": True,
                    "metadata": {
                        "layout": plan.get("layout"),
                        "design_system": plan.get("color_scheme", {}),
                        "priority": widget_spec.get("priority"),
                        "accessibility_score": widget.accessibility_score,
                    },
                }
            )

        logger.info(f"✅ Tier 3 - Generated {len(widgets)} widgets")

        # Create prediction and set attributes directly
        prediction = dspy.Prediction()
        prediction.widgets = widgets
        prediction.layout = plan.get("layout", "simple_vertical")
        prediction.design_system = plan.get("color_scheme", {})
        prediction.reasoning = f"Analyzed as {getattr(context, 'content_analysis', 'mixed')}, intent: {getattr(context, 'user_intent', 'general')}"

        return prediction
