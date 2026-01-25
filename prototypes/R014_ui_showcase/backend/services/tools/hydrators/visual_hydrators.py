# =============================================================================
# AGENTX Hydrators - Visual Hydrators Module
# =============================================================================
# Hydrates image and gallery widgets with real image search
# =============================================================================

import logging

import dspy

from services.tools.researcher.searxng_search import SearXNGSearchModule

logger = logging.getLogger(__name__)


class ImageHydratorModule(dspy.Module):
    """Hydrates image widgets with image URLs from SearXNG search."""

    def __init__(self):
        super().__init__()
        self.image_search = SearXNGSearchModule()

    def forward(self, presentation_ready: dict) -> dict:
        """Search for images and return first result as single image widget."""
        query = presentation_ready.get("query", "")

        # Perform BOTH general and image search
        text_result = self.image_search(query=query, search_type="general")  # type: ignore[call-arg]
        image_result = self.image_search(query=query, search_type="images")  # type: ignore[call-arg]

        text_list = text_result.get("url_list", [])  # type: ignore[missing-attribute]
        image_list = image_result.get("url_list", [])  # type: ignore[missing-attribute]

        # Build image widget data
        if image_list and len(image_list) > 0:
            image_url = image_list[0].get("url", "")
            title = image_list[0].get("title", "Image")
        else:
            # Fallback - no image found
            return {
                "descriptor_type": "image",
                "content": "",
                "metadata": {"error": "No images found"},
            }

        # Extract caption from text search results
        caption = ""
        if text_list and len(text_list) > 0:
            caption = text_list[0].get("snippet", "")[:200]

        return {
            "descriptor_type": "image",
            "content": image_url,
            "title": title,
            "metadata": {"caption": caption} if caption else None,
        }


class GalleryHydratorModule(dspy.Module):
    """Hydrates gallery widgets with multiple images from SearXNG search."""

    def __init__(self):
        super().__init__()
        self.image_search = SearXNGSearchModule()

    def forward(self, presentation_ready: dict) -> dict:
        """Search for images and return gallery items."""
        query = presentation_ready.get("query", "")

        # Perform BOTH general and image search
        text_result = self.image_search(query=query, search_type="general")  # type: ignore[call-arg]
        image_result = self.image_search(query=query, search_type="images")  # type: ignore[call-arg]

        text_list = text_result.get("url_list", [])  # type: ignore[missing-attribute]
        image_list = image_result.get("url_list", [])  # type: ignore[missing-attribute]

        # Build gallery items (max 8 images)
        gallery_items = []
        for img in image_list[:8]:
            gallery_items.append(
                {
                    "url": img.get("url", ""),
                    "title": img.get("title", "Image"),
                    "caption": img.get("snippet", "")[:100]
                    if img.get("snippet")
                    else "",
                }
            )

        # Extract description from text search results
        description = ""
        if text_list and len(text_list) > 0:
            description = text_list[0].get("snippet", "")[:300]

        logger.info(
            f"[GalleryHydrator] Found {len(gallery_items)} images for query: {query[:60]}..."
        )

        return {
            "descriptor_type": "gallery",
            "content": gallery_items,
            "title": "Image Gallery",
            "metadata": {"description": description} if description else None,
        }
