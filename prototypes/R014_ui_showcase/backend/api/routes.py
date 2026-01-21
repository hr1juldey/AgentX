# =============================================================================
# AGENTX R014 - UI Showcase API Routes
# =============================================================================
# API endpoints for UI showcase
# =============================================================================

import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter

from api.content_generator import ContentGenerator
from api.models import GenerateRequest, UIDescriptor, IntelligentGenerateRequest
from api.routes_examples import router as examples_router
from config.dspy import configure_dspy, get_lm_info
from services.widget_spawner import get_widget_spawner_service
from services.widget_spawner.intelligent_agent import IntelligentUIGenerator

router = APIRouter()
logger = logging.getLogger(__name__)

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
    logger.debug(f"🔵 /generate-widget called: prompt='{request.prompt}', widget_type={request.widget_type}")

    service = get_widget_spawner_service()

    try:
        # widget_type is optional - if None, multi-widget ReAct agent will decide
        logger.debug("🔵 Calling service.generate_widget...")
        response = await service.generate_widget(
            prompt=request.prompt,
            widget_type=request.widget_type if request.widget_type else None,
        )

        logger.debug(f"🔵 Service returned {len(response.widgets)} widgets")
        for i, widget in enumerate(response.widgets):
            logger.debug(f"🔵   Widget {i+1}: id={widget.id}, type={widget.type}, title={widget.title}")

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

        result = {
            "widgets": widgets,
            "tools_used": response.tools_used,
            "reasoning": response.reasoning,
        }
        logger.debug(f"🔵 Returning result: {len(result['widgets'])} widgets")
        return result
    except Exception as e:
        # Fallback on error - return single markdown widget with error message
        logger.error(f"🔴 Error generating widget: {e}", exc_info=True)
        error_widget = UIDescriptor(
            id=f"error-{datetime.now().timestamp()}",
            type="markdown",
            timestamp=datetime.now().isoformat(),
            title="Widget Generation Error",
            content=f"**Error:** {str(e)}\n\nThe DSPy agent encountered an error while generating widgets.",
            metadata={"error": True, "format": "markdown"},
        )
        return {"widgets": [error_widget], "tools_used": None, "reasoning": None}


@router.post("/generate-intelligent")
async def generate_intelligent(request: IntelligentGenerateRequest) -> dict[str, Any]:
    """Generate intelligent UI using three-tier DSPy architecture.

    This endpoint uses advanced DSPy patterns for automatic decision-making:
    1. ReAct - Context analysis (content type, user intent, device awareness)
    2. BestOfN - Generate 5 presentation options, select best
    3. Refine - Self-improve accessibility until WCAG AA compliance

    Key differences from /generate-widget:
    - NO widget_type required - system decides automatically
    - Device-aware layout selection (mobile vs desktop)
    - Automatic color scheme generation
    - Optional position suggestions (x, y coordinates)
    - WCAG accessibility validation

    Returns:
        {
            "widgets": [...],  // List of UIDescriptor with optional x, y
            "layout": "...",  // Selected layout pattern
            "design_system": {...},  // Color scheme, typography
            "reasoning": "..."  // Agent's reasoning
        }
    """
    logger.info(
        f"🤖 /generate-intelligent called: prompt='{request.prompt}', "
        f"device={request.device_context.get('type')}"
    )

    try:
        # Create intelligent generator
        generator = IntelligentUIGenerator()

        # Generate intelligent UI
        result = generator(
            user_query=request.prompt,
            device_context=request.device_context
        )

        # Convert widgets to UIDescriptor format
        widgets = [
            UIDescriptor(
                id=w.get("id", ""),
                type=w.get("type", "markdown"),
                timestamp=datetime.now().isoformat(),
                title=w.get("title"),
                content=w.get("content"),
                dismissible=w.get("dismissible", True),
                metadata=w.get("metadata", {}),
            )
            for w in result.widgets
        ]

        response = {
            "widgets": widgets,
            "layout": result.layout,
            "design_system": result.design_system,
            "reasoning": result.reasoning,
        }

        logger.info(f"🤖 Generated {len(widgets)} widgets with layout: {result.layout}")
        return response

    except Exception as e:
        logger.error(f"🤖 Error in intelligent generation: {e}", exc_info=True)
        # Fallback - return single markdown widget with error
        error_widget = UIDescriptor(
            id=f"error-{datetime.now().timestamp()}",
            type="markdown",
            timestamp=datetime.now().isoformat(),
            title="Intelligent Generation Error",
            content=f"**Error:** {str(e)}\n\nThe intelligent agent encountered an error.",
            metadata={"error": True, "format": "markdown"},
        )
        return {
            "widgets": [error_widget],
            "layout": "simple_vertical",
            "design_system": {},
            "reasoning": f"Error: {str(e)}",
        }
