# =============================================================================
# AGENTX R014 - Multi-Hop Search Routes
# =============================================================================

import logging
import uuid
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from application.use_cases.search import get_search_use_case
from config.settings import settings
from services.multihop_search.agents import MultiHopSearchAgent
from services.multihop_search.schemas import HopEvent, SearchRequest

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/search")
async def search_endpoint(request: dict[str, Any]) -> dict[str, Any]:
    """REST endpoint for multi-hop search using application layer."""
    query = request.get("query", "")

    logger.info(f"🔍 /search called: query='{query[:50]}...'")

    try:
        from application.dtos.requests import SearchRequest as AppSearchRequest

        use_case = get_search_use_case()
        dto_request = AppSearchRequest(query=query)
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

        async def send_progress(event: HopEvent) -> None:
            await websocket.send_json(
                {
                    "type": "hop_event",
                    "data": event.model_dump(),
                }
            )

        agent = MultiHopSearchAgent(
            max_hops=request.max_hops or settings.max_hops,
            progress_callback=send_progress,
            stop_threshold=settings.stop_threshold,
        )

        result = await agent(question=request.query)

        citations = []
        if result.citations:
            for cit in result.citations:
                if isinstance(cit, dict):
                    citations.append(cit)

        await websocket.send_json(
            {
                "type": "final_result",
                "data": {
                    "answer": result.answer,
                    "summary": getattr(result, "summary", ""),
                    "confidence": getattr(result, "confidence", "medium"),
                    "citations": citations,
                    "hops": result.hops or [],
                    "metadata": result.metadata or {},
                    "queries_used": result.metadata.get("queries_used", [])
                    if result.metadata
                    else [],
                    "final_reflection_reasoning": getattr(
                        result, "final_reflection_reasoning", None
                    ),
                },
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
