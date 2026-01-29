"""Widget Matcher Module for Widget Selector agent.

Ported from R014: services/tools/widgets/widget_matcher.py

Uses few-shot learning for semantic widget matching.
Selects appropriate widgets based on content analysis.
"""

import dspy

from agentx.agent.dspy_signatures.widgets.selection import SelectWidgetSignature
from agentx.agent.tools.common.dspy_helpers import safe_extract
from agentx.agent.tools.common.type_utils import _to_float


class WidgetMatcherModule(dspy.Module):
    """Matches content to appropriate widgets using few-shot learning.

    Uses semantic understanding to select the best widget type.
    Runs multiple iterations for diverse matching, then selects best result.
    """

    # Available widget types (frozen set from C007)
    WIDGET_TYPES = {
        "markdown",
        "card",
        "form",
        "progress",
        "action",
        "confirmation",
        "image",
        "gallery",
        "chart",
        "searchResult",
        "hopProgress",
        "citationCard",
    }

    def __init__(self, num_iterations: int = 3) -> None:
        """Initialize the widget matcher.

        Args:
            num_iterations: Number of matching iterations for diversity
        """
        super().__init__()
        self.matcher = dspy.ChainOfThought(SelectWidgetSignature)
        self.num_iterations = num_iterations

    def forward(
        self,
        query: str,
        content_type: str,
        content_summary: str,
        existing_widgets: list[str],
    ) -> dict:
        """Match content to best widget using few-shot learning.

        Args:
            query: User's original question
            content_type: Type of content (text, data, image, etc.)
            content_summary: Brief content summary
            existing_widgets: List of already shown widget types

        Returns:
            dict with selected_widget, confidence, and reasoning
        """
        all_matches = []

        # Build existing widgets string
        existing_str = ", ".join(existing_widgets) if existing_widgets else "none"

        # Run multiple iterations for diversity
        for _ in range(self.num_iterations):
            result = self.matcher(
                query=query,
                content_type=content_type,
                content_summary=content_summary,
                existing_widgets=existing_str,
            )

            selected_widget = safe_extract(result, "selected_widget", "card")
            confidence = _to_float(safe_extract(result, "confidence", 0.5), default=0.5)
            reasoning = safe_extract(result, "reasoning", "")

            # Validate widget type
            if selected_widget in self.WIDGET_TYPES:
                # Check for duplicates
                if selected_widget not in existing_widgets:
                    all_matches.append(
                        {
                            "widget": selected_widget,
                            "confidence": confidence,
                            "reasoning": reasoning,
                        }
                    )

        # Select best match (highest confidence)
        if all_matches:
            best_match = max(all_matches, key=lambda x: x["confidence"])
            return {
                "selected_widget": best_match["widget"],
                "confidence": best_match["confidence"],
                "reasoning": best_match["reasoning"],
            }

        # Fallback: return card if no valid matches
        return {
            "selected_widget": "card",
            "confidence": 0.5,
            "reasoning": "Fallback to card widget (no valid matches found)",
        }
