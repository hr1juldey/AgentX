# AGENTX Agent Runtime LLD

**Version**: 1.0.0
**Date**: 2026-01-19
**Status**: Locked
**Dependencies**: domain_model.md, infrastructure_adapters.md

---

## Table of Contents

1. [DSPy Signatures](#1-dspy-signatures)
2. [DSPy Tools](#2-dspy-tools)
3. [DSPy Agents](#3-dspy-agents)
4. [LangGraph State Machines](#4-langgraph-state-machines)

---

## 1. DSPy Signatures

### 1.1 Main Signatures

**File**: `agent/dspy_signatures/main_signatures.py`

```python
import dspy
from typing import List


class MainAgentSignature(dspy.Signature):
    """Main agent reasoning signature for handling user queries."""

    user_query: str = dspy.InputField(desc="User's query or request")
    conversation_history: List[str] = dspy.InputField(desc="Conversation history (list of messages)")
    retrieved_context: str = dspy.InputField(desc="Retrieved context from RAG")
    reasoning: str = dspy.OutputField(desc="Step-by-step reasoning process")
    final_answer: str = dspy.OutputField(desc="Final response to user")


class ToolSelectionSignature(dspy.Signature):
    """Select appropriate tools based on query analysis."""

    query_analysis: str = dspy.InputField(desc="Analysis of user query")
    available_tools: List[str] = dspy.InputField(desc="List of available tool names")
    selected_tools: List[str] = dspy.OutputField(desc="Tools to use for this query")
    tool_rationale: str = dspy.OutputField(desc="Reasoning for tool selection")


class ConfidenceScoringSignature(dspy.Signature):
    """Score confidence in the generated response."""

    response: str = dspy.InputField(desc="Generated response")
    context_quality: str = dspy.InputField(desc="Quality of retrieved context")
    confidence_score: float = dspy.OutputField(desc="Confidence from 0.0 to 1.0")
    confidence_reasoning: str = dspy.OutputField(desc="Explanation of confidence score")
```

### 1.2 UI Signatures

**File**: `agent/dspy_signatures/ui_signatures.py`

```python
import dspy
from typing import List, Dict, Any


class SelectWidgetSignature(dspy.Signature):
    """Select the appropriate UI widget for displaying content."""

    content_type: str = dspy.InputField(desc="Type of content (text, data, action, etc.)")
    context: str = dspy.InputField(desc="Additional context for widget selection")
    widget_type: str = dspy.OutputField(desc="Selected widget type")
    widget_config: Dict[str, Any] = dspy.OutputField(desc="Widget configuration")


class ConfigureFormSignature(dspy.Signature):
    """Configure a form schema for user input."""

    required_fields: List[str] = dspy.InputField(desc="Fields required from user")
    context: str = dspy.InputField(desc="Context for form configuration")
    form_schema: Dict[str, Any] = dspy.OutputField(desc="Form schema definition")


class ShowCardSignature(dspy.Signature):
    """Generate a card widget with title and content."""

    title: str = dspy.InputField(desc="Card title")
    content: str = dspy.InputField(desc="Card content (markdown supported)")
    context: str = dspy.InputField(desc="Additional context")
    show_actions: bool = dspy.OutputField(desc="Whether to show action buttons")
    card_descriptor: Dict[str, Any] = dspy.OutputField(desc="Card widget descriptor")


class RequestConfirmationSignature(dspy.Signature):
    """Request user confirmation for an action."""

    action_description: str = dspy.InputField(desc="Description of action to confirm")
    risk_level: str = dspy.InputField(desc="Risk level: low, medium, high")
    confirmation_dialog: Dict[str, Any] = dspy.OutputField(desc="Confirmation dialog descriptor")


class UpdateProgressSignature(dspy.Signature):
    """Update a progress indicator."""

    task_name: str = dspy.InputField(desc="Name of the task")
    current_step: int = dspy.InputField(desc="Current step number")
    total_steps: int = dspy.InputField(desc="Total number of steps")
    progress_descriptor: Dict[str, Any] = dspy.OutputField(desc="Progress widget descriptor")
```

### 1.3 RAG Signatures

**File**: `agent/dspy_signatures/rag_signatures.py`

```python
import dspy
from typing import List, Dict, Any


class RetrievalSignature(dspy.Signature):
    """Retrieve relevant context for a query."""

    query: str = dspy.InputField(desc="User query")
    user_context: str = dspy.InputField(desc="Additional user context")
    retrieved_memories: List[Dict[str, Any]] = dspy.OutputField(desc="Retrieved memories")
    retrieval_summary: str = dspy.OutputField(desc="Summary of retrieved information")


class ContextInjectionSignature(dspy.Signature):
    """Decide whether to inject retrieved context."""

    query: str = dspy.InputField(desc="User query")
    retrieved_context: str = dspy.InputField(desc="Retrieved context from RAG")
    should_inject: bool = dspy.OutputField(desc="Whether to inject context")
    injection_rationale: str = dspy.OutputField(desc="Reasoning for injection decision")
    filtered_context: str = dspy.OutputField(desc="Filtered context to inject")
```

---

## 2. DSPy Tools

### 2.1 Main Tools

**File**: `agent/tools/main_tools.py`

```python
import dspy
import operator
import ast
from typing import Dict, Any


def safe_calculator(expression: str) -> str:
    """Safely evaluate a mathematical expression using AST parsing."""
    allowed_operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
    }

    def eval_node(node):
        if isinstance(node, ast.Expression):
            return eval_node(node.body)
        elif isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.BinOp):
            left = eval_node(node.left)
            right = eval_node(node.right)
            op_type = type(node.op)
            if op_type in allowed_operators:
                return allowed_operators[op_type](left, right)
            raise ValueError(f"Operator not allowed: {op_type}")
        elif isinstance(node, ast.UnaryOp):
            operand = eval_node(node.operand)
            op_type = type(node.op)
            if op_type in allowed_operators:
                return allowed_operators[op_type](operand)
            raise ValueError(f"Operator not allowed: {op_type}")
        else:
            raise ValueError(f"Expression type not allowed: {type(node)}")

    try:
        tree = ast.parse(expression, mode="eval")
        result = eval_node(tree)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"


def searxng_search(query: str) -> str:
    """Search the web using SearXNG for current information.

    Returns formatted search results.
    """
    import aiohttp
    import json

    async def _search():
        async with aiohttp.ClientSession() as session:
            params = {
                "q": query,
                "format": "json",
                "engines": "google,bing,duckduckgo",
            }
            async with session.get(
                "http://192.168.1.4:8080/search",
                params=params
            ) as response:
                data = await response.json()
                results = data.get("results", [])[:5]

                formatted = []
                for r in results:
                    formatted.append(f"- {r.get('title', '')}: {r.get('url', '')}")
                    formatted.append(f"  {r.get('content', '')[:200]}...")

                return "\n\n".join(formatted)

    import asyncio
    return asyncio.run(_search())


def get_current_weather(location: str) -> str:
    """Get current weather information for a location.

    Uses wttr.in service (no API key required).
    """
    import aiohttp

    async def _weather():
        async with aiohttp.ClientSession() as session:
            url = f"http://wttr.in/{location}?format=j1"
            async with session.get(url) as response:
                data = await response.json()
                current = data.get("current_condition", [{}])[0]

                temp = current.get("temp_C", "N/A")
                desc = current.get("weatherDesc", [{}])[0].get("value", "N/A")
                humidity = current.get("humidity", "N/A")
                wind = current.get("windspeedKmph", "N/A")

                return f"Weather in {location}: {desc}, {temp}°C, Humidity: {humidity}%, Wind: {wind} km/h"

    import asyncio
    return asyncio.run(_weather())


def company_mis_search(query: str) -> str:
    """Search company MIS for business data.

    This is a placeholder for company-specific data access.
    """
    return f"MIS search results for: {query}\n(Not implemented - requires company data source)"
```

### 2.2 UI Tools

**File**: `agent/tools/ui_tools.py`

```python
import dspy
from typing import Dict, Any, List
from datetime import datetime, timedelta
from uuid import UUID, uuid4


def render_markdown_block(text: str) -> str:
    """Render a markdown text block in the UI.

    Returns: UI descriptor ID
    """
    from ui.descriptors.markdown_block import MarkdownBlockDescriptor

    descriptor = MarkdownBlockDescriptor(
        descriptor_id=str(uuid4()),
        content=text,
        allow_copy=True,
    )

    # Store in UI component registry
    return f"MARKDOWN_BLOCK:{descriptor.descriptor_id}"


def render_card(title: str, content: str, actions: List[str]) -> str:
    """Render a card widget with title, content, and action buttons.

    Returns: UI descriptor ID
    """
    from ui.descriptors.card import CardDescriptor, CardAction

    card_actions = [
        CardAction(label=action, action_id=f"action_{i}")
        for i, action in enumerate(actions)
    ]

    descriptor = CardDescriptor(
        descriptor_id=str(uuid4()),
        title=title,
        content=content,
        actions=card_actions,
        dismissible=True,
    )

    return f"CARD:{descriptor.descriptor_id}"


def request_confirmation(action_description: str, risk_level: str = "medium") -> str:
    """Request user confirmation for an action.

    Returns: UI descriptor ID
    """
    from ui.descriptors.confirmation import ConfirmationDescriptor

    descriptor = ConfirmationDescriptor(
        descriptor_id=str(uuid4()),
        title="Confirmation Required",
        message=action_description,
        confirm_text="Confirm",
        cancel_text="Cancel",
        risk_level=risk_level,
    )

    return f"CONFIRMATION:{descriptor.descriptor_id}"


def update_progress(task_name: str, progress_percent: int) -> str:
    """Update a progress indicator for a long-running task.

    Returns: UI descriptor ID
    """
    from ui.descriptors.progress import ProgressDescriptor

    descriptor = ProgressDescriptor(
        descriptor_id=str(uuid4()),
        task_name=task_name,
        progress_percent=progress_percent,
        status_text=f"In progress: {progress_percent}%",
        indeterminate=False,
    )

    return f"PROGRESS:{descriptor.descriptor_id}"
```

---

## 3. DSPy Agents

### 3.1 Main DSPy ReAct Agent

**File**: `agent/dspy_agents/main_react_agent.py`

```python
import dspy
from typing import List, Dict, Any, Optional, Callable
from uuid import UUID

from agent.dspy_signatures.main_signatures import (
    MainAgentSignature,
    ToolSelectionSignature,
    ConfidenceScoringSignature
)


class MainDSPyReActAgent(dspy.Module):
    """Main agent using multi-signature ReAct pattern.

    Conference Room Pattern:
    - CEO Agent (this class) orchestrates specialists
    - UI Agent (UIDSPyAgent) handles UI generation
    - RAG Agent (RAGDSPyAgent) handles context retrieval
    """

    def __init__(
        self,
        tools: List[dspy.Tool],
        max_iters: int = 8,
        confidence_threshold: float = 0.7
    ):
        super().__init__()

        self.tools = tools
        self.max_iters = max_iters
        self.confidence_threshold = confidence_threshold

        # Sub-modules
        self.tool_selector = dspy.Predict(ToolSelectionSignature)
        self.confidence_scorer = dspy.Predict(ConfidenceScoringSignature)

        # Main ReAct loop
        self.react = dspy.ReAct(
            signature=MainAgentSignature,
            tools=tools,
            max_iters=max_iters
        )

    def forward(
        self,
        user_query: str,
        conversation_history: List[str],
        retrieved_context: str = ""
    ) -> dspy.Prediction:
        """Execute agent reasoning."""

        # Step 1: Select tools (optional optimization)
        tool_selection = self.tool_selector(
            query_analysis=self._analyze_query(user_query),
            available_tools=[tool.name for tool in self.tools]
        )

        # Step 2: Run ReAct with selected tools
        result = self.react(
            user_query=user_query,
            conversation_history=conversation_history,
            retrieved_context=retrieved_context
        )

        # Step 3: Score confidence
        confidence = self.confidence_scorer(
            response=result.final_answer,
            context_quality="high" if retrieved_context else "low"
        )

        # Step 4: Return prediction with metadata
        return dspy.Prediction(
            reasoning=result.reasoning,
            final_answer=result.final_answer,
            confidence_score=float(confidence.confidence_score),
            confidence_reasoning=confidence.confidence_reasoning,
            tool_calls=result.trajectory,
            reasoning_steps=self._extract_reasoning_steps(result.trajectory)
        )

    def _analyze_query(self, query: str) -> str:
        """Quick query analysis for tool selection."""
        # Simple keyword-based analysis
        # In production, use LLM for semantic analysis
        if any(word in query.lower() for word in ["calculate", "math", "multiply", "add"]):
            return "calculation"
        elif any(word in query.lower() for word in ["search", "find", "look up", "weather"]):
            return "information_retrieval"
        else:
            return "general"

    def _extract_reasoning_steps(self, trajectory: List[Any]) -> List[Dict[str, Any]]:
        """Extract reasoning steps from trajectory."""
        steps = []
        for i, step in enumerate(trajectory):
            steps.append({
                "step_number": i + 1,
                "thought": getattr(step, "thought", ""),
                "action": getattr(step, "action", None),
                "observation": getattr(step, "observation", None),
            })
        return steps

    async def execute(
        self,
        user_query: str,
        conversation_history: List[str],
        retrieved_context: str,
        ui_callback: Optional[Callable] = None
    ) -> dspy.Prediction:
        """Execute agent with optional UI callback for streaming."""
        # Run the forward pass
        result = self.forward(
            user_query=user_query,
            conversation_history=conversation_history,
            retrieved_context=retrieved_context
        )

        # Call UI callback if provided
        if ui_callback:
            for step in result.reasoning_steps:
                await ui_callback({
                    "type": "reasoning_step",
                    "step": step
                })

        return result
```

### 3.2 UI DSPy Agent

**File**: `agent/dspy_agents/ui_agent.py`

```python
import dspy
from typing import Dict, Any, List

from agent.dspy_signatures.ui_signatures import (
    SelectWidgetSignature,
    ConfigureFormSignature,
    ShowCardSignature,
    RequestConfirmationSignature,
    UpdateProgressSignature
)


class UIDSPyAgent(dspy.Module):
    """UI specialist agent for generating UI descriptors.

    Responsible for:
    - Selecting appropriate widgets
    - Configuring forms
    - Generating cards and confirmations
    - Updating progress indicators
    """

    def __init__(self):
        super().__init__()

        self.widget_selector = dspy.Predict(SelectWidgetSignature)
        self.form_configurer = dspy.Predict(ConfigureFormSignature)
        self_card_generator = dspy.Predict(ShowCardSignature)
        self.confirmation_requester = dspy.Predict(RequestConfirmationSignature)
        self.progress_updater = dspy.Predict(UpdateProgressSignature)

    def select_widget(
        self,
        content_type: str,
        context: str
    ) -> dspy.Prediction:
        """Select appropriate UI widget."""
        return self.widget_selector(
            content_type=content_type,
            context=context
        )

    def configure_form(
        self,
        required_fields: List[str],
        context: str
    ) -> dspy.Prediction:
        """Configure form schema."""
        return self.form_configurer(
            required_fields=required_fields,
            context=context
        )

    def show_card(
        self,
        title: str,
        content: str,
        context: str
    ) -> dspy.Prediction:
        """Generate card widget."""
        return self.card_generator(
            title=title,
            content=content,
            context=context
        )

    def request_confirmation(
        self,
        action_description: str,
        risk_level: str
    ) -> dspy.Prediction:
        """Request user confirmation."""
        return self.confirmation_requester(
            action_description=action_description,
            risk_level=risk_level
        )

    def update_progress(
        self,
        task_name: str,
        current_step: int,
        total_steps: int
    ) -> dspy.Prediction:
        """Update progress indicator."""
        return self.progress_updater(
            task_name=task_name,
            current_step=current_step,
            total_steps=total_steps
        )
```

### 3.3 RAG DSPy Agent

**File**: `agent/dspy_agents/rag_agent.py`

```python
import dspy
from typing import List, Dict, Any

from agent.dspy_signatures.rag_signatures import (
    RetrievalSignature,
    ContextInjectionSignature
)


class RAGDSPyAgent(dspy.Module):
    """RAG specialist agent for context retrieval and injection.

    Agentic RAG Pattern:
    - Retrieves relevant memories
    - Scores context quality
    - Decides whether to inject
    - Filters and formats context
    """

    def __init__(self, vector_store, memory_repository):
        super().__init__()

        self._vector_store = vector_store
        self._memory_repository = memory_repository

        self.context_retriever = dspy.Predict(RetrievalSignature)
        self.injection_decider = dspy.Predict(ContextInjectionSignature)

    def retrieve_context(
        self,
        query: str,
        user_id: str,
        limit: int = 10
    ) -> dspy.Prediction:
        """Retrieve and format context."""
        # Search memories
        memories = await self._memory_repository.search_memories(
            query=query,
            user_id=user_id,
            limit=limit
        )

        # Format for DSPy
        memory_summaries = [
            f"- {m.get('content', '')}" for m in memories
        ]
        memories_text = "\n".join(memory_summaries)

        # Use DSPy to summarize
        retrieval = self.context_retriever(
            query=query,
            user_context=memories_text
        )

        return dspy.Prediction(
            retrieved_memories=memories,
            retrieval_summary=retrieval.retrieval_summary,
            context_quality="high" if len(memories) > 3 else "low"
        )

    def should_inject_context(
        self,
        query: str,
        retrieved_context: str
    ) -> dspy.Prediction:
        """Decide whether to inject retrieved context."""
        decision = self.injection_decider(
            query=query,
            retrieved_context=retrieved_context
        )

        return dspy.Prediction(
            should_inject=decision.should_inject,
            injection_rationale=decision.injection_rationale,
            filtered_context=decision.filtered_context
        )
```

---

## 4. LangGraph State Machines

### 4.1 Backend State Machine

**File**: `agent/langgraph/backend_state_machine.py`

```python
from typing import TypedDict, List, Dict, Any, Literal
from uuid import UUID

from langgraph.graph import StateGraph, END
from domain.entities.enums import AgentStatus


class BackendLangGraphState(TypedDict):
    """Backend state for agent reasoning."""

    session_id: str
    user_query: str
    conversation_history: List[Dict[str, str]]
    retrieved_context: str
    reasoning_steps: List[Dict[str, Any]]
    current_step: int
    agent_status: AgentStatus
    confidence_score: float
    should_continue: bool
    error_message: str


def create_backend_state_machine() -> StateGraph:
    """Create LangGraph state machine for backend agent flow."""

    # Define state machine
    workflow = StateGraph(BackendLangGraphState)

    # Define nodes
    async def start_reasoning(state: BackendLangGraphState) -> BackendLangGraphState:
        """Start agent reasoning."""
        state["agent_status"] = AgentStatus.THINKING
        state["current_step"] = 0
        return state

    async def execute_step(state: BackendLangGraphState) -> BackendLangGraphState:
        """Execute single reasoning step."""
        state["current_step"] += 1
        # Agent execution logic here
        return state

    async def check_completion(state: BackendLangGraphState) -> BackendLangGraphState:
        """Check if reasoning is complete."""
        state["agent_status"] = AgentStatus.COMPLETED
        state["should_continue"] = False
        return state

    async def handle_error(state: BackendLangGraphState) -> BackendLangGraphState:
        """Handle agent error."""
        state["agent_status"] = AgentStatus.FAILED
        state["should_continue"] = False
        return state

    # Add nodes
    workflow.add_node("start", start_reasoning)
    workflow.add_node("execute_step", execute_step)
    workflow.add_node("complete", check_completion)
    workflow.add_node("error", handle_error)

    # Define edges
    workflow.add_edge("start", "execute_step")
    workflow.add_conditional_edges(
        "execute_step",
        lambda s: "complete" if s["should_continue"] else "continue",
        {
            "complete": "complete",
            "continue": "execute_step"
        }
    )
    workflow.add_edge("complete", END)
    workflow.add_edge("error", END)

    # Set entry point
    workflow.set_entry_point("start")

    return workflow.compile()
```

### 4.2 Frontend State Machine

**File**: `agent/langgraph/frontend_state_machine.py`

```python
from typing import TypedDict, List, Dict, Any, Literal
from uuid import UUID

from langgraph.graph import StateGraph, END
from domain.entities.enums import VisibilityState, UIComponentType


class FrontendLangGraphState(TypedDict):
    """Frontend state for UI lifecycle management."""

    session_id: str
    active_components: Dict[str, Dict[str, Any]]
    visibility_state: VisibilityState
    focused_component_id: str
    pending_forms: Dict[str, Dict[str, Any]]
    stream_queue: List[Dict[str, Any]]
    form_interrupt: bool


def create_frontend_state_machine() -> StateGraph:
    """Create LangGraph state machine for frontend UI flow."""

    workflow = StateGraph(FrontendLangGraphState)

    async def create_component(state: FrontendLangGraphState) -> FrontendLangGraphState:
        """Create new UI component."""
        return state

    async def update_component(state: FrontendLangGraphState) -> FrontendLangGraphState:
        """Update existing UI component."""
        return state

    async def dismiss_component(state: FrontendLangGraphState) -> FrontendLangGraphState:
        """Dismiss UI component."""
        return state

    async def handle_form_submit(state: FrontendLangGraphState) -> FrontendLangGraphState:
        """Handle form submission."""
        state["form_interrupt"] = False
        return state

    async def show_progress(state: FrontendLangGraphState) -> FrontendLangGraphState:
        """Show progress indicator."""
        return state

    # Add nodes
    workflow.add_node("create", create_component)
    workflow.add_node("update", update_component)
    workflow.add_node("dismiss", dismiss_component)
    workflow.add_node("form_submit", handle_form_submit)
    workflow.add_node("progress", show_progress)

    # Define edges
    workflow.add_edge("create", END)
    workflow.add_edge("update", END)
    workflow.add_edge("dismiss", END)
    workflow.add_edge("form_submit", END)
    workflow.add_edge("progress", END)

    workflow.set_entry_point("create")

    return workflow.compile()
```

---

**This agent runtime document is part of AGENTX LLD v1.0. All names and types are locked.**
