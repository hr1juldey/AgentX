"""Response DTOs for AGENTX API."""

from pydantic import BaseModel


class AgentResponse(BaseModel):
    """Response from agent execution.

    Attributes:
        answer: Agent's answer
        reasoning: Agent's reasoning (if available)
        session_id: Session identifier
    """

    answer: str
    reasoning: str = ""
    session_id: str


class GraphResponse(BaseModel):
    """Response from graph operations.

    Attributes:
        graph_id: Graph identifier
        status: Operation status
        result: Operation result
    """

    graph_id: str
    status: str
    result: dict


class MemoryResponse(BaseModel):
    """Response from memory operations.

    Attributes:
        memories: Retrieved memories
        count: Number of memories
    """

    memories: list[dict]
    count: int
