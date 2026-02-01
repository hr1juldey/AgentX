# Spec: Research Sub-Agent

**Domain**: agent-runtime
**Generated**: 2026-02-02
**Status**: Draft

---

## 1. Purpose

Define the Research sub-agent with exactly 3 tools (search, scrape, cite) to prevent hallucination.

**Success Criteria**:
- ResearchAgent has exactly 3 tools
- Each tool is a simple function wrapped as dspy.Tool
- ReAct with max_iters=3
- Returns dspy.Prediction

---

## 2. Scope

### In Scope

- ResearchAgent DSPy class
- 3 tools: SearXNGSearch, WebScraper, CitationBuilder
- Tool limit enforcement (via BaseReActAgent)

### Out of Scope

- Tool implementations (infrastructure layer)
- BaseReActAgent (covered by base-react-agent spec)
- Coordinator deployment (covered by coordinator-agent spec)

---

## 3. Requirements

### 3.1 Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-RSA-001 | ResearchAgent MUST have exactly 3 tools | Must |
| FR-RSA-002 | Tools MUST be search_web, scrape_page, build_citation | Must |
| FR-RSA-003 | MUST use max_iters=3 | Must |
| FR-RSA-004 | MUST return dspy.Prediction | Must |

### 3.2 Non-Functional Requirements

| ID | Requirement | Target Metric |
|----|-------------|---------------|
| NFR-RSA-001 | File size | < 80 lines |
| NFR-RSA-002 | Execution time | < 30s |

---

## 4. API Contract

```python
# agent/react_agents/research_agent.py
import dspy
from dspy import Tool
from agent.react_agents.base_agent import BaseReActAgent

# Tool wrappers (infrastructure layer)
from infrastructure.external.searxng import searxng_search
from infrastructure.external.web_scraper import scrape_page
from infrastructure.external.citation_builder import build_citation

class ResearchAgent(dspy.Module):
    """Research specialist with ONLY 3 tools (prevents hallucination).

    Why 3 tools?
    - Prevents tool confusion
    - Forces focused scope
    - Reduces reasoning steps
    """

    def __init__(self):
        super().__init__()

        # 🔴 CRITICAL: Only 3 tools (prevents tool confusion)
        tools = [
            Tool(searxng_search, name="search_web"),
            Tool(scrape_page, name="scrape_page"),
            Tool(build_citation, name="build_citation"),
        ]

        # Validate tool count (raises if > 5)
        BaseReActAgent.validate_tool_count(tools, max_tools=3)

        # ReAct with limited toolset
        self.react = dspy.ReAct(
            "query -> research_findings",
            tools=tools,
            max_iters=3,  # Limited iterations
        )

    def forward(self, query: str) -> dspy.Prediction:
        """Execute research with limited tools.

        Args:
            query: Research query

        Returns:
            dspy.Prediction: With research_findings, sources
        """
        result = self.react(query=query)

        # 🔴 CRITICAL: Return Prediction, not dict
        return dspy.Prediction(
            research_findings=result.research_findings,
            sources=result.sources,
        )
```

---

## 5. Tool Definitions

```python
# infrastructure/external/searxng.py
def searxng_search(query: str, limit: int = 5) -> str:
    """Search the web using SearXNG.

    Args:
        query: Search query
        limit: Max results

    Returns:
        str: Search results as text
    """
    # Implementation
    pass

# infrastructure/external/web_scraper.py
def scrape_page(url: str) -> str:
    """Scrape content from a URL.

    Args:
        url: URL to scrape

    Returns:
        str: Page content
    """
    # Implementation
    pass

# infrastructure/external/citation_builder.py
def build_citation(source: str, title: str, url: str) -> str:
    """Build a citation string.

    Args:
        source: Source name
        title: Title
        url: URL

    Returns:
        str: Formatted citation
    """
    return f"[{source}] {title} - {url}"
```

---

## 6. Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| BR-RSA-001 | Exactly 3 tools | Hard-coded in __init__ |
| BR-RSA-002 | No more tools | BaseReActAgent raises ValueError |
| BR-RSA-003 | max_iters=3 | ReAct parameter |

---

## 7. Acceptance Criteria

- [ ] ResearchAgent has exactly 3 tools
- [ ] Tools are search_web, scrape_page, build_citation
- [ ] max_iters=3 set
- [ ] Returns dspy.Prediction (not dict)
- [ ] File size < 80 lines
- [ ] Ruff and pyrefly checks pass

---

## 8. Test Scenarios

| Query | Expected Tools Used |
|-------|-------------------|
| "Find iPhone reviews" | search_web → scrape_page → build_citation |
| "What is climate change?" | search_web only |
| "Cite this source" | build_citation only |

---

**Next**: See `widget-sub-agent/spec.md` for Widget Agent implementation.
