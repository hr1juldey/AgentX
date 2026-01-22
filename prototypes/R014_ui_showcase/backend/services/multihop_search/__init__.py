# =============================================================================
# AGENTX Multi-Hop Search Service
# =============================================================================
# DSPy-based multi-hop search with runtime reflection
# =============================================================================

from services.multihop_search.agents import (
    CompletenessAssessor,
    HopPlanner,
    MultiHopSearchAgent,
)
from services.multihop_search.schemas import (
    Citation,
    HopEvent,
    SearchRequest,
    SearchResult,
)
from services.multihop_search.search_client import SearXNGClient, get_search_client
from services.multihop_search.signatures import (
    AnswerWithSources,
    CheckCompleteness,
    GenerateNextQuery,
    GenerateSearchQuery,
    SynthesizeFinalAnswer,
)
from services.multihop_search.time_estimator import (
    HopTimingStats,
    TimeEstimator,
    get_time_estimator,
)

__all__ = [
    # Agents
    "CompletenessAssessor",
    "HopPlanner",
    "MultiHopSearchAgent",
    # Schemas
    "Citation",
    "HopEvent",
    "SearchRequest",
    "SearchResult",
    # Signatures
    "AnswerWithSources",
    "CheckCompleteness",
    "GenerateNextQuery",
    "GenerateSearchQuery",
    "SynthesizeFinalAnswer",
    # Clients
    "SearXNGClient",
    "get_search_client",
    # Time estimator
    "HopTimingStats",
    "TimeEstimator",
    "get_time_estimator",
]
