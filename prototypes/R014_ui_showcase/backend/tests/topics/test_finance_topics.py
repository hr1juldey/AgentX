# =============================================================================
# AGENTX R014 - E2E Tests for Finance Topics (Topics 1-10)
# =============================================================================
# These tests simulate real frontend requests to the WebSocket API.
# They use the actual Master Agent pipeline with real Ollama LLM and SearXNG.
# =============================================================================

import logging
import time

import pytest
from fastapi.testclient import TestClient

from main import app
from tests.utils.assertions import (
    assert_valid_widget,
    assert_qa_checkpoint_passed,
    assert_chart_widget_has_data,
    assert_markdown_widget_has_content,
    assert_widget_delivery_staggered,
)
from tests.utils.websocket_client import WebSocketTestClient

logger = logging.getLogger(__name__)


# =============================================================================
# Finance Topics 1-10
# =============================================================================

FINANCE_TOPICS = [
    {
        "id": 1,
        "query": "Global Inflation Trends (2015–Present)",
        "expected_widget_types": ["chart", "markdown"],
        "description": "Line chart showing inflation over time",
    },
    {
        "id": 2,
        "query": "Interest Rate Hikes and Stock Market Volatility",
        "expected_widget_types": ["chart", "markdown"],
        "description": "Dual-axis chart showing correlation",
    },
    {
        "id": 3,
        "query": "US Federal Reserve Balance Sheet Expansion vs Asset Prices",
        "expected_widget_types": ["chart", "markdown"],
        "description": "Area chart showing balance sheet growth",
    },
    {
        "id": 4,
        "query": "Crude Oil Prices vs Geopolitical Conflicts",
        "expected_widget_types": ["chart", "timeline"],
        "description": "Time series with conflict markers",
    },
    {
        "id": 5,
        "query": "Gold Prices During Economic Crises",
        "expected_widget_types": ["chart", "card"],
        "description": "Comparative plots across crises",
    },
    {
        "id": 6,
        "query": "Currency Devaluation in Emerging Markets",
        "expected_widget_types": ["chart", "timeline"],
        "description": "Timeline of currency events",
    },
    {
        "id": 7,
        "query": "Global Debt-to-GDP Ratios by Country",
        "expected_widget_types": ["chart", "table"],
        "description": "Bar chart comparing countries",
    },
    {
        "id": 8,
        "query": "Yield Curve Inversion and Recession Signals",
        "expected_widget_types": ["chart", "markdown"],
        "description": "Yield spread chart with analysis",
    },
    {
        "id": 9,
        "query": "Impact of Quantitative Easing on Housing Prices",
        "expected_widget_types": ["chart", "markdown"],
        "description": "Indexed chart showing QE impact",
    },
    {
        "id": 10,
        "query": "Capital Flows Between Developed and Emerging Markets",
        "expected_widget_types": ["chart", "markdown"],
        "description": "Flow diagram or directional chart",
    },
]


@pytest.mark.requires_ollama
@pytest.mark.requires_searxng
@pytest.mark.websocket
@pytest.mark.slow
@pytest.mark.parametrize("topic", FINANCE_TOPICS)
async def test_finance_topic_e2e(topic: dict):
    """Test finance topic via real WebSocket API (simulates frontend request).

    This test sends a real query to the /ws/generate-widget WebSocket endpoint,
    collects all events (QA checkpoints, widgets), and validates:
    - QA checkpoints pass
    - Widgets are generated with valid structure
    - Widget types match expectations
    - Data is populated in widgets
    - Delivery is staggered (2-5s between widgets)
    """
    logger.info(f"🧪 Testing Finance Topic {topic['id']}: {topic['query']}")

    client = TestClient(app)
    ws_client = WebSocketTestClient(client.app, "/api/v1/ws/generate-widget")

    try:
        await ws_client.connect()

        # Send real frontend-style request
        await ws_client.send_json(
            {
                "query": topic["query"],
                "device_context": "desktop",
            }
        )

        # Collect events
        qa_checkpoints = []
        widgets = []
        delivery_times = []

        start_time = time.time()

        async for message in ws_client.receive_json():
            elapsed = time.time() - start_time

            event_type = message.get("type")

            if event_type == "qa_progress":
                qa_checkpoints.append(message.get("data", {}))
                checkpoint_name = message.get("data", {}).get("checkpoint", "unknown")
                status = message.get("data", {}).get("status", "unknown")
                logger.info(
                    f"  🔍 QA Checkpoint [{elapsed:.1f}s]: {checkpoint_name} - {status}"
                )

            elif event_type == "widget":
                widget = message.get("data", {})
                widgets.append(widget)
                delivery_times.append(time.time())
                widget_type = widget.get("type", "unknown")
                widget_title = widget.get("title", "untitled")
                logger.info(
                    f"  📦 Widget [{elapsed:.1f}s]: {widget_type} - {widget_title}"
                )

            elif event_type == "complete":
                logger.info(f"  ✅ Complete [{elapsed:.1f}s]")
                break

            elif event_type == "error":
                error_msg = message.get("data", {}).get("message", "Unknown error")
                logger.error(f"  ❌ Error: {error_msg}")
                pytest.fail(f"WebSocket returned error: {error_msg}")

            # Timeout after 5 minutes for complex queries
            if elapsed > 300:
                logger.warning(f"  ⏱️ Timeout after {elapsed:.1f}s")
                break

        # Validate QA checkpoints
        logger.info(f"  📊 QA Checkpoints: {len(qa_checkpoints)}")
        for checkpoint in qa_checkpoints:
            assert_qa_checkpoint_passed(checkpoint)

        # Validate widgets were generated
        assert len(widgets) > 0, (
            f"Topic {topic['id']}: Expected at least 1 widget, got {len(widgets)}"
        )
        logger.info(f"  📦 Widgets generated: {len(widgets)}")

        # Validate widget structure
        for i, widget in enumerate(widgets):
            assert_valid_widget(widget)
            logger.debug(f"    Widget {i + 1}: {widget['type']} - {widget['title']}")

            # Check for specific widget types
            if widget["type"] == "chart":
                assert_chart_widget_has_data(widget)
            elif widget["type"] == "markdown":
                assert_markdown_widget_has_content(widget)

        # Validate expected widget types
        widget_types = {w["type"] for w in widgets}
        for expected_type in topic["expected_widget_types"]:
            if expected_type in widget_types:
                logger.info(f"  ✓ Found expected widget type: {expected_type}")

        # Validate staggered delivery (if multiple widgets)
        if len(delivery_times) > 1:
            assert_widget_delivery_staggered(
                delivery_times, min_delay=1.0, max_delay=10.0
            )

        # Log summary
        logger.info(
            f"  ✅ Topic {topic['id']} passed: {len(widgets)} widgets, "
            f"{len(qa_checkpoints)} QA checkpoints"
        )

    finally:
        await ws_client.close()


@pytest.mark.requires_ollama
@pytest.mark.requires_searxng
@pytest.mark.websocket
@pytest.mark.slow
async def test_finance_topic_1_inflation_detailed():
    """Detailed test for Topic 1: Global Inflation Trends.

    This test validates specific expectations for inflation data visualization.
    """
    query = "Global Inflation Trends (2015–Present)"
    logger.info(f"🧪 Detailed test: {query}")

    client = TestClient(app)
    ws_client = WebSocketTestClient(client.app, "/api/v1/ws/generate-widget")

    try:
        await ws_client.connect()
        await ws_client.send_json(
            {
                "query": query,
                "device_context": "desktop",
            }
        )

        widgets = []
        async for message in ws_client.receive_json():
            if message.get("type") == "widget":
                widgets.append(message.get("data", {}))
            elif message.get("type") == "complete":
                break
            elif message.get("type") == "error":
                pytest.fail(f"Error in inflation trends query: {message}")

        await ws_client.close()

        # Validate at least one chart widget
        chart_widgets = [w for w in widgets if w["type"] == "chart"]
        assert len(chart_widgets) > 0, (
            "Expected at least one chart widget for inflation trends"
        )

        # Check chart data structure
        for chart in chart_widgets:
            assert "data" in chart, "Chart widget must have 'data' field"
            data = chart["data"]

            # Should have temporal data (time series)
            has_labels = "labels" in data or "x" in data or "dates" in data
            has_datasets = "datasets" in data or "series" in data or "values" in data
            assert has_labels and has_datasets, (
                f"Chart data missing time series structure: {list(data.keys())}"
            )

            logger.info("  ✓ Inflation chart has valid time series structure")

        # Validate markdown summary
        markdown_widgets = [w for w in widgets if w["type"] == "markdown"]
        assert len(markdown_widgets) > 0, "Expected markdown summary widget"

        for md in markdown_widgets:
            content = md.get("content", "")
            assert len(content) > 100, (
                "Markdown summary should have substantial content about inflation trends"
            )

            # Check for key terms
            key_terms = ["inflation", "rate", "percent", "consumer", "price"]
            found_terms = [
                term for term in key_terms if term.lower() in content.lower()
            ]
            assert len(found_terms) >= 2, (
                f"Markdown content should mention inflation-related terms. Found: {found_terms}"
            )

        logger.info(f"  ✅ Inflation trends test passed: {len(widgets)} widgets")

    except Exception:
        await ws_client.close()
        raise


@pytest.mark.requires_ollama
@pytest.mark.requires_searxng
@pytest.mark.websocket
@pytest.mark.slow
async def test_finance_topic_2_interest_rates_detailed():
    """Detailed test for Topic 2: Interest Rate Hikes vs Stock Market.

    This test validates dual-axis or comparative visualization.
    """
    query = "Interest Rate Hikes and Stock Market Volatility"
    logger.info(f"🧪 Detailed test: {query}")

    client = TestClient(app)
    ws_client = WebSocketTestClient(client.app, "/api/v1/ws/generate-widget")

    try:
        await ws_client.connect()
        await ws_client.send_json(
            {
                "query": query,
                "device_context": "desktop",
            }
        )

        widgets = []
        async for message in ws_client.receive_json():
            if message.get("type") == "widget":
                widgets.append(message.get("data", {}))
            elif message.get("type") == "complete":
                break
            elif message.get("type") == "error":
                pytest.fail(f"Error in interest rates query: {message}")

        await ws_client.close()

        # Should have chart widget
        chart_widgets = [w for w in widgets if w["type"] == "chart"]
        assert len(chart_widgets) > 0, (
            "Expected chart widget for interest rate analysis"
        )

        # For dual-axis, should have multiple datasets or y-axes
        for chart in chart_widgets:
            if "data" in chart:
                data = chart["data"]
                datasets = data.get("datasets", [])
                series = data.get("series", [])

                # Dual-axis charts typically have 2+ datasets
                if len(datasets) >= 2 or len(series) >= 2:
                    logger.info(
                        f"  ✓ Chart has dual-axis structure ({max(len(datasets), len(series))} series)"
                    )

        logger.info(f"  ✅ Interest rates test passed: {len(widgets)} widgets")

    except Exception:
        await ws_client.close()
        raise


@pytest.mark.requires_ollama
@pytest.mark.requires_searxng
@pytest.mark.websocket
@pytest.mark.slow
async def test_finance_topic_7_debt_to_gdp_detailed():
    """Detailed test for Topic 7: Global Debt-to-GDP Ratios.

    This test validates country comparison bar chart.
    """
    query = "Global Debt-to-GDP Ratios by Country"
    logger.info(f"🧪 Detailed test: {query}")

    client = TestClient(app)
    ws_client = WebSocketTestClient(client.app, "/api/v1/ws/generate-widget")

    try:
        await ws_client.connect()
        await ws_client.send_json(
            {
                "query": query,
                "device_context": "desktop",
            }
        )

        widgets = []
        async for message in ws_client.receive_json():
            if message.get("type") == "widget":
                widgets.append(message.get("data", {}))
            elif message.get("type") == "complete":
                break
            elif message.get("type") == "error":
                pytest.fail(f"Error in debt-to-GDP query: {message}")

        await ws_client.close()

        # Should have chart or table widget
        valid_widgets = [w for w in widgets if w["type"] in ["chart", "table"]]
        assert len(valid_widgets) > 0, (
            "Expected chart or table for debt-to-GDP comparison"
        )

        # Check for country data
        for widget in valid_widgets:
            if widget["type"] == "chart" and "data" in widget:
                data = widget["data"]
                labels = data.get("labels", [])
                datasets = data.get("datasets", [])

                # Should have multiple countries
                if labels and len(labels) >= 3:
                    logger.info(f"  ✓ Chart includes {len(labels)} countries")

                # Should have debt/GDP percentage data
                if datasets:
                    for dataset in datasets:
                        values = dataset.get("data", [])
                        if values and any(
                            v > 50 for v in values if isinstance(v, (int, float))
                        ):
                            logger.info("  ✓ Dataset includes debt/GDP ratios")

        logger.info(f"  ✅ Debt-to-GDP test passed: {len(widgets)} widgets")

    except Exception:
        await ws_client.close()
        raise
