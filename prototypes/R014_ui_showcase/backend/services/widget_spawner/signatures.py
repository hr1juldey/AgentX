# =============================================================================
# AGENTX Widget Spawner DSPy Signatures
# =============================================================================
# DSPy signatures for widget generation
# =============================================================================

import dspy


class SelectWidgetSignature(dspy.Signature):
    """Select the appropriate UI widget type based on user query intent.

    Widget types:
    - markdown: Reports, articles, documents, explanations
    - card: Key facts, metrics, highlights, summaries
    - chart: Visualizations, graphs, data comparisons
    - form: Data COLLECTION (collecting user input, NOT presenting data)
    - progress: Status tracking, loading states
    - action: Buttons, operations, user actions
    - confirmation: Yes/no prompts, confirmations
    - image/gallery: Visual content display

    IMPORTANT: Use 'form' ONLY when collecting user input.
    When presenting research/analysis, use markdown/card/chart.
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
    """Generate chart data and configuration for visualization.

    Output MUST be valid JSON only, no markdown formatting.
    """

    user_query: str = dspy.InputField(desc="User's query or request")
    chart_type: str = dspy.OutputField(desc="Chart type: bar, line, pie, or area")
    chart_title: str = dspy.OutputField(desc="Chart title")
    chart_data_json: str = dspy.OutputField(
        desc="Valid JSON array of chart data points (no markdown code blocks)"
    )
