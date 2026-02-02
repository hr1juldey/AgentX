"""DSPy signatures for widget selection.

Defines signatures for content pattern detection.
"""

import dspy


class DetectContentPatternSignature(dspy.Signature):
    """Signature for detecting content patterns in findings.

    The LLM analyzes research findings and identifies patterns
    that map to specific widget types.
    """

    query = dspy.InputField(desc="User's original query")
    research_findings = dspy.InputField(desc="Accumulated research findings")
    has_comparison = dspy.OutputField(desc="True if comparing items")
    has_temporal_data = dspy.OutputField(desc="True if time-series data")
    has_geographic_data = dspy.OutputField(desc="True if location-based data")
    has_ranking = dspy.OutputField(desc="True if ranked items")
    suggested_widgets = dspy.OutputField(
        desc="JSON string of widget types: ['data_table', 'chart', etc.]"
    )
