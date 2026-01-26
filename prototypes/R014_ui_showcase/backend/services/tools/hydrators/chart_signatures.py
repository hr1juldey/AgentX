# =============================================================================
# AGENTX Chart & Table Signatures
# =============================================================================
# DSPy signatures for chart and table widget hydration
# =============================================================================

"""DSPy signatures for chart and table widget hydration."""

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


class ChartTypeSelector(dspy.Signature):
    """Select the appropriate chart type based on data characteristics."""

    data_sample = dspy.InputField(
        desc="Sample of extracted numbers showing data pattern"
    )
    query = dspy.InputField(desc="User query for context")

    chart_type = dspy.OutputField(
        desc="Chart type: bar, line, area, pie, radar, or radial"
    )


class ChartTitleGenerator(dspy.Signature):
    """Generate a descriptive title for the chart."""

    query = dspy.InputField(desc="User query")
    data_context = dspy.InputField(desc="Brief description of what data shows")

    title = dspy.OutputField(desc="Chart title")


class AxisLabelSelector(dspy.Signature):
    """Select appropriate axis labels based on data structure."""

    data_sample = dspy.InputField(desc="Sample of extracted numbers")
    chart_type = dspy.InputField(desc="Selected chart type")

    x_label = dspy.OutputField(desc="X-axis label")
    y_label = dspy.OutputField(desc="Y-axis label")


class TableData(dspy.Signature):
    """Generate table widget data from extracted numbers.

    Creates structured table for displaying extracted numbers
    when chart visualization is not appropriate.
    """

    extracted_numbers = dspy.InputField(
        desc="Structured numbers from NumberExtractorModule. "
        "Each entry has: label, value, unit, context, year, source_title, url."
    )
    query = dspy.InputField(desc="User query for context")

    columns = dspy.OutputField(
        desc="JSON array of column definitions. "
        "Each column: {key: string, header: string}. "
        "Example: [{'key': 'country', 'header': 'Country'}, {'key': 'value', 'header': 'Value'}]"
    )
    rows = dspy.OutputField(
        desc="JSON array of row objects. "
        "Each row must have keys matching column keys. "
        "Example: [{'country': 'US', 'value': '3.7'}, {'country': 'Brazil', 'value': '5.8'}]"
    )
    title = dspy.OutputField(desc="Table title")


def transform_extracted_numbers_to_chart_data(
    extracted_numbers: list, x_label: str, y_label: str
) -> list:
    """Deterministically transform extracted numbers to chart data points.

    No LLM involved - pure Python transformation.

    Args:
        extracted_numbers: List of dicts with label, value, unit, context
        x_label: X-axis field name
        y_label: Y-axis field name

    Returns:
        List of chart data point dicts
    """
    chart_data = []
    for item in extracted_numbers:
        label = item.get("label", "")
        value = item.get("value", 0)

        # Try to convert value to float
        try:
            numeric_value = float(value)
        except (ValueError, TypeError):
            continue

        chart_data.append({x_label: label, y_label: numeric_value})

    return chart_data
