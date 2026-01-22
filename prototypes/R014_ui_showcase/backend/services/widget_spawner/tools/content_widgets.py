# =============================================================================
# AGENTX Widget Spawner - Content Widget Tools
# =============================================================================
# Content-focused widgets: markdown, card, form, progress, chart
# =============================================================================

import json
import uuid

import dspy

from services.widget_spawner.builders import (
    build_card_widget,
    build_chart_widget,
    build_form_widget,
    build_markdown_widget,
    build_progress_widget,
)
from services.widget_spawner.signatures import (
    GenerateCardSignature,
    GenerateChartSignature,
    GenerateFormSignature,
    GenerateMarkdownSignature,
    GenerateProgressSignature,
)

# DSPy generators
_markdown_generator = dspy.Predict(GenerateMarkdownSignature)
_card_generator = dspy.Predict(GenerateCardSignature)
_form_generator = dspy.Predict(GenerateFormSignature)
_progress_generator = dspy.Predict(GenerateProgressSignature)
_chart_generator = dspy.Predict(GenerateChartSignature)


def _generate_widget_id() -> str:
    """Generate unique widget ID."""
    return str(uuid.uuid4())


def create_markdown_widget(query: str, context: str = "") -> str:
    """Create a markdown widget for reports, documents, articles.

    Use for:
    - Reports, documents, text content
    - Articles, guides, explanations
    - Summaries, detailed text
    """
    full_query = f"{query}\n{context}".strip() if context else query
    result = _markdown_generator(user_query=full_query)

    widget_data = build_markdown_widget(result, _generate_widget_id())
    return json.dumps({"widget": widget_data, "tool_used": "markdown"})


def create_card_widget(query: str, context: str = "") -> str:
    """Create a card widget for highlights, key points, facts.

    Use for:
    - Highlights, key points, facts
    - Notifications, simple information
    - Quick summaries or bullet points
    """
    full_query = f"{query}\n{context}".strip() if context else query
    result = _card_generator(user_query=full_query)

    widget_data = build_card_widget(result, _generate_widget_id())
    return json.dumps({"widget": widget_data, "tool_used": "card"})


def create_form_widget(query: str, context: str = "") -> str:
    """Create a form widget for user input, surveys, data entry.

    Use for:
    - Input forms, surveys
    - Data entry, user input collection
    - Questionnaires, signup forms
    """
    full_query = f"{query}\n{context}".strip() if context else query
    result = _form_generator(user_query=full_query)

    widget_data = build_form_widget(result, _generate_widget_id())
    return json.dumps({"widget": widget_data, "tool_used": "form"})


def create_progress_widget(query: str, context: str = "") -> str:
    """Create a progress widget for status tracking, progress display.

    Use for:
    - Status updates, progress tracking
    - Loading states, completion percentage
    - Progress bars, task completion
    """
    full_query = f"{query}\n{context}".strip() if context else query
    result = _progress_generator(user_query=full_query)

    widget_data = build_progress_widget(result, _generate_widget_id())
    return json.dumps({"widget": widget_data, "tool_used": "progress"})


def create_chart_widget(query: str, context: str = "") -> str:
    """Create a chart widget for graphs, visualizations, data viz.

    Use for:
    - Graphs, plots, visualizations
    - Data viz, statistics, trends
    - Charts (bar/line/pie/area)
    """
    full_query = f"{query}\n{context}".strip() if context else query
    result = _chart_generator(user_query=full_query)

    widget_data = build_chart_widget(result, _generate_widget_id())
    return json.dumps({"widget": widget_data, "tool_used": "chart"})
