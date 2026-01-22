# =============================================================================
# AGENTX Hydrators - Visual Hydrators Module
# =============================================================================
# Hydrates image and gallery widgets
# =============================================================================

import dspy


class ImageHydratorModule(dspy.Module):
    """Hydrates image widgets with image URLs."""

    def __init__(self):
        super().__init__()
        self.extract_images = dspy.Predict("data -> image_urls")

    def forward(self, presentation_ready: dict) -> dict:
        """Extract image URLs from data."""
        data = presentation_ready.get("researched_data", {})

        image_result = self.extract_images(data=str(data))

        return {
            "descriptor_type": "image",
            "content": image_result.image_urls
            if hasattr(image_result, "image_urls")
            else [],
        }


class GalleryHydratorModule(dspy.Module):
    """Hydrates gallery widgets with multiple images."""

    def __init__(self):
        super().__init__()
        self.extract_gallery = dspy.Predict("data -> gallery_items")

    def forward(self, presentation_ready: dict) -> dict:
        """Extract gallery items from data."""
        data = presentation_ready.get("researched_data", {})

        gallery_result = self.extract_gallery(data=str(data))

        return {
            "descriptor_type": "gallery",
            "content": gallery_result.gallery_items
            if hasattr(gallery_result, "gallery_items")
            else [],
        }
