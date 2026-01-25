# =============================================================================
# AGENTX Widget Spawner - Image Widget Builders
# =============================================================================
# Helper functions for building image and gallery widgets
# =============================================================================

import uuid
from datetime import datetime
from typing import Any

from services.widget_spawner.config import (
    DEFAULT_GALLERY_IMAGE_HEIGHT,
    DEFAULT_GALLERY_IMAGE_WIDTH,
    DEFAULT_IMAGE_BASE_URL,
    DEFAULT_IMAGE_HEIGHT,
    DEFAULT_IMAGE_WIDTH,
)


def build_image_widget(
    user_query: str,
    widget_id: str,
    image_urls: list | None = None,
    text_context: list | None = None,
) -> dict[str, Any]:
    """Build image widget data.

    Args:
        user_query: The user's query
        widget_id: Unique widget identifier
        image_urls: Optional list of image URLs from SearXNG search
        text_context: Optional list of text results from general search
    """
    # Use real image URLs if provided, otherwise fallback to placeholder
    if image_urls and len(image_urls) > 0:
        image_url = image_urls[0].get("url", "")
        title = image_urls[0].get("title", "Image")
    else:
        image_url = f"{DEFAULT_IMAGE_BASE_URL}/{DEFAULT_IMAGE_WIDTH}x{DEFAULT_IMAGE_HEIGHT}?random={uuid.uuid4().hex}"
        title = "Generated Image"

    # Extract caption from text context (general search results)
    caption = ""
    if text_context and len(text_context) > 0:
        # Use snippet from first text result as caption
        caption = text_context[0].get("snippet", "")[:200]

    return {
        "id": widget_id,
        "type": "image",
        "title": title,
        "content": image_url,  # ImageWidget expects content = image URL
        "metadata": {"caption": caption} if caption else None,
        "timestamp": datetime.utcnow().isoformat(),
        "dismissible": True,
    }


def build_gallery_widget(
    user_query: str,
    widget_id: str,
    image_urls: list | None = None,
    text_context: list | None = None,
) -> dict[str, Any]:
    """Build gallery widget data.

    Args:
        user_query: The user's query
        widget_id: Unique widget identifier
        image_urls: Optional list of image URLs from SearXNG search
        text_context: Optional list of text results from general search
    """
    # Use real image URLs if provided, otherwise fallback to placeholders
    if image_urls and len(image_urls) > 0:
        images = []
        for img in image_urls[:8]:  # Max 8 images
            images.append(
                {
                    "url": img.get("url", ""),
                    "title": img.get("title", "Image"),
                    "caption": img.get("snippet", "")[:100]
                    if img.get("snippet")
                    else "",
                }
            )
    else:
        # Fallback to placeholders
        images = [
            {
                "url": f"{DEFAULT_IMAGE_BASE_URL}/seed/{uuid.uuid4().hex}/{DEFAULT_GALLERY_IMAGE_WIDTH}x{DEFAULT_GALLERY_IMAGE_HEIGHT}",
                "title": "Gallery Image 1",
                "caption": "Generated image",
            },
            {
                "url": f"{DEFAULT_IMAGE_BASE_URL}/seed/{uuid.uuid4().hex}/{DEFAULT_GALLERY_IMAGE_WIDTH}x{DEFAULT_GALLERY_IMAGE_HEIGHT}",
                "title": "Gallery Image 2",
                "caption": "Generated image",
            },
            {
                "url": f"{DEFAULT_IMAGE_BASE_URL}/seed/{uuid.uuid4().hex}/{DEFAULT_GALLERY_IMAGE_WIDTH}x{DEFAULT_GALLERY_IMAGE_HEIGHT}",
                "title": "Gallery Image 3",
                "caption": "Generated image",
            },
            {
                "url": f"{DEFAULT_IMAGE_BASE_URL}/seed/{uuid.uuid4().hex}/{DEFAULT_GALLERY_IMAGE_WIDTH}x{DEFAULT_GALLERY_IMAGE_HEIGHT}",
                "title": "Gallery Image 4",
                "caption": "Generated image",
            },
        ]

    # Extract description from text context
    description = ""
    if text_context and len(text_context) > 0:
        # Use snippet from first text result as description
        description = text_context[0].get("snippet", "")[:300]

    return {
        "id": widget_id,
        "type": "gallery",
        "title": "Image Gallery",
        "content": images,  # GalleryWidget expects content = array of images
        "metadata": {"description": description} if description else None,
        "timestamp": datetime.utcnow().isoformat(),
        "dismissible": True,
    }
