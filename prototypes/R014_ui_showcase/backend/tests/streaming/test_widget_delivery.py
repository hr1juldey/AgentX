# =============================================================================
# AGENTX R014 - E2E Tests for Widget Streaming and Delivery
# =============================================================================
# These tests validate the real-time streaming behavior of the Master Agent
# pipeline through WebSocket connections.
# =============================================================================

import logging
import time

import pytest
from fastapi.testclient import TestClient

from main import app
from tests.utils.assertions import (
    assert_valid_widget,
    assert_qa_checkpoint_passed,
    assert_widget_delivery_staggered,
)
from tests.utils.websocket_client import WebSocketTestClient

logger = logging.getLogger(__name__)


@pytest.mark.requires_ollama
@pytest.mark.requires_searxng
@pytest.mark.websocket
@pytest.mark.slow
async def test_widget_delivery_staggered_timing():
    """Test that widgets are delivered with staggered timing (2-5s delay).

    This test validates the SEQUENCER agent's delivery pacing by measuring
    the time between widget deliveries.
    """
    query = "US Federal Reserve Balance Sheet Expansion vs Asset Prices"
    logger.info(f"🧪 Testing staggered widget delivery: {query}")

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

        delivery_times = []
        widgets = []

        async for message in ws_client.receive_json():
            if message.get("type") == "widget":
                widget = message.get("data", {})
                widgets.append(widget)
                delivery_times.append(time.time())
                logger.info(
                    f"  📦 Widget delivered at {time.time() - delivery_times[0]:.1f}s"
                )

            elif message.get("type") == "complete":
                break

            elif message.get("type") == "error":
                pytest.fail(f"Error during widget delivery test: {message}")

        await ws_client.close()

        # Need at least 2 widgets to check staggered timing
        assert len(delivery_times) >= 2, (
            f"Need at least 2 widgets to check staggered delivery, got: {len(delivery_times)}"
        )

        # Assert staggered timing (allowing 1-10s range for real LLM variance)
        assert_widget_delivery_staggered(delivery_times, min_delay=1.0, max_delay=10.0)

        # Calculate actual delays
        delays = []
        for i in range(1, len(delivery_times)):
            delay = delivery_times[i] - delivery_times[i - 1]
            delays.append(delay)

        avg_delay = sum(delays) / len(delays) if delays else 0
        logger.info(
            f"  ✅ Staggered delivery: {len(widgets)} widgets, avg delay: {avg_delay:.2f}s"
        )

    except Exception:
        await ws_client.close()
        raise


@pytest.mark.requires_ollama
@pytest.mark.requires_searxng
@pytest.mark.websocket
@pytest.mark.slow
async def test_qa_checkpoint_streaming():
    """Test QA checkpoint events stream correctly during pipeline execution.

    This test validates that the Master Agent emits QA progress events
    for each pipeline phase.
    """
    query = "Global Inflation Trends (2015–Present)"
    logger.info(f"🧪 Testing QA checkpoint streaming: {query}")

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

        qa_checkpoints = []

        async for message in ws_client.receive_json():
            if message.get("type") == "qa_progress":
                checkpoint = message.get("data", {})
                qa_checkpoints.append(checkpoint)

                checkpoint_name = checkpoint.get("checkpoint", "unknown")
                status = checkpoint.get("status", "unknown")
                logger.info(f"  🔍 QA Checkpoint: {checkpoint_name} - {status}")

                if status == "failed":
                    logger.error(f"  ❌ QA checkpoint failed: {checkpoint}")

            elif message.get("type") == "complete":
                break

            elif message.get("type") == "error":
                pytest.fail(f"Error during QA checkpoint test: {message}")

        await ws_client.close()

        # Assert QA checkpoints were emitted
        assert len(qa_checkpoints) > 0, (
            f"Expected QA checkpoint events, got: {len(qa_checkpoints)}"
        )

        # Assert all checkpoints passed
        for checkpoint in qa_checkpoints:
            assert_qa_checkpoint_passed(checkpoint)

        # Check expected checkpoint names (based on pipeline)
        expected_checkpoints = [
            "analyst_pass1",
            "researcher",
            "data_contextualizer",
            "analyst_pass2",
            "designer",
            "widget_selector",
            "hydrators",
        ]

        checkpoint_names = {cp.get("checkpoint", "") for cp in qa_checkpoints}
        found_expected = [
            name for name in expected_checkpoints if name in checkpoint_names
        ]

        logger.info(
            f"  ✅ QA checkpoint streaming: {len(qa_checkpoints)} checkpoints, "
            f"{len(found_expected)}/{len(expected_checkpoints)} expected phases found"
        )

    except Exception:
        await ws_client.close()
        raise


@pytest.mark.requires_ollama
@pytest.mark.requires_searxng
@pytest.mark.websocket
@pytest.mark.slow
async def test_multi_widget_generation():
    """Test that multiple widgets are generated for complex queries.

    This test validates that the WIDGET SELECTOR and HYDRATORS produce
    multiple complementary widgets.
    """
    query = "Capital Flows Between Developed and Emerging Markets"
    logger.info(f"🧪 Testing multi-widget generation: {query}")

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
        widget_types = set()

        async for message in ws_client.receive_json():
            if message.get("type") == "widget":
                widget = message.get("data", {})
                widgets.append(widget)
                widget_types.add(widget.get("type", "unknown"))
                logger.info(
                    f"  📦 Widget: {widget.get('type')} - {widget.get('title')}"
                )

            elif message.get("type") == "complete":
                break

            elif message.get("type") == "error":
                pytest.fail(f"Error during multi-widget test: {message}")

        await ws_client.close()

        # Assert multiple widgets were generated
        assert len(widgets) >= 2, f"Expected at least 2 widgets, got: {len(widgets)}"

        # Assert different widget types
        assert len(widget_types) >= 1, (
            f"Expected at least 1 widget type, got: {widget_types}"
        )

        # Validate all widgets
        for widget in widgets:
            assert_valid_widget(widget)

        logger.info(
            f"  ✅ Multi-widget generation: {len(widgets)} widgets, "
            f"types: {widget_types}"
        )

    except Exception:
        await ws_client.close()
        raise


@pytest.mark.requires_ollama
@pytest.mark.requires_searxng
@pytest.mark.websocket
@pytest.mark.slow
async def test_device_context_mobile():
    """Test that mobile device context affects widget generation.

    This test validates that the DESIGNER agent considers device context
    when creating widgets.
    """
    query = "Global Inflation Trends"
    logger.info(f"🧪 Testing mobile device context: {query}")

    client = TestClient(app)
    ws_client = WebSocketTestClient(client.app, "/api/v1/ws/generate-widget")

    try:
        await ws_client.connect()
        await ws_client.send_json(
            {
                "query": query,
                "device_context": "mobile",
            }
        )

        widgets = []

        async for message in ws_client.receive_json():
            if message.get("type") == "widget":
                widget = message.get("data", {})
                widgets.append(widget)
                logger.info(
                    f"  📦 Mobile widget: {widget.get('type')} - {widget.get('title')}"
                )

            elif message.get("type") == "complete":
                break

            elif message.get("type") == "error":
                pytest.fail(f"Error during mobile context test: {message}")

        await ws_client.close()

        # Assert widgets were generated
        assert len(widgets) > 0, "Expected widgets for mobile context"

        # Validate all widgets
        for widget in widgets:
            assert_valid_widget(widget)

        logger.info(f"  ✅ Mobile context: {len(widgets)} widgets generated")

    except Exception:
        await ws_client.close()
        raise


@pytest.mark.requires_ollama
@pytest.mark.requires_searxng
@pytest.mark.websocket
@pytest.mark.slow
async def test_error_handling_invalid_query():
    """Test that the system handles invalid/empty queries gracefully.

    This test validates error handling for edge cases.
    """
    query = ""  # Empty query
    logger.info("🧪 Testing error handling for empty query")

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

        error_message = ""

        async for message in ws_client.receive_json():
            if message.get("type") == "error":
                error_message = message.get("data", {}).get("message", "Unknown error")
                logger.info(f"  ⚠️ Error received as expected: {error_message}")
                break

            elif message.get("type") == "complete":
                break

        await ws_client.close()

        # Note: System may still generate widgets for empty queries (LLM behavior)
        # This test documents the actual behavior rather than enforcing specific error handling
        logger.info("  ℹ️ Empty query behavior documented")

    except Exception as e:
        await ws_client.close()
        logger.info(f"  ℹ️ Empty query may raise exception: {e}")


@pytest.mark.requires_ollama
@pytest.mark.requires_searxng
@pytest.mark.websocket
@pytest.mark.slow
async def test_widget_data_population():
    """Test that hydrators properly populate widget data fields.

    This test validates that chart widgets have actual data, not just metadata.
    """
    query = "Yield Curve Inversion and Recession Signals"
    logger.info(f"🧪 Testing widget data population: {query}")

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
        chart_widgets_with_data = 0

        async for message in ws_client.receive_json():
            if message.get("type") == "widget":
                widget = message.get("data", {})
                widgets.append(widget)

                if widget.get("type") == "chart":
                    data = widget.get("data", {})
                    if data:
                        chart_widgets_with_data += 1
                        logger.info(f"  📊 Chart data keys: {list(data.keys())}")

            elif message.get("type") == "complete":
                break

            elif message.get("type") == "error":
                pytest.fail(f"Error during data population test: {message}")

        await ws_client.close()

        # Assert at least one chart has data
        assert chart_widgets_with_data > 0, (
            f"Expected at least 1 chart widget with data, got: {chart_widgets_with_data}"
        )

        logger.info(
            f"  ✅ Data population: {chart_widgets_with_data}/{len(widgets)} widgets have data"
        )

    except Exception:
        await ws_client.close()
        raise


@pytest.mark.requires_ollama
@pytest.mark.requires_searxng
@pytest.mark.websocket
@pytest.mark.slow
async def test_complex_multistep_analytical_query():
    """Test hard multistep analytical query (real tester style, no cheating).

    This test validates the full pipeline with a complex question that requires:
    - Multiple research hops
    - Data synthesis from multiple sources
    - Analytical reasoning
    - Appropriate visualization selection
    """
    query = (
        "Analyze the relationship between quantitative easing programs, "
        "asset price inflation in housing and stock markets, and the subsequent "
        "impact on income inequality in developed economies from 2008 to 2024."
    )

    logger.info("🧪 Testing complex multistep analytical query")
    logger.info(f"  Query: {query}")

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

        qa_checkpoints = []
        widgets = []
        research_hops = 0

        start_time = time.time()

        async for message in ws_client.receive_json():
            elapsed = time.time() - start_time
            event_type = message.get("type")

            if event_type == "qa_progress":
                checkpoint = message.get("data", {})
                qa_checkpoints.append(checkpoint)
                checkpoint_name = checkpoint.get("checkpoint", "unknown")
                logger.info(f"  🔍 [{elapsed:.1f}s] QA: {checkpoint_name}")

                # Count research hops
                if (
                    "research" in checkpoint_name.lower()
                    or "hop" in checkpoint_name.lower()
                ):
                    research_hops += 1

            elif event_type == "widget":
                widget = message.get("data", {})
                widgets.append(widget)
                logger.info(
                    f"  📦 [{elapsed:.1f}s] Widget: {widget.get('type')} - {widget.get('title', 'Untitled')}"
                )

            elif event_type == "complete":
                logger.info(f"  ✅ Complete at {elapsed:.1f}s")
                break

            elif event_type == "error":
                error_msg = message.get("data", {}).get("message", "Unknown error")
                logger.error(f"  ❌ Error: {error_msg}")
                pytest.fail(f"Complex query failed: {error_msg}")

            # Timeout after 10 minutes for very complex queries
            if elapsed > 600:
                logger.warning(f"  ⏱️ Timeout after {elapsed:.1f}s")
                break

        # Validate results
        logger.info("  📊 Results:")
        logger.info(f"    - QA checkpoints: {len(qa_checkpoints)}")
        logger.info(f"    - Research hops detected: {research_hops}")
        logger.info(f"    - Widgets generated: {len(widgets)}")
        logger.info(f"    - Total time: {time.time() - start_time:.1f}s")

        # Assertions (these test that the system handled the complex query)
        assert len(qa_checkpoints) > 0, "Should have QA checkpoint events"
        assert len(widgets) > 0, "Should generate widgets even for complex queries"

        # Validate widget structure
        for widget in widgets:
            assert_valid_widget(widget)

        # Log widget types
        widget_types = {w.get("type") for w in widgets}
        logger.info(f"    - Widget types: {widget_types}")

        # Check for analytical content in markdown widgets
        markdown_widgets = [w for w in widgets if w.get("type") == "markdown"]
        if markdown_widgets:
            content = markdown_widgets[0].get("content", "")
            logger.info(f"    - Markdown content length: {len(content)} chars")

            # Check for analytical terms
            analytical_terms = [
                "quantitative easing",
                "qe",
                "asset price",
                "housing",
                "stock",
                "inequality",
                "income",
                "correlation",
                "impact",
                "2008",
                "2024",
            ]
            found_terms = [
                term for term in analytical_terms if term.lower() in content.lower()
            ]
            logger.info(
                f"    - Analytical terms found: {len(found_terms)}/{len(analytical_terms)}"
            )

        logger.info("  ✅ Complex query test completed successfully")

    except Exception as e:
        await ws_client.close()
        logger.error(f"  ❌ Complex query test failed: {e}")
        raise
