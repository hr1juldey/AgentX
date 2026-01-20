# =============================================================================
# AGENTX R014 - UI Showcase API Routes
# =============================================================================
# API endpoints for UI showcase
# =============================================================================

from datetime import datetime
from typing import Any

import dspy
from fastapi import APIRouter

from api.content_generator import ContentGenerator
from api.models import GenerateRequest, UIDescriptor
from api.routes_examples import router as examples_router
from config.dspy import configure_dspy, get_lm_info
from services.widget_spawner import get_widget_spawner_service

router = APIRouter()

# Include example data endpoints
router.include_router(examples_router)

# =============================================================================
# Configure DSPy with LLM from environment settings
# =============================================================================

# Configure DSPy once at module load using settings from .env
configure_dspy()


# =============================================================================
# Health Check
# =============================================================================


@router.get("/health")
async def health_check() -> dict[str, Any]:
    """Health check endpoint with LLM configuration info."""
    lm_info = get_lm_info()
    return {
        "status": "healthy",
        "service": "R014 UI Showcase (DSPy Generative UI)",
        "llm": lm_info,
    }


# =============================================================================
# Widget Generation Endpoints
# =============================================================================


@router.post("/mock/generate")
async def generate_content(request: GenerateRequest) -> UIDescriptor:
    """Generate UI content using DSPy + Ollama."""
    generator = ContentGenerator()

    try:
        if request.widget_type == "markdown":
            return await generator.generate_markdown(request.prompt)
        elif request.widget_type == "card":
            return await generator.generate_card(request.prompt)
        elif request.widget_type == "form":
            return await generator.generate_form(request.prompt)
        elif request.widget_type == "progress":
            return await generator.generate_progress(request.prompt)
        elif request.widget_type == "action":
            return await generator.generate_action(request.prompt)
        elif request.widget_type == "confirmation":
            return await generator.generate_confirmation(request.prompt)
        elif request.widget_type == "image":
            return await generator.generate_image(request.prompt)
        elif request.widget_type == "gallery":
            return await generator.generate_gallery(request.prompt)
        elif request.widget_type == "chart":
            return await generator.generate_chart(request.prompt)
        else:
            raise ValueError(f"Unknown widget type: {request.widget_type}")
    except Exception as e:
        # Fallback on error
        return UIDescriptor(
            id=f"error-{datetime.now().timestamp()}",
            type=request.widget_type,
            timestamp=datetime.now().isoformat(),
            title="Generation Error",
            content=f"Could not generate content: {str(e)}",
            metadata={"error": True},
        )


@router.post("/generate-widget")
async def generate_widget(request: GenerateRequest) -> dict[str, Any]:
    """Generate widget(s) using DSPy ReAct agent with automatic widget selection.

    This endpoint uses a DSPy ReAct agent that:
    1. Automatically analyzes what widgets are needed based on the query
    2. Can generate multiple widgets (e.g., chart + summary markdown)
    3. Returns a list of complete UI descriptors ready for rendering

    Unlike /mock/generate, this endpoint does NOT require widget_type to be specified.
    If widget_type is provided, it will force that type and skip ReAct reasoning.

    Returns:
        {
            "widgets": [...],  // List of UIDescriptor objects
            "tools_used": [...],  // Optional: list of tools called by ReAct
            "reasoning": "..."  // Optional: ReAct reasoning trace
        }
    """
    from typing import Any

    service = get_widget_spawner_service()

    try:
        # widget_type is optional - if None, multi-widget ReAct agent will decide
        response = await service.generate_widget(
            prompt=request.prompt,
            widget_type=request.widget_type if request.widget_type else None,
        )

        # Convert all WidgetDescriptors to UIDescriptor format for frontend compatibility
        widgets = [
            UIDescriptor(
                id=widget.id,
                type=widget.type,
                timestamp=datetime.now().isoformat(),
                title=widget.title,
                content=widget.content,
                metadata=widget.metadata or {},
                dismissible=widget.dismissible,
            )
            for widget in response.widgets
        ]

        return {
            "widgets": widgets,
            "tools_used": response.tools_used,
            "reasoning": response.reasoning,
        }
    except Exception as e:
        # Fallback on error - return single markdown widget with error message
        error_widget = UIDescriptor(
            id=f"error-{datetime.now().timestamp()}",
            type="markdown",
            timestamp=datetime.now().isoformat(),
            title="Widget Generation Error",
            content=f"**Error:** {str(e)}\n\nThe DSPy agent encountered an error while generating widgets.",
            metadata={"error": True, "format": "markdown"},
        )
        return {"widgets": [error_widget], "tools_used": None, "reasoning": None}
