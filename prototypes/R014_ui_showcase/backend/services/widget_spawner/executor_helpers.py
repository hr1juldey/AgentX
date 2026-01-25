# =============================================================================
# AGENTX Widget Spawner - Executor Helpers
# =============================================================================
# Helper functions for widget executor (image/gallery generation)
# =============================================================================

import logging

from services.tools.researcher.searxng_search import SearXNGSearchModule
from services.widget_spawner.builders import build_gallery_widget, build_image_widget

logger = logging.getLogger(__name__)


def generate_image_widget(
    context: str,
    widget_id: str,
    image_search: SearXNGSearchModule,
) -> dict:
    """Generate image widget with both text and image search.

    Args:
        context: The user's query/context
        widget_id: Unique widget identifier
        image_search: SearXNG search module instance

    Returns:
        Widget data dictionary
    """
    logger.info(f"[Executor] Generating image widget for: {context[:60]}...")
    # Search for both text content and images
    text_result = image_search(query=context, search_type="general")  # type: ignore[call-arg]
    image_result = image_search(query=context, search_type="images")  # type: ignore[call-arg]
    text_list = text_result.get("url_list", [])  # type: ignore[missing-attribute]
    image_list = image_result.get("url_list", [])  # type: ignore[missing-attribute]
    return build_image_widget(
        context, widget_id, image_urls=image_list, text_context=text_list
    )


def generate_gallery_widget(
    context: str,
    widget_id: str,
    image_search: SearXNGSearchModule,
) -> dict:
    """Generate gallery widget with both text and image search.

    Args:
        context: The user's query/context
        widget_id: Unique widget identifier
        image_search: SearXNG search module instance

    Returns:
        Widget data dictionary
    """
    logger.info(f"[Executor] Generating gallery widget for: {context[:60]}...")
    # Search for both text content and images
    text_result = image_search(query=context, search_type="general")  # type: ignore[call-arg]
    image_result = image_search(query=context, search_type="images")  # type: ignore[call-arg]
    text_list = text_result.get("url_list", [])  # type: ignore[missing-attribute]
    image_list = image_result.get("url_list", [])  # type: ignore[missing-attribute]
    return build_gallery_widget(
        context, widget_id, image_urls=image_list, text_context=text_list
    )
