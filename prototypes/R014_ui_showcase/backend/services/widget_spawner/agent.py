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
        widget_results = result.widget_results if hasattr(result, "widget_results") else []

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


class SingleWidgetSpawnerAgent(dspy.Module):
    """Fallback agent for single widget generation (legacy behavior).

    This is used when you want to force a single widget type
    or as a simpler fallback when multi-widget is not needed.
    """

    def __init__(self):
        """Initialize the single widget spawner agent."""
        super().__init__()

        from services.widget_spawner.builders import (
            build_action_widget,
            build_card_widget,
            build_chart_widget,
            build_confirmation_widget,
            build_form_widget,
            build_gallery_widget,
            build_image_widget,
            build_markdown_widget,
            build_progress_widget,
        )
        from services.widget_spawner.signatures import (
            GenerateCardSignature,
            GenerateChartSignature,
            GenerateFormSignature,
            GenerateMarkdownSignature,
            GenerateProgressSignature,
            SelectWidgetSignature,
        )

        # Initialize DSPy predictors
        self.widget_selector = dspy.Predict(SelectWidgetSignature)
        self.markdown_generator = dspy.Predict(GenerateMarkdownSignature)
        self.card_generator = dspy.Predict(GenerateCardSignature)
        self.form_generator = dspy.Predict(GenerateFormSignature)
        self.progress_generator = dspy.Predict(GenerateProgressSignature)
        self.chart_generator = dspy.Predict(GenerateChartSignature)

        # Store builder functions
        self._builders = {
            "markdown": (self.markdown_generator, build_markdown_widget),
            "card": (self.card_generator, build_card_widget),
            "form": (self.form_generator, build_form_widget),
            "progress": (self.progress_generator, build_progress_widget),
            "chart": (self.chart_generator, build_chart_widget),
            "action": (None, build_action_widget),
            "confirmation": (None, build_confirmation_widget),
            "image": (None, build_image_widget),
            "gallery": (None, build_gallery_widget),
        }

    def forward(
        self, user_query: str, widget_type: str | None = None
    ) -> dspy.Prediction:
        """Generate a single widget descriptor based on user query.

        Args:
            user_query: The user's request
            widget_type: Optional specific widget type to force

        Returns:
            dspy.Prediction with single widget and selected type
        """
        import uuid

        from services.widget_spawner.config import AVAILABLE_WIDGET_TYPES

        # Select widget type if not provided
        if widget_type is None:
            selection = self.widget_selector(
                user_query=user_query, available_widgets=AVAILABLE_WIDGET_TYPES
            )
            selected_widget = selection.selected_widget
        else:
            selected_widget = widget_type

        # Generate widget ID
        widget_id = str(uuid.uuid4())

        # Get generator and builder for this widget type
        generator, builder = self._builders.get(selected_widget, (None, None))

        if builder is None:
            raise ValueError(f"Unknown widget type: {selected_widget}")

        # Generate widget content using generator (if has DSPy signature)
        # or build directly
        if generator is not None:
            result = generator(user_query=user_query)
            widget_data = builder(result, widget_id)
        else:
            widget_data = builder(user_query, widget_id)

        return dspy.Prediction(
            widgets=[WidgetDescriptor(**widget_data)], selected_widget=selected_widget
        )
