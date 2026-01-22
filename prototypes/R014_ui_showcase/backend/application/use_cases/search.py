# =============================================================================
# AGENTX R014 - Application Layer - Search Use Cases
# =============================================================================
# Use case facades that wrap existing multi-hop search services
# =============================================================================

from collections.abc import Callable
from typing import Any

from application.dtos.requests import SearchRequest
from application.dtos.responses import SearchResultResponse
from config.settings import settings


class SearchUseCase:
    """Use case for multi-hop search operations.

    This is a facade that wraps the existing MultiHopSearchAgent
    to provide a clean architectural boundary.

    Phase 1: Thin wrapper - no behavior changes, just delegates to service.
    Phase 3: Will implement full use case logic.
    """

    async def search(self, request: SearchRequest) -> str:
        """Execute multi-hop search and return final answer.

        Phase 1: Delegates to existing service.
        """
        from services.multihop_search.agents import MultiHopSearchAgent

        agent = MultiHopSearchAgent()
        result = await agent(query=request.query)
        return result.answer


class MultiHopSearchWebSocketUseCase:
    """Use case for multi-hop search with WebSocket streaming.

    Wraps MultiHopSearchAgent with progress callback support.
    """

    async def search_with_streaming(
        self,
        request: SearchRequest,
        progress_callback: Callable[[dict[str, Any]], None] | None = None,
    ) -> SearchResultResponse:
        """Execute multi-hop search with streaming progress updates."""
        from services.multihop_search.agents import MultiHopSearchAgent

        agent = MultiHopSearchAgent(
            max_hops=request.max_hops or settings.max_hops,
            progress_callback=progress_callback,
            stop_threshold=settings.stop_threshold,
        )

        result = await agent(question=request.query)

        # Convert citations to dict format
        citations = []
        if result.citations:
            for cit in result.citations:
                if isinstance(cit, dict):
                    citations.append(cit)

        return SearchResultResponse(
            answer=result.answer,
            summary=getattr(result, "summary", ""),
            confidence=getattr(result, "confidence", "medium"),
            citations=citations,
            hops=result.hops or [],
            metadata=result.metadata or {},
            queries_used=result.metadata.get("queries_used", [])
            if result.metadata
            else [],
            final_reflection_reasoning=getattr(
                result, "final_reflection_reasoning", None
            ),
        )


# Singleton getter for dependency injection
_search_use_case: SearchUseCase | None = None


def get_search_use_case() -> SearchUseCase:
    """Get singleton instance of SearchUseCase."""
    global _search_use_case
    if _search_use_case is None:
        _search_use_case = SearchUseCase()
    return _search_use_case


_websocket_search_use_case: MultiHopSearchWebSocketUseCase | None = None


def get_websocket_search_use_case() -> MultiHopSearchWebSocketUseCase:
    """Get singleton instance of MultiHopSearchWebSocketUseCase."""
    global _websocket_search_use_case
    if _websocket_search_use_case is None:
        _websocket_search_use_case = MultiHopSearchWebSocketUseCase()
    return _websocket_search_use_case
