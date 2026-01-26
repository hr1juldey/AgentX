# =============================================================================
# AGENTX Table Hydrator Module
# =============================================================================
# Generates table widgets from extracted_numbers
# =============================================================================

import json
import logging
from typing import Any

import dspy
from services.tools.hydrators.chart_signatures import TableData

logger = logging.getLogger(__name__)


class TableHydratorModule(dspy.Module):
    """Table Hydrator: Generates tables from structured data.

    Creates table widgets for displaying extracted_numbers
    in a structured format when charts aren't appropriate.
    """

    def __init__(self):
        super().__init__()
        self.table_generator = dspy.Predict(TableData)

    def forward(
        self,
        presentation_ready: dict[str, Any],
    ) -> dict[str, Any]:
        """Generate table widget from extracted numbers.

        Args:
            presentation_ready: Output from PRESENTER agent

        Returns:
            Table widget descriptor
        """
        researched_data = presentation_ready.get("researched_data", {})
        beautiful_data = researched_data.get("beautiful_data", {})
        extracted_numbers = beautiful_data.get("extracted_numbers", [])
        query = presentation_ready.get("query", "")

        if not extracted_numbers:
            return self._empty_table()

        try:
            result = self.table_generator(
                extracted_numbers=extracted_numbers,
                query=query,
            )

            content = self._build_table_content(result, extracted_numbers)

            return {
                "descriptor_type": "table",
                "content": content,
                "metadata": {
                    "row_count": len(content.get("rows", [])),
                    "column_count": len(content.get("columns", [])),
                },
            }

        except Exception as e:
            logger.error(f"Table hydrator error: {e}")
            return self._empty_table()

    def _build_table_content(self, result, numbers) -> dict:
        """Build table content from LLM result."""
        # Get structured output from LLM
        columns_str = getattr(result, "columns", "[]")
        rows_str = getattr(result, "rows", "[]")
        title = getattr(result, "title", "Data Table")

        try:
            if isinstance(columns_str, str):
                columns = json.loads(columns_str)
            else:
                columns = list(columns_str) if hasattr(columns_str, "__iter__") else []

            if isinstance(rows_str, str):
                rows = json.loads(rows_str)
            else:
                rows = list(rows_str) if hasattr(rows_str, "__iter__") else []
        except (json.JSONDecodeError, TypeError):
            # Fallback: build directly from extracted_numbers
            return self._build_table_from_numbers(numbers)

        return {
            "title": title,
            "columns": columns,
            "rows": rows,
        }

    def _build_table_from_numbers(self, numbers) -> dict:
        """Build table directly from extracted_numbers (fallback)."""
        if not numbers:
            return {"title": "No Data", "columns": [], "rows": []}

        columns = [
            {"key": "label", "header": "Name"},
            {"key": "value", "header": "Value"},
            {"key": "unit", "header": "Unit"},
            {"key": "context", "header": "Context"},
        ]

        # Build rows
        rows = [
            {
                "label": n.get("label", ""),
                "value": str(n.get("value", "")),
                "unit": n.get("unit", ""),
                "context": n.get("context", ""),
            }
            for n in numbers
        ]

        return {
            "title": "Extracted Data",
            "columns": columns,
            "rows": rows,
        }

    def _empty_table(self) -> dict:
        """Return empty table widget."""
        return {
            "descriptor_type": "table",
            "content": {
                "title": "No Data Available",
                "columns": [],
                "rows": [],
            },
            "metadata": {"row_count": 0, "column_count": 0},
        }
