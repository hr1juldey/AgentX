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

    def setup_master_agent_with_pipeline(
        self,
        widget_callback,  # type: ignore
        qa_callback,  # type: ignore
    ):
        """Create and fully configure a Master Agent with pipeline and hydrators.

        This encapsulates the complexity of setting up all pipeline agents
        and hydrators, maintaining a clean architectural boundary.

        Returns a configured Master Agent ready for execution.
        """
        from config.settings import settings
        from services.hydrators.card_hydrator import CardHydrator
        from services.hydrators.chart_hydrator import ChartHydrator
        from services.hydrators.form_hydrator import FormHydrator
        from services.hydrators.gallery_hydrator import GalleryHydrator
        from services.hydrators.image_hydrator import ImageHydrator
        from services.hydrators.markdown_hydrator import MarkdownHydrator
        from services.master_agent import DeliveryPlan, create_master_agent
        from services.pipeline.analyst import AnalystAgent
        from services.pipeline.data_contextualizer import DataContextualizerAgent
        from services.pipeline.designer import DesignerAgent
        from services.pipeline.presenter import PresenterAgent
        from services.pipeline.researcher import ResearcherAgent
        from services.pipeline.sequencer import SequencerAgent
        from services.pipeline.widget_selector import WidgetSelectorAgent

        # Create master agent
        master_agent = create_master_agent(
            widget_callback=widget_callback,
            qa_callback=qa_callback,
        )

        # Initialize all pipeline agents
        analyst = AnalystAgent()
        researcher = ResearcherAgent(searxng_url=settings.searxng_url)

        data_contextualizer = DataContextualizerAgent()
        designer = DesignerAgent()
        widget_selector = WidgetSelectorAgent()
        sequencer = SequencerAgent()
        presenter = PresenterAgent()

        # Initialize all hydrators
        hydrators = [
            ChartHydrator(),
            MarkdownHydrator(),
            CardHydrator(),
            FormHydrator(),
            ImageHydrator(),
            GalleryHydrator(),
        ]

        # Configure master agent with pipeline
        master_agent.set_pipeline_agents(
            analyst=analyst,
            researcher=researcher,
            data_contextualizer=data_contextualizer,
            designer=designer,
            widget_selector=widget_selector,
            sequencer=sequencer,
            presenter=presenter,
            hydrators=hydrators,
        )

        return master_agent, DeliveryPlan


# Singleton getter for dependency injection
_master_agent_use_case: MasterAgentUseCase | None = None


def get_master_agent_use_case() -> MasterAgentUseCase:
    """Get singleton instance of MasterAgentUseCase."""
    global _master_agent_use_case
    if _master_agent_use_case is None:
        _master_agent_use_case = MasterAgentUseCase()
    return _master_agent_use_case
