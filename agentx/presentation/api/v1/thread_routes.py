"""Thread routes facade for backward compatibility.

This facade maintains backward compatibility with existing imports.
Actual implementation has been moved to the threads/ subdirectory.

Deprecated: Import from agentx.presentation.api.v1.threads instead.
"""

from agentx.presentation.api.v1.threads.thread_routes import router

__all__ = ["router"]
