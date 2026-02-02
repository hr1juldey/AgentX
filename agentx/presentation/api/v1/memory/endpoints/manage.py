"""Management endpoints facade for memory routes.

Re-exports consolidation, health check, and active states endpoints.
"""

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

__all__ = [
    "consolidate_memory",
    "health_check",
    "get_active_states",
    "consolidate_endpoint_config",
    "health_endpoint_config",
    "active_states_endpoint_config",
]
