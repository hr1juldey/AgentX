"""DSPy signatures for Widget Selector agent.

Ported from R014: services/tools/widgets/selection.py

Implements semantic widget selection with few-shot learning.
Selects appropriate widgets based on content and user query.
"""

import dspy


class SelectWidgetSignature(dspy.Signature):
    """Select appropriate widget for content presentation.

    Uses semantic understanding to match content to best widget type.
    Few-shot learning pattern for robust selection.

    Widget types:
    - markdown: Text-heavy content, documentation
    - card: Structured information with title and content
    - form: User input with fields
    - progress: Multi-step process tracking
    - action: User action buttons/confirmations
    - confirmation: Yes/no decisions
    - image: Single image display
    - gallery: Multiple images grid
    - chart: Data visualization (bar, line, pie)
    - searchResult: Search results list
    - hopProgress: Multi-hop reasoning progress
    - citationCard: Source citations with metadata
    """

    query: str = dspy.InputField(
        desc="User's original question or request",
        prefix="Query: ",
    )
    content_type: str = dspy.InputField(
        desc="Type of content (text, data, image, form, etc.)",
        prefix="Content type: ",
    )
    content_summary: str = dspy.InputField(
        desc="Brief summary of the content to present",
        prefix="Summary: ",
    )
    existing_widgets: str = dspy.InputField(
        desc="Already shown widget types (avoid duplicates)",
        prefix="Existing: ",
    )
    selected_widget: str = dspy.OutputField(
        desc="Selected widget type from the 12 available options",
        prefix="Widget: ",
    )
    confidence: float = dspy.OutputField(
        desc="Confidence in this selection (0.0 to 1.0)",
        prefix="Confidence: ",
    )
    reasoning: str = dspy.OutputField(
        desc="Explanation for why this widget is best suited",
        prefix="Reasoning: ",
    )


class ValidateWidgetChoice(dspy.Signature):
    """Validate widget choice against constraints.

    Checks if the selected widget:
    - Is not already shown (if unique)
    - Matches content type
    - Fits available screen space
    - Is appropriate for user context
    """

    selected_widget: str = dspy.InputField(
        desc="Proposed widget type",
        prefix="Widget: ",
    )
    content_type: str = dspy.InputField(
        desc="Type of content to present",
        prefix="Content: ",
    )
    existing_widgets: str = dspy.InputField(
        desc="Already shown widgets",
        prefix="Existing: ",
    )
    is_valid: bool = dspy.OutputField(
        desc="Whether this widget choice is valid",
        prefix="Valid: ",
    )
    issues: str = dspy.OutputField(
        desc="Any issues with this choice (empty if valid)",
        prefix="Issues: ",
    )
