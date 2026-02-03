"""Keyword constants for query characteristic analysis."""

# Keyword lists for characteristic detection
CURRENT_EVENT_KEYWORDS = [
    "latest",
    "recent",
    "breaking",
    "today",
    "yesterday",
    "this week",
    "this month",
    "this year",
    "2024",
    "2025",
    "2026",
    "news",
    "happening",
]

PREDICTION_KEYWORDS = [
    "will",
    "predict",
    "forecast",
    "future",
    "expect",
    "likely",
    "probability",
    "chance",
    "upcoming",
]

ESTABLISHED_KEYWORDS = [
    "what is",
    "define",
    "explain",
    "history",
    "capital of",
    "population of",
    "who was",
    "when did",
]

NICHE_KEYWORDS = [
    "obscure",
    "rare",
    "little known",
    "uncommon",
    "specialized",
    "technical",
]

CONTRADICTING_KEYWORDS = [
    "compare",
    "versus",
    "vs",
    "difference",
    "conflict",
    "contradiction",
    "debate",
    "controversy",
]


__all__ = [
    "CURRENT_EVENT_KEYWORDS",
    "PREDICTION_KEYWORDS",
    "ESTABLISHED_KEYWORDS",
    "NICHE_KEYWORDS",
    "CONTRADICTING_KEYWORDS",
]
