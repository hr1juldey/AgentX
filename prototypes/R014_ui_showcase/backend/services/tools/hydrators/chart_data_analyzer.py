# =============================================================================
# AGENTX Hydrators - Chart Data Analyzer
# =============================================================================
# Analyzes extracted numbers to build semantic context
# =============================================================================

import logging


logger = logging.getLogger(__name__)


def build_data_sample(extracted_numbers: list) -> str:
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


def build_data_context(extracted_numbers: list) -> str:
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
