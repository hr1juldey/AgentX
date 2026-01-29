"""Execute agent query use case.

Orchestrates the agent query processing workflow.
Following the use case pattern from mimicus.
"""

from uuid import UUID


from agentx.application.dtos.agent_dtos import (
    ExecuteAgentQueryRequest,
    ExecuteAgentQueryResponse,
)
from agentx.application.dtos.ui_dtos import UIComponentDTO
from agentx.application.mappers.agent_session_mapper import AgentSessionMapper
from agentx.core.dependencies import get_agent_session_repository
from agentx.domain.entities.agent_session import AgentSessionEntity, SHA256Hash


class ExecuteAgentQueryUseCase:
    """Use case for executing agent queries.

    Orchestrates the complete query processing workflow:
    1. Retrieve or create session
    2. Analyze query with analyst agent
    3. Retrieve context from memory
    4. Process query with main agent
    5. Select UI widgets with designer agent
    6. Return response with UI components
    """

    def __init__(self) -> None:
        """Initialize the use case with dependencies."""
        self._session_repository = get_agent_session_repository()
        self._session_mapper = AgentSessionMapper()

    async def execute(
        self, request: ExecuteAgentQueryRequest
    ) -> ExecuteAgentQueryResponse:
        """Execute an agent query.

        Args:
            request: The query request DTO.

        Returns:
            ExecuteAgentQueryResponse: The query response DTO.
        """
        # Step 1: Get or create session
        session = await self._get_or_create_session(request)

        # Step 2: Analyze query (would use analyst agent)
        # analysis = await self._analyst_agent.analyze(query=request.query)

        # Step 3: Retrieve context from memory (would use memory agent)
        # context = await self._memory_agent.retrieve(query=request.query, session_id=session.session_id)

        # Step 4: Process with main agent (would use DSPy agent)
        # response = await self._main_agent(query=request.query, context=context)

        # Placeholder response
        response_text = f"Processed: {request.query}"

        # Step 5: Select UI components (would use designer agent)
        # ui_components = []  # Would be populated by designer agent

        # Step 6: Build response
        return ExecuteAgentQueryResponse(
            session_id=str(session.session_id),
            response=response_text,
            reasoning="Placeholder reasoning",
            ui_components=[
                UIComponentDTO(
                    component_id="placeholder",
                    component_type="markdown",
                    props={"content": response_text},
                )
            ],
            tool_calls=[],
        )

    async def _get_or_create_session(
        self, request: ExecuteAgentQueryRequest
    ) -> AgentSessionEntity:
        """Get existing session or create new one.

        Args:
            request: The query request DTO.

        Returns:
            AgentSessionEntity: The session entity.
        """
        if request.session_id:
            session = await self._session_repository.find_by_id(
                UUID(request.session_id)
            )
            if session:
                return session

        # Create new session
        user_hash = SHA256Hash.from_string(request.user_id or "anonymous")
        session = AgentSessionEntity.create(user_hash)
        await self._session_repository.save(session)
        return session
