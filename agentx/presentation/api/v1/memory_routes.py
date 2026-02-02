"""Memory routes facade for backward compatibility.

This facade maintains backward compatibility with existing imports.
Actual implementation has been moved to the memory/ subdirectory.

Deprecated: Import from agentx.presentation.api.v1.memory instead.
"""

# Re-export router for backward compatibility
from agentx.presentation.api.v1.memory.memory_routes import router

__all__ = ["router"]
