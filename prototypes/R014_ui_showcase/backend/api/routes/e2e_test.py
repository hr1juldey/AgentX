# =============================================================================
# AGENTX R014 - E2E Test Routes
# =============================================================================
# Development endpoints for testing widget delivery without full pipeline
# =============================================================================

import logging
import uuid
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from services.master_agent.delivery_planner import DeliveryPlanner
from tests.e2e.mock_widget_factory import MockWidgetFactory

router = APIRouter()
logger = logging.getLogger(__name__)


@router.websocket("/ws/e2e-test-widget-delivery")
async def e2e_test_widget_delivery(websocket: WebSocket) -> None:
    """WebSocket endpoint for E2E testing of widget delivery.

    This endpoint bypasses the LLM pipeline and directly delivers
    pre-configured mock widgets for testing the frontend.

    Message format:
    {
        "widget_types": ["markdown", "chart", "gallery"],
        "sequence": ["markdown", "chart", "gallery"],
        "min_delay": 0.5,
        "max_delay": 1.0
    }
    """
    await websocket.accept()
    session_id = str(uuid.uuid4())[:8]
    connection_active = True

    try:
        data = await websocket.receive_json()

        widget_types = data.get("widget_types", MockWidgetFactory.WIDGET_TYPES)
        sequence = data.get("sequence", widget_types)
        min_delay = data.get("min_delay", 0.5)
        max_delay = data.get("max_delay", 1.0)

        logger.info(
            f"🧪 [E2E-{session_id}] Starting test with {len(widget_types)} widgets"
        )

        async def send_widget(widget: dict) -> None:
            """Send a single widget to the frontend."""
            if not connection_active:
                return
            try:
                await websocket.send_json(
                    {
                        "type": "widget",
                        "data": widget,
                    }
                )
                widget_type = widget.get("type", "unknown")
                logger.info(f"  📦 [E2E-{session_id}] Sent {widget_type}")
            except Exception:
                pass

        # Create mock widgets
        widgets = [MockWidgetFactory.create_widget(t) for t in widget_types]

        # Create delivery plan
        planner = DeliveryPlanner(min_delay=min_delay, max_delay=max_delay)
        delivery_plan = planner.plan_delivery(widgets, sequence)

        # Send progress message
        await websocket.send_json(
            {
                "type": "test_start",
                "data": {
                    "widget_count": len(widgets),
                    "estimated_duration": delivery_plan.total_duration,
                },
            }
        )

        # Deliver widgets with delays
        await planner.deliver_with_delay(delivery_plan, send_widget)

        # Send completion message
        await websocket.send_json(
            {
                "type": "complete",
                "data": {
                    "delivered_count": len(widgets),
                    "session_id": session_id,
                },
            }
        )

        logger.info(f"✅ [E2E-{session_id}] Delivered {len(widgets)} widgets")

    except WebSocketDisconnect:
        connection_active = False
        logger.info(f"🔌 [E2E-{session_id}] Disconnected")
    except Exception as e:
        connection_active = False
        logger.error(f"🔴 [E2E-{session_id}] {e}", exc_info=True)
        try:
            if websocket.client_state != "disconnected":
                await websocket.send_json(
                    {
                        "type": "error",
                        "message": str(e),
                    }
                )
        except Exception:
            pass


@router.post("/e2e/mock-widgets")
async def create_mock_widgets(config: dict[str, Any]) -> dict[str, Any]:
    """Create mock widgets for testing without WebSocket.

    Args:
        config: Configuration with keys:
            - widget_types: list of widget types to create
            - count: number of each type (default: 1)

    Returns:
        Dict with created widgets
    """
    widget_types = config.get("widget_types", ["markdown", "chart"])
    count = config.get("count", 1)

    widgets = []
    for _ in range(count):
        for wtype in widget_types:
            widgets.append(MockWidgetFactory.create_widget(wtype))

    return {
        "widgets": widgets,
        "count": len(widgets),
    }


@router.get("/e2e/widget-types")
async def get_available_widget_types() -> dict[str, Any]:
    """Get list of available widget types for testing.

    Returns:
        Dict with available widget types
    """
    return {
        "widget_types": MockWidgetFactory.WIDGET_TYPES,
        "count": len(MockWidgetFactory.WIDGET_TYPES),
    }


@router.post("/e2e/validate-widget")
async def validate_widget(widget: dict[str, Any]) -> dict[str, Any]:
    """Validate a widget structure.

    Args:
        widget: Widget descriptor to validate

    Returns:
        Dict with validation result
    """
    is_valid, errors = MockWidgetFactory.validate_widget_structure(widget)

    return {
        "valid": is_valid,
        "errors": errors,
    }
