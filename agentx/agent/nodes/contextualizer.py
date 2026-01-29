"""Contextualizer node for LangGraph.

Ported from R014: services/pipeline/contextualizer.py

Coordinates contextualizer tools for context reranking, filtering, and injection.
Improves research findings by enriching with relevant context.
"""

from typing import Any

from langchain_core.messages import AIMessage

from agentx.agent.state import AgentState
from agentx.agent.tools.contextualizer.contextualizer import ContextInjectorModule
from agentx.agent.tools.contextualizer.filter import ContextFilterModule
from agentx.agent.tools.contextualizer.reranker import RelevanceScorerModule


async def contextualizer_node(state: AgentState) -> dict[str, Any]:
    """Contextualizer node: Rerank, filter, and inject context.

    Coordinates:
    - Relevance scorer for reranking by relevance
    - Context filter for removing irrelevant chunks
    - Context injector for enriching findings

    Args:
        state: Current agent state

    Returns:
        Updated state with contextualized findings
    """
    # Get research findings and context
    research: dict[str, object] = state.get("_research", {})  # type: ignore[assignment]
    findings = str(research.get("findings", ""))
    citations = list(research.get("citations", []))  # type: ignore[arg-type]

    if not findings:
        return {
            "messages": [AIMessage(content="No research findings to contextualize.")],
            "total_tool_calls": state.get("total_tool_calls", 0),
        }

    # Build context chunks from citations
    context_chunks = _build_context_from_citations(citations)

    if not context_chunks:
        return {
            "messages": [AIMessage(content=findings)],
            "contextualized_data": {"findings": findings},
            "total_tool_calls": state.get("total_tool_calls", 0),
        }

    # Get user query
    messages = state["messages"]
    user_query: str = ""
    for msg in reversed(messages):
        if hasattr(msg, "content") and isinstance(msg.content, str):
            user_query = msg.content
            break

    # Initialize modules
    reranker = RelevanceScorerModule()
    filter_module = ContextFilterModule()
    injector = ContextInjectorModule()

    # Step 1: Rerank by relevance
    reranked_result = reranker.forward(query=user_query, context_chunks=context_chunks)
    reordered_context = reranked_result["reordered_context"]

    # Step 2: Filter irrelevant chunks
    filtered_result = filter_module.forward(
        query=user_query, context_chunks=reordered_context
    )
    filtered_context = filtered_result["filtered_context"]
    filter_stats = filtered_result["stats"]

    # Step 3: Inject context into findings
    injected_result = injector.forward(
        findings=findings,
        context=filtered_context,
        query=user_query,
    )
    enriched_findings = injected_result["enriched_findings"]
    injected_count = injected_result["injected_count"]

    # Create contextualization message
    contextualization_content = f"""Contextualized Findings:

{enriched_findings}

---
Context Statistics:
- Total sources: {len(citations)}
- After filtering: {filter_stats.get("kept", 0)}  # type: ignore[arg-type]
- Context injected: {injected_count} chunks
"""

    message = AIMessage(content=contextualization_content)

    return {
        "messages": [message],
        "contextualized_data": {
            "findings": enriched_findings,
            "filter_stats": filter_stats,
            "injected_count": injected_count,
        },
        "total_tool_calls": state.get("total_tool_calls", 0) + 1,
    }


def _build_context_from_citations(citations: list[dict]) -> list[dict]:
    """Build context chunks from research citations.

    Args:
        citations: List of citation dicts

    Returns:
        list of dict with text and source
    """
    context_chunks = []

    for citation in citations:
        title = citation.get("title", "")
        url = citation.get("url", "")
        snippet = citation.get("snippet", "")

        if snippet:
            context_chunks.append(
                {
                    "text": snippet,
                    "source": f"{title} ({url})",
                }
            )

    return context_chunks
