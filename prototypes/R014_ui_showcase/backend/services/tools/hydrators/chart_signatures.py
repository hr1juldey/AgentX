# =============================================================================
# AGENTX Chart & Table Signatures
# =============================================================================
# DSPy signatures for chart and table widget hydration
# =============================================================================

"""DSPy signatures for chart and table widget hydration."""

import dspy


class ExtractDocumentNumbers(dspy.Signature):
    """Extract query-relevant numerical data points from document text.

    Focus on numbers that directly address the research query.
    Skip generic index data unless it relates to the query topic.

    For war economic impact queries, prioritize:
    - GDP changes (pre-war vs post-war)
    - Sanctions costs and economic penalties
    - Reconstruction spending
    - Casualty counts and refugee numbers
    - Trade volume changes
    - Currency devaluation
    - Defense spending increases

    Skip generic commodity prices unless they show war-related changes.
    """

    query = dspy.InputField(desc="Research query for context")
    document_text = dspy.InputField(desc="Document content to extract numbers from")
    document_title = dspy.InputField(desc="Document title for context")

    structured_numbers = dspy.OutputField(
        desc="JSON array of extracted numbers with label, numeric value, unit, context, and year"
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
    """Generate table widget data from extracted numbers for structured display."""

    extracted_numbers = dspy.InputField(
        desc="Structured numbers with label, value, unit, context, year"
    )
    query = dspy.InputField(desc="User query for context")

    columns = dspy.OutputField(
        desc="JSON array of column definitions with key and header"
    )
    rows = dspy.OutputField(
        desc="JSON array of row objects with values matching column keys"
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
