# =============================================================================
# AGENTX Markdown Hydrator
# =============================================================================
# Fills markdown widgets with content + citations + POVs
# =============================================================================

import logging
import uuid
from datetime import datetime

from typing import Any

import dspy
from services.tools.hydrators import MarkdownHydratorModule

logger = logging.getLogger(__name__)


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
        structured_report = researched_data.get("structured_report", "")
        points_of_view = design.get("points_of_view", [])
        nuanced_analysis = design.get("nuanced_analysis", "")

        # Log what we received for debugging
        logger.info("  📊 [MARKDOWN HYDRATOR] Received data:")
        logger.info(f"      - beautiful_data keys: {list(beautiful_data.keys())}")
        logger.info(f"      - citations: {len(citations)} items")
        logger.info(f"      - structured_report: {len(structured_report)} chars")
        logger.info(f"      - points_of_view: {len(points_of_view)} items")

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
            "id": str(uuid.uuid4())[:8],
            "type": "markdown",
            "timestamp": datetime.utcnow().isoformat(),
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
