"""Memory routes module for Real AgentX v0.1.

Provides memory REST API endpoints for storage, search, and consolidation.
This module is a facade that re-exports from split components.
"""

from agentx.presentation.api.v1.memory.memory_routes import router

__all__ = ["router"]
