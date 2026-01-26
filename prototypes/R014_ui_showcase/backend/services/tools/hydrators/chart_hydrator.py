# =============================================================================
# AGENTX Hydrators - Chart Hydrator Module
# =============================================================================
# Orchestrates multiple DSPy signatures to build chart widgets
# =============================================================================

import dspy
import json
import logging

from services.tools.designer.color_palette import get_chart_colors
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
        # Log presentation_ready structure for debugging
        logger.info(
            f"📊 [CHART HYDRATOR] presentation_ready keys: {list(presentation_ready.keys())}"
        )

        # Try multiple paths for design (handle both old and new structure)
        design = presentation_ready.get("design") or presentation_ready.get(
            "design_context", {}
        )
        query = presentation_ready.get("query", "")

        # Extract extracted_numbers from nested structure (e2e) or direct (unit test)
        researched_data = presentation_ready.get("researched_data", {})
        logger.info(
            f"📊 [CHART HYDRATOR] researched_data keys: {list(researched_data.keys())}"
        )

        beautiful_data = researched_data.get("beautiful_data", {})
        logger.info(
            f"📊 [CHART HYDRATOR] beautiful_data keys: {list(beautiful_data.keys())}"
        )
        logger.info(
            f"📊 [CHART HYDRATOR] beautiful_data item counts: {[(k, len(v) if isinstance(v, list) else type(v).__name__) for k, v in beautiful_data.items()]}"
        )

        extracted_numbers = beautiful_data.get("extracted_numbers", [])
        logger.info(
            f"📊 [CHART HYDRATOR] extracted_numbers from nested: {len(extracted_numbers)} items"
        )

        # Fallback to direct extracted_numbers for unit test compatibility
        if not extracted_numbers:
            extracted_numbers = researched_data.get("extracted_numbers", [])
            logger.info(
                f"📊 [CHART HYDRATOR] extracted_numbers from fallback: {len(extracted_numbers)} items"
            )

        # Fallback to top-level beautiful_data
        if not extracted_numbers:
            beautiful_data_direct = presentation_ready.get("beautiful_data", {})
            extracted_numbers = beautiful_data_direct.get("extracted_numbers", [])
            logger.info(
                f"📊 [CHART HYDRATOR] extracted_numbers from direct: {len(extracted_numbers)} items"
            )

        if not extracted_numbers:
            logger.warning(
                "📊 [CHART HYDRATOR] No extracted numbers available for chart generation"
            )
            logger.warning(
                f"📊 [CHART HYDRATOR] Full presentation_ready structure: {json.dumps({k: str(v)[:100] for k, v in presentation_ready.items()})}"
            )
            return self._empty_chart()

        try:
            # Step 1: Select chart type
            # Build structured data sample showing patterns (labels, units, years)
            data_sample = self._build_data_sample(extracted_numbers)
            type_result = self.type_selector(data_sample=data_sample, query=query)
            chart_type = getattr(type_result, "chart_type", "bar")

            # Step 2: Generate title
            # Build semantic context with actual data themes, not just count
            data_context = self._build_data_context(extracted_numbers)
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
            return self._empty_chart()

    def _build_data_sample(self, extracted_numbers: list) -> str:
        """Build structured data sample showing patterns."""
        if not extracted_numbers:
            return "No data available"

        # Group by context/theme
        contexts = {}
        for num in extracted_numbers[:20]:  # First 20 for pattern analysis
            ctx = num.get("context", "unknown")
            if ctx not in contexts:
                contexts[ctx] = []
            contexts[ctx].append(num)

        # Build summary
        themes = list(contexts.keys())[:5]
        sample = f"Data themes: {', '.join(themes)}\n"

        # Add representative samples
        for theme in themes[:3]:
            sample += f"\n{theme}:\n"
            for num in contexts[theme][:3]:
                label = num.get("label", "N/A")
                value = num.get("value", "N/A")
                unit = num.get("unit", "")
                year = num.get("year", "")
                sample += f"  - {label}: {value} {unit} {year}\n"

        return sample

    def _build_data_context(self, extracted_numbers: list) -> str:
        """Build semantic context for title generation."""
        if not extracted_numbers:
            return "No data available"

        # Analyze what data represents
        contexts = [num.get("context", "") for num in extracted_numbers[:30]]
        unique_contexts = list(set([c for c in contexts if c]))[:5]

        # Check for temporal data
        has_years = any(num.get("year") for num in extracted_numbers)

        # Check for units
        units = list(
            set([num.get("unit", "") for num in extracted_numbers if num.get("unit")])
        )

        context_desc = f"Dataset with {len(extracted_numbers)} data points"
        if unique_contexts:
            context_desc += f" covering: {', '.join(unique_contexts[:3])}"
        if has_years:
            context_desc += ", includes temporal data"
        if units:
            context_desc += f", units: {', '.join(units[:3])}"

        return context_desc

    def _empty_chart(self) -> dict:
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
