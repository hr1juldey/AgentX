# =============================================================================
# AGENTX Multi-Hop Search - Sync Forward Mixin
# =============================================================================
# Synchronous forward method for DSPy compatibility
# =============================================================================

import time
import dspy

from services.multihop_search.result_builder import build_search_result


class SyncForwardMixin:
    """Mixin providing sync forward method for DSPy compatibility."""

    def forward(self, question: str) -> dspy.Prediction:
        """Execute multi-hop search (sync entry point for DSPy).

        This method runs synchronously (DSPy requirement) but internally
        uses async execution for I/O-bound operations when hardware allows.

        Args:
            question: The search question

        Returns:
            Search result prediction
        """
        overall_start = time.time()

        hop_answers, hop_contexts, hop_queries, hop_num = self._execute_hops_sync(
            self._orchestrator, question
        )

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
