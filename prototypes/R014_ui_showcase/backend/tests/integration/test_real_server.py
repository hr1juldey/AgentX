# =============================================================================
# AGENTX R014 - Integration Tests against Real Server on Port 8014
# =============================================================================
# These tests make real HTTP/WebSocket calls to the running server.
# Ensure the backend is running: python main.py (port 8014)
# =============================================================================

import json
import logging
import time

import httpx
import pytest
import websockets

logger = logging.getLogger(__name__)

# Real server URL
BASE_URL = "http://localhost:8014"
WS_BASE_URL = "ws://localhost:8014"


@pytest.mark.requires_real_server
async def test_real_server_health():
    """Test the real server health endpoint."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/v1/health", timeout=10.0)
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        logger.info(f"✅ Real server health check: {data}")


@pytest.mark.requires_real_server
async def test_real_server_mock_generate():
    """Test the real /mock/generate endpoint."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/v1/mock/generate",
            json={"widget_type": "markdown", "prompt": "Test prompt"},
            timeout=60.0,
        )

        assert response.status_code == 200
        data = response.json()

        assert "id" in data
        assert data["type"] == "markdown"
        logger.info(f"✅ Mock generate result: {data.get('id')}")


@pytest.mark.requires_real_server
@pytest.mark.requires_ollama
async def test_real_server_generate_widget():
    """Test the real /generate-widget endpoint."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/v1/generate-widget",
            json={"prompt": "Show me a chart of stock prices"},
            timeout=180.0,
        )

        assert response.status_code == 200
        data = response.json()

        assert "widgets" in data
        assert isinstance(data["widgets"], list)
        logger.info(f"✅ Generate widget: {len(data['widgets'])} widgets")


@pytest.mark.requires_real_server
@pytest.mark.requires_ollama
@pytest.mark.requires_searxng
async def test_real_server_search():
    """Test the real /search endpoint.

    NOTE: Multi-hop search can take 5-10 minutes with qwen3:8b model.
    Each hop involves multiple LLM calls (plan, answer, reflect).
    5 hops × ~40-60 seconds per hop = 3-5+ minutes total.
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/v1/search",
            json={"query": "What is the current stock market trend?"},
            timeout=600.0,  # 10 minutes for multi-hop search
        )

        assert response.status_code == 200
        data = response.json()

        assert "answer" in data
        assert len(data["answer"]) > 0
        logger.info(f"✅ Search result: {len(data['answer'])} chars")


@pytest.mark.requires_real_server
@pytest.mark.requires_ollama
@pytest.mark.requires_searxng
@pytest.mark.websocket
async def test_real_server_websocket_generate_widget():
    """Test the real WebSocket /ws/generate-widget endpoint."""
    uri = f"{WS_BASE_URL}/api/v1/ws/generate-widget"

    widgets = []
    qa_checkpoints = []

    try:
        # Disable keepalive pings (ping_interval=None) since server takes longer than 20s to process
        async with websockets.connect(
            uri, close_timeout=10.0, ping_interval=None
        ) as websocket:
            # Send the request (websockets 16.0 uses send() with JSON dump)
            await websocket.send(
                json.dumps(
                    {
                        "query": "Global Inflation Trends (2015–Present)",
                        "device_context": "desktop",
                    }
                )
            )

            # Collect messages
            start_time = time.time()
            async for message in websocket:
                # websockets 16.0 returns str or bytes
                if isinstance(message, bytes):
                    message = message.decode("utf-8")
                message = json.loads(message)

                event_type = message.get("type")

                if event_type == "qa_progress":
                    qa_checkpoints.append(message.get("data", {}))
                    checkpoint = message.get("data", {}).get("checkpoint", "unknown")
                    status = message.get("data", {}).get("status", "unknown")
                    logger.info(f"  🔍 QA: {checkpoint} - {status}")

                elif event_type == "widget":
                    widget = message.get("data", {})
                    widgets.append(widget)
                    logger.info(
                        f"  📦 Widget: {widget.get('type')} - {widget.get('title')}"
                    )

                elif event_type == "complete":
                    logger.info("  ✅ Complete")
                    break

                elif event_type == "error":
                    error_msg = message.get("data", {}).get("message", "Unknown error")
                    pytest.fail(f"WebSocket error: {error_msg}")

                # Timeout after 5 minutes
                if time.time() - start_time > 300:
                    logger.warning("  ⏱️ Timeout after 5 minutes")
                    break

    except Exception as e:
        logger.error(f"❌ WebSocket test failed: {e}")
        raise

    # Validate results
    logger.info(
        f"📊 Results: {len(qa_checkpoints)} QA checkpoints, {len(widgets)} widgets"
    )

    # At minimum, we should have received something
    assert len(qa_checkpoints) > 0 or len(widgets) > 0, (
        "Expected at least QA checkpoints or widgets"
    )

    # If we got widgets, validate their structure
    for widget in widgets:
        assert "id" in widget, "Widget missing id"
        assert "type" in widget, "Widget missing type"
        assert "title" in widget, "Widget missing title"

    logger.info("✅ Real server WebSocket test passed")


@pytest.mark.requires_real_server
@pytest.mark.requires_ollama
@pytest.mark.requires_searxng
@pytest.mark.websocket
async def test_real_server_websocket_search():
    """Test the real WebSocket /ws/search endpoint."""
    uri = f"{WS_BASE_URL}/api/v1/ws/search"

    try:
        # Disable keepalive pings (ping_interval=None) since server takes longer than 20s to process
        async with websockets.connect(
            uri, close_timeout=10.0, ping_interval=None
        ) as websocket:
            # Send the request (websockets 16.0 uses send() with JSON dump)
            await websocket.send(
                json.dumps(
                    {
                        "query": "What is the current stock market trend?",
                    }
                )
            )

            # Collect messages
            hops = []
            final_answer = None

            start_time = time.time()
            async for message in websocket:
                # websockets 16.0 returns str or bytes
                if isinstance(message, bytes):
                    message = message.decode("utf-8")
                message = json.loads(message)

                event_type = message.get("type")

                if event_type == "hop":
                    hops.append(message.get("data", {}))
                    hop_num = message.get("data", {}).get("hop", "?")
                    confidence = message.get("data", {}).get("confidence", 0)
                    logger.info(f"  🔍 Hop {hop_num}: confidence={confidence}")

                elif event_type == "final_answer":
                    final_answer = message.get("data", {}).get("answer", "")
                    logger.info("  📝 Final answer received")
                    break

                elif event_type == "complete":
                    logger.info("  ✅ Complete")
                    break

                elif event_type == "error":
                    error_msg = message.get("data", {}).get("message", "Unknown error")
                    pytest.fail(f"WebSocket error: {error_msg}")

                # Timeout after 5 minutes
                if time.time() - start_time > 300:
                    logger.warning("  ⏱️ Timeout after 5 minutes")
                    break

    except Exception as e:
        logger.error(f"❌ WebSocket search test failed: {e}")
        raise

    logger.info(f"📊 Results: {len(hops)} hops, final_answer: {bool(final_answer)}")
    logger.info("✅ Real server WebSocket search test passed")
