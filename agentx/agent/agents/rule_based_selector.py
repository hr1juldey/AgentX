"""Rule-Based Widget Selector for Widget Selector agent.

Ported from R014: services/tools/widgets/rule_based_selector.py

Provides fast path for common widget selection patterns.
Used as first pass before LLM-based selection for complex cases.
"""

from typing import Any


class RuleBasedWidgetSelector:
    """Rule-based widget selector for fast common cases.

    Provides deterministic selection for:
    - Text-heavy content → markdown
    - Structured data → card
    - User input → form
    - Progress tracking → progress
    - Confirmations → confirmation
    - etc.

    Falls back to None for complex cases requiring LLM.
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

    def __init__(self) -> None:
        """Initialize the rule-based selector."""
        # Common patterns for fast matching
        self.patterns = {
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

    def select(
        self,
        query: str,
        content_type: str,
        existing_widgets: list[str],
    ) -> dict[str, Any] | None:
        """Select widget using rule-based patterns.

        Args:
            query: User's question
            content_type: Type of content
            existing_widgets: Already shown widgets

        Returns:
            dict with widget selection, or None if no rule matches
        """
        query_lower = query.lower()

        # Check for existing widgets (avoid duplicates)
        def is_available(widget: str) -> bool:
            return widget not in existing_widgets

        # Rule 1: Text-heavy content → markdown
        if (
            content_type == "text"
            and any(kw in query_lower for kw in self.patterns["markdown_keywords"])
            and is_available(self.WIDGET_MARKDOWN)
        ):
            return {
                "widget": self.WIDGET_MARKDOWN,
                "confidence": 0.9,
                "reasoning": "Rule: Text-heavy content matched markdown keywords",
            }

        # Rule 2: Structured data → card
        if (
            content_type in ("data", "structured")
            and any(kw in query_lower for kw in self.patterns["card_keywords"])
            and is_available(self.WIDGET_CARD)
        ):
            return {
                "widget": self.WIDGET_CARD,
                "confidence": 0.85,
                "reasoning": "Rule: Structured data matched card keywords",
            }

        # Rule 3: User input → form
        if any(
            kw in query_lower for kw in self.patterns["form_keywords"]
        ) and is_available(self.WIDGET_FORM):
            return {
                "widget": self.WIDGET_FORM,
                "confidence": 0.9,
                "reasoning": "Rule: User input matched form keywords",
            }

        # Rule 4: Progress tracking → progress
        if any(
            kw in query_lower for kw in self.patterns["progress_keywords"]
        ) and is_available(self.WIDGET_PROGRESS):
            return {
                "widget": self.WIDGET_PROGRESS,
                "confidence": 0.95,
                "reasoning": "Rule: Progress tracking matched progress keywords",
            }

        # Rule 5: Confirmations → confirmation
        if any(
            kw in query_lower for kw in self.patterns["confirmation_keywords"]
        ) and is_available(self.WIDGET_CONFIRMATION):
            return {
                "widget": self.WIDGET_CONFIRMATION,
                "confidence": 0.9,
                "reasoning": "Rule: Confirmation request matched confirmation keywords",
            }

        # Rule 6: Data visualization → chart
        if any(
            kw in query_lower for kw in self.patterns["chart_keywords"]
        ) and is_available(self.WIDGET_CHART):
            return {
                "widget": self.WIDGET_CHART,
                "confidence": 0.85,
                "reasoning": "Rule: Data visualization matched chart keywords",
            }

        # Rule 7: Search results → searchResult
        if any(
            kw in query_lower for kw in self.patterns["search_keywords"]
        ) and is_available(self.WIDGET_SEARCH_RESULT):
            return {
                "widget": self.WIDGET_SEARCH_RESULT,
                "confidence": 0.9,
                "reasoning": "Rule: Search query matched searchResult keywords",
            }

        # No rule matched - return None for LLM fallback
        return None
