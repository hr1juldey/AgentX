"""Execute agent query use case.

Orchestrates the agent query processing workflow using LangGraph.
Following the use case pattern from mimicus.
"""

from uuid import UUID

from langchain_core.messages import HumanMessage

from agentx.agent.graph import get_graph
from agentx.application.dtos.agent_dtos import (
    ExecuteAgentQueryRequest,
    ExecuteAgentQueryResponse,
)
from agentx.application.dtos.ui_dtos import UIComponentDTO
from agentx.application.mappers.agent_session_mapper import AgentSessionMapper
from agentx.core.dependencies import (
    ensure_dspy_configured,
    get_agent_session_repository,
)
from agentx.domain.entities.agent_session import AgentSessionEntity, SHA256Hash


class ExecuteAgentQueryUseCase:
    """Use case for executing agent queries.

    Orchestrates the complete query processing workflow via LangGraph:
    1. Retrieve or create session
    2. Ensure DSPy is configured
    3. Invoke LangGraph with user query
    4. Extract response and UI components from final state
    5. Return response with UI components
    """

    def __init__(self) -> None:
        """Initialize the use case with dependencies."""
        self._session_repository = get_agent_session_repository()
        self._session_mapper = AgentSessionMapper()
        self._graph = get_graph().compile()  # type: ignore[arg-type]

    async def execute(
        self, request: ExecuteAgentQueryRequest
    ) -> ExecuteAgentQueryResponse:
        """Execute an agent query.

        Args:
            request: The query request DTO.

        Returns:
            ExecuteAgentQueryResponse: The query response DTO.
        """
        # Step 1: Ensure DSPy is configured
        ensure_dspy_configured()

        # Step 2: Get or create session
        session = await self._get_or_create_session(request)

        # Step 3: Build initial state for LangGraph
        initial_state = {
            "messages": [HumanMessage(content=request.query)],
            "ui": [],
            "session_id": str(session.session_id),
            "reasoning_steps": 0,
            "total_tool_calls": 0,
        }

        # Step 4: Invoke LangGraph (this runs the 7-pipeline agent sequence)
        final_state = await self._graph.ainvoke(initial_state)

        # Step 5: Extract response from final state
        messages = final_state.get("messages", [])
        response_text = ""
        reasoning = ""

        for msg in messages:
            if hasattr(msg, "content") and isinstance(msg.content, str):
                if not response_text:
                    response_text = msg.content
                else:
                    reasoning += msg.content + "\n"

        if not response_text:
            response_text = "No response generated."

        # Step 6: Extract UI components from state
        ui_messages = final_state.get("ui", [])
        ui_components = _extract_ui_components(ui_messages)

        # Step 7: Build response
        return ExecuteAgentQueryResponse(
            session_id=str(session.session_id),
            response=response_text,
            reasoning=reasoning or "Agent processing complete.",
            ui_components=ui_components,
            tool_calls=[],  # TODO: Extract from state if needed
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


def _extract_ui_components(ui_messages: list) -> list[UIComponentDTO]:
    """Extract UI components from LangGraph UI messages.

    Args:
        ui_messages: List of UI messages from LangGraph state.

    Returns:
        list[UIComponentDTO]: List of UI component DTOs.
    """
    components = []

    for msg in ui_messages:
        # Extract UI component data from message
        if hasattr(msg, "content"):
            content = msg.content
            if isinstance(content, dict):
                component_type = content.get("type", "markdown")
                props = content.get("props", {})
                component_id = content.get("id", f"component-{len(components)}")

                components.append(
                    UIComponentDTO(
                        component_id=component_id,
                        component_type=component_type,
                        props=props,
                    )
                )

    return components
