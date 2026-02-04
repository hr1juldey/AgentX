"""Agent-related API endpoints."""

from fastapi import APIRouter

from agentx.presentation.models.requests import AgentRequest
from agentx.presentation.models.responses import AgentResponse

router = APIRouter(prefix="/agents", tags=["agents"])


@router.post("/execute", response_model=AgentResponse)
async def execute_agent(request: AgentRequest) -> AgentResponse:
    """Execute an agent with the given query.

    Args:
        request: Agent execution request

    Returns:
        Agent response

    Raises:
        HTTPException: If execution fails
        NotImplementedError: If not yet implemented
    """
    raise NotImplementedError("POST /agents/execute not yet implemented")


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str) -> AgentResponse:
    """Get agent information.

    Args:
        agent_id: Agent identifier

    Returns:
        Agent information

    Raises:
        HTTPException: If agent not found
        NotImplementedError: If not yet implemented
    """
    raise NotImplementedError("GET /agents/{id} not yet implemented")
