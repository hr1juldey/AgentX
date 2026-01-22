# =============================================================================
# AGENTX R014 - Application Layer - Widget Generation Use Cases
# =============================================================================
# Use case facades that wrap existing services for clean architecture
# =============================================================================

from application.dtos.requests import GenerateWidgetRequest, IntelligentGenerateRequest
from domain.entities.ui_descriptor import UIDescriptor


class WidgetGenerationUseCase:
    """Use case for widget generation operations.

    This is a facade that wraps the existing WidgetSpawnerService
    to provide a clean architectural boundary.

    Returns domain entities, not DTOs.
    """

    async def generate_widget(
        self, request: GenerateWidgetRequest
    ) -> list[UIDescriptor]:
        """Generate widgets based on prompt and optional widget type.

        Returns domain entities (UIDescriptor).
        """
        from services.widget_spawner import get_widget_spawner_service

        service = get_widget_spawner_service()
        result = await service.generate_widget(
            prompt=request.prompt, widget_type=request.widget_type
        )

        # Convert service response to domain entities
        return [UIDescriptor(**widget.model_dump()) for widget in result.widgets]

    async def generate_intelligent(
        self, request: IntelligentGenerateRequest
    ) -> list[UIDescriptor]:
        """Generate intelligent UI with device context awareness.

        Returns domain entities (UIDescriptor).
        """
        from services.widget_spawner.intelligent_agent import IntelligentUIGenerator

        generator = IntelligentUIGenerator()
        result = generator(
            user_query=request.prompt, device_context=request.device_context
        )

        # Convert service response to domain entities
        return [
            UIDescriptor(
                id=w.get("id", ""),
                type=w.get("type", "markdown"),
                timestamp=w.get("timestamp", ""),
                title=w.get("title"),
                content=w.get("content"),
                dismissible=w.get("dismissible", True),
                metadata=w.get("metadata", {}),
            )
            for w in result.widgets
        ]


# Singleton getter for dependency injection
_widget_generation_use_case: WidgetGenerationUseCase | None = None


def get_widget_generation_use_case() -> WidgetGenerationUseCase:
    """Get singleton instance of WidgetGenerationUseCase."""
    global _widget_generation_use_case
    if _widget_generation_use_case is None:
        _widget_generation_use_case = WidgetGenerationUseCase()
    return _widget_generation_use_case
