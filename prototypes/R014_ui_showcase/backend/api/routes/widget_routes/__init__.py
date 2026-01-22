# =============================================================================
# AGENTX R014 - Widget Routes Package
# =============================================================================

from fastapi import APIRouter

from api.routes.widget_routes.endpoints import router as endpoints_router
from api.routes.widget_routes.mock import router as mock_router

# Combine all routers
router = APIRouter()
router.include_router(mock_router)
router.include_router(endpoints_router)

__all__ = ["router"]
