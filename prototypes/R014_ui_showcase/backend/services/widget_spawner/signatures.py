# =============================================================================
# AGENTX Widget Spawner DSPy Signatures
# =============================================================================
# DSPy signatures for widget generation
# =============================================================================

import dspy


class SelectWidgetSignature(dspy.Signature):
    """Select the appropriate UI widget for displaying content based on user query.

    Widget Selection Guide:
    - "markdown": User asks for reports, documents, text, articles, guides, explanations, summaries
    - "card": User asks for highlights, key points, facts, notifications, simple information
    - "form": ONLY when user explicitly asks for: input forms, surveys, data collection, user feedback, signup forms, questionnaires. DO NOT use forms for: information display, explanations, reports, comparisons, or data visualization. Use forms ONLY when the query contains keywords like: create form, build form, signup, submit, collect data, survey, questionnaire
    - "progress": User asks for status, progress, loading state, completion percentage
    - "chart": User asks for graphs, plots, visualizations, data viz, statistics, trends (bar/line/pie/area)
    - "action": User asks for buttons, actions, triggers, execute operations
    - "confirmation": User asks for confirm dialogs, yes/no prompts, approve/reject
    - "image": User asks for pictures, photos, graphics, visual content
    - "gallery": User asks for multiple images, image collection, photo gallery

    Examples:
    - "write a report about X" → markdown
    - "show me the key points" → card
    - "create a signup form" → form
    - "track the download progress" → progress
    - "display sales data" → chart
    - "add a submit button" → action
    - "confirm deletion" → confirmation
    - "show me a picture" → image
    - "display photos" → gallery
    """

    user_query: str = dspy.InputField(desc="User's query or request")
    available_widgets: list[str] = dspy.InputField(
        desc="List of available widget types: markdown, card, form, progress, chart, action, confirmation, image, gallery"
    )
    selected_widget: str = dspy.OutputField(
        desc="Selected widget type (must be one of: markdown, card, form, progress, chart, action, confirmation, image, gallery)"
    )
    widget_rationale: str = dspy.OutputField(
        desc="Brief explanation of why this widget type was chosen"
    )


class GenerateMarkdownSignature(dspy.Signature):
    """Generate markdown content for a markdown widget."""

    user_query: str = dspy.InputField(desc="User's query or request")
    markdown_content: str = dspy.OutputField(desc="Generated markdown content")


class GenerateCardSignature(dspy.Signature):
    """Generate title and content for a card widget."""

    user_query: str = dspy.InputField(desc="User's query or request")
    card_title: str = dspy.OutputField(desc="Card title")
    card_content: str = dspy.OutputField(desc="Card content (markdown supported)")


class GenerateFormSignature(dspy.Signature):
    """Generate form schema for user input."""

    user_query: str = dspy.InputField(desc="User's query or request")
    form_fields_json: str = dspy.OutputField(
        desc="JSON array of form fields with name, type, label, required"
    )


class GenerateProgressSignature(dspy.Signature):
    """Generate progress indicator data."""

    user_query: str = dspy.InputField(desc="User's query or request")
    task_name: str = dspy.OutputField(desc="Task name")
    progress_percent: int = dspy.OutputField(desc="Progress percentage (0-100)")
    status_text: str = dspy.OutputField(desc="Status text description")


class GenerateChartSignature(dspy.Signature):
    """Generate chart data and configuration.

    IMPORTANT: Output MUST be valid JSON only, no markdown formatting.
    Example: [{"year": 2023, "sales": 80000}, {"year": 2024, "sales": 120000}]
    """

    user_query: str = dspy.InputField(desc="User's query or request")
    chart_type: str = dspy.OutputField(desc="Chart type: bar, line, pie, or area")
    chart_title: str = dspy.OutputField(desc="Chart title")
    chart_data_json: str = dspy.OutputField(
        desc='JSON array of chart data points. MUST be valid JSON only, no markdown code blocks. Example: [{"year": 2023, "sales": 80000}]'
    )
