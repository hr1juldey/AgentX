# =============================================================================
# AGENTX Master Agent - Hydration Coordinator
# =============================================================================
# Coordinates widget hydrators for final data population
# =============================================================================

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


class HydrationCoordinator:
    """Coordinates widget hydrators for final data population.

    Runs all hydrators and aggregates their results.
    """

    def __init__(self, hydrators: list) -> None:
        """Initialize hydration coordinator.

        Args:
            hydrators: List of hydrator instances
        """
        self.hydrators = hydrators

    def hydrate_widgets(self, presentation_ready: dict[str, Any]) -> list:
        """Run all hydrators and aggregate results.

        Args:
            presentation_ready: Data from Presenter agent

        Returns:
            List of hydrated widgets
        """
        hydrated_widgets = []
        for hydrator in self.hydrators:
            try:
                result = hydrator.forward(
                    presentation_ready=presentation_ready,
                    researched_data=presentation_ready.get("researched_data", {}),
                    design=presentation_ready.get("design_context", {}),
                )
                if result:
                    hydrated_widgets.append(result)
            except Exception:
                # Log but continue with other hydrators
                pass

        return hydrated_widgets
