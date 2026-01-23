# =============================================================================
# AGENTX WIDGET SELECTOR Agent
# =============================================================================
# Phase 6: What Widgets?
# =============================================================================

import dspy

from services.tools.selector_tools import WidgetMatcherModule


class WidgetSelectorAgent(dspy.Module):
    """WIDGET SELECTOR Agent: Decides which widgets to use.

    Runs AFTER research is complete, selects appropriate widgets
    based on complete data context and user intent.
    """

    def __init__(self):
        super().__init__()
        self.widget_matcher = WidgetMatcherModule()

    def forward(
        self,
        designed_data: dict,
        device_context: str = "desktop",
    ) -> dict:
        """Execute WIDGET SELECTOR agent pipeline.

        Args:
            designed_data: Design output from DESIGNER agent
            device_context: Device context (desktop, mobile, etc.)

        Returns:
            Selected widgets with rationale
        """
        # URL-related keywords (search, find, look up)
        url_keywords = [
            "search",
            "find",
            "look up",
            "information about",
            "what is",
            "tell me about",
            "show me",
        ]

        # Check if query is likely to return URLs
        query = designed_data.get("query", "").lower()
        metadata = designed_data.get("metadata", {})
        url_count = metadata.get("url_count", 0)
        is_url_query = any(keyword in query for keyword in url_keywords)

        # Multiple URLs → OpenGraph gallery
        if is_url_query and url_count > 1:
            return {
                "widgets": ["gallery", "markdown"],
                "rationale": "Gallery for multiple URLs, markdown for summary",
                "device_context": device_context,
            }

        # Single URL → OpenGraph card (via image hydrator)
        if is_url_query and url_count == 1:
            return {
                "widgets": ["image", "markdown"],
                "rationale": "Image card for single URL, markdown for context",
                "device_context": device_context,
            }

        # Match widgets based on designed data
        match_result_raw = self.widget_matcher(
            designed_data=designed_data,
            device_context=device_context,
        )
        match_result = match_result_raw if hasattr(match_result_raw, "get") else {}

        matched_widgets = match_result.get("widgets", ["markdown"])  # type: ignore[missing-attribute]

        return {
            "widgets": matched_widgets,
            "rationale": match_result.get(  # type: ignore[missing-attribute]
                "rationale", "Selected based on data type and context"
            ),
            "device_context": device_context,
        }

    def suggest_fallback_widget(self, error_type: str = "") -> str:
        """Suggest a fallback widget when selection fails.

        Args:
            error_type: Type of error for context

        Returns:
            Fallback widget name
        """
        if "data" in error_type.lower() or "research" in error_type.lower():
            return "markdown"
        if "visual" in error_type.lower():
            return "card"
        return "markdown"  # Default fallback
