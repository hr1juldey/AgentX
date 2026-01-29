"""Health check endpoint for Real AgentX v0.1.

Provides health status for monitoring and load balancers.
"""

from datetime import datetime

from fastapi import APIRouter
from pydantic import BaseModel

from agentx.core.config import get_settings

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "healthy"
    version: str
    timestamp: datetime
    dependencies: dict[str, str] = {}


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Check application health.

    Returns:
        HealthResponse: Health status information.
    """
    settings = get_settings()

    # Check dependencies (simplified)
    dependencies = {
        "redis": "unknown",  # Would ping Redis
        "sqlite": "unknown",  # Would check SQLite
        "ollama": "unknown",  # Would ping Ollama
    }

    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        timestamp=datetime.now(),
        dependencies=dependencies,
    )


@router.get("/")
async def root() -> dict[str, str]:
    """Root endpoint.

    Returns:
        dict: Basic API information.
    """
    settings = get_settings()
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
    }
