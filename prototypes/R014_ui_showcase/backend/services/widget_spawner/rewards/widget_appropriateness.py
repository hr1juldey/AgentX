# =============================================================================
# AGENTX Widget Spawner - Widget Appropriateness Rewards
# =============================================================================
# Reward functions for widget appropriateness scoring
# =============================================================================

"""Widget appropriateness scoring functions.

Provides pure logic for scoring how appropriate different widget types
are for various content types.
"""


def widget_appropriateness_score(content_analysis: str, widget_type: str) -> float:
    """Score how appropriate a widget type is for the content.

    Pure logic based on content-type to widget-type mapping.
    """
    content_type = content_analysis.lower()

    # Data-heavy content
    if any(
        kw in content_type
        for kw in ["data", "trends", "statistics", "analytics", "metrics"]
    ):
        if widget_type in ["chart", "table", "card"]:
            return 0.9
        elif widget_type == "markdown":
            return 0.3

    # Text-heavy content
    if any(
        kw in content_type
        for kw in ["article", "blog", "guide", "explanation", "summary"]
    ):
        if widget_type in ["markdown", "card"]:
            return 0.9
        elif widget_type == "chart":
            return 0.2

    # Form/input content
    if any(
        kw in content_type for kw in ["input", "form", "survey", "feedback", "collect"]
    ):
        if widget_type == "form":
            return 1.0
        elif widget_type == "card":
            return 0.4

    # Visual/gallery content
    if any(
        kw in content_type for kw in ["images", "photos", "gallery", "visual", "media"]
    ):
        if widget_type in ["gallery", "image"]:
            return 0.95
        elif widget_type == "card":
            return 0.5

    # Progress/status content
    if any(
        kw in content_type for kw in ["loading", "progress", "status", "processing"]
    ):
        if widget_type == "progress":
            return 1.0
        elif widget_type == "card":
            return 0.6

    return 0.5


def form_appropriateness_penalty(content_analysis: str, widget_type: str) -> float:
    """Apply penalty for inappropriate form usage.

    Pure logic - no LLM calls.
    """
    if widget_type != "form":
        return 0.0

    content_lower = content_analysis.lower()

    # Informational query keywords that should NOT have forms
    info_keywords = [
        "explain",
        "what is",
        "tell me about",
        "show me",
        "describe",
        "compare",
        "latest",
        "developments",
        "news",
        "trends",
        "overview",
        "summary",
    ]

    # Collection keywords that SHOULD have forms
    collect_keywords = [
        "create form",
        "build form",
        "signup",
        "submit",
        "collect data",
        "survey",
        "questionnaire",
        "feedback",
        "register",
        "enter data",
        "input form",
    ]

    # Check if query is informational
    if any(kw in content_lower for kw in info_keywords):
        # Only allow form if collection keywords are also present
        if not any(kw in content_lower for kw in collect_keywords):
            return -0.5  # Significant penalty for form in informational query

    return 0.0
