"""UI tools for generating UI descriptors.

Locked from LLD: agent_runtime.md:260-346

These tools return descriptor IDs in the format {TYPE}:{uuid}.
The actual descriptor objects are created by UIService (Phase 6).

Integration with LangGraph: Use push_ui_message() from @langchain/langgraph-sdk.
"""

from typing import Dict, Any, List
from uuid import uuid4


def render_markdown_block(text: str) -> str:
    """Render a markdown text block in the UI.

    Args:
        text: Markdown content to render

    Returns:
        UI descriptor ID in format MARKDOWN_BLOCK:{uuid}
    """
    descriptor_id = str(uuid4())
    return f"MARKDOWN_BLOCK:{descriptor_id}"


def render_card(title: str, content: str, actions: List[str]) -> str:
    """Render a card widget with title, content, and action buttons.

    Args:
        title: Card title
        content: Card content (markdown supported)
        actions: List of action button labels

    Returns:
        UI descriptor ID in format CARD:{uuid}
    """
    descriptor_id = str(uuid4())
    return f"CARD:{descriptor_id}"


def request_confirmation(action_description: str, risk_level: str = "medium") -> str:
    """Request user confirmation for an action.

    Args:
        action_description: Description of action to confirm
        risk_level: Risk level (low, medium, high)

    Returns:
        UI descriptor ID in format CONFIRMATION:{uuid}
    """
    descriptor_id = str(uuid4())
    return f"CONFIRMATION:{descriptor_id}"


def update_progress(task_name: str, progress_percent: int) -> str:
    """Update a progress indicator for a long-running task.

    Args:
        task_name: Name of the task being tracked
        progress_percent: Progress percentage (0-100)

    Returns:
        UI descriptor ID in format PROGRESS:{uuid}
    """
    descriptor_id = str(uuid4())
    return f"PROGRESS:{descriptor_id}"


def show_form(form_schema: Dict[str, Any]) -> str:
    """Render a form for user input.

    Args:
        form_schema: Form schema with field definitions

    Returns:
        UI descriptor ID in format FORM:{uuid}
    """
    descriptor_id = str(uuid4())
    return f"FORM:{descriptor_id}"


def show_image(image_url: str, caption: str = "") -> str:
    """Render an image with optional caption.

    Args:
        image_url: URL of the image to display
        caption: Optional image caption

    Returns:
        UI descriptor ID in format IMAGE:{uuid}
    """
    descriptor_id = str(uuid4())
    return f"IMAGE:{descriptor_id}"


def show_gallery(images: List[Dict[str, str]]) -> str:
    """Render a gallery of multiple images.

    Args:
        images: List of image dicts with 'url' and 'caption' keys

    Returns:
        UI descriptor ID in format GALLERY:{uuid}
    """
    descriptor_id = str(uuid4())
    return f"GALLERY:{descriptor_id}"


def show_chart(chart_data: Dict[str, Any]) -> str:
    """Render a data visualization chart.

    Args:
        chart_data: Chart configuration (type, data, options)

    Returns:
        UI descriptor ID in format CHART:{uuid}
    """
    descriptor_id = str(uuid4())
    return f"CHART:{descriptor_id}"
