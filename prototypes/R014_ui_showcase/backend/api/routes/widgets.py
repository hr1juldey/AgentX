# =============================================================================
# AGENTX R014 - Widget Generation Routes
# =============================================================================

from datetime import datetime
from typing import Any

from fastapi import APIRouter

from api.content_generator import ContentGenerator
from api.models import GenerateRequest, IntelligentGenerateRequest, UIDescriptor
from application.use_cases.widget_generation import get_widget_generation_use_case

router = APIRouter()
logger = __import__("logging").getLogger(__name__)


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
        return UIDescriptor(
            id=f"error-{datetime.now().timestamp()}",
            type=request.widget_type or "markdown",
            timestamp=datetime.now().isoformat(),
            title="Generation Error",
            content=f"Could not generate content: {str(e)}",
            metadata={"error": True},
        )


@router.post("/generate-widget")
async def generate_widget(request: GenerateRequest) -> dict[str, Any]:
    """Generate widget(s) using application layer use case."""
    logger.info(f"🔵 {request.prompt[:100]}...")

    try:
        from application.dtos.requests import GenerateWidgetRequest

        use_case = get_widget_generation_use_case()
        dto_request = GenerateWidgetRequest(
            prompt=request.prompt, widget_type=request.widget_type
        )
        widgets = await use_case.generate_widget(dto_request)

        # Convert DTOs back to UIDescriptor for frontend compatibility
        ui_descriptors = [
            UIDescriptor(
                id=w.id,
                type=w.type,
                timestamp=w.timestamp,
                title=w.title,
                content=w.content,
                metadata=w.metadata,
                dismissible=w.dismissible,
            )
            for w in widgets
        ]

        return {
            "widgets": ui_descriptors,
            "tools_used": None,
            "reasoning": None,
        }
    except Exception as e:
        logger.error(f"🔴 Widget: {e}")
        error_widget = UIDescriptor(
            id=f"error-{datetime.now().timestamp()}",
            type="markdown",
            timestamp=datetime.now().isoformat(),
            title="Widget Generation Error",
            content=f"**Error:** {str(e)}",
            metadata={"error": True, "format": "markdown"},
        )
        return {"widgets": [error_widget], "tools_used": None, "reasoning": None}


@router.post("/generate-intelligent")
async def generate_intelligent(request: IntelligentGenerateRequest) -> dict[str, Any]:
    """Generate intelligent UI using application layer use case."""
    logger.info(f"🤖 {request.prompt[:100]}...")

    try:
        from application.dtos.requests import (
            IntelligentGenerateRequest as AppIntelligentRequest,
        )

        use_case = get_widget_generation_use_case()
        dto_request = AppIntelligentRequest(
            prompt=request.prompt, device_context=request.device_context
        )
        widgets = await use_case.generate_intelligent(dto_request)

        # Convert DTOs back to UIDescriptor for frontend compatibility
        ui_descriptors = [
            UIDescriptor(
                id=w.id,
                type=w.type,
                timestamp=w.timestamp,
                title=w.title,
                content=w.content,
                metadata=w.metadata,
                dismissible=w.dismissible,
            )
            for w in widgets
        ]

        return {
            "widgets": ui_descriptors,
            "layout": "responsive",
            "design_system": {},
            "reasoning": "Generated via application layer",
        }

    except Exception as e:
        logger.error(f"🔴 Intelligent: {e}")
        error_widget = UIDescriptor(
            id=f"error-{datetime.now().timestamp()}",
            type="markdown",
            timestamp=datetime.now().isoformat(),
            title="Intelligent Generation Error",
            content=f"**Error:** {str(e)}",
            metadata={"error": True, "format": "markdown"},
        )
        return {
            "widgets": [error_widget],
            "layout": "simple_vertical",
            "design_system": {},
            "reasoning": f"Error: {str(e)}",
        }
