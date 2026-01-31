"""Researcher node for LangGraph.

Ported from R014: services/pipeline/researcher.py

Coordinates all researcher tools for web search and data extraction.
Executes searches, structures data, builds citations, and beautifies findings.
"""

from typing import Any

from langchain_core.messages import AIMessage

from agentx.agent.state import AgentState
from agentx.agent.tools.researcher.citation_builder import CitationBuilderModule
from agentx.agent.tools.researcher.data_structurer import DataStructurerModule
from agentx.agent.tools.researcher.findings_beautifier import FindingsBeautifierModule
from agentx.agent.tools.researcher.search_executor import SearchExecutorModule


async def researcher_node(state: AgentState) -> dict[str, Any]:
    """Researcher node: Execute web search and extract findings.

    Coordinates:
    - Search executor for web searches
    - Data structurer for organizing results
    - Citation builder for source attribution
    - Findings beautifier for presentation

    Args:
        state: Current agent state

    Returns:
        Updated state with research findings
    """
    # Get search terms from analyst
    analysis: dict[str, object] = state.get("_analysis", {})  # type: ignore[assignment]
    search_terms = list(analysis.get("search_terms", []))  # type: ignore[arg-type]
    domain = str(analysis.get("domain", "general"))  # type: ignore[arg-type]

    if not search_terms:
        return {
            "messages": [AIMessage(content="No search terms provided by analyst.")],
            "total_tool_calls": state.get("total_tool_calls", 0),
        }

    # Initialize modules
    search_executor = SearchExecutorModule()
    data_structurer = DataStructurerModule()
    citation_builder = CitationBuilderModule()
    findings_beautifier = FindingsBeautifierModule()

    # Get user query for relevance assessment
    messages = state["messages"]
    user_query: str = ""
    for msg in reversed(messages):
        if hasattr(msg, "content") and isinstance(msg.content, str):
            user_query = msg.content
            break

    # Execute searches for all terms
    all_results = []
    for term in search_terms[:3]:  # Limit to top 3 terms
        search_result = await search_executor.search(
            query=term, num_results=5, domain=domain
        )
        if "results" in search_result:
            all_results.extend(search_result["results"])

    if not all_results:
        return {
            "messages": [AIMessage(content="No search results found.")],
            "total_tool_calls": state.get("total_tool_calls", 0),
        }

    # Structure the data
    structured_result = data_structurer(
        raw_results=str(all_results), query_context=user_query
    )
    structured_data = structured_result["structured_data"]

    # Build citations
    citation_result = citation_builder(
        structured_data=structured_data, query=user_query
    )
    citations = citation_result["citations"]

    # Beautify findings
    beautified_result = findings_beautifier(
        structured_data=structured_data,
        citations=citations,
        query=user_query,
    )
    findings = beautified_result["beautified_findings"]
    confidence = beautified_result["confidence"]

    # Create research message
    research_content = f"""Research Findings:

Confidence Level: {confidence.upper()}

{findings}

Top Sources:
{chr(10).join(f"- {title}" for title in citation_result.get("top_sources", []))}  # type: ignore[arg-type]
"""

    message = AIMessage(content=research_content)

    return {
        "messages": [message],
        "_research": {
            "structured_data": structured_data,
            "citations": citations,
            "findings": findings,
            "confidence": confidence,
            "total_sources": len(citations),
        },
        "total_tool_calls": state.get("total_tool_calls", 0) + 1,
    }
