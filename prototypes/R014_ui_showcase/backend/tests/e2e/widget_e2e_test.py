# =============================================================================
# AGENTX R014 - E2E Widget Hydration Test
# =============================================================================
# Tests that mocked widgets properly flow from backend to frontend
# =============================================================================

import asyncio
import json

import pytest
import websockets

from services.master_agent.delivery_planner import DeliveryPlan
from tests.e2e.mock_widget_factory import MockWidgetFactory


class WidgetTracker:
    """Tracks widgets received during WebSocket connection."""

    def __init__(self) -> None:
        self.received_widgets: list[dict] = []
        self.received_qa_progress: list[dict] = []
        self.errors: list[str] = []
        self.completed = False

    def reset(self) -> None:
        """Reset all tracking state."""
        self.received_widgets = []
        self.received_qa_progress = []
        self.errors = []
        self.completed = False


@pytest.fixture
def widget_tracker() -> WidgetTracker:
    """Fixture providing a fresh widget tracker for each test."""
    return WidgetTracker()


@pytest.fixture
def mock_delivery_plan() -> DeliveryPlan:
    """Fixture providing a mock delivery plan with test widgets."""
    widgets = MockWidgetFactory.create_widget_sequence()
    delays = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]

    return DeliveryPlan(
        widgets=widgets,
        delays=delays[: len(widgets)],
        total_duration=sum(delays[: len(widgets)]),
    )


class TestWidgetE2EFlow:
    """End-to-end tests for widget hydration and delivery."""

    @pytest.mark.asyncio
    async def test_mock_widget_factory_creates_valid_widgets(self) -> None:
        """Test that the mock widget factory creates valid widgets."""
        widgets = MockWidgetFactory.create_widget_sequence()

        assert len(widgets) == len(MockWidgetFactory.WIDGET_TYPES)

        for widget in widgets:
            is_valid, errors = MockWidgetFactory.validate_widget_structure(widget)
            assert is_valid, f"Widget validation failed: {errors}"

    @pytest.mark.asyncio
    async def test_delivery_plan_with_mock_widgets(
        self, mock_delivery_plan: DeliveryPlan
    ) -> None:
        """Test that delivery plan can be created with mock widgets."""
        schedule = mock_delivery_plan.get_delivery_schedule()

        assert len(schedule) == len(MockWidgetFactory.WIDGET_TYPES)

        # Verify schedule structure
        for delay, widget in schedule:
            assert isinstance(delay, float)
            assert isinstance(widget, dict)
            assert "id" in widget
            assert "type" in widget

    @pytest.mark.asyncio
    async def test_mock_widget_delivery_sequence(
        self, mock_delivery_plan: DeliveryPlan
    ) -> None:
        """Test that mock widgets can be delivered in sequence with delays."""

        delivered_widgets: list[dict] = []

        async def mock_callback(widget: dict) -> None:
            """Mock delivery callback."""
            delivered_widgets.append(widget)

        # Execute delivery
        from services.master_agent.delivery_planner import DeliveryPlanner

        planner = DeliveryPlanner(min_delay=0.5, max_delay=1.0)
        await planner.deliver_with_delay(mock_delivery_plan, mock_callback)

        # Verify all widgets were delivered
        assert len(delivered_widgets) == len(MockWidgetFactory.WIDGET_TYPES)

        # Verify they have unique IDs
        ids = [w.get("id") for w in delivered_widgets]
        assert len(ids) == len(set(ids)), "Widget IDs are not unique!"


class WebSocketTestClient:
    """Test client for WebSocket widget reception."""

    def __init__(self, uri: str) -> None:
        """Initialize the test client.

        Args:
            uri: WebSocket URI to connect to
        """
        self.uri = uri
        self.received_messages: list[dict] = []
        self.connected = False

    async def connect_and_receive(
        self, payload: dict, timeout: float = 30.0
    ) -> list[dict]:
        """Connect to WebSocket and receive all messages.

        Args:
            payload: Initial JSON payload to send
            timeout: Maximum time to wait for messages

        Returns:
            List of received JSON messages
        """
        self.received_messages = []

        try:
            async with websockets.connect(self.uri) as websocket:
                self.connected = True

                # Send the initial payload
                await websocket.send(json.dumps(payload))

                # Receive messages until timeout or complete signal
                start_time = asyncio.get_event_loop().time()
                while (asyncio.get_event_loop().time() - start_time) < timeout:
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                        data = json.loads(message)
                        self.received_messages.append(data)

                        # Check for completion signal
                        if data.get("type") == "complete":
                            break
                        elif data.get("type") == "error":
                            break

                    except asyncio.TimeoutError:
                        # Check if we've timed out overall
                        if (asyncio.get_event_loop().time() - start_time) >= timeout:
                            break
                        continue

        except Exception as e:
            self.received_messages.append({"type": "connection_error", "error": str(e)})

        return self.received_messages


@pytest.mark.skipif(
    True,  # Skip by default - requires running server
    reason="Requires running backend server on ws://localhost:8000",
)
class TestLiveWebSocketWidgetDelivery:
    """Live tests against a running backend server."""

    @pytest.mark.asyncio
    async def test_websocket_receives_mock_widgets(self) -> None:
        """Test that WebSocket properly receives widgets from backend."""

        client = WebSocketTestClient("ws://localhost:8000/ws/generate-widget")

        payload = {
            "query": "Show me a test dashboard",
            "device_context": "desktop",
        }

        messages = await client.connect_and_receive(payload, timeout=60.0)

        # Verify we got some messages
        assert len(messages) > 0, "No messages received from WebSocket"

        # Count widget messages
        widget_messages = [m for m in messages if m.get("type") == "widget"]
        assert len(widget_messages) > 0, "No widget messages received"

        # Validate widget structures
        for msg in widget_messages:
            widget_data = msg.get("data", {})
            is_valid, errors = MockWidgetFactory.validate_widget_structure(widget_data)
            assert is_valid, f"Invalid widget received: {errors}"

        # Check for completion message
        complete_messages = [m for m in messages if m.get("type") == "complete"]
        assert len(complete_messages) > 0, "No completion message received"

    @pytest.mark.asyncio
    async def test_websocket_sequence_ordering(self) -> None:
        """Test that widgets are delivered in the correct sequence."""

        client = WebSocketTestClient("ws://localhost:8000/ws/generate-widget")

        payload = {
            "query": "Create a report with multiple sections",
            "device_context": "desktop",
        }

        messages = await client.connect_and_receive(payload, timeout=60.0)

        # Extract widget messages in order
        widget_messages = [m for m in messages if m.get("type") == "widget"]

        # Verify we got multiple widgets
        assert len(widget_messages) >= 2, "Expected at least 2 widgets"

        # Verify each has a unique ID
        widget_ids = []
        for msg in widget_messages:
            widget_id = msg.get("data", {}).get("id")
            if widget_id:
                widget_ids.append(widget_id)

        assert len(widget_ids) == len(set(widget_ids)), "Widget IDs are not unique!"


# Manual test runner for development
async def run_manual_e2e_test() -> None:
    """Manually run the E2E test without pytest."""

    print("=== E2E Widget Hydration Test ===\n")

    # Test 1: Mock Widget Factory
    print("Test 1: Mock Widget Factory")
    widgets = MockWidgetFactory.create_widget_sequence()
    print(f"  Created {len(widgets)} widgets")

    all_valid = True
    for widget in widgets:
        is_valid, errors = MockWidgetFactory.validate_widget_structure(widget)
        if not is_valid:
            print(f"  ❌ Invalid widget: {errors}")
            all_valid = False

    if all_valid:
        print("  ✅ All widgets valid\n")

    # Test 2: Delivery Plan
    print("Test 2: Delivery Plan Creation")
    delivered = []

    async def mock_callback(widget: dict) -> None:
        delivered.append(widget)

    from services.master_agent.delivery_planner import DeliveryPlanner

    delivery_plan = DeliveryPlan(
        widgets=widgets,
        delays=[0.0] * len(widgets),
        total_duration=0.0,
    )

    planner = DeliveryPlanner(min_delay=0.1, max_delay=0.2)
    await planner.deliver_with_delay(delivery_plan, mock_callback)

    print(f"  Delivered {len(delivered)} widgets")
    if len(delivered) == len(widgets):
        print("  ✅ All widgets delivered\n")
    else:
        print(f"  ❌ Expected {len(widgets)}, got {len(delivered)}\n")

    # Test 3: Widget Structure Validation
    print("Test 3: Widget Structure Validation")
    test_widgets = MockWidgetFactory.create_widget_sequence(
        ["markdown", "chart", "gallery"]
    )
    for w in test_widgets:
        is_valid, _ = MockWidgetFactory.validate_widget_structure(w)
        status = "✅" if is_valid else "❌"
        print(f"  {status} {w.get('type')}: {w.get('id')}")

    print("\n=== Test Complete ===")


if __name__ == "__main__":
    asyncio.run(run_manual_e2e_test())
