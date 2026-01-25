# =============================================================================
# AGENTX Hydrators - Markdown Hydrator Module
# =============================================================================
# Hydrates markdown widgets with content
# =============================================================================

import dspy


class MarkdownHydratorModule(dspy.Module):
    """Hydrates markdown widgets with content."""

    def __init__(self):
        super().__init__()
        self.generate_markdown = dspy.Predict(
            "data, povs, citations -> markdown_content"
        )

    def forward(self, presentation_ready: dict) -> dict:
        """Generate markdown content."""
        data = presentation_ready.get("researched_data", {})
        design = presentation_ready.get("design", {})

        povs = design.get("points_of_view", [])
        citations = data.get("citations", [])

        markdown_result = self.generate_markdown(
            data=str(data),
            povs=str(povs),
            citations=str(citations),
        )

        return {
            "descriptor_type": "markdown",
            "content": markdown_result.markdown_content
            if hasattr(markdown_result, "markdown_content")
            else "",
            "citations": citations,  # Include citations for frontend display
        }
