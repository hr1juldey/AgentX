# =============================================================================
# AGENTX R014 - Application Layer - Master Agent Use Cases
# =============================================================================
# Use case facades that wrap the existing Master Agent service
# =============================================================================


class MasterAgentUseCase:
    """Use case for Master Agent widget generation operations.

    This is a facade that wraps the existing Master Agent
    to provide a clean architectural boundary.

    Phase 1: Returns the factory function (no behavior changes).
    Phase 3: Will implement full use case logic with streaming support.
    """

    def create_master_agent(
        self,
        widget_callback,  # type: ignore
        qa_callback,  # type: ignore
    ):
        """Create a Master Agent instance with callbacks.

        Phase 1: Delegates to existing factory function.
        """
        from services.master_agent import create_master_agent

        return create_master_agent(
            widget_callback=widget_callback,
            qa_callback=qa_callback,
        )


# Singleton getter for dependency injection
_master_agent_use_case: MasterAgentUseCase | None = None


def get_master_agent_use_case() -> MasterAgentUseCase:
    """Get singleton instance of MasterAgentUseCase."""
    global _master_agent_use_case
    if _master_agent_use_case is None:
        _master_agent_use_case = MasterAgentUseCase()
    return _master_agent_use_case
