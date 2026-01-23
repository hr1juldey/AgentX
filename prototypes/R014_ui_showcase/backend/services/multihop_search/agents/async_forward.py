# =============================================================================
# AGENTX Multi-Hop Search - Async Forward Mixin
# =============================================================================
# Async forward method for high-performance async contexts
# =============================================================================

import time

from services.multihop_search.result_builder import build_search_result


class AsyncForwardMixin:
    """Mixin providing async forward method for direct async calls."""

    async def aforward(self, question: str):
        """Async forward method for direct async calls.

        Use this when calling from async context for better performance
        on multi-GPU systems like DGX Pro.

        Args:
            question: The search question

        Returns:
            Search result prediction
        """
        overall_start = time.time()

        (
            hop_answers,
            hop_contexts,
            hop_queries,
            hop_num,
        ) = await self._orchestrator.execute_hops(question)

        self._send_progress(hop_num, "Synthesizing final answer...", 0.95)

        final_result = self.synthesize_final(
            question=question,
            all_hop_answers=hop_answers,
            all_context=hop_contexts,
        )

        self._send_progress(hop_num, "Search complete", 1.0)

        return build_search_result(
            final_result=final_result,
            hop_answers=hop_answers,
            hop_queries=hop_queries,
            hop_num=hop_num,
            total_elapsed=time.time() - overall_start,
        )
