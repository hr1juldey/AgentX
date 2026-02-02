"""Search strategies facade for temporal RAG.

Re-exports search functionality from split components.
"""

from agentx.application.services.temporal_rag.multi_hop import (
    multi_hop_search,
)
from agentx.application.services.temporal_rag.temporal_search import (
    search_with_temporal_filter,
)

__all__ = [
    "search_with_temporal_filter",
    "multi_hop_search",
]
