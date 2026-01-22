# =============================================================================
# AGENTX R014 - Mock Widget Generation Routes
# =============================================================================
# Legacy mock endpoints for backward compatibility
# =============================================================================

from datetime import datetime

from fastapi import APIRouter

from api.content_generator import ContentGenerator
from api.models import GenerateRequest, UIDescriptor

router = APIRouter()
logger = __import__("logging").getLogger(__name__)


@router.post("/mock/generate")
async def generate_content(request: GenerateRequest) -> UIDescriptor:
    """Generate UI content using DSPy + Ollama (legacy endpoint)."""
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
