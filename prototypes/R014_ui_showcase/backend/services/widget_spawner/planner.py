# =============================================================================
# AGENTX Widget Spawner - Planner Agent
# =============================================================================
# Decides WHAT widgets to spawn based on user query
# =============================================================================

import json
import logging

import dspy

from services.widget_spawner.config import AVAILABLE_WIDGET_TYPES

logger = logging.getLogger(__name__)


class PlanWidgetsSignature(dspy.Signature):
    """Plan which widgets are needed based on user query.

    This planner analyzes the user's request and decides:
    1. What widget types are needed
    2. In what order
    3. With what context/instructions for each

    Widget Selection Guide:
    - "markdown": User asks for reports, documents, text, articles, guides, explanations, summaries
    - "card": User asks for highlights, key points, facts, notifications, simple information
    - "form": User asks for input forms, surveys, data entry, user input, collect information
    - "progress": User asks for status, progress, loading state, completion percentage
    - "chart": User asks for graphs, plots, visualizations, data viz, statistics, trends (bar/line/pie/area)
    - "action": User asks for buttons, actions, triggers, execute operations
    - "confirmation": User asks for confirm dialogs, yes/no prompts, approve/reject
    - "image": User asks for pictures, photos, graphics, visual content
    - "gallery": User asks for multiple images, image collection, photo gallery

    Examples:
    - "Show me EV sales with a summary" → [{type: "chart", context: "EV sales data"}, {type: "markdown", context: "Summary"}]
    - "Create a signup form with terms" → [{type: "form", context: "User signup"}, {type: "card", context: "Terms and conditions"}]
    - "Write a report" → [{type: "markdown", context: "Full report"}]
    """

    user_query: str = dspy.InputField(desc="User's query or request")
    available_widgets: list[str] = dspy.InputField(
        desc="List of available widget types: markdown, card, form, progress, chart, action, confirmation, image, gallery"
    )
    widget_plan: str = dspy.OutputField(
        desc="""JSON array of widget plans. Each item must have: type (widget type), context (what content to generate).
Example: [{"type": "chart", "context": "EV sales data by year"}, {"type": "markdown", "context": "Summary of trends"}]"""
    )


class WidgetPlannerAgent(dspy.Module):
    """DSPy agent for planning what widgets to generate.

    This agent focuses ONLY on decision making:
    - Analyzes user intent
    - Decides which widgets are needed
    - Provides context for each widget

    It does NOT generate any widget content - that's the executor's job.
    """

    def __init__(self):
        """Initialize the widget planner agent."""
        super().__init__()
        self.planner = dspy.Predict(PlanWidgetsSignature)

    def forward(self, user_query: str) -> dspy.Prediction:
        """Create a plan for what widgets to generate.

        Args:
            user_query: The user's request

        Returns:
            dspy.Prediction with plan (list of {type, context} dicts)
        """
        # Run the planner
        result = self.planner(
            user_query=user_query, available_widgets=AVAILABLE_WIDGET_TYPES
        )

        logger.debug(f"🟣 Planner raw output: {repr(result.widget_plan)}")

        # Parse the widget_plan JSON
        try:
            plan_json = result.widget_plan
            logger.debug(f"🟣 Plan JSON before strip: {repr(plan_json)}")

            # Strip markdown code blocks if present
            if "```" in plan_json:
                lines = plan_json.split("\n")
                json_lines = []
                in_code_block = False
                for line in lines:
                    if line.strip().startswith("```"):
                        in_code_block = not in_code_block
                        continue
                    if in_code_block:
                        json_lines.append(line)
                plan_json = "\n".join(json_lines).strip()

            logger.debug(f"🟣 Plan JSON after strip: {repr(plan_json)}")
            plan = json.loads(plan_json)
            logger.debug(f"🟣 Parsed plan: {plan}")

            # Validate plan structure
            if not isinstance(plan, list):
                plan = [{"type": "markdown", "context": user_query}]

            # Ensure each item has type and context
            for item in plan:
                if "type" not in item:
                    item["type"] = "markdown"
                if "context" not in item:
                    item["context"] = user_query

        except (json.JSONDecodeError, TypeError, AttributeError) as e:
            logger.error(f"🔴 Failed to parse plan, using fallback: {e}")
            logger.error(f"🔴 Raw plan that failed: {repr(result.widget_plan)}")
            # Fallback: single markdown widget
            plan = [{"type": "markdown", "context": user_query}]

        return dspy.Prediction(plan=plan, raw_plan=result.widget_plan)
