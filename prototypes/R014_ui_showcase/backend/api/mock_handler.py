# =============================================================================
# AGENTX R014 - Mock Mode WebSocket Handler
# =============================================================================
# Sends pre-defined widgets without LLM calls when MOCK_MODE is enabled
# =============================================================================

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path

from fastapi import WebSocket

logger = logging.getLogger(__name__)

MOCK_DATA_PATH = (
    Path(__file__).parent.parent / "services" / "mock_data" / "widgets.json"
)


async def handle_mock_mode(websocket: WebSocket, session_id: str, query: str) -> None:
    """Handle mock mode - send pre-defined widgets without LLM calls.

    Args:
        websocket: WebSocket connection
        session_id: Session identifier for logging
        query: User query (for logging purposes)
    """
    try:
        if not MOCK_DATA_PATH.exists():
            await websocket.send_json(
                {"type": "error", "message": "Mock data not found"}
            )
            return

        with open(MOCK_DATA_PATH, "r") as f:
            mock_data = json.load(f)

        widgets = mock_data.get("widgets", {})
        defaults = mock_data.get(
            "delivery_defaults", {"delays": [0.0], "total_duration": 1.0}
        )

        # Prepare widgets with timestamps
        widgets_to_send = []
        for widget_data in widgets.values():
            prepared = widget_data.copy()
            if prepared.get("timestamp") == "auto":
                prepared["timestamp"] = datetime.utcnow().isoformat()
            widgets_to_send.append(prepared)

        delays = defaults["delays"][: len(widgets_to_send)]

        # Send delivery plan
        await websocket.send_json(
            {
                "type": "delivery_plan",
                "data": {
                    "widgets": widgets_to_send,
                    "delays": delays,
                    "total_duration": defaults["total_duration"],
                },
            }
        )
        logger.info(f"📦 [{session_id}] MOCK: Sending {len(widgets_to_send)} widgets")

        # Send widgets with delays
        for widget in widgets_to_send:
            await asyncio.sleep(0.5)
            await websocket.send_json({"type": "widget", "data": widget})
            logger.info(f"  📦 [{session_id}] MOCK: {widget.get('type', 'unknown')}")

        # Send completion
        await websocket.send_json(
            {"type": "complete", "data": {"total_widgets": len(widgets_to_send)}}
        )
        logger.info(f"✅ [{session_id}] MOCK: Complete")

    except Exception as e:
        logger.error(f"🔴 [{session_id}] MOCK error: {e}")
        try:
            await websocket.send_json(
                {"type": "error", "message": f"Mock mode error: {e}"}
            )
        except Exception:
            pass
