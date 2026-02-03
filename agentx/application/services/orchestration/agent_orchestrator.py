"""Agent orchestrator service.

Coordinates LangGraph state machine + DSPy agents.
Following the service pattern from mimicus.
"""

from uuid import UUID

from agentx.agent.state import AgentState
from agentx.core.dependencies import ensure_dspy_configured


class AgentOrchestrator:
    """Orchestrates agent execution with LangGraph state machine.

    Coordinates:
    - LangGraph StateGraph invocation
    - DSPy agent coordination
    - UI state tracking
    - RAG context injection
    """

    def __init__(self) -> None:
        """Initialize the orchestrator with dependencies."""
        ensure_dspy_configured()
        # Lazy import to avoid circular dependency with agentx.agent.graph
        from agentx.agent.graph import get_graph

        self._graph = get_graph()

    async def execute_query(
        self,
        query: str,
        session_id: UUID,
        user_id: str,
        context: list[str] | None = None,
    ) -> dict:
        """Execute a query through the agent pipeline.

        Args:
            query: User's question or request.
            session_id: Session identifier.
            user_id: User identifier.
            context: Optional additional context.

        Returns:
            dict: Execution results with response, UI components, etc.
        """
        # Step 1: Prepare initial state
        initial_state: AgentState = {
            "messages": [],  # Will be populated with query message
            "ui": [],
            "session_id": str(session_id),
            "reasoning_steps": 0,
            "total_tool_calls": 0,
            "contextualized_data": {},
            "_analysis": {},
            "_research": {},
            "_widget_design": {},
            "_widget_selection": {},
        }

        # Step 2: Invoke LangGraph StateGraph
        # Note: In full implementation, would use astream() for streaming
        final_state = await self._graph.ainvoke(initial_state)  # type: ignore[attr-defined]

        # Step 3: Extract results
        return {
            "session_id": session_id,
            "response": self._extract_response(final_state),
            "reasoning_steps": final_state.get("reasoning_steps", 0),
            "tool_calls": final_state.get("total_tool_calls", 0),
            "ui_components": self._extract_ui_components(final_state),
        }

    def _extract_response(self, state: AgentState) -> str:
        """Extract response text from state.

        Args:
            state: Final agent state.

        Returns:
            str: Response text.
        """
        messages = state.get("messages", [])
        if messages:
            last_message = messages[-1]
            if hasattr(last_message, "content"):
                return str(last_message.content)
        return "No response generated"

    def _extract_ui_components(self, state: AgentState) -> list[dict]:
        """Extract UI components from state.

        Args:
            state: Final agent state.

        Returns:
            list[dict]: UI components as dicts.
        """
        ui_messages = state.get("ui", [])
        components = []
        for ui_msg in ui_messages:
            # Convert UI message to dict for JSON serialization
            components.append(
                {
                    "name": getattr(ui_msg, "name", "unknown"),
                    "props": getattr(ui_msg, "props", {}),
                }
            )
        return components
