"""Widget Pattern Library for Rule-Based Selector.

Keyword patterns for fast widget selection based on query content.
"""

# Widget type constants (from C007)
WIDGET_MARKDOWN = "markdown"
WIDGET_CARD = "card"
WIDGET_FORM = "form"
WIDGET_PROGRESS = "progress"
WIDGET_ACTION = "action"
WIDGET_CONFIRMATION = "confirmation"
WIDGET_IMAGE = "image"
WIDGET_GALLERY = "gallery"
WIDGET_CHART = "chart"
WIDGET_SEARCH_RESULT = "searchResult"
WIDGET_HOP_PROGRESS = "hopProgress"
WIDGET_CITATION_CARD = "citationCard"


# Widget selection patterns
WIDGET_PATTERNS = {
    # Keywords that suggest markdown
    "markdown_keywords": {
        "document",
        "documentation",
        "article",
        "blog",
        "tutorial",
        "guide",
        "explanation",
        "instructions",
        "readme",
        "notes",
    },
    # Keywords that suggest card
    "card_keywords": {
        "result",
        "answer",
        "summary",
        "information",
        "details",
        "overview",
        "statistic",
        "fact",
        "definition",
        "profile",
    },
    # Keywords that suggest form
    "form_keywords": {
        "input",
        "enter",
        "submit",
        "fill",
        "provide",
        "specify",
        "choose",
        "select",
        "options",
        "parameters",
        "settings",
    },
    # Keywords that suggest progress
    "progress_keywords": {
        "loading",
        "processing",
        "progress",
        "step",
        "stage",
        "phase",
        "downloading",
        "uploading",
        "analyzing",
        "computing",
        "working",
    },
    # Keywords that suggest confirmation
    "confirmation_keywords": {
        "confirm",
        "approve",
        "deny",
        "reject",
        "accept",
        "decline",
        "yes",
        "no",
        "agree",
        "disagree",
        "allow",
        "permit",
    },
    # Keywords that suggest chart
    "chart_keywords": {
        "graph",
        "chart",
        "plot",
        "visualization",
        "trend",
        "analytics",
        "statistics",
        "data",
        "comparison",
        "distribution",
        "metrics",
    },
    # Keywords that suggest search result
    "search_keywords": {
        "search",
        "results",
        "found",
        "matching",
        "items",
        "entries",
        "query",
        "look for",
        "find",
        "locate",
        "retrieve",
    },
}


__all__ = [
    "WIDGET_MARKDOWN",
    "WIDGET_CARD",
    "WIDGET_FORM",
    "WIDGET_PROGRESS",
    "WIDGET_ACTION",
    "WIDGET_CONFIRMATION",
    "WIDGET_IMAGE",
    "WIDGET_GALLERY",
    "WIDGET_CHART",
    "WIDGET_SEARCH_RESULT",
    "WIDGET_HOP_PROGRESS",
    "WIDGET_CITATION_CARD",
    "WIDGET_PATTERNS",
]
