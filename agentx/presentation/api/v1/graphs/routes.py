"""Graph management API endpoints."""

from fastapi import APIRouter

from agentx.presentation.models.requests import GraphRequest
from agentx.presentation.models.responses import GraphResponse

router = APIRouter(prefix="/graphs", tags=["graphs"])


@router.post("/compile", response_model=GraphResponse)
async def compile_graph(request: GraphRequest) -> GraphResponse:
    """Compile a graph from specification.

    Args:
        request: Graph compilation request

    Returns:
        Compiled graph response

    Raises:
        NotImplementedError: If not yet implemented
    """
    raise NotImplementedError("POST /graphs/compile not yet implemented")


@router.post("/execute", response_model=GraphResponse)
async def execute_graph(request: GraphRequest) -> GraphResponse:
    """Execute a compiled graph.

    Args:
        request: Graph execution request

    Returns:
        Graph execution response

    Raises:
        NotImplementedError: If not yet implemented
    """
    raise NotImplementedError("POST /graphs/execute not yet implemented")
