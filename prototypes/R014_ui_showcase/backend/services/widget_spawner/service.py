# =============================================================================
# AGENTX Widget Spawner Service
# =============================================================================
# Service for managing DSPy widget generation with two-agent pattern
# =============================================================================

from services.widget_spawner.executor import WidgetExecutorAgent
from services.widget_spawner.models import MultiWidgetGenerationResponse
from services.widget_spawner.planner import WidgetPlannerAgent


class WidgetSpawnerService:
    """Service for managing DSPy widget generation using two-agent pattern.

    Architecture:
    1. WidgetPlannerAgent - Decides WHAT widgets to spawn
    2. WidgetExecutorAgent - Actually SPAWNS the widgets

    This provides clean separation of concerns:
    - Planner: Decision making, intent analysis, widget selection
    - Executor: Content generation, widget building

    Note: DSPy is configured globally via config/dspy.configure_dspy()
    which reads from environment variables (.env file).
    """

    def __init__(self):
        """Initialize the widget spawner service.

        LLM configuration is handled by config/dspy.py, not here.
        """
        self._planner: WidgetPlannerAgent | None = None
        self._executor: WidgetExecutorAgent | None = None
        self._configured = False

    def _ensure_configured(self) -> None:
        """Ensure DSPy agents are initialized.

        Note: DSPy is already configured in api/routes.py at module level.
        We only need to initialize the agents here.
        """
        if not self._configured:
            # Decision agent: Decides what to create
            self._planner = WidgetPlannerAgent()
            # Execution agent: Creates the widgets
            self._executor = WidgetExecutorAgent()
            self._configured = True

    async def generate_widget(
        self, prompt: str, widget_type: str | None = None
    ) -> MultiWidgetGenerationResponse:
        """Generate widget(s) based on the prompt.

        Uses the two-agent pattern:
        1. Planner analyzes prompt and decides what widgets are needed
        2. Executor generates each widget with appropriate content

        Args:
            prompt: User's prompt
            widget_type: Optional specific widget type to force (skips planning)

        Returns:
            Multi-widget response with all generated widgets
        """
        self._ensure_configured()
        assert self._planner is not None
        assert self._executor is not None

        # If widget_type is forced, skip planning and create single widget directly
        if widget_type is not None:
            plan = [{"type": widget_type, "context": prompt}]
        else:
            # Step 1: Plan what widgets to create
            plan_result = self._planner(user_query=prompt)
            plan = plan_result.plan

        # Step 2: Execute the plan and generate widgets
        widgets = self._executor.execute_plan(plan)

        return MultiWidgetGenerationResponse(
            widgets=widgets,
            tools_used=[item["type"] for item in plan],
            reasoning=f"Planned {len(plan)} widget(s): {', '.join([item['type'] for item in plan])}",
            preview_data={"plan": plan},
        )


# =============================================================================
# Singleton Instance
# =============================================================================

_widget_spawner_service: WidgetSpawnerService | None = None


def get_widget_spawner_service() -> WidgetSpawnerService:
    """Get the singleton widget spawner service instance."""
    global _widget_spawner_service
    if _widget_spawner_service is None:
        _widget_spawner_service = WidgetSpawnerService()
    return _widget_spawner_service
