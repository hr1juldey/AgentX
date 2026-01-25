# =============================================================================
# AGENTX Widget Spawner - Executor Agent
# =============================================================================
# Generates the actual widgets based on a plan
# =============================================================================

import logging
import uuid

import dspy

from services.tools.researcher.searxng_search import SearXNGSearchModule
from services.widget_spawner.builders import (
    build_action_widget,
    build_card_widget,
    build_chart_widget,
    build_confirmation_widget,
    build_form_widget,
    build_markdown_widget,
    build_progress_widget,
)
from services.widget_spawner.executor_helpers import (
    generate_gallery_widget,
    generate_image_widget,
)
from services.widget_spawner.models import WidgetDescriptor
from services.widget_spawner.signatures import (
    GenerateCardSignature,
    GenerateChartSignature,
    GenerateFormSignature,
    GenerateMarkdownSignature,
    GenerateProgressSignature,
)

logger = logging.getLogger(__name__)


class WidgetExecutorAgent:
    """Executor agent that generates widgets based on a plan.

    This agent focuses ONLY on execution:
    - Takes a plan from the planner
    - Generates each widget with its specific context
    - Returns the complete list of generated widgets

    It does NOT decide what to create - that's the planner's job.
    """

    def __init__(self):
        """Initialize the widget executor agent."""
        # Initialize DSPy predictors for content generation
        self.markdown_generator = dspy.Predict(GenerateMarkdownSignature)
        self.card_generator = dspy.Predict(GenerateCardSignature)
        self.form_generator = dspy.Predict(GenerateFormSignature)
        self.progress_generator = dspy.Predict(GenerateProgressSignature)
        self.chart_generator = dspy.Predict(GenerateChartSignature)

        # Initialize SearXNG search for image widgets
        self.image_search = SearXNGSearchModule()

        # Store DSPy-backed builders
        self._dspy_builders = {
            "markdown": (self.markdown_generator, build_markdown_widget),
            "card": (self.card_generator, build_card_widget),
            "form": (self.form_generator, build_form_widget),
            "progress": (self.progress_generator, build_progress_widget),
            "chart": (self.chart_generator, build_chart_widget),
        }

        # Store simple builders (no DSPy)
        self._simple_builders = {
            "action": build_action_widget,
            "confirmation": build_confirmation_widget,
        }

    def execute_plan(self, plan: list[dict]) -> list[WidgetDescriptor]:
        """Execute a widget plan and generate all widgets.

        Args:
            plan: List of {type, context} dicts from the planner

        Returns:
            List of generated WidgetDescriptor objects
        """
        widgets = []

        for item in plan:
            widget_type = item.get("type", "markdown")
            context = item.get("context", "")

            try:
                widget = self._generate_widget(widget_type, context)
                widgets.append(widget)
            except Exception as e:
                print(f"Warning: Failed to generate {widget_type} widget: {e}")
                # Continue with other widgets even if one fails
                continue

        return widgets

    def _generate_widget(self, widget_type: str, context: str) -> WidgetDescriptor:
        """Generate a single widget.

        Args:
            widget_type: The type of widget to generate
            context: The context/instruction for content generation

        Returns:
            WidgetDescriptor object
        """
        widget_id = str(uuid.uuid4())

        # Image widgets: use helper function (does both general + image search)
        if widget_type == "image":
            widget_data = generate_image_widget(context, widget_id, self.image_search)
            return WidgetDescriptor(**widget_data)

        # Gallery widgets: use helper function (does both general + image search)
        if widget_type == "gallery":
            widget_data = generate_gallery_widget(context, widget_id, self.image_search)
            return WidgetDescriptor(**widget_data)

        # Check DSPy-backed builders first
        if widget_type in self._dspy_builders:
            generator, builder = self._dspy_builders[widget_type]
            # Generate content using DSPy
            result = generator(user_query=context)
            # Build widget descriptor
            widget_data = builder(result, widget_id)  # type: ignore[arg-type]
            return WidgetDescriptor(**widget_data)

        # Check simple builders
        if widget_type in self._simple_builders:
            builder = self._simple_builders[widget_type]
            # Build widget directly (no DSPy)
            widget_data = builder(context, widget_id)
            return WidgetDescriptor(**widget_data)

        # Fallback to markdown if unknown type
        result = self.markdown_generator(user_query=context)
        widget_data = build_markdown_widget(result, widget_id)  # type: ignore[arg-type]
        return WidgetDescriptor(**widget_data)
