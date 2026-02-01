# Spec: Coordinator Agent

**Domain**: agent-runtime
**Generated**: 2026-02-02
**Status**: Draft

---

## 1. Purpose

Define the Coordinator Agent that analyzes queries and deploys specialized sub-agents.

**Problem**: Single ReAct agent with 20+ tools causes hallucination and poor performance.

**Success Criteria**:
- Coordinator analyzes query and selects sub-agent
- Each sub-agent has maximum 5 tools (preferably 3)
- Coordinator provides reasoning for selection
- All DSPy signatures are class-based

---

## 2. Scope

### In Scope

- CoordinatorAgent DSPy class
- CoordinatorSignature DSPy signature
- Sub-agent deployment logic
- Reasoning output

### Out of Scope

- Sub-agent implementations (covered by research-sub-agent, widget-sub-agent, etc.)
- Tool limit enforcement (covered by base-react-agent spec)

---

## 3. Requirements

### 3.1 Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-CA-001 | Coordinator MUST analyze query complexity | Must |
| FR-CA-002 | MUST select appropriate sub-agent | Must |
| FR-CA-003 | MUST provide reasoning for selection | Should |
| FR-CA-004 | MUST support "direct" mode for simple queries | Should |
| FR-CA-005 | Class-based DSPy signature | Must |

---

## 4. Data Model

```python
# domain/models/coordinator.py
from pydantic import BaseModel, Field
from enum import Enum

class SubAgentType(str, Enum):
    """Types of sub-agents."""
    RESEARCH = "research"
    WIDGET = "widget"
    SYNTHESIS = "synthesis"
    MEMORY = "memory"
    DIRECT = "direct"

class CoordinatorDecision(BaseModel):
    """Decision from Coordinator Agent."""

    selected_agent: SubAgentType = Field(
        description="Which sub-agent should handle this query"
    )
    reasoning: str = Field(description="Why this agent was selected")
    sub_task: str = Field(description="Specific task for the sub-agent")
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="Confidence in this decision"
    )
```

---

## 5. API Contract

```python
# agent/react_agents/coordinator_agent.py
import dspy
from dspy import InputField, OutputField, Signature

class CoordinatorSignature(dspy.Signature):
    """Coordinator decides which sub-agent to deploy."""

    query: str = InputField(desc="User's original query")
    conversation_history: str = InputField(desc="Previous messages (optional)")
    available_agents: str = InputField(desc="List of available sub-agents")

    # Structured output
    selected_agent: str = OutputField(desc="Which sub-agent: research/widget/synthesis/memory/direct")
    reasoning: str = OutputField(desc="Why this agent")
    sub_task: str = OutputField(desc="Specific task for the sub-agent")

class CoordinatorAgent(dspy.Module):
    """Main coordinator that deploys specialized sub-agents.

    Each sub-agent has LIMITED tools (3-5 max) to prevent hallucination.
    """

    def __init__(
        self,
        research_agent,
        widget_agent,
        synthesis_agent,
        memory_agent,
    ):
        super().__init__()
        self.decide = dspy.Predict(CoordinatorSignature)

        # Sub-agents (each with limited tools)
        self.research_agent = research_agent
        self.widget_agent = widget_agent
        self.synthesis_agent = synthesis_agent
        self.memory_agent = memory_agent

    def forward(
        self,
        query: str,
        conversation_history: str = "",
    ) -> dspy.Prediction:
        """Decide which sub-agent handles this query.

        Args:
            query: User's query
            conversation_history: Optional conversation context

        Returns:
            dspy.Prediction: With selected_agent, reasoning, sub_task, result
        """
        # Get decision from LLM
        decision = self.decide(
            query=query,
            conversation_history=conversation_history or "",
            available_agents="research, widget, synthesis, memory, direct",
        )

        # Route to appropriate sub-agent
        agent = decision.selected_agent.lower()

        if agent == "research":
            result = self.research_agent(query=query)
        elif agent == "widget":
            result = self.widget_agent(query=query)
        elif agent == "synthesis":
            result = self.synthesis_agent(query=query)
        elif agent == "memory":
            result = self.memory_agent(query=query)
        else:  # direct
            result = dspy.Prediction(response=query)

        # Return combined result
        return dspy.Prediction(
            selected_agent=decision.selected_agent,
            reasoning=decision.reasoning,
            sub_task=decision.sub_task,
            result=result,
        )
```

---

## 6. Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| BR-CA-001 | Research for search queries | "search", "find", "compare" keywords |
| BR-CA-002 | Widget for UI queries | "show", "display", "chart" keywords |
| BR-CA-003 | Synthesis for summary | "summarize", "explain" keywords |
| BR-CA-004 | Memory for recall | "remember", "what did I say" keywords |
| BR-CA-005 | Direct for simple | Math, facts, simple questions |

---

## 7. Acceptance Criteria

- [ ] CoordinatorAgent analyzes query
- [ ] Routes to correct sub-agent
- [ ] Provides reasoning for selection
- [ ] Supports "direct" mode for simple queries
- [ ] Returns dspy.Prediction (not dict)
- [ ] Class-based signature
- [ ] Ruff and pyrefly checks pass

---

## 8. Test Scenarios

| Query | Expected Agent | Reason |
|-------|---------------|--------|
| "Compare iPhone vs Pixel" | research | Needs web search |
| "Show me a chart" | widget | Needs UI generation |
| "Summarize this" | synthesis | Needs text processing |
| "What did I ask earlier?" | memory | Needs memory retrieval |
| "What is 2+2?" | direct | Simple, no tools needed |

---

**Next**: See `research-sub-agent/spec.md` for Research Agent implementation.
