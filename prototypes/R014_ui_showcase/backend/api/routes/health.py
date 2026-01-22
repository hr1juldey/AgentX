# =============================================================================
# AGENTX R014 - Health Check Routes
# =============================================================================

from typing import Any

from fastapi import APIRouter

from config.dspy import get_lm_info

router = APIRouter()
logger = logger = __import__("logging").getLogger(__name__)


@router.get("/health")
async def health_check() -> dict[str, Any]:
    """Health check endpoint with LLM configuration info."""
    lm_info = get_lm_info()
    return {
        "status": "healthy",
        "service": "R014 UI Showcase (DSPy Generative UI)",
        "llm": lm_info,
    }
