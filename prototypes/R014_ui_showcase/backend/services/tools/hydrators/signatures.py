# =============================================================================
# AGENTX Hydrator Signatures
# =============================================================================
# DSPy signatures for widget hydration with proper type definitions
# =============================================================================

"""DSPy signatures for widget hydration with proper type definitions."""

import dspy


class ExtractDocumentNumbers(dspy.Signature):
    """Extract structured numbers from document text.

    For use in chart/table generation. Extracts all numerical data
    with labels, units, and temporal context.
    """

    document_text = dspy.InputField(desc="Document content to extract numbers from")
    document_title = dspy.InputField(desc="Document title for context")

    structured_numbers = dspy.OutputField(
        desc="JSON array of extracted numbers. Each entry must have: "
        "label (entity name), value (number), unit (%, $, etc.), "
        "context (what the number represents), year (if available). "
        "Example: [{'label': 'US', 'value': 3.7, 'unit': '%', 'context': 'inflation rate', 'year': '2023'}]. "
        "Return ONLY numbers explicitly found in text. Do not make up values."
    )


class ChartData(dspy.Signature):
    """Generate chart widget data from extracted numbers.

    Analyzes extracted_numbers structure to determine the appropriate
    chart type (bar/line/area/pie/radar/radial) and format data.
    """

    extracted_numbers = dspy.InputField(
        desc="Structured numbers from NumberExtractorModule. "
        "Each entry has: label, value, unit, context, year, source_title, url."
    )
    query = dspy.InputField(desc="User query for context")

    chart_type = dspy.OutputField(
        desc="Chart type based on data pattern analysis. "
        "Options: bar (categories comparison), line (time series trends), "
        "area (filled time series), pie (parts of whole percentages), "
        "radar (multi-dimensional comparison), radial (cyclic data). "
        "Examples: "
        "- 5 countries with inflation rates → bar "
        "- Stock prices over months → line "
        "- Temperature over days → area "
        "- Market share percentages → pie "
        "- Skills across dimensions → radar "
        "- Hourly temperature pattern → radial"
    )
    data_points = dspy.OutputField(
        desc="JSON array of data points. Each point has label, value, and optional metadata. "
        "Must be REAL values from extracted_numbers. Do not hallucinate."
    )
    x_axis_key = dspy.OutputField(
        desc="Field name for x-axis (e.g., 'Country', 'Year', 'Date'). "
        "Use the most appropriate label from extracted_numbers."
    )
    y_axis_key = dspy.OutputField(
        desc="Field name for primary y-axis (e.g., 'Inflation Rate', 'Price'). "
        "Use the context from extracted_numbers."
    )
    title = dspy.OutputField(desc="Chart title derived from query and data context")


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
