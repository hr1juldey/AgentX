# =============================================================================
# AGENTX R013 - API Routes
# =============================================================================
# Main router and health check
# =============================================================================

import logging

from fastapi import APIRouter
from services.chains.travel_chain import TravelPlanningChain

from api.travel_chain_ws import travel_websocket
from api.travel_stream_ws import travel_websocket_stream

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize chain
travel_chain = TravelPlanningChain()

# Will be set by main.py after warmup to avoid circular import
_travel_agent = None


def set_travel_agent(agent) -> None:
    """Set the travel agent from main.py to avoid circular import.

    Called during startup after agent is warmed up.
    """
    global _travel_agent
    _travel_agent = agent


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "prototype": "R013"}


# Register WebSocket endpoints
router.add_websocket_route("/ws/travel", travel_websocket)
router.add_websocket_route("/ws/travel/stream", travel_websocket_stream)
