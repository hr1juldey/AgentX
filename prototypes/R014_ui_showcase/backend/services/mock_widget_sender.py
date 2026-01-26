# =============================================================================
# AGENTX Mock Widget Sender
# =============================================================================
# Sends pre-crafted mock widgets to frontend for isolated testing
# =============================================================================

"""Mock widget sender - standalone script to send test widgets to frontend.

Run with: uv run python services/mock_widget_sender.py

This script connects to the frontend WebSocket endpoint and sends pre-crafted
widget data without making LLM calls, allowing isolated frontend testing.

Data is loaded from mock_data/widgets.json following DDD principles.
"""

import asyncio
import json
import logging
from datetime import datetime

import websockets

from services.mock_widget_repository import MockWidgetRepository

# =============================================================================
# Configuration
# =============================================================================

WS_URL = "ws://localhost:8014/ws/widgets?query=mock_test"
DEFAULT_WIDGET_TYPES = ["chart", "card", "form", "markdown"]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =============================================================================
# Widget Sender Service (Business Logic)
# =============================================================================


class MockWidgetSender:
    """Service for sending mock widgets to frontend via WebSocket.

    Follows Single Responsibility Principle - handles only WebSocket communication.
    """

    def __init__(self, repository: MockWidgetRepository, ws_url: str = WS_URL):
        self._repository = repository
        self._ws_url = ws_url

    def _prepare_widget(self, widget: dict) -> dict:
        """Prepare widget for sending by adding timestamp.

        Args:
            widget: Raw widget data

        Returns:
            Widget data with timestamp added
        """
        prepared = widget.copy()
        if prepared.get("timestamp") == "auto":
            prepared["timestamp"] = datetime.utcnow().isoformat()
        return prepared

    async def send_widgets(self, widget_types: list[str] | None = None) -> None:
        """Send mock widgets to frontend WebSocket.

        Args:
            widget_types: List of widget types to send (default: all available)
        """
        if widget_types is None:
            widget_types = DEFAULT_WIDGET_TYPES

        # Validate widget types
        available = self._repository.get_available_widget_types()
        valid_types = [wt for wt in widget_types if wt in available]
        invalid_types = set(widget_types) - set(valid_types)

        if invalid_types:
            logger.warning(f"Unknown widget types: {invalid_types}")

        if not valid_types:
            logger.error("No valid widget types to send")
            return

        try:
            async with websockets.connect(self._ws_url) as websocket:
                logger.info(f"Connected to {self._ws_url}")

                # Prepare delivery plan
                widgets_to_send = [
                    self._prepare_widget(self._repository.get_widget(wt))
                    for wt in valid_types
                ]
                defaults = self._repository.get_delivery_defaults()
                delays = defaults["delays"][: len(valid_types)]

                delivery_plan = {
                    "widgets": widgets_to_send,
                    "delays": delays,
                    "total_duration": defaults["total_duration"],
                }

                # Send delivery plan
                await websocket.send(
                    json.dumps({"type": "delivery_plan", "data": delivery_plan})
                )
                logger.info(f"Sent delivery plan for {len(valid_types)} widgets")

                # Send widgets with delays
                for i, widget_type in enumerate(valid_types):
                    await asyncio.sleep(0.5)  # Delay between widgets
                    await websocket.send(
                        json.dumps({"type": "widget", "data": widgets_to_send[i]})
                    )
                    logger.info(f"Sent {widget_type} widget")

                # Send completion
                await websocket.send(
                    json.dumps(
                        {
                            "type": "complete",
                            "data": {"total_widgets": len(valid_types)},
                        }
                    )
                )
                logger.info("Mock widget delivery complete")

        except ConnectionRefusedError:
            logger.error(
                "Connection refused. Is the frontend running on localhost:8014?"
            )
        except Exception as e:
            logger.error(f"Error sending mock widgets: {e}")


# =============================================================================
# CLI Entry Point
# =============================================================================


if __name__ == "__main__":
    from services.mock_widget_sender_cli import main

    main()
