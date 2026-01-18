# =============================================================================
# AGENTX R013 - Chain-based WebSocket Endpoint
# =============================================================================
# WebSocket endpoint for travel planning using chain
# =============================================================================

import logging

from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


async def travel_websocket(websocket: WebSocket) -> None:
    """WebSocket endpoint for travel planning conversation.

    Receives streaming input chunks and responds with streaming output.
    """
    from api.routes import travel_chain

    await websocket.accept()
    logger.info("WebSocket connection established")

    input_buffer = []
    input_complete = False

    try:
        # Receive input stream
        while not input_complete:
            data = await websocket.receive_json()

            if data.get("type") == "chunk":
                input_buffer.append(data.get("text", ""))
                # Acknowledge immediately
                await websocket.send_json(
                    {"type": "ack", "received": len(input_buffer)}
                )

            elif data.get("type") == "end":
                input_complete = True
                logger.info(f"Input complete. Received {len(input_buffer)} chunks")

        # Process complete input
        user_question = "".join(input_buffer)
        logger.info(f"Processing question: {user_question[:400]}...")

        # Use chain to plan trip
        await websocket.send_json({"type": "status", "msg": "Planning your trip..."})

        result = await travel_chain.plan_full_trip(
            question=user_question, budget="moderate", group_size="2"
        )

        # Send results
        await websocket.send_json(
            {"type": "partial", "data": f"Destination: {result['destination']}"}
        )
        await websocket.send_json(
            {"type": "partial", "data": f"Info: {result['info'][:200]}..."}
        )
        await websocket.send_json(
            {"type": "partial", "data": f"Itinerary: {result['itinerary'][:200]}..."}
        )

        # Signal completion
        await websocket.send_json({"type": "done", "final": "Trip planning complete!"})

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.send_json({"type": "error", "msg": str(e)})
