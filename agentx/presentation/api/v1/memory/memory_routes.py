"""Memory REST API routes facade.

This facade composes all memory endpoints into a single router.
"""

from fastapi import APIRouter

from agentx.presentation.api.v1.memory.endpoints.consolidate import (
    consolidate_endpoint_config,
    consolidate_memory,
)
from agentx.presentation.api.v1.memory.endpoints.health import (
    active_states_endpoint_config,
    get_active_states,
    health_check,
    health_endpoint_config,
)
from agentx.presentation.api.v1.memory.endpoints.search import (
    search_endpoint_config,
    search_memory,
)
from agentx.presentation.api.v1.memory.endpoints.store import (
    store_endpoint_config,
    store_memory,
)


router = APIRouter()


# POST endpoints
router.post(**store_endpoint_config)(store_memory)
router.post(**search_endpoint_config)(search_memory)
router.post(**consolidate_endpoint_config)(consolidate_memory)


# GET endpoints
router.get(**health_endpoint_config)(health_check)
router.get(**active_states_endpoint_config)(get_active_states)


__all__ = ["router"]
