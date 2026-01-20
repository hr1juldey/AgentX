# =============================================================================
# AGENTX Widget Spawner - Widget Generation Tools
# =============================================================================
# Individual widget generation tools for ReAct agent
# =============================================================================

import json
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
from services.widget_spawner.signatures import (
    GenerateCardSignature,
    GenerateChartSignature,
    GenerateFormSignature,
    GenerateMarkdownSignature,
    GenerateProgressSignature,
)


# Initialize DSPy predictors (will use configured LM from routes.py)
_markdown_generator = dspy.Predict(GenerateMarkdownSignature)
_card_generator = dspy.Predict(GenerateCardSignature)
_form_generator = dspy.Predict(GenerateFormSignature)
_progress_generator = dspy.Predict(GenerateProgressSignature)
_chart_generator = dspy.Predict(GenerateChartSignature)


def create_markdown_widget(query: str, context: str = "") -> str:
    """Create a markdown widget for displaying reports, documents, articles, guides.

    Use this when the user asks for:
    - Reports, documents, text content
    - Articles, guides, explanations
    - Summaries, detailed text

    Args:
        query: The user's request
        context: Additional context from previous tool calls

    Returns:
        JSON string with widget data including id, type, title, content
    """
    full_query = f"{query}\n{context}".strip() if context else query
    result = _markdown_generator(user_query=full_query)

    widget_id = str(uuid.uuid4())
    widget_data = build_markdown_widget(result, widget_id)

    return json.dumps({"widget": widget_data, "tool_used": "markdown"})


def create_card_widget(query: str, context: str = "") -> str:
    """Create a card widget for highlights, key points, facts, notifications.

    Use this when the user asks for:
    - Highlights, key points, facts
    - Notifications, simple information
    - Quick summaries or bullet points

    Args:
        query: The user's request
        context: Additional context from previous tool calls

    Returns:
        JSON string with widget data including id, type, title, content
    """
    full_query = f"{query}\n{context}".strip() if context else query
    result = _card_generator(user_query=full_query)

    widget_id = str(uuid.uuid4())
    widget_data = build_card_widget(result, widget_id)

    return json.dumps({"widget": widget_data, "tool_used": "card"})


def create_form_widget(query: str, context: str = "") -> str:
    """Create a form widget for user input, surveys, data entry.

    Use this when the user asks for:
    - Input forms, surveys
    - Data entry, user input collection
    - Questionnaires, signup forms

    Args:
        query: The user's request
        context: Additional context from previous tool calls

    Returns:
        JSON string with widget data including id, type, fields
    """
    full_query = f"{query}\n{context}".strip() if context else query
    result = _form_generator(user_query=full_query)

    widget_id = str(uuid.uuid4())
    widget_data = build_form_widget(result, widget_id)

    return json.dumps({"widget": widget_data, "tool_used": "form"})


def create_progress_widget(query: str, context: str = "") -> str:
    """Create a progress widget for status tracking, progress display.

    Use this when the user asks for:
    - Status updates, progress tracking
    - Loading states, completion percentage
    - Progress bars, task completion

    Args:
        query: The user's request
        context: Additional context from previous tool calls

    Returns:
        JSON string with widget data including id, type, progress value
    """
    full_query = f"{query}\n{context}".strip() if context else query
    result = _progress_generator(user_query=full_query)

    widget_id = str(uuid.uuid4())
    widget_data = build_progress_widget(result, widget_id)

    return json.dumps({"widget": widget_data, "tool_used": "progress"})


def create_chart_widget(query: str, context: str = "") -> str:
    """Create a chart widget for graphs, visualizations, data viz.

    Use this when the user asks for:
    - Graphs, plots, visualizations
    - Data viz, statistics, trends
    - Charts (bar/line/pie/area)

    Args:
        query: The user's request
        context: Additional context from previous tool calls

    Returns:
        JSON string with widget data including id, type, chart data
    """
    full_query = f"{query}\n{context}".strip() if context else query
    result = _chart_generator(user_query=full_query)

    widget_id = str(uuid.uuid4())
    widget_data = build_chart_widget(result, widget_id)

    return json.dumps({"widget": widget_data, "tool_used": "chart"})


def create_action_widget(query: str, context: str = "") -> str:
    """Create an action widget for buttons, triggers, execute operations.

    Use this when the user asks for:
    - Buttons, actions, triggers
    - Execute operations, run commands

    Args:
        query: The user's request
        context: Additional context from previous tool calls

    Returns:
        JSON string with widget data including id, type, actions
    """
    widget_id = str(uuid.uuid4())
    widget_data = build_action_widget(query, widget_id)

    return json.dumps({"widget": widget_data, "tool_used": "action"})


def create_confirmation_widget(query: str, context: str = "") -> str:
    """Create a confirmation widget for confirm dialogs, yes/no prompts.

    Use this when the user asks for:
    - Confirm dialogs, yes/no prompts
    - Approve/reject actions

    Args:
        query: The user's request
        context: Additional context from previous tool calls

    Returns:
        JSON string with widget data including id, type, confirmation
    """
    widget_id = str(uuid.uuid4())
    widget_data = build_confirmation_widget(query, widget_id)

    return json.dumps({"widget": widget_data, "tool_used": "confirmation"})


def create_image_widget(query: str, context: str = "") -> str:
    """Create an image widget for pictures, photos, graphics.

    Use this when the user asks for:
    - Pictures, photos, graphics
    - Visual content, images

    Args:
        query: The user's request
        context: Additional context from previous tool calls

    Returns:
        JSON string with widget data including id, type, image URL
    """
    widget_id = str(uuid.uuid4())
    widget_data = build_image_widget(query, widget_id)

    return json.dumps({"widget": widget_data, "tool_used": "image"})


def create_gallery_widget(query: str, context: str = "") -> str:
    """Create a gallery widget for multiple images, photo collections.

    Use this when the user asks for:
    - Multiple images, image collection
    - Photo gallery, image grid

    Args:
        query: The user's request
        context: Additional context from previous tool calls

    Returns:
        JSON string with widget data including id, type, image URLs
    """
    widget_id = str(uuid.uuid4())
    widget_data = build_gallery_widget(query, widget_id)

    return json.dumps({"widget": widget_data, "tool_used": "gallery"})


# =============================================================================
# Tool Registry
# =============================================================================

WIDGET_TOOLS = [
    create_markdown_widget,
    create_card_widget,
    create_form_widget,
    create_progress_widget,
    create_chart_widget,
    create_action_widget,
    create_confirmation_widget,
    create_image_widget,
    create_gallery_widget,
]
