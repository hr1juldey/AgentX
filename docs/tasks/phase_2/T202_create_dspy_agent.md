# T202: Create Main DSPy ReAct Agent

**Phase**: 2
**Estimated Time**: 45 minutes
**Dependencies**: T001, T200, T201
**Blocked By**: None

---

## Context

**LLD References**:
- `lld/agent_runtime.md` - Main ReAct agent definition
- `lld/incremental_release_plan.md` - Phase 2: Main DSPy agent

**Description**:
Creates the main DSPy ReAct agent that uses tools to answer user queries. Implements multi-signature pattern with tool selection and confidence scoring.

---

## Acceptance Criteria

**Passing Criteria**:
- MainDSPyReActAgent class exists
- Uses dspy.ReAct with tools
- Implements multi-signature pattern (tool selection, reasoning, confidence)
- Can be instantiated
- Has forward() method for queries

**Verification Commands**:
```bash
cd /home/riju279/Documents/Code/XRIG/AgentX/prototypes/R013_travel_planning_stream/backend

# Verify agent file exists
test -f agentx/agent/dspy_agents/main_react_agent.py && echo "Main agent exists"

# Verify import works
python3 -c "from agentx.agent.dspy_agents.main_react_agent import MainDSPyReActAgent; print('Import OK')"
```

---

## Implementation Steps

### Step 1: Create main ReAct agent

Create file `agentx/agent/dspy_agents/main_react_agent.py`:

```python
"""Main DSPy ReAct agent for AGENTX."""

import dspy
from typing import Optional

from agentx.agent.dspy_signatures import (
    MainAgentSignature,
    ToolSelectionSignature,
    ConfidenceScoringSignature,
)
from agentx.agent.tools.main_tools import wrap_tools
from agentx.core.config import get_settings


class MainDSPyReActAgent(dspy.Module):
    """Main agent using multi-signature ReAct pattern.

    This agent combines:
    1. Tool selection - Analyze query and select relevant tools
    2. ReAct reasoning - Step-by-step reasoning with tool use
    3. Confidence scoring - Evaluate response confidence

    Example:
        >>> agent = MainDSPyReActAgent()
        >>> result = agent(user_query="What is 2+2?", conversation_history="")
        >>> print(result.final_answer)
    """

    def __init__(
        self,
        max_iters: int = 8,
        confidence_threshold: float = 0.7
    ):
        super().__init__()
        self.max_iters = max_iters
        self.confidence_threshold = confidence_threshold

        # Get settings
        settings = get_settings()

        # Initialize DSPy sub-modules
        self.tool_selector = dspy.Predict(ToolSelectionSignature)
        self.react = dspy.ReAct(
            signature=MainAgentSignature,
            tools=wrap_tools(),
            max_iters=max_iters
        )
        self.confidence_scorer = dspy.Predict(ConfidenceScoringSignature)

    def forward(
        self,
        user_query: str,
        conversation_history: str = "",
        retrieved_context: str = ""
    ) -> dspy.Prediction:
        """Process user query through multi-signature pipeline.

        Args:
            user_query: User's question or request
            conversation_history: Previous conversation turns
            retrieved_context: Context from RAG or memory

        Returns:
            dspy.Prediction with reasoning, final_answer, confidence, tool_calls
        """
        # Step 1: Select tools based on query analysis
        tool_selection = self._select_tools(user_query)

        # Step 2: Run ReAct reasoning with selected tools
        react_result = self.react(
            user_query=user_query,
            conversation_history=conversation_history,
            retrieved_context=retrieved_context
        )

        # Step 3: Score confidence in the answer
        confidence = self._score_confidence(
            react_result.final_answer,
            user_query
        )

        return dspy.Prediction(
            reasoning=react_result.reasoning,
            final_answer=react_result.final_answer,
            confidence_score=confidence.confidence_score,
            confidence_reasoning=confidence.confidence_reasoning,
            tool_calls=react_result.trajectory,
            selected_tools=tool_selection.selected_tools,
        )

    def _select_tools(self, query: str) -> dspy.Prediction:
        """Select appropriate tools for the query.

        Args:
            query: User query to analyze

        Returns:
            Tool selection prediction
        """
        available_tools = "calculator, search, get_current_weather"
        query_analysis = f"User is asking: {query}"

        return self.tool_selector(
            query_analysis=query_analysis,
            available_tools=available_tools
        )

    def _score_confidence(
        self,
        response: str,
        query_context: str
    ) -> dspy.Prediction:
        """Score confidence in the generated response.

        Args:
            response: Generated answer
            query_context: Original query

        Returns:
            Confidence score prediction
        """
        return self.confidence_scorer(
            response=response,
            query_context=query_context
        )

    def is_confident(self, prediction: dspy.Prediction) -> bool:
        """Check if prediction meets confidence threshold.

        Args:
            prediction: Agent prediction

        Returns:
            True if confidence >= threshold
        """
        confidence = getattr(prediction, "confidence_score", 0.0)
        return confidence >= self.confidence_threshold


class AgentFactory:
    """Factory for creating configured agents."""

    _instance: Optional[MainDSPyReActAgent] = None

    @classmethod
    def create_agent(cls) -> MainDSPyReActAgent:
        """Create or return singleton agent instance.

        Returns:
            Configured MainDSPyReActAgent

        Note:
            Agent is warmed up on first creation for better performance.
        """
        if cls._instance is None:
            settings = get_settings()
            cls._instance = MainDSPyReActAgent(
                max_iters=settings.dspy_max_iters,
                confidence_threshold=settings.dspy_confidence_threshold
            )
            cls._warmup_agent(cls._instance)
        return cls._instance

    @classmethod
    def _warmup_agent(cls, agent: MainDSPyReActAgent) -> None:
        """Warm up the agent with a simple query.

        DSPy performs lazy compilation on first call. This ensures
        the agent is ready before processing real user queries.

        Args:
            agent: Agent to warm up
        """
        try:
            _ = agent(
                user_query="warmup",
                conversation_history="",
                retrieved_context=""
            )
        except Exception:
            # Warmup may fail if LLM not ready - that's OK
            pass

    @classmethod
    def reset(cls) -> None:
        """Reset singleton instance (for testing)."""
        cls._instance = None


def get_main_agent() -> MainDSPyReActAgent:
    """Get the main agent instance.

    Returns:
        Configured and warmed-up MainDSPyReActAgent
    """
    return AgentFactory.create_agent()
```

### Step 2: Update dspy_agents/__init__.py

Create file `agentx/agent/dspy_agents/__init__.py`:

```python
"""DSPy agents for AGENTX."""

from agentx.agent.dspy_agents.main_react_agent import (
    MainDSPyReActAgent,
    AgentFactory,
    get_main_agent,
)

__all__ = [
    "MainDSPyReActAgent",
    "AgentFactory",
    "get_main_agent",
]
```

---

## Expected Failures & Countermeasures

### Failure: DSPy ReAct compilation fails

**Likelihood**: Medium
**Symptoms**: DSPy compilation error or tool wrapping failure

**Countermeasures**:
1. Ensure tools from T201 are properly defined
2. Check DSPy version: `python3 -c "import dspy; print(dspy.__version__)"`
3. Verify tools return string values
4. Check signatures have correct field definitions

**Recovery Time**: 10 minutes

### Failure: Ollama not configured

**Likelihood**: High
**Symptoms**: Agent fails to invoke Ollama LLM

**Countermeasures**:
1. Ensure Ollama is running: `ollama serve`
2. Pull required model: `ollama pull gemma3:4b`
3. Check .env has correct OLLAMA_BASE_URL
4. Verify Ollama accessible: `curl http://localhost:11434/`

**Recovery Time**: 5 minutes

### Failure: Warmup fails

**Likelihood**: Low
**Symptoms**: Agent creation throws exception during warmup

**Countermeasures**:
1. Warmup failures are caught and ignored (expected behavior)
2. Agent still created, just not compiled yet
3. First real query will trigger compilation
4. Set DSPY_WARMUP_ENABLED=false in .env to skip

**Recovery Time**: 0 minutes (graceful degradation)

---

## Retroactive Measures

### Upstream Drift Recovery

**Scenario**: T200 signatures changed
**Detection**: Signature field names don't match
**Action**: Update agent to use new signature definitions

**Recovery Time**: 10 minutes

**Scenario**: T201 tools changed
**Detection**: Tool function names or signatures changed
**Action**: Update wrap_tools() to use new tools

**Recovery Time**: 5 minutes

### Downstream Impact

**Scenario**: Agent class name changes
**Prevention**: MainDSPyReActAgent class name is LOCKED
**Mitigation**: Update all imports and use sites
**Affected Tasks**: T203 (Agent Use Cases), T204 (Tests)

---

## Artifacts

**Files Created**:
- `agentx/agent/dspy_agents/main_react_agent.py` (Main agent, LOCKED)
- `agentx/agent/dspy_agents/__init__.py` (Package marker)

**Locked APIs**:
- `MainDSPyReActAgent` class name
- `forward()` method signature
- `is_confident()` method signature
- `get_main_agent()` function signature
- `AgentFactory` class name

---

## Quality Gates

**Quality Checks**:
- **Check**: Agent file exists
  - Command: `test -f agentx/agent/dspy_agents/main_react_agent.py && echo "OK"`
  - Expected: `OK`
  - Required: Yes

- **Check**: Agent can be imported
  - Command: `python3 -c "from agentx.agent.dspy_agents.main_react_agent import MainDSPyReActAgent; print('OK')"`
  - Expected: `OK`
  - Required: Yes

- **Check**: Agent can be instantiated
  - Command: `python3 -c "from agentx.agent.dspy_agents.main_react_agent import MainDSPyReActAgent; a = MainDSPyReActAgent(); print(type(a).__name__)"`
  - Expected: `MainDSPyReActAgent`
  - Required: Yes

---

## Notes

1. Multi-signature pattern: tool selection → ReAct → confidence
2. Singleton pattern via AgentFactory for performance
3. Warmup on first creation (DSPy compilation)
4. Confidence threshold from settings (default 0.7)
5. Max iterations from settings (default 8)
6. Returns dspy.Prediction with all intermediate results

---

## Completion Checklist

- [ ] main_react_agent.py created
- [ ] MainDSPyReActAgent implements multi-signature pattern
- [ ] AgentFactory singleton pattern implemented
- [ ] get_main_agent() factory function created
- [ ] dspy_agents/__init__.py exports agent
- [ ] Agent can be imported
- [ ] Agent can be instantiated
- [ ] Ready for T203 (Agent Use Cases)

---

**Task T202 is part of Phase 2: Main DSPy Agent**
**Locked APIs**: Agent class name, method signatures
