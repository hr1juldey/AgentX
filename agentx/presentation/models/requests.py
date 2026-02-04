"""Request DTOs for AGENTX API."""

from pydantic import BaseModel


class AgentRequest(BaseModel):
    """Request for agent execution.

    Attributes:
        query: User query/question
        user_id: User identifier
        agent_type: Optional agent type to use
    """

    query: str
    user_id: str
    agent_type: str = "conversation"


class GraphRequest(BaseModel):
    """Request for graph compilation/execution.

    Attributes:
        spec: Graph specification JSON
        input: Input data for graph execution
    """

    spec: dict
    input: dict


class MemoryRequest(BaseModel):
    """Request for memory operations.

    Attributes:
        query: Search query
        user_id: User identifier
    """

    query: str
    user_id: str
