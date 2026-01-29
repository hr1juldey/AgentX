# Agent Layer

**Purpose**: DSPy agents, tools, and LangGraph integration.

## Structure

- `dspy_signatures/`: DSPy signature definitions
- `tools/`: DSPy tool implementations
- `dspy_agents/`: ReAct agents (Main, Analyst, Designer, Memory)
- `nodes/`: LangGraph node functions
- `graph.py`: LangGraph StateGraph definition
- `state.py`: AgentState TypedDict with ui_message_reducer
- `ui.tsx`: React components (colocated with graph!)

## Key Pattern: LangGraph Server-Driven UI (C007)

```python
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    ui: Annotated[Sequence[AnyUIMessage], ui_message_reducer]

async def designer_node(state: AgentState):
    existing_widgets = [msg.name for msg in state.ui]  # State awareness!
    push_ui_message("card", {"title": "...", "content": "..."}, message=message)
    return {"messages": [message]}
```

## Component Colocation

`ui.tsx` is placed next to `graph.py` in this directory for industry-standard LangSmith/LangChain integration.

## Files

- `main_signatures.py`: Main, Analyst, Designer, Memory, ToolExecutor signatures
- `main_tools.py`: Calculator, web search, time, weather tools
- `main_react_agent.py`: MainDSPyReActAgent and agent singletons
