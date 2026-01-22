# =============================================================================
# AGENTX R014 - Multi-Hop Search Routes
# =============================================================================

import logging
import uuid
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from application.dtos.requests import SearchRequest
from application.use_cases.search import (
    get_search_use_case,
    get_websocket_search_use_case,
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/search")
async def search_endpoint(request: dict[str, Any]) -> dict[str, Any]:
    """REST endpoint for multi-hop search using application layer."""
    query = request.get("query", "")

    logger.info(f"🔍 /search called: query='{query[:50]}...'")

    try:
        use_case = get_search_use_case()
        dto_request = SearchRequest(query=query)
        answer = await use_case.search(dto_request)

        return {
            "answer": answer,
            "summary": "",
            "confidence": "medium",
            "citations": [],
            "hops": [],
            "metadata": {},
            "queries_used": [],
        }
    except Exception as e:
        logger.error(f"🔴 Error in search: {e}", exc_info=True)
        return {
            "answer": f"Error: {str(e)}",
            "summary": "",
            "confidence": "low",
            "citations": [],
            "hops": [],
            "metadata": {"error": True},
            "queries_used": [],
        }


@router.websocket("/ws/search")
async def search_websocket(websocket: WebSocket) -> None:
    """WebSocket endpoint for streaming multi-hop search progress."""
    await websocket.accept()
    session_id = str(uuid.uuid4())

    logger.info(f"🔍 WebSocket search connected: {session_id}")

    try:
        data = await websocket.receive_json()
        request = SearchRequest(**data)

        logger.info(
            f"🔍 Search request: query='{request.query[:50]}...', "
            f"max_hops={request.max_hops}"
        )

        async def send_progress(event_dict: dict[str, Any]) -> None:
            await websocket.send_json(
                {
                    "type": "hop_event",
                    "data": event_dict,
                }
            )

        use_case = get_websocket_search_use_case()
        result = await use_case.search_with_streaming(
            request=request, progress_callback=send_progress
        )

        await websocket.send_json(
            {
                "type": "final_result",
                "data": result.model_dump(),
            }
        )

        logger.info(f"🔍 Search complete: {session_id}")

    except WebSocketDisconnect:
        logger.info(f"🔍 WebSocket disconnected: {session_id}")
    except Exception as e:
        logger.error(f"🔴 WebSocket error: {e}", exc_info=True)
        try:
            await websocket.send_json(
                {
                    "type": "error",
                    "message": str(e),
                }
            )
        except Exception:
            pass
