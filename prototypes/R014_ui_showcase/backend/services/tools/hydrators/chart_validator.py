# =============================================================================
# AGENTX Chart Data Validator
# =============================================================================
# Validates chart data structure and quality
# =============================================================================

import logging
from typing import Any

logger = logging.getLogger(__name__)


class ChartValidationError(Exception):
    """Raised when chart data validation fails."""

    pass


def validate_chart_data(content: dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate chart data structure and quality.

    Args:
        content: Chart content from hydrator

    Returns:
        Tuple of (is_valid, list of error messages)
    """
    errors = []

    # Check required fields
    required_fields = ["type", "data", "x_axis", "y_axis"]
    for field in required_fields:
        if field not in content:
            errors.append(f"Missing required field: {field}")

    # Validate chart type
    valid_types = ["bar", "line", "area", "pie", "radar", "radial"]
    if content.get("type") not in valid_types:
        errors.append(f"Invalid chart type: {content.get('type')}")

    # Validate data array
    data = content.get("data", [])
    if not isinstance(data, list):
        errors.append("Data must be an array")
    elif len(data) == 0:
        errors.append("Data array is empty")
    elif len(data) > 100:
        errors.append(f"Too many data points ({len(data)} > 100)")

    # Validate data points have required keys
    if isinstance(data, list) and len(data) > 0:
        x_axis = content.get("x_axis", "")
        y_axis = content.get("y_axis", [])

        for i, point in enumerate(data[:10]):
            if not isinstance(point, dict):
                errors.append(f"Data point {i} is not an object")
                continue

            if x_axis and x_axis not in point:
                errors.append(f"Data point {i} missing x_axis key '{x_axis}'")

            for key in y_axis[:3]:
                if key not in point:
                    errors.append(f"Data point {i} missing y_axis key '{key}'")

    # Validate values are numeric
    if isinstance(data, list) and len(data) > 0:
        y_axis = content.get("y_axis", [])
        for i, point in enumerate(data[:10]):
            if not isinstance(point, dict):
                continue
            for key in y_axis[:3]:
                if key in point:
                    try:
                        float(point[key])
                    except (ValueError, TypeError):
                        errors.append(
                            f"Data point {i}, field '{key}' is not numeric: {point[key]}"
                        )

    is_valid = len(errors) == 0
    return is_valid, errors


def sanitize_chart_data(content: dict[str, Any]) -> dict[str, Any]:
    """Sanitize chart data by fixing common issues.

    Args:
        content: Chart content from hydrator

    Returns:
        Sanitized chart content
    """
    sanitized = content.copy()
    data = sanitized.get("data", [])

    if not isinstance(data, list):
        sanitized["data"] = []
        return sanitized

    # Clean data points
    clean_data = []
    for point in data:
        if isinstance(point, dict):
            clean_point = {}
            for key, value in point.items():
                try:
                    clean_point[key] = float(value)
                except (ValueError, TypeError):
                    clean_point[key] = value
            clean_data.append(clean_point)

    sanitized["data"] = clean_data

    return sanitized
