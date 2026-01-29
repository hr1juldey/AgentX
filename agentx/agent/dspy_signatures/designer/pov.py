"""DSPy signatures for Designer agent.

Ported from R014: services/tools/designer/pov.py

Implements 3 signatures for UI widget design:
- DesignPOV: Design point of view for content
- DesignColors: Design color scheme
- DesignHierarchy: Design visual hierarchy
"""

import dspy


class DesignPOV(dspy.Signature):
    """Design the point of view for content presentation.

    Determines the best widget type and presentation strategy
    based on content type, user query, and existing UI state.
    """

    query: str = dspy.InputField(
        desc="User's original question",
        prefix="Query: ",
    )
    content: str = dspy.InputField(
        desc="Content to present (findings, data, etc.)",
        prefix="Content: ",
    )
    existing_widgets: str = dspy.InputField(
        desc="List of already shown widget types (e.g., 'card, markdown, chart')",
        prefix="Existing widgets: ",
    )
    recommended_widget: str = dspy.OutputField(
        desc="""Recommended widget type from:
        - markdown: For text-heavy content
        - card: For structured information
        - form: For user input
        - progress: For multi-step processes
        - action: For user actions/confirmations
        - confirmation: For yes/no decisions
        - image: For visual content
        - gallery: For multiple images
        - chart: For data visualization
        - searchResult: For search results
        - hopProgress: For multi-hop reasoning
        - citationCard: For source citations"""
    )
    widget_props: str = dspy.OutputField(
        desc="JSON string with widget-specific properties (title, content, options, etc.)"
    )
    rationale: str = dspy.OutputField(
        desc="Explanation for why this widget was chosen",
        prefix="Rationale: ",
    )


class DesignColors(dspy.Signature):
    """Design color scheme for widgets.

    Selects appropriate colors based on:
    - Content type (data, text, media)
    - User intent (inform, alert, guide)
    - Brand guidelines
    """

    widget_type: str = dspy.InputField(
        desc="Type of widget being colored",
        prefix="Widget: ",
    )
    content_purpose: str = dspy.InputField(
        desc="Purpose of the content (info, warning, success, error)",
        prefix="Purpose: ",
    )
    color_scheme: str = dspy.OutputField(
        desc="""Color scheme as JSON with:
        - primary: Main color (hex)
        - secondary: Accent color (hex)
        - background: Background color (hex)
        - text: Text color (hex)
        - border: Border color (hex)"""
    )


class DesignHierarchy(dspy.Signature):
    """Design visual hierarchy for complex widgets.

    Determines layout and information architecture:
    - Primary/secondary/tertiary elements
    - Grouping and spacing
    - Visual flow
    """

    widget_type: str = dspy.InputField(
        desc="Type of widget being designed",
        prefix="Widget: ",
    )
    content_structure: str = dspy.InputField(
        desc="Structure of the content (sections, fields, data points)",
        prefix="Structure: ",
    )
    hierarchy_plan: str = dspy.OutputField(
        desc="""Hierarchy plan with:
        - primary: Most important elements (what user sees first)
        - secondary: Supporting elements
        - tertiary: Background/contextual elements
        - spacing: Recommended spacing between elements
        - grouping: How to group related elements"""
    )
