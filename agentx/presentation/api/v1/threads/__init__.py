"""Thread routes module for Real AgentX v0.1.

Provides LangGraph streaming API endpoints compatible with @langchain/langgraph-sdk.
This module is a facade that re-exports from split components for backward compatibility.

Endpoints:
- POST /api/v1/threads - Create thread
- GET /api/v1/threads/{thread_id} - Get thread state
- DELETE /api/v1/threads/{thread_id} - Delete thread
- GET /api/v1/threads/{thread_id}/stream - Stream graph execution
- POST /api/v1/threads/{thread_id}/invoke - Execute graph once
"""

from agentx.presentation.api.v1.threads.thread_routes import router

__all__ = ["router"]
