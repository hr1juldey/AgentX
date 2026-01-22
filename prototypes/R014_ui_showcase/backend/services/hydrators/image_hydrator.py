# =============================================================================
# AGENTX Image Hydrator
# =============================================================================
# Fills image widgets with image URLs from research
# =============================================================================

from typing import Any

import dspy

from services.tools.hydrators import ImageHydratorModule


class ImageHydrator(dspy.Module):
    """Image Hydrator: Fills image widgets with image URLs.

    Extracts relevant images from research data for visual
    presentation of information.
    """

    def __init__(self):
        super().__init__()
        self.hydrator = ImageHydratorModule()

    def forward(
        self,
        presentation_ready: dict,
        researched_data: dict,
        design: dict,
    ) -> dict[str, Any]:
        """Hydrate widget with OpenGraph URL card.

        Args:
            presentation_ready: Output from PRESENTER agent
            researched_data: Research output from RESEARCHER/CONTEXTUALIZER
            design: Design output from DESIGNER agent

        Returns:
            OpenGraph card widget descriptor with URL metadata
        """
        url_list = researched_data.get("url_list", [])

        if url_list:
            # First URL becomes an OpenGraph card
            first_url = url_list[0]
            return {
                "descriptor_type": "opengraph-card",
                "metadata": {
                    "url": first_url["url"],
                    "title": first_url["title"],
                    "description": first_url["snippet"],
                    "site_name": first_url["source"],
                },
            }

        # Fallback: generic placeholder
        return {
            "descriptor_type": "markdown",
            "content": "No URLs found for display.",
        }


def create_image_hydrator() -> ImageHydrator:
    """Factory function for ImageHydrator."""
    return ImageHydrator()
