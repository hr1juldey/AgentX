# =============================================================================
# AGENTX Widget Signatures
# =============================================================================
# DSPy signatures for card, form, markdown widget hydration
# =============================================================================

"""DSPy signatures for widget hydration."""

import dspy


class CardData(dspy.Signature):
    """Generate card widget data displaying key metrics and information."""

    query = dspy.InputField(desc="User query topic")
    data = dspy.InputField(desc="Research data with key_facts, trends")
    design = dspy.InputField(desc="Color scheme and styling preferences")

    cards = dspy.OutputField(
        desc="JSON array of card objects with title, value, description, icon, and color"
    )


class FormFieldNames(dspy.Signature):
    """Extract field names for a data collection form based on research insights."""

    query = dspy.InputField(desc="User query topic")
    data = dspy.InputField(desc="Research data with collection methodology")
    insights = dspy.InputField(desc="Insights about what data to collect")

    field_names = dspy.OutputField(
        desc="JSON array of field name strings (2-5 words each)"
    )


class FormFieldDetails(dspy.Signature):
    """Determine field type, description, and options for a single form field."""

    field_name = dspy.InputField(desc="Name of the field")
    query = dspy.InputField(desc="User query topic")
    data = dspy.InputField(desc="Research data for context")

    field_type = dspy.OutputField(
        desc="Input type: text, textarea, number, select, or checkbox"
    )
    description = dspy.OutputField(desc="Help text explaining what to enter")
    options = dspy.OutputField(
        desc="For select: JSON array of options. For other types: empty JSON array"
    )


class MarkdownContent(dspy.Signature):
    """Generate markdown content from research data with proper formatting."""

    query = dspy.InputField(desc="User query topic")
    data = dspy.InputField(desc="Research data with beautiful_data, structured_report")
    povs = dspy.InputField(desc="Points of view to incorporate")
    citations = dspy.InputField(desc="Citations to include")

    markdown_content = dspy.OutputField(
        desc="Markdown formatted content with headings, bullet points, and numbered lists"
    )


class POVGeneration(dspy.Signature):
    """Generate multiple balanced points of view from research data."""

    query = dspy.InputField(desc="User query topic")
    research_data = dspy.InputField(desc="Research data to analyze")

    points_of_view = dspy.OutputField(
        desc="JSON array of 3-5 perspectives (bullish, bearish, neutral, alternative, skeptical)"
    )


class WidgetInsights(dspy.Signature):
    """Generate insights specific to widget types from research data."""

    query = dspy.InputField(desc="User query topic")
    data = dspy.InputField(desc="Research data")
    widget_type = dspy.InputField(desc="Type of widget: card, form, chart, markdown")

    insights = dspy.OutputField(
        desc="JSON array of 3-5 insights specific to the widget type"
    )
