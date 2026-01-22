# =============================================================================
# AGENTX Common Tool Utilities - Type Conversion
# =============================================================================
# Helper functions for LLM output type conversion with fallbacks
# =============================================================================


def _to_float(value: str | float | bool | None, default: float = 0.5) -> float:
    """Convert LLM output to float with fallbacks.

    Handles:
    - Already-float values
    - String floats ("0.75")
    - Text scores ("High" -> 0.9, "Medium" -> 0.5, "Low" -> 0.2)
    - Booleans (True -> 1.0, False -> 0.0)
    - Percentages ("75%" -> 0.75)

    Args:
        value: Value to convert
        default: Default value if conversion fails

    Returns:
        Float value
    """
    if value is None:
        return default
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if isinstance(value, (int, float)):
        return float(value)
    if not isinstance(value, str):
        return default

    value_clean = value.strip().lower()

    # Text-based scores
    text_map = {
        "very high": 0.95,
        "high": 0.85,
        "good": 0.75,
        "medium": 0.50,
        "moderate": 0.50,
        "low": 0.25,
        "very low": 0.15,
        "poor": 0.20,
    }
    if value_clean in text_map:
        return text_map[value_clean]

    # Percentage format
    if "%" in value_clean:
        try:
            return float(value_clean.replace("%", "")) / 100.0
        except ValueError:
            pass

    # Direct float conversion
    try:
        return float(value_clean)
    except ValueError:
        return default


def _to_bool(value: str | bool | None, default: bool = False) -> bool:
    """Convert LLM output to bool with fallbacks.

    Args:
        value: Value to convert
        default: Default value if conversion fails

    Returns:
        Boolean value
    """
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if not isinstance(value, str):
        return default

    value_clean = value.strip().lower()
    true_values = {"true", "yes", "1", "t", "y", "high", "good", "very high"}
    false_values = {"false", "no", "0", "f", "n", "low", "poor", "very low"}

    if value_clean in true_values:
        return True
    if value_clean in false_values:
        return False
    return default
