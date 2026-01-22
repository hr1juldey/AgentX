# =============================================================================
# AGENTX Gallery Hydrator
# =============================================================================
# Fills gallery widgets with multiple images
# =============================================================================

from typing import Any

import dspy

from services.tools.hydration_tools import GalleryHydratorModule


class GalleryHydrator(dspy.Module):
    """Gallery Hydrator: Fills gallery widgets with multiple images.

    Creates curated image galleries from research data,
    organized by theme or relevance.
    """

    def __init__(self):
        super().__init__()
        self.hydrator = GalleryHydratorModule()

    def forward(
        self,
        presentation_ready: dict,
        researched_data: dict,
        design: dict,
    ) -> dict[str, Any]:
        """Hydrate gallery with multiple OpenGraph URL cards.

        Args:
            presentation_ready: Output from PRESENTER agent
            researched_data: Research output from RESEARCHER/CONTEXTUALIZER
            design: Design output from DESIGNER agent

        Returns:
            Gallery widget descriptor with OpenGraph URLs
        """
        url_list = researched_data.get("url_list", [])

        if len(url_list) > 1:
            # Multiple URLs → gallery of OpenGraph cards
            return {
                "descriptor_type": "opengraph-gallery",
                "metadata": {
                    "images": [
                        {
                            "url": item["url"],
                            "title": item["title"],
                            "caption": item["snippet"][:150] if len(item["snippet"]) > 150 else item["snippet"],
                        }
                        for item in url_list[:8]
                    ],
                    "item_count": min(len(url_list), 8),
                },
            }

        # Single URL → single OpenGraph card
        elif url_list:
            return {
                "descriptor_type": "opengraph-card",
                "metadata": {
                    "url": url_list[0]["url"],
                    "title": url_list[0]["title"],
                    "description": url_list[0]["snippet"][:150],
                    "site_name": url_list[0]["source"],
                },
            }

        # Fallback
        return {
            "descriptor_type": "markdown",
            "content": "No URLs found for display.",
        }


def create_gallery_hydrator() -> GalleryHydrator:
    """Factory function for GalleryHydrator."""
    return GalleryHydrator()
