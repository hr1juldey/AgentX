# =============================================================================
# AGENTX Multi-Hop Search - Time Estimator
# =============================================================================
# Heuristic time estimation tuned by LLM usage patterns
# =============================================================================

from __future__ import annotations

import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class HopTimingStats:
    """Statistics for a single hop type."""

    avg_time: float = 2.0  # Base estimate: 2 seconds per hop
    sample_count: int = 0
    total_time: float = 0.0

    def update(self, elapsed_time: float) -> None:
        """Update stats with new timing sample.

        Uses exponential moving average with alpha=0.2.
        """
        self.sample_count += 1
        self.total_time += elapsed_time
        # Exponential moving average
        alpha = 0.2
        self.avg_time = alpha * elapsed_time + (1 - alpha) * self.avg_time


@dataclass
class TimeEstimator:
    """Heuristic time estimator with learning from LLM behavior."""

    hop_stats: dict[str, HopTimingStats] = field(default_factory=dict)

    def estimate_hop_time(self, hop_type: str = "default") -> float:
        """Estimate time for a hop based on historical data.

        Args:
            hop_type: Type of hop (e.g., "INITIAL", "REFINE_TOPIC", "DISCOVER_NEW")

        Returns:
            Estimated time in seconds
        """
        if hop_type not in self.hop_stats:
            self.hop_stats[hop_type] = HopTimingStats()
        return self.hop_stats[hop_type].avg_time

    def record_hop_time(self, hop_type: str, elapsed_time: float) -> None:
        """Record actual hop time for learning.

        Args:
            hop_type: Type of hop
            elapsed_time: Actual elapsed time in seconds
        """
        if hop_type not in self.hop_stats:
            self.hop_stats[hop_type] = HopTimingStats()
        self.hop_stats[hop_type].update(elapsed_time)
        logger.debug(
            f"Recorded {hop_type} hop: {elapsed_time:.2f}s, "
            f"avg: {self.hop_stats[hop_type].avg_time:.2f}s"
        )

    def estimate_total_time(
        self,
        num_hops: int,
        hop_types: list[str],
    ) -> float:
        """Estimate total time for multi-hop search.

        Args:
            num_hops: Number of hops
            hop_types: Expected type of each hop

        Returns:
            Estimated total time in seconds
        """
        total = 0.0
        for i in range(num_hops):
            hop_type = hop_types[i] if i < len(hop_types) else "default"
            total += self.estimate_hop_time(hop_type)
        return total


# Global estimator instance
_time_estimator: TimeEstimator | None = None


def get_time_estimator() -> TimeEstimator:
    """Get or create global time estimator."""
    global _time_estimator
    if _time_estimator is None:
        _time_estimator = TimeEstimator()
    return _time_estimator
