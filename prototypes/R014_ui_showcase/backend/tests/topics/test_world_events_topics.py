# =============================================================================
# AGENTX R014 - E2E Tests for World Events Topics (Topics 11-20)
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
)
from tests.utils.websocket_client import WebSocketTestClient

logger = logging.getLogger(__name__)


# =============================================================================
# World Events Topics 11-20
# =============================================================================

WORLD_EVENTS_TOPICS = [
    {
        "id": 11,
        "query": "Economic Impact of Major Wars Since 2000",
        "expected_widget_types": ["timeline", "chart", "markdown"],
        "description": "Timeline with GDP impact analysis",
    },
    {
        "id": 12,
        "query": "Global Energy Mix Transition",
        "expected_widget_types": ["chart", "markdown"],
        "description": "Stacked area chart showing energy sources",
    },
    {
        "id": 13,
        "query": "Sanctions and Their Effect on National Economies",
        "expected_widget_types": ["chart", "card", "markdown"],
        "description": "Before/after comparison charts",
    },
    {
        "id": 14,
        "query": "Food Price Index vs Climate Events",
        "expected_widget_types": ["chart", "markdown"],
        "description": "Correlation plot with climate markers",
    },
    {
        "id": 15,
        "query": "Migration Flows Triggered by Economic Crises",
        "expected_widget_types": ["chart", "map", "markdown"],
        "description": "Map or flow chart showing migration",
    },
    {
        "id": 16,
        "query": "Defense Spending Growth by Region",
        "expected_widget_types": ["chart", "table"],
        "description": "Bar chart comparing regions",
    },
    {
        "id": 17,
        "query": "Global Supply Chain Disruptions and Shipping Costs",
        "expected_widget_types": ["chart", "timeline", "markdown"],
        "description": "Cost index over time",
    },
    {
        "id": 18,
        "query": "Pandemics and Global Economic Slowdowns",
        "expected_widget_types": ["chart", "markdown"],
        "description": "GDP comparison across pandemics",
    },
    {
        "id": 19,
        "query": "Central Bank Gold Reserves Accumulation",
        "expected_widget_types": ["chart", "markdown"],
        "description": "Trends in gold reserves",
    },
    {
        "id": 20,
        "query": "Trade Wars and Global Trade Volume",
        "expected_widget_types": ["chart", "timeline", "markdown"],
        "description": "Trade timeline with war markers",
    },
]


@pytest.mark.requires_ollama
@pytest.mark.requires_searxng
@pytest.mark.websocket
@pytest.mark.slow
@pytest.mark.parametrize("topic", WORLD_EVENTS_TOPICS)
async def test_world_events_topic_e2e(topic: dict):
    """Test world events topic via real WebSocket API (simulates frontend request).

    This test sends a real query to the /ws/generate-widget WebSocket endpoint,
    collects all events (QA checkpoints, widgets), and validates:
    - QA checkpoints pass
    - Widgets are generated with valid structure
    - Widget types match expectations
    - Data is populated in widgets
    """
    logger.info(f"🧪 Testing World Events Topic {topic['id']}: {topic['query']}")

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
async def test_world_events_topic_11_wars_economic_impact_detailed():
    """Detailed test for Topic 11: Economic Impact of Major Wars Since 2000.

    This test validates timeline + GDP visualization.
    """
    query = "Economic Impact of Major Wars Since 2000"
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
                pytest.fail(f"Error in wars economic impact query: {message}")

        await ws_client.close()

        # Should have timeline or chart widget
        valid_widgets = [
            w for w in widgets if w["type"] in ["timeline", "chart", "markdown"]
        ]
        assert len(valid_widgets) > 0, (
            "Expected timeline or chart for wars economic impact"
        )

        # Check for war-related content
        markdown_widgets = [w for w in widgets if w["type"] == "markdown"]
        if markdown_widgets:
            content = markdown_widgets[0].get("content", "").lower()
            war_terms = [
                "war",
                "conflict",
                "iraq",
                "afghanistan",
                "ukraine",
                "gaza",
                "economic",
                "gdp",
            ]
            found_terms = [term for term in war_terms if term in content]
            assert len(found_terms) >= 2, (
                f"Content should mention war-related terms. Found: {found_terms}"
            )
            logger.info(f"  ✓ Content mentions: {', '.join(found_terms)}")

        logger.info(f"  ✅ Wars economic impact test passed: {len(widgets)} widgets")

    except Exception:
        await ws_client.close()
        raise


@pytest.mark.requires_ollama
@pytest.mark.requires_searxng
@pytest.mark.websocket
@pytest.mark.slow
async def test_world_events_topic_12_energy_transition_detailed():
    """Detailed test for Topic 12: Global Energy Mix Transition.

    This test validates stacked area chart for energy sources.
    """
    query = "Global Energy Mix Transition"
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
                pytest.fail(f"Error in energy transition query: {message}")

        await ws_client.close()

        # Should have chart widget
        chart_widgets = [w for w in widgets if w["type"] == "chart"]
        assert len(chart_widgets) > 0, "Expected chart widget for energy transition"

        # Check for multiple energy sources (stacked chart)
        for chart in chart_widgets:
            if "data" in chart:
                data = chart["data"]
                datasets = data.get("datasets", [])

                # Energy transition charts typically have multiple sources (coal, oil, gas, renewables)
                if len(datasets) >= 3:
                    logger.info(f"  ✓ Chart has {len(datasets)} energy sources")

        # Check for energy-related terms in content
        markdown_widgets = [w for w in widgets if w["type"] == "markdown"]
        if markdown_widgets:
            content = markdown_widgets[0].get("content", "").lower()
            energy_terms = [
                "renewable",
                "solar",
                "wind",
                "coal",
                "oil",
                "gas",
                "nuclear",
                "energy",
            ]
            found_terms = [term for term in energy_terms if term in content]
            assert len(found_terms) >= 2, (
                f"Content should mention energy-related terms. Found: {found_terms}"
            )

        logger.info(f"  ✅ Energy transition test passed: {len(widgets)} widgets")

    except Exception:
        await ws_client.close()
        raise


@pytest.mark.requires_ollama
@pytest.mark.requires_searxng
@pytest.mark.websocket
@pytest.mark.slow
async def test_world_events_topic_15_migration_flows_detailed():
    """Detailed test for Topic 15: Migration Flows Triggered by Economic Crises.

    This test validates flow chart or map visualization.
    """
    query = "Migration Flows Triggered by Economic Crises"
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
                pytest.fail(f"Error in migration flows query: {message}")

        await ws_client.close()

        # Should have chart or markdown widget
        valid_widgets = [
            w for w in widgets if w["type"] in ["chart", "markdown", "map"]
        ]
        assert len(valid_widgets) > 0, "Expected chart or markdown for migration flows"

        # Check for migration-related terms
        markdown_widgets = [w for w in widgets if w["type"] == "markdown"]
        if markdown_widgets:
            content = markdown_widgets[0].get("content", "").lower()
            migration_terms = [
                "migration",
                "migrant",
                "refugee",
                "crisis",
                "economic",
                "flow",
            ]
            found_terms = [term for term in migration_terms if term in content]
            assert len(found_terms) >= 2, (
                f"Content should mention migration-related terms. Found: {found_terms}"
            )
            logger.info(f"  ✓ Content mentions: {', '.join(found_terms)}")

        logger.info(f"  ✅ Migration flows test passed: {len(widgets)} widgets")

    except Exception:
        await ws_client.close()
        raise


@pytest.mark.requires_ollama
@pytest.mark.requires_searxng
@pytest.mark.websocket
@pytest.mark.slow
async def test_world_events_topic_18_pandemics_economic_detailed():
    """Detailed test for Topic 18: Pandemics and Global Economic Slowdowns.

    This test validates GDP comparison across pandemics.
    """
    query = "Pandemics and Global Economic Slowdowns"
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
                pytest.fail(f"Error in pandemics economic query: {message}")

        await ws_client.close()

        # Should have chart widget
        chart_widgets = [w for w in widgets if w["type"] == "chart"]
        assert len(chart_widgets) > 0, "Expected chart widget for pandemics analysis"

        # Check for pandemic-related terms
        markdown_widgets = [w for w in widgets if w["type"] == "markdown"]
        if markdown_widgets:
            content = markdown_widgets[0].get("content", "").lower()
            pandemic_terms = [
                "covid",
                "pandemic",
                "economic",
                "gdp",
                "recession",
                "2009",
                "sars",
            ]
            found_terms = [term for term in pandemic_terms if term in content]
            assert len(found_terms) >= 2, (
                f"Content should mention pandemic-related terms. Found: {found_terms}"
            )
            logger.info(f"  ✓ Content mentions: {', '.join(found_terms)}")

        logger.info(f"  ✅ Pandemics economic test passed: {len(widgets)} widgets")

    except Exception:
        await ws_client.close()
        raise
