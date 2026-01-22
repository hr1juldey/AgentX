# =============================================================================
# AGENTX Multi-Hop Search - Hop Progress Tracker
# =============================================================================
# Progress tracking and event sending for hop execution
# =============================================================================

from typing import Any


class HopProgressTracker:
    """Tracks and sends progress updates during hop execution."""

    def __init__(
        self,
        progress_callback: Any,
        max_hops: int,
    ):
        """Initialize progress tracker.

        Args:
            progress_callback: Callback for progress updates
            max_hops: Maximum number of hops
        """
        self.progress_callback = progress_callback
        self.max_hops = max_hops

    def send_hop_start(
        self,
        hop_number: int,
        strategy: str,
        search_query: str,
    ) -> None:
        """Send hop start event.

        Args:
            hop_number: Current hop number
            strategy: Search strategy being used
            search_query: Query being executed
        """
        self._send_progress_event(
            event_type="hop_start",
            hop_number=hop_number,
            message=f"Hop {hop_number}: {strategy}",
            progress=(hop_number - 1) / self.max_hops,
            query_used=search_query,
        )

    def send_documents_found(
        self,
        hop_number: int,
        results_count: int,
    ) -> None:
        """Send documents found event.

        Args:
            hop_number: Current hop number
            results_count: Number of documents found
        """
        self._send_progress_event(
            event_type="hop_progress",
            hop_number=hop_number,
            message=f"Found {results_count} documents",
            progress=(hop_number - 0.7) / self.max_hops,
            documents_found=results_count,
        )

    def send_assessing(self, hop_number: int) -> None:
        """Send assessing completeness event.

        Args:
            hop_number: Current hop number
        """
        self._send_progress_event(
            event_type="hop_progress",
            hop_number=hop_number,
            message="Assessing completeness...",
            progress=(hop_number - 0.4) / self.max_hops,
        )

    def send_complete(
        self,
        hop_number: int,
        reasoning: str,
    ) -> None:
        """Send hop complete event.

        Args:
            hop_number: Current hop number
            reasoning: Reason for completion
        """
        self._send_progress_event(
            event_type="hop_complete",
            hop_number=hop_number,
            message=reasoning,
            progress=1.0,
            reflection_reasoning=reasoning,
        )

    def _send_progress_event(
        self,
        event_type: str,
        hop_number: int,
        message: str,
        progress: float,
        eta_seconds: float | None = None,
        documents_found: int = 0,
        query_used: str | None = None,
        reflection_reasoning: str | None = None,
    ) -> None:
        """Send progress update via callback.

        Args:
            event_type: Type of event
            hop_number: Current hop number
            message: Progress message
            progress: Progress percentage (0-1)
            eta_seconds: Optional ETA
            documents_found: Number of documents found
            query_used: Search query used
            reflection_reasoning: Reflection reasoning
        """
        from services.multihop_search.execution.hop_helpers import send_progress_event

        send_progress_event(
            callback=self.progress_callback,
            event_type=event_type,
            hop_number=hop_number,
            total_hops=self.max_hops,
            message=message,
            progress=progress,
            eta_seconds=eta_seconds,
            documents_found=documents_found,
            query_used=query_used,
            reflection_reasoning=reflection_reasoning,
        )
