# =============================================================================
# AGENTX Multi-Hop Search - Async Execution Helpers
# =============================================================================
# Helper methods for async execution with graceful degradation
# =============================================================================

import asyncio
import logging

from core.async_compat import SafeAsyncExecutor
from services.multihop_search.schemas import HopEvent

logger = logging.getLogger(__name__)


class AsyncExecutionMixin:
    """Mixin providing async execution capabilities with hardware detection."""

    def _init_executor(self, module_name: str) -> SafeAsyncExecutor:
        """Initialize async executor with hardware detection.

        Args:
            module_name: Name of module for hardware detection

        Returns:
            SafeAsyncExecutor instance
        """
        return SafeAsyncExecutor(module_name)

    def _execute_hops_sync(self, orchestrator, question: str):
        """Execute hops using optimal execution strategy.

        Uses async internally if hardware supports it, otherwise runs sequentially.

        Args:
            orchestrator: HopOrchestrator instance
            question: The search question

        Returns:
            Tuple of (hop_answers, hop_contexts, hop_queries, hop_num)
        """
        if self.executor.use_async:
            return asyncio.run(orchestrator.execute_hops(question))
        return asyncio.run(orchestrator.execute_hops(question))

    def _send_progress(
        self,
        hop_number: int,
        message: str,
        progress: float,
    ) -> None:
        """Send progress update via callback.

        Args:
            hop_number: Current hop number
            message: Progress message
            progress: Progress value (0-1)
        """
        if self.progress_callback is None:
            return

        try:
            self.progress_callback(
                HopEvent(
                    event_type="hop_progress" if progress < 1.0 else "search_complete",
                    hop_number=hop_number,
                    total_hops=self.max_hops,
                    message=message,
                    progress=progress,
                )
            )
        except Exception:
            pass
