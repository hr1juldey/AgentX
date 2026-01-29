"""Safe DSPy extraction helpers.

Ported from R014 pattern (multiple files)

DSPy returns special Prediction objects, not plain dicts.
These helpers prevent crashes when accessing DSPy results.
"""

from typing import Any


def safe_extract(obj: Any, key: str, default: Any = None) -> Any:
    """Safely extract a value from a DSPy Prediction or dict-like object.

    This helper handles:
    - DSPy Prediction objects (use hasattr + getattr)
    - Dict-like objects (use .get() method)
    - Regular objects (use getattr with default)

    Args:
        obj: Object to extract from (DSPy Prediction, dict, or any object)
        key: Attribute/key name to extract
        default: Default value if key not found

    Returns:
        Extracted value or default

    Examples:
        >>> result = dspy.Prediction(field1="value1")
        >>> safe_extract(result, "field1", "default")
        "value1"
        >>> safe_extract(result, "missing_field", "default")
        "default"
        >>> data = {"key": "value"}
        >>> safe_extract(data, "key", "default")
        "value"
    """
    if obj is None:
        return default

    # Try dict-like access first (for dict, DSPy Prediction, etc.)
    if hasattr(obj, "get"):
        try:
            return obj.get(key, default)
        except (AttributeError, TypeError):
            pass

    # Try attribute access
    if hasattr(obj, key):
        return getattr(obj, key)

    return default


def safe_extract_list(obj: Any, key: str) -> list:
    """Safely extract a list value from a DSPy Prediction or dict-like object.

    This is a convenience wrapper around safe_extract for list fields.

    Args:
        obj: Object to extract from
        key: Attribute/key name to extract

    Returns:
        List value (empty list if not found or not a list)

    Examples:
        >>> result = dspy.Prediction(items=[1, 2, 3])
        >>> safe_extract_list(result, "items")
        [1, 2, 3]
        >>> safe_extract_list(result, "missing")
        []
    """
    value = safe_extract(obj, key, [])
    if isinstance(value, list):
        return value
    return []


def safe_extract_dict(obj: Any, key: str) -> dict:
    """Safely extract a dict value from a DSPy Prediction or dict-like object.

    This is a convenience wrapper around safe_extract for dict fields.

    Args:
        obj: Object to extract from
        key: Attribute/key name to extract

    Returns:
        Dict value (empty dict if not found or not a dict)

    Examples:
        >>> result = dspy.Prediction(data={"key": "value"})
        >>> safe_extract_dict(result, "data")
        {"key": "value"}
        >>> safe_extract_dict(result, "missing")
        {}
    """
    value = safe_extract(obj, key, {})
    if isinstance(value, dict):
        return value
    return {}
