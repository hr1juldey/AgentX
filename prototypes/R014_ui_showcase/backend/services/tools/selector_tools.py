# =============================================================================
# AGENTX Selector Tools
# =============================================================================
# DSPy modules for the WIDGET SELECTOR agent (What Widgets?)
# =============================================================================

import dspy


class SelectWidgetSignature(dspy.Signature):
    """Select appropriate widgets based on query intent and data characteristics.

    SEMANTIC PATTERNS (learn from these examples):

    Example 1:
    Query: "Show real-time stock prices"
    Data: numerical_time_series
    Selected: chart
    Reasoning: Stock prices are time-series data that change continuously.
               Charts visualize trends over time better than static widgets.

    Example 2:
    Query: "Display photo gallery"
    Data: visual_image
    Selected: gallery
    Reasoning: Multiple images need a grid layout. Gallery widget handles
               image collections with captions and metadata.

    Example 3:
    Query: "Compare pricing plans"
    Data: comparative
    Selected: card
    Reasoning: Comparison needs side-by-side layout. Cards present discrete
               options with clear visual boundaries for easy comparison.

    Example 4:
    Query: "Create form wizard"
    Data: general
    Selected: form
    Reasoning: Multi-step input requires form widget with validation and
               progression states.

    Example 5:
    Query: "Show clock"
    Data: temporal
    Selected: clock
    Reasoning: Direct time display request. Clock widget is the semantic match.

    NOTE: These are EXAMPLES to learn from, not hard-coded rules.
    You are free to reason about new queries based on these patterns.
    """

    query: str = dspy.InputField(desc="User's natural language request")
    data_type: str = dspy.InputField(
        desc="Type of data: numerical_time_series, visual_image, comparative, general, temporal"
    )
    device_context: str = dspy.InputField(desc="Device type: mobile, desktop, tablet")
    widgets: str = dspy.OutputField(
        desc="1-3 widgets from VALID_WIDGETS, comma-separated. "
        "Choose based on semantic patterns above. "
        "Example: 'chart' or 'gallery, markdown'"
    )
    rationale: str = dspy.OutputField(
        desc="Brief explanation following the pattern: "
        "'[Data characteristic] requires [visualization need]. "
        "[Widget] provides [capability].'"
    )


class WidgetMatcherModule(dspy.Module):
    """Match widgets using semantic understanding, not hard-coded rules."""

    VALID_WIDGETS = {
        "chart",
        "markdown",
        "gallery",
        "card",
        "form",
        "image",
        "map",
        "clock",
        "calendar",
        "calculator",
        "media controls",
        "opengraph-card",
        "opengraph-gallery",
    }

    def __init__(self):
        super().__init__()
        self.matcher = dspy.ChainOfThought(SelectWidgetSignature)

    def forward(
        self,
        designed_data: dict,
        device_context: str = "desktop",
    ) -> dict:
        """Let LLM reason about the best widget based on semantic patterns."""
        result = self.matcher(
            query=designed_data.get("query", ""),
            data_type=designed_data.get("data_type", "general"),
            device_context=device_context,
        )

        # Validate LLM output
        suggested_widgets = [
            w.strip()
            for w in result.widgets.split(",")
            if w.strip() in self.VALID_WIDGETS
        ]

        return {
            "widgets": suggested_widgets or ["markdown"],
            "rationale": result.rationale,
        }

