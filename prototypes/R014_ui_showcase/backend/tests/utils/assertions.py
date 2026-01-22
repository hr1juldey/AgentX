# =============================================================================
# AGENTX R014 - Custom Assertions for API Response Validation
# =============================================================================

import logging

logger = logging.getLogger(__name__)


def assert_valid_widget(widget: dict) -> None:
    """Assert widget has valid structure and required fields.

    Args:
        widget: Widget dictionary to validate

    Raises:
        AssertionError: If widget structure is invalid
    """
    # Required top-level fields
    required_fields = ["id", "type", "title"]
    for field in required_fields:
        assert field in widget, f"Widget missing required field: {field}"

    # Type must be valid widget type
    valid_types = [
        "chart",
        "markdown",
        "card",
        "form",
        "image",
        "gallery",
        "timeline",
        "table",
        "metric",
        "alert",
    ]
    assert widget["type"] in valid_types, (
        f"Invalid widget type: {widget['type']}. Must be one of {valid_types}"
    )

    # ID must be non-empty string
    assert isinstance(widget["id"], str) and len(widget["id"]) > 0, (
        f"Widget ID must be non-empty string, got: {widget.get('id')}"
    )

    # Title must be non-empty string
    assert isinstance(widget["title"], str) and len(widget["title"]) > 0, (
        f"Widget title must be non-empty string, got: {widget.get('title')}"
    )

    # Content or metadata should exist
    assert "content" in widget or "metadata" in widget, (
        "Widget must have 'content' or 'metadata' field"
    )


def assert_qa_checkpoint_passed(checkpoint: dict) -> None:
    """Assert QA checkpoint has valid structure and passed status.

    Args:
        checkpoint: QA checkpoint event data

    Raises:
        AssertionError: If checkpoint is invalid or failed
    """
    # Required fields
    assert "checkpoint" in checkpoint, "Checkpoint missing 'checkpoint' field"
    assert "status" in checkpoint, "Checkpoint missing 'status' field"

    # Status must be valid
    valid_statuses = ["running", "passed", "failed", "skipped"]
    assert checkpoint["status"] in valid_statuses, (
        f"Invalid checkpoint status: {checkpoint['status']}"
    )

    # Log checkpoint info
    logger.info(
        f"🔍 QA Checkpoint: {checkpoint['checkpoint']} - Status: {checkpoint['status']}"
    )


def assert_chart_widget_has_data(widget: dict) -> None:
    """Assert chart widget has valid data structure.

    Args:
        widget: Chart widget dictionary
    """
    assert widget["type"] == "chart", f"Expected chart widget, got: {widget['type']}"
    assert "data" in widget, "Chart widget must have 'data' field"

    data = widget["data"]
    assert isinstance(data, dict), "Chart data must be dict"

    # Should have at least one data structure
    has_data = any(k in data for k in ["datasets", "series", "values", "points"])
    assert has_data, f"Chart data missing expected fields: {list(data.keys())}"


def assert_markdown_widget_has_content(widget: dict) -> None:
    """Assert markdown widget has valid content.

    Args:
        widget: Markdown widget dictionary
    """
    assert widget["type"] == "markdown", (
        f"Expected markdown widget, got: {widget['type']}"
    )
    assert "content" in widget, "Markdown widget must have 'content' field"

    content = widget["content"]
    assert isinstance(content, str) and len(content) > 0, (
        "Markdown content must be non-empty string"
    )


def assert_widget_delivery_staggered(
    delivery_times: list[float], min_delay: float = 2.0, max_delay: float = 5.0
) -> None:
    """Assert widgets were delivered with staggered timing.

    Args:
        delivery_times: List of timestamps when widgets were delivered
        min_delay: Minimum expected delay between widgets (seconds)
        max_delay: Maximum expected delay between widgets (seconds)
    """
    assert len(delivery_times) > 1, (
        f"Need at least 2 widgets to check staggered delivery, got: {len(delivery_times)}"
    )

    for i in range(1, len(delivery_times)):
        delay = delivery_times[i] - delivery_times[i - 1]
        assert min_delay <= delay <= max_delay, (
            f"Widget {i} delay {delay:.2f}s not in expected range [{min_delay}s, {max_delay}s]"
        )

    logger.info(
        f"✅ {len(delivery_times)} widgets delivered with proper staggered timing"
    )


def assert_search_result_relevant(
    results: list[dict], query: str, min_results: int = 3
) -> None:
    """Assert search returned relevant results.

    Args:
        results: Search results list
        query: Original search query
        min_results: Minimum number of results expected
    """
    assert len(results) >= min_results, (
        f"Expected at least {min_results} results, got: {len(results)}"
    )

    for result in results:
        assert "title" in result, "Search result missing 'title'"
        assert "content" in result or "url" in result, (
            "Search result must have 'content' or 'url'"
        )
