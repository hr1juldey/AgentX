# =============================================================================
# AGENTX Widget Spawner - DSPy Widget Builders
# =============================================================================
# Helper functions for building widget data from DSPy results
# =============================================================================

import json
from datetime import datetime
from typing import Any

from services.widget_spawner.config import (
    DEFAULT_CARD_ACTIONS,
    DEFAULT_CHART_DATA,
    DEFAULT_CHART_DATA_KEYS,
    DEFAULT_FORM_FIELDS,
    DEFAULT_FORM_SUBMIT_LABEL,
    DEFAULT_FORM_TITLE,
    DEFAULT_PROGRESS_VALUE_DIVISOR,
)
from services.widget_spawner.signatures import (
    GenerateCardSignature,
    GenerateChartSignature,
    GenerateFormSignature,
    GenerateMarkdownSignature,
    GenerateProgressSignature,
)


def build_markdown_widget(
    result: GenerateMarkdownSignature, widget_id: str
) -> dict[str, Any]:
    """Build markdown widget data from DSPy result."""
    return {
        "id": widget_id,
        "type": "markdown",
        "title": None,
        "content": result.markdown_content,
        "metadata": None,
        "timestamp": datetime.utcnow().isoformat(),
        "dismissible": True,
    }


def build_card_widget(result: GenerateCardSignature, widget_id: str) -> dict[str, Any]:
    """Build card widget data from DSPy result."""
    return {
        "id": widget_id,
        "type": "card",
        "title": result.card_title,
        "content": result.card_content,
        "metadata": {"actions": DEFAULT_CARD_ACTIONS},
        "timestamp": datetime.utcnow().isoformat(),
        "dismissible": True,
    }


def build_form_widget(result: GenerateFormSignature, widget_id: str) -> dict[str, Any]:
    """Build form widget data from DSPy result."""
    try:
        fields = json.loads(result.form_fields_json)
    except json.JSONDecodeError:
        fields = DEFAULT_FORM_FIELDS

    return {
        "id": widget_id,
        "type": "form",
        "title": DEFAULT_FORM_TITLE,
        "content": None,
        "metadata": {"fields": fields, "submit_label": DEFAULT_FORM_SUBMIT_LABEL},
        "timestamp": datetime.utcnow().isoformat(),
        "dismissible": True,
    }


def build_progress_widget(
    result: GenerateProgressSignature, widget_id: str
) -> dict[str, Any]:
    """Build progress widget data from DSPy result."""
    return {
        "id": widget_id,
        "type": "progress",
        "title": result.task_name,
        "content": None,
        "metadata": {
            "value": result.progress_percent / DEFAULT_PROGRESS_VALUE_DIVISOR,
            "status_text": result.status_text,
        },
        "timestamp": datetime.utcnow().isoformat(),
        "dismissible": True,
    }


def build_chart_widget(
    result: GenerateChartSignature, widget_id: str
) -> dict[str, Any]:
    """Build chart widget data from DSPy result."""
    try:
        json_str = result.chart_data_json

        # Strip markdown code blocks if present (e.g., ```json ... ```)
        if "```" in json_str:
            # Extract content between code blocks
            lines = json_str.split("\n")
            json_lines = []
            in_code_block = False
            for line in lines:
                if line.strip().startswith("```"):
                    in_code_block = not in_code_block
                    continue
                if in_code_block or not line.strip().startswith("```"):
                    json_lines.append(line)
            json_str = "\n".join(json_lines).strip()

        chart_data = json.loads(json_str)

        # Extract data keys from the actual data (exclude label keys like year, month, name)
        if chart_data and len(chart_data) > 0:
            first_item = chart_data[0]
            # Common label keys to exclude
            label_keys = {"year", "month", "name", "label", "category", "date"}
            # Find numeric keys (value keys)
            extracted_keys = [
                k for k in first_item.keys()
                if k not in label_keys and isinstance(first_item[k], (int, float))
            ]
            data_keys = extracted_keys if extracted_keys else DEFAULT_CHART_DATA_KEYS
        else:
            data_keys = DEFAULT_CHART_DATA_KEYS

    except (json.JSONDecodeError, ValueError, AttributeError):
        # If JSON parsing fails, generate sensible default data
        chart_data = DEFAULT_CHART_DATA
        data_keys = DEFAULT_CHART_DATA_KEYS

    return {
        "id": widget_id,
        "type": "chart",
        "title": result.chart_title,
        "content": "Generated chart visualization",
        "metadata": {
            "chart_type": result.chart_type,
            "data": chart_data,
            "data_keys": data_keys,
        },
        "timestamp": datetime.utcnow().isoformat(),
        "dismissible": True,
    }
