# =============================================================================
# AGENTX Widget Spawner - Multi-Widget ReAct Agent
# =============================================================================
# DSPy ReAct agent for spawning multiple widgets based on user query
# =============================================================================

import json

import dspy

from services.widget_spawner.models import WidgetDescriptor
from services.widget_spawner.tools import WIDGET_TOOLS


class MultiWidgetSpawnerAgent(dspy.Module):
    """DSPy ReAct agent for spawning multiple widgets based on user query.

    This agent uses ReAct reasoning to:
    1. Analyze the user's request
    2. Decide which widgets are needed (can be multiple)
    3. Call the appropriate widget generation tools
    4. Return a list of generated widgets

    Example scenarios:
    - "Show me EV sales with a summary" → chart widget + markdown widget
    - "Create a signup form with terms" → form widget + card widget
    - "Track download progress with action buttons" → progress widget + action widget
    """

    def __init__(self, max_iters: int = 10):
        """Initialize the multi-widget spawner agent.

        Args:
            max_iters: Maximum number of ReAct reasoning iterations
        """
        super().__init__()
        self.max_iters = max_iters

        # Create ReAct signature for multi-widget generation
        # The signature takes user_query and returns widget_results (list of widget JSON)
        self.react = dspy.ReAct(
            "user_query -> widget_results: list[str]",
            tools=WIDGET_TOOLS,
            max_iters=max_iters,
        )

    def forward(self, user_query: str) -> dspy.Prediction:
        """Generate one or more widget descriptors based on user query.

        The ReAct agent will:
        1. Analyze the query to understand what information is needed
        2. Call appropriate widget generation tools (can call multiple)
        3. Aggregate results from all tool calls
        4. Return the list of generated widgets

        Args:
            user_query: The user's request

        Returns:
            dspy.Prediction with widgets list and reasoning trace
        """
        # Run the ReAct agent
        result = self.react(user_query=user_query)

        # Parse the widget_results from the agent
        # Each result is a JSON string like: {"widget": {...}, "tool_used": "..."}
        widget_results = (
            result.widget_results if hasattr(result, "widget_results") else []
        )

        widgets = []
        tools_used = []

        for widget_result_str in widget_results:
            try:
                # Parse each widget result JSON
                widget_data = json.loads(widget_result_str)
                widget_dict = widget_data.get("widget", {})
                tool_used = widget_data.get("tool_used", "unknown")

                # Convert to WidgetDescriptor
                widget = WidgetDescriptor(**widget_dict)
                widgets.append(widget)
                tools_used.append(tool_used)

            except (json.JSONDecodeError, TypeError) as e:
                # Skip invalid widget results
                print(f"Warning: Failed to parse widget result: {e}")
                continue

        # Return prediction with widgets and metadata
        return dspy.Prediction(
            widgets=widgets,
            tools_used=tools_used,
            reasoning=result.reasoning if hasattr(result, "reasoning") else None,
            trajectory=result.trajectory if hasattr(result, "trajectory") else None,
        )
