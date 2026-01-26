# =============================================================================
# AGENTX E2E WebSocket Tests - Real Backend Integration
# =============================================================================
# Tests connect to the live backend server on port 3014
# and validate websocket message flow like the frontend does.
# =============================================================================

"""E2E WebSocket Tests - Real Backend Integration

Tests connect to the live backend server on port 3014
and validate websocket message flow like the frontend does.
"""

import pytest

import json
from websockets import connect

SERVER_URL = "ws://localhost:8014/api/v1/ws/generate-widget"


@pytest.mark.websocket
@pytest.mark.slow
@pytest.mark.requires_ollama
@pytest.mark.requires_searxng
async def test_e2e_chart_has_data() -> None:
    """Test that chart widgets contain actual data (not empty arrays)."""
    captured_messages = []

    async with connect(SERVER_URL, ping_interval=None, close_timeout=600) as ws:
        # Send query
        await ws.send(
            json.dumps(
                {
                    "query": "Show me inflation rates by country in 2024",
                    "device_context": "desktop",
                }
            )
        )

        # Capture all messages
        async for message in ws:
            data = json.loads(message)
            captured_messages.append(data)

            # Check for completion
            if data.get("type") == "complete":
                break
            elif data.get("type") == "error":
                pytest.fail(f"Server error: {data}")

    # Validate: at least one chart with data
    charts = [
        m["data"]
        for m in captured_messages
        if m.get("type") == "widget" and m["data"].get("type") == "chart"
    ]

    assert len(charts) > 0, "No chart widgets received"
    for chart in charts:
        chart_data = chart["content"].get("data", [])
        assert len(chart_data) > 0, f"Chart {chart['id']} has empty data array"


@pytest.mark.websocket
@pytest.mark.slow
@pytest.mark.requires_ollama
@pytest.mark.requires_searxng
async def test_e2e_form_has_fields() -> None:
    """Test that form widgets contain form fields."""
    captured_messages = []

    async with connect(SERVER_URL, ping_interval=None, close_timeout=600) as ws:
        await ws.send(
            json.dumps(
                {
                    "query": "Create a feedback form for user input",
                    "device_context": "desktop",
                }
            )
        )

        async for message in ws:
            data = json.loads(message)
            captured_messages.append(data)
            if data.get("type") == "complete":
                break

    # Validate: at least one form with fields
    forms = [
        m["data"]
        for m in captured_messages
        if m.get("type") == "widget" and m["data"].get("type") == "form"
    ]

    assert len(forms) > 0, "No form widgets received"
    for form in forms:
        form_fields = form["content"].get("form_fields", [])
        assert len(form_fields) > 0, f"Form {form['id']} has 0 form fields"


@pytest.mark.websocket
@pytest.mark.slow
@pytest.mark.requires_ollama
@pytest.mark.requires_searxng
async def test_e2e_message_sequence() -> None:
    """Test that message sequence is valid: qa_progress -> widgets -> complete."""
    captured_messages = []

    async with connect(SERVER_URL, ping_interval=None, close_timeout=600) as ws:
        await ws.send(
            json.dumps(
                {
                    "query": "Analyze global inflation trends",
                    "device_context": "desktop",
                }
            )
        )

        async for message in ws:
            data = json.loads(message)
            captured_messages.append(data)
            if data.get("type") == "complete":
                break

    # Validate message types
    message_types = [m.get("type") for m in captured_messages]

    # Should have qa_progress events
    assert "qa_progress" in message_types, "No qa_progress events"

    # Should have widget events
    assert "widget" in message_types, "No widget events"

    # Should end with complete
    assert message_types[-1] == "complete", "Last message should be 'complete'"

    # No errors
    assert "error" not in message_types, f"Error in message stream: {captured_messages}"
