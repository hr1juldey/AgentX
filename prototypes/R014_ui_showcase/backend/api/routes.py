# =============================================================================
# AGENTX R014 - API Routes (DEPRECATED - Use api.routes module)
# =============================================================================
# ⚠️  DEPRECATED: This file is maintained for backward compatibility.
# The router has been split into:
#   - api.routes.health - Health check endpoint
#   - api.routes.widgets - Widget generation endpoints
#   - api.routes.search - Search endpoints (REST + WebSocket)
#   - api.routes.master_agent - Master Agent WebSocket endpoint
#
# Import from: from api.routes import router
# =============================================================================

# Import the combined router from the new module structure
from api.routes import router

# Also export the examples router for backwards compatibility
from api.routes_examples import router as examples_router

# Attach examples router to maintain backwards compatibility
router.include_router(examples_router)

__all__ = ["router"]
