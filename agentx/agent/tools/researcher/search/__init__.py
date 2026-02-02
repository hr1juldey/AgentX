"""Search Executor Module for Researcher agent.

Ported from R014: services/tools/researcher/search_executor.py

Executes web searches using SearXNG with async wrapper.
Provides configurable search with domain-specific optimization.
"""

from agentx.agent.tools.researcher.search.batch_ops import BatchSearchOperations
from agentx.agent.tools.researcher.search.result_parser import SearchResultParser
from agentx.agent.tools.researcher.search.searxng_client import SearXNGClient

__all__ = [
    "SearXNGClient",
    "SearchResultParser",
    "BatchSearchOperations",
]
