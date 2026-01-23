# =============================================================================
# AGENTX R014 - API Routes Module
# =============================================================================
# Combined router from all route modules
# =============================================================================

from fastapi import APIRouter

from api.routes.e2e_test import router as e2e_test_router
from api.routes.health import router as health_router
from api.routes.master_agent import router as master_agent_router
from api.routes.search import router as search_router
from api.routes.widgets import router as widgets_router

# Combine all routers into one
router = APIRouter()

# Include individual routers with proper prefixes
router.include_router(health_router, tags=["health"])
router.include_router(widgets_router, tags=["widgets"])
router.include_router(search_router, tags=["search"])
router.include_router(master_agent_router, tags=["master-agent"])
router.include_router(e2e_test_router, prefix="/e2e", tags=["e2e-test"])

# Also export individual routers for direct use if needed
__all__ = [
    "router",
    "health_router",
    "widgets_router",
    "search_router",
    "master_agent_router",
]
