# =============================================================================
# AGENTX Hydrators - Markdown Hydrator Module
# =============================================================================
# Hydrates markdown widgets with content
# =============================================================================

import dspy

from services.tools.researcher.number_extractor_utils import strip_markdown_wrapper


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

        # Get raw markdown content from LLM
        raw_content = (
            markdown_result.markdown_content
            if hasattr(markdown_result, "markdown_content")
            else ""
        )

        # Strip markdown code block wrapper (14B coder models)
        clean_content = strip_markdown_wrapper(raw_content)

        return {
            "descriptor_type": "markdown",
            "content": clean_content,
            "citations": citations,  # Include citations for frontend display
        }
