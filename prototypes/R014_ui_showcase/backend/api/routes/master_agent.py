# =============================================================================
# AGENTX R014 - Master Agent WebSocket Route
# =============================================================================

import logging
import uuid
from typing import Any

from fastapi import WebSocket, WebSocketDisconnect

from application.use_cases.master_agent import get_master_agent_use_case

router = __import__("fastapi").APIRouter()
logger = logging.getLogger(__name__)


@router.websocket("/ws/generate-widget")
async def generate_widget_master_agent(websocket: WebSocket) -> None:
    """WebSocket endpoint for Master Agent widget generation with streaming.

    Implements the complete R014 Master-Agent pipeline with 10 phases.
    """
    await websocket.accept()
    session_id = str(uuid.uuid4())[:8]

    # Track connection state to stop callbacks after error
    connection_active = True

    try:
        data = await websocket.receive_json()

        user_query = data.get("query", "")
        device_context_raw = data.get("device_context", "desktop")

        if isinstance(device_context_raw, str):
            device_context = device_context_raw
        elif isinstance(device_context_raw, dict):
            device_context = device_context_raw.get("type", "desktop")
        else:
            device_context = "desktop"

        logger.info(f"🎯 [{session_id}] {user_query[:100]}...")

        def _serialize_delivery_plan(delivery_plan: Any) -> dict:
            """Safely serialize DeliveryPlan to dict with error handling."""
            try:
                if hasattr(delivery_plan, "model_dump"):
                    return delivery_plan.model_dump()
                # Fallback: serialize widgets manually
                return {
                    "widgets": [
                        w.model_dump() if hasattr(w, "model_dump") else w
                        for w in getattr(delivery_plan, "widgets", [])
                    ],
                    "delays": getattr(delivery_plan, "delays", []),
                    "total_duration": getattr(delivery_plan, "total_duration", 0),
                }
            except Exception:
                # Ultimate fallback: return minimal dict
                return {"widgets": [], "delays": [], "total_duration": 0}

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
                widget_type = widget.get(
                    "type", widget.get("descriptor_type", "unknown")
                )
                logger.info(f"  📦 {widget_type}")
            except Exception:
                pass  # WebSocket closed, stop sending

        async def send_qa_progress(checkpoint: str, status: str, data: dict) -> None:
            """Send QA checkpoint progress to frontend."""
            if not connection_active:
                return
            try:
                await websocket.send_json(
                    {
                        "type": "qa_progress",
                        "data": {
                            "checkpoint": checkpoint,
                            "status": status,
                            "details": data,
                        },
                    }
                )
                logger.info(f"  ✓ [{checkpoint}] {status}")
            except Exception:
                pass  # WebSocket closed, stop sending

        # Use application layer use case to create and configure master agent
        use_case = get_master_agent_use_case()
        master_agent, delivery_plan_type = use_case.setup_master_agent_with_pipeline(
            widget_callback=send_widget,
            qa_callback=send_qa_progress,
        )

        delivery_plan: Any = await master_agent.execute_with_streaming(
            user_query=user_query,
            device_context=device_context,
        )

        await websocket.send_json(
            {
                "type": "complete",
                "data": {
                    "delivery_plan": _serialize_delivery_plan(delivery_plan),
                },
            }
        )

        logger.info(f"✅ [{session_id}] Complete")

    except WebSocketDisconnect:
        connection_active = False
    except Exception as e:
        connection_active = False
        logger.error(f"🔴 [{session_id}] {e}", exc_info=True)
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
