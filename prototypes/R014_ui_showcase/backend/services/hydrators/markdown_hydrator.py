# =============================================================================
# AGENTX Markdown Hydrator
# =============================================================================
# Fills markdown widgets with content + citations + POVs
# =============================================================================

from typing import Any

import dspy

from services.tools.hydrators import MarkdownHydratorModule


class MarkdownHydrator(dspy.Module):
    """Markdown Hydrator: Fills markdown widgets with rich content.

    Creates markdown content with citations, multiple points of view,
    and proper formatting for presentation.
    """

    def __init__(self):
        super().__init__()
        self.hydrator = MarkdownHydratorModule()

    def forward(
        self,
        presentation_ready: dict,
        researched_data: dict,
        design: dict,
    ) -> dict[str, Any]:
        """Hydrate markdown widget with content.

        Args:
            presentation_ready: Output from PRESENTER agent
            researched_data: Research output from RESEARCHER/CONTEXTUALIZER
            design: Design output from DESIGNER agent

        Returns:
            Markdown widget descriptor with hydrated content
        """
        beautiful_data = researched_data.get("beautiful_data", {})
        citations = researched_data.get("citations", [])
        points_of_view = design.get("points_of_view", [])
        nuanced_analysis = design.get("nuanced_analysis", "")

        # Prepare data for hydration
        hydration_input = {
            "researched_data": {
                "key_facts": beautiful_data.get("key_facts", []),
                "trends": beautiful_data.get("trends", {}),
                "structured_report": researched_data.get("structured_report", ""),
            },
            "design": {
                "points_of_view": points_of_view,
                "nuanced_analysis": nuanced_analysis,
            },
            "citations": citations,
        }

        # Generate markdown content
        markdown_content = self.hydrator(presentation_ready=hydration_input)

        # Extract content from result (DSPy Predict returns special object)
        content = (
            markdown_content.get("content", "")
            if hasattr(markdown_content, "get")
            else ""
        )

        return {
            "descriptor_type": "markdown",
            "content": content,
            "metadata": {
                "citation_count": len(citations),
                "pov_count": len(points_of_view),
                "word_count": len(content.split()),
            },
        }


def create_markdown_hydrator() -> MarkdownHydrator:
    """Factory function for MarkdownHydrator."""
    return MarkdownHydrator()
