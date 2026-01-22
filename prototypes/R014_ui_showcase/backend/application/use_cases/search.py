# =============================================================================
# AGENTX R014 - Application Layer - Search Use Cases
# =============================================================================
# Use case facades that wrap existing multi-hop search services
# =============================================================================

from application.dtos.requests import SearchRequest


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
        result = await agent.search(query=request.query)
        return result.answer


# Singleton getter for dependency injection
_search_use_case: SearchUseCase | None = None


def get_search_use_case() -> SearchUseCase:
    """Get singleton instance of SearchUseCase."""
    global _search_use_case
    if _search_use_case is None:
        _search_use_case = SearchUseCase()
    return _search_use_case
