# =============================================================================
# AGENTX R014 - Widget Generation Endpoints
# =============================================================================
# Main widget generation and intelligent UI endpoints
# =============================================================================

from datetime import datetime
from typing import Any

from fastapi import APIRouter

from api.models import GenerateRequest, IntelligentGenerateRequest, UIDescriptor
from application.use_cases.widget_generation import get_widget_generation_use_case

router = APIRouter()
logger = __import__("logging").getLogger(__name__)


def _convert_dto_to_ui_descriptor(widget) -> UIDescriptor:
    """Convert DTO to UIDescriptor for frontend compatibility.

    Args:
        widget: Widget DTO from use case

    Returns:
        UIDescriptor for frontend
    """
    return UIDescriptor(
        id=widget.id,
        type=widget.type,
        timestamp=widget.timestamp,
        title=widget.title,
        content=widget.content,
        metadata=widget.metadata,
        dismissible=widget.dismissible,
    )


def _create_error_widget(error: Exception, endpoint_name: str) -> UIDescriptor:
    """Create an error widget for display.

    Args:
        error: The exception that occurred
        endpoint_name: Name of the endpoint that failed

    Returns:
        Error widget descriptor
    """
    return UIDescriptor(
        id=f"error-{datetime.now().timestamp()}",
        type="markdown",
        timestamp=datetime.now().isoformat(),
        title=f"{endpoint_name} Error",
        content=f"**Error:** {str(error)}",
        metadata={"error": True, "format": "markdown"},
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
        ui_descriptors = [_convert_dto_to_ui_descriptor(w) for w in widgets]

        return {
            "widgets": ui_descriptors,
            "tools_used": None,
            "reasoning": None,
        }
    except Exception as e:
        logger.error(f"🔴 Widget: {e}")
        error_widget = _create_error_widget(e, "Widget Generation")
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
        ui_descriptors = [_convert_dto_to_ui_descriptor(w) for w in widgets]

        return {
            "widgets": ui_descriptors,
            "layout": "responsive",
            "design_system": {},
            "reasoning": "Generated via application layer",
        }

    except Exception as e:
        logger.error(f"🔴 Intelligent: {e}")
        error_widget = _create_error_widget(e, "Intelligent Generation")
        return {
            "widgets": [error_widget],
            "layout": "simple_vertical",
            "design_system": {},
            "reasoning": f"Error: {str(e)}",
        }
