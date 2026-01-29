"""DSPy signatures for Sequencer agent.

Ported from R014: services/pipeline/sequencer.py

Implements signatures for widget sequencing and pacing calculation.
"""

import dspy


class SequenceWidgets(dspy.Signature):
    """Determine optimal order for presenting multiple widgets.

    Orders widgets based on:
    - Logical flow (foundation → details → actions)
    - User attention (most important first)
    - Dependencies (some widgets require context from others)
    """

    widgets: str = dspy.InputField(
        desc="List of widgets to sequence (JSON array with type and purpose)",
        prefix="Widgets: ",
    )
    query: str = dspy.InputField(
        desc="User's original question for context",
        prefix="Query: ",
    )
    optimal_order: str = dspy.OutputField(
        desc="Optimal widget order as JSON array of widget indices",
        prefix="Order: ",
    )
    reasoning: str = dspy.OutputField(
        desc="Explanation for the chosen sequence",
        prefix="Reasoning: ",
    )


class CalculatePacing(dspy.Signature):
    """Calculate pacing for widget delivery.

    Determines:
    - Initial delay before first widget
    - Inter-widget delays
    - Total delivery time
    """

    num_widgets: int = dspy.InputField(
        desc="Number of widgets to deliver",
        prefix="Count: ",
    )
    urgency: str = dspy.InputField(
        desc="Urgency level (immediate, routine, background)",
        prefix="Urgency: ",
    )
    pacing_plan: str = dspy.OutputField(
        desc="""Pacing plan as JSON with:
        - delays: Array of delay times (seconds)
        - total_time: Total delivery time
        - reasoning: Explanation for pacing choices"""
    )
