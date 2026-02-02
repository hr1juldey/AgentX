"""Execute agent query use case.

Orchestrates the agent query processing workflow using LangGraph.
Following the use case pattern from mimicus.

Actual implementation has been moved to the query/ subdirectory.
This facade maintains backward compatibility with existing imports.
"""

import logging

from agentx.application.dtos.agent_dtos import (
    ExecuteAgentQueryRequest,
    ExecuteAgentQueryResponse,
)
from agentx.application.use_cases.query import get_or_create_session
from agentx.application.use_cases.query.query_execution import execute_query

logger = logging.getLogger(__name__)


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
        """Initialize the use case."""
        pass

    async def execute(
        self, request: ExecuteAgentQueryRequest
    ) -> ExecuteAgentQueryResponse:
        """Execute an agent query.

        Args:
            request: The query request DTO.

        Returns:
            ExecuteAgentQueryResponse: The query response DTO.
        """
        logger.info(
            f"[ExecuteAgentQuery] Starting query execution: {request.query[:100]}..."
        )

        # Step 1: Get or create session
        session = await get_or_create_session(request)
        logger.info(f"[ExecuteAgentQuery] Session ID: {session.session_id}")

        # Step 2: Execute query
        response_text, reasoning, ui_components, tool_calls = await execute_query(
            str(session.session_id), request.query
        )

        # Step 3: Build response
        return ExecuteAgentQueryResponse(
            session_id=str(session.session_id),
            response=response_text,
            reasoning=reasoning,
            ui_components=ui_components,
            tool_calls=[],  # TODO: Extract from state if needed
        )


async def _get_or_create_session_legacy(request):
    """Legacy function for backward compatibility.

    Deprecated: Use get_or_create_session from query module instead.
    """
    return await get_or_create_session(request)


def _extract_ui_components_legacy(ui_messages):
    """Legacy function for backward compatibility.

    Deprecated: Use extract_ui_components from query module instead.
    """
    from agentx.application.use_cases.query.ui_extraction import extract_ui_components

    return extract_ui_components(ui_messages)
