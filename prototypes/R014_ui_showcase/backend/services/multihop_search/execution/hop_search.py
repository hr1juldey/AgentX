# =============================================================================
# AGENTX Multi-Hop Search - Hop Search Module
# =============================================================================
# Executes search for a single hop and builds context
# =============================================================================

from __future__ import annotations

import logging
import time
from typing import Any

logger = logging.getLogger(__name__)


class HopSearch:
    """Handles search execution for a single hop.

    SRP: Execute search and build context only.
    """

    def __init__(
        self,
        search_client: Any,
        docs_per_hop: int,
        time_estimator: Any,
    ) -> None:
        """Initialize hop search module.

        Args:
            search_client: Search client service
            docs_per_hop: Number of documents to retrieve
            time_estimator: Time estimator service
        """
        self.search_client = search_client
        self.docs_per_hop = docs_per_hop
        self.time_estimator = time_estimator

    async def execute(
        self,
        search_query: str,
        strategy: str,
    ) -> tuple[str, list[Any], float]:
        """Execute search and build context.

        Args:
            search_query: Query to search for
            strategy: Search strategy name for timing

        Returns:
            Tuple of (context, results, elapsed_time)
        """
        start_time = time.time()

        results = await self.search_client.search(
            query=search_query,
            max_results=self.docs_per_hop,
        )

        # Build context from results
        context_parts: list[str] = []
        for i, result in enumerate(results):  # type: ignore[bad-argument-type]
            context_parts.append(f"[{i + 1}] {result.title}\n{result.content}")

        context = "\n\n".join(context_parts)
        elapsed = time.time() - start_time

        # Record timing
        self.time_estimator.record_hop_time(strategy, elapsed)

        return context, results, elapsed

    def generate_query(
        self,
        question: str,
        hop_num: int,
        plan_result: Any,
    ) -> tuple[str, str]:
        """Generate search query for this hop.

        Returns:
            Tuple of (search_query, strategy)
        """
        if hop_num == 1:
            return question, "INITIAL"
        elif plan_result is not None:
            return (
                plan_result.next_query,  # type: ignore[missing-attribute]
                plan_result.strategy,  # type: ignore[missing-attribute]
            )
        else:
            return f"{question} details", "REFINE_TOPIC"
