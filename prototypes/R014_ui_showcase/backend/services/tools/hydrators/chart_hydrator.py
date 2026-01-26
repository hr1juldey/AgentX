# =============================================================================
# AGENTX Hydrators - Chart Hydrator Module
# =============================================================================
# Orchestrates multiple DSPy signatures to build chart widgets
# =============================================================================

import dspy
import logging

from services.tools.designer.color_palette import get_chart_colors
from services.tools.hydrators.chart_data_analyzer import (
    build_data_context,
    build_data_sample,
)
from services.tools.hydrators.chart_data_extractor import (
    extract_numbers_from_presentation_ready,
)
from services.tools.hydrators.chart_signatures import (
    AxisLabelSelector,
    ChartTitleGenerator,
    ChartTypeSelector,
    transform_extracted_numbers_to_chart_data,
)

logger = logging.getLogger(__name__)


class ChartHydratorModule(dspy.Module):
    """Orchestrates chart type selection, title generation, and data transformation."""

    def __init__(self):
        super().__init__()
        self.type_selector = dspy.Predict(ChartTypeSelector)
        self.title_generator = dspy.Predict(ChartTitleGenerator)
        self.label_selector = dspy.Predict(AxisLabelSelector)

    def forward(self, presentation_ready: dict) -> dict:
        """Generate chart configuration using orchestrated signatures.

        Orchestrates:
        1. ChartTypeSelector - chooses bar/line/pie/etc
        2. ChartTitleGenerator - generates descriptive title
        3. AxisLabelSelector - selects axis labels
        4. Deterministic transform - converts extracted_numbers to chart data
        """
        # Extract data using helper
        extracted_numbers = extract_numbers_from_presentation_ready(presentation_ready)

        if not extracted_numbers:
            return _empty_chart()

        # Get design and query
        design = presentation_ready.get("design") or presentation_ready.get(
            "design_context", {}
        )
        query = presentation_ready.get("query", "")

        try:
            # Step 1: Select chart type
            data_sample = build_data_sample(extracted_numbers)
            type_result = self.type_selector(data_sample=data_sample, query=query)
            chart_type = getattr(type_result, "chart_type", "bar")

            # Step 2: Generate title
            data_context = build_data_context(extracted_numbers)
            title_result = self.title_generator(query=query, data_context=data_context)
            title = getattr(title_result, "title", "Chart")

            # Step 3: Select axis labels
            label_result = self.label_selector(
                data_sample=data_sample, chart_type=chart_type
            )
            x_label = getattr(label_result, "x_label", "Category")
            y_label = getattr(label_result, "y_label", "Value")

            # Step 4: Deterministically transform data (no LLM)
            chart_data = transform_extracted_numbers_to_chart_data(
                extracted_numbers=extracted_numbers,
                x_label=x_label,
                y_label=y_label,
            )

            # Get colors
            domain = design.get("domain", "general")
            colors = get_chart_colors(domain=domain, count=1)

            # Build content
            content = {
                "title": title,
                "type": chart_type,
                "data": chart_data,
                "x_axis": x_label,
                "y_axis": [y_label],
                "colors": colors,
                "metadata": {
                    "data_points": len(chart_data),
                    "chart_type": chart_type,
                },
            }

            return {
                "descriptor_type": "chart",
                "content": content,
                "metadata": {
                    "chart_type": chart_type,
                    "data_points": len(chart_data),
                },
            }

        except Exception as e:
            logger.error(f"Chart hydrator error: {e}")
            return _empty_chart()


def _empty_chart() -> dict:
    """Return empty chart when no data available."""
    default_colors = get_chart_colors(domain="general", count=1)
    return {
        "descriptor_type": "chart",
        "content": {
            "title": "No Data Available",
            "type": "bar",
            "data": [],
            "x_axis": "Category",
            "y_axis": ["Value"],
            "colors": default_colors,
            "metadata": {"error": "No extracted numbers available"},
        },
        "metadata": {"error": "No extracted numbers available"},
    }
