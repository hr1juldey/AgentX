# =============================================================================
# AGENTX Widget Signatures
# =============================================================================
# DSPy signatures for card, form, markdown widget hydration
# =============================================================================

"""DSPy signatures for widget hydration."""

import dspy


class CardData(dspy.Signature):
    """Generate card widget data with structured card objects."""

    query = dspy.InputField(desc="User query topic")
    data = dspy.InputField(desc="Research data with key_facts, trends")
    design = dspy.InputField(desc="Color scheme and styling preferences")

    cards = dspy.OutputField(
        desc="Array of card objects. Each card: title (string), value (string metric), description (string explanation), icon (emoji), color (tailwind color). Return as JSON array."
    )


class FormData(dspy.Signature):
    """Generate form widget data with structured field objects."""

    query = dspy.InputField(desc="User query topic")
    data = dspy.InputField(desc="Research data with collection methodology")
    insights = dspy.InputField(desc="Insights about what data to collect")

    form_fields = dspy.OutputField(
        desc="Array of field objects. Each field: label (string), type (text|textarea|number|select|checkbox), description (string help text), required (boolean), options (array if select). Return as JSON array."
    )


class MarkdownContent(dspy.Signature):
    """Generate markdown content from research data."""

    query = dspy.InputField(desc="User query topic")
    data = dspy.InputField(desc="Research data with beautiful_data, structured_report")
    povs = dspy.InputField(desc="Points of view to incorporate")
    citations = dspy.InputField(desc="Citations to include")

    markdown_content = dspy.OutputField(
        desc="Markdown formatted content with headings, bullet points, numbered lists. Use ## for main sections, ### for subsections. Include key findings, trends, comparisons."
    )


class POVGeneration(dspy.Signature):
    """Generate multiple balanced points of view."""

    query = dspy.InputField(desc="User query topic")
    research_data = dspy.InputField(desc="Research data to analyze")

    points_of_view = dspy.OutputField(
        desc='Array of 3-5 perspectives. Each must be a distinct viewpoint: bullish/optimistic, bearish/cautious, neutral/objective, alternative/skeptical. Return as JSON array of strings: ["bullish: ...", "bearish: ...", "neutral: ..."].'
    )


class WidgetInsights(dspy.Signature):
    """Generate insights specific to widget types."""

    query = dspy.InputField(desc="User query topic")
    data = dspy.InputField(desc="Research data")
    widget_type = dspy.InputField(desc="Type of widget: card, form, chart, markdown")

    insights = dspy.OutputField(
        desc="Array of 3-5 insights specific to the widget type. For cards: key metrics. For forms: data collection points. For charts: trends. For markdown: narrative themes. Return as JSON array."
    )
