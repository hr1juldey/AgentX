# =============================================================================
# AGENTX Widget Spawner - Single Widget Agent
# =============================================================================
# Fallback agent for single widget generation (legacy behavior)
# =============================================================================

import uuid

import dspy

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
from services.widget_spawner.config import AVAILABLE_WIDGET_TYPES
from services.widget_spawner.models import WidgetDescriptor
from services.widget_spawner.signatures import (
    GenerateCardSignature,
    GenerateChartSignature,
    GenerateFormSignature,
    GenerateMarkdownSignature,
    GenerateProgressSignature,
    SelectWidgetSignature,
)


class SingleWidgetSpawnerAgent(dspy.Module):
    """Fallback agent for single widget generation (legacy behavior).

    This is used when you want to force a single widget type
    or as a simpler fallback when multi-widget is not needed.
    """

    def __init__(self):
        """Initialize the single widget spawner agent."""
        super().__init__()

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
