# GEPA (DSPy Training) Integration with LangGraph Orchestration

**Date**: 2026-02-04
**Research Focus**: Can GEPA train individual DSPy agents while LangGraph handles routing? How to separate concerns: training vs. orchestration.

---

## Executive Summary

**Key Finding**: DSPy's GEPA optimizer and LangGraph orchestration are **highly complementary** and designed to work together through a clean separation of concerns:

- **LangGraph** = Orchestration layer (workflow control, state management, multi-agent coordination)
- **DSPy + GEPA** = Training/Optimization layer (prompt optimization, automatic tuning, performance improvement)

**Critical Insight**: GEPA can train individual DSPy agents **independently** of LangGraph's orchestration logic. The trained agents are then "hot-swapped" into LangGraph nodes without breaking the workflow state.

---

## 1. Can GEPA Train Individual DSPy Agents While LangGraph Handles Routing?

### Answer: YES - Through Clean Separation of Concerns

#### Architecture Pattern

```
┌─────────────────────────────────────────────────────────────────┐
│                    LangGraph Orchestration                      │
│  (Routing, State Management, Multi-Agent Coordination)         │
└─────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┼─────────┐
                    ▼         ▼         ▼
        ┌──────────────┬──────────────┬──────────────┐
        │  DSPy Agent  │  DSPy Agent  │  DSPy Agent  │
        │   Module 1   │   Module 2   │   Module 3   │
        └──────────────┴──────────────┴──────────────┘
                    │
                    ▼
        ┌──────────────────────────────┐
        │      GEPA Optimizer          │
        │  (Independent Training)      │
        └──────────────────────────────┘
```

#### Key Points

1. **DSPy modules live inside LangGraph nodes** as executable components
2. **GEPA optimizes DSPy modules independently** through offline training
3. **LangGraph routing logic remains unchanged** - it just calls different node functions
4. **Hot-swapping is possible** because optimized modules expose the same API

### Evidence from Research

According to [LangGraph & DSPy: Orchestrating Multi-Agent AI Workflows](https://medium.com/@akankshasinha247/langgraph-dspy-orchestrating-multi-agent-ai-workflows-with-declarative-prompting-93b2bd06e995):

> "LangGraph fits into the Orchestration & Agent Framework layer, enabling complex, multi-agent LLM workflows. DSPy's role is in declarative prompting, ensuring prompt logic is reliable, testable, and maintainable."

From [Choosing Between DSPy and LangGraph for Agentic Workflows](https://www.linkedin.com/posts/devanshbhatt26_langgraph-overview-docs-by-langchain-activity-7396607119543758848-7k7x):

> "Use LangGraph for orchestration and DSPy for optimizing individual components."

---

## 2. How to Separate Concerns: Training vs. Orchestration

### Layered Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Application Layer                          │
│                  (User Interface, API)                      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Orchestration Layer (LangGraph)                │
│                                                              │
│  - Workflow orchestration                                   │
│  - State management                                         │
│  - Multi-agent coordination                                 │
│  - Conditional routing logic                                │
│  - Checkpointing & persistence                              │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│               Agent Layer (DSPy Modules)                    │
│                                                              │
│  - Individual DSPy programs (ReAct, ChainOfThought, etc.)   │
│  - Tool definitions                                         │
│  - Signature definitions                                    │
│  - Business logic                                           │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│           Training/Optimization Layer (GEPA)                │
│                                                              │
│  - Prompt optimization                                      │
│  - Automatic tuning                                         │
│  - Performance metric evaluation                            │
│  - Training data management                                 │
└─────────────────────────────────────────────────────────────┘
```

### Separation Principles

#### Orchestration Layer (LangGraph)

**Responsibilities**:
- Define workflow graphs (nodes, edges, conditions)
- Manage conversation state and context
- Handle parallel execution of independent agents
- Implement routing logic between agents
- Provide checkpointing for fault tolerance
- Enable time-travel debugging

**What it SHOULD NOT do**:
- Modify agent prompts directly
- Handle training logic
- Collect performance metrics for optimization

#### Agent Layer (DSPy Modules)

**Responsibilities**:
- Implement individual agent behaviors
- Define tool interfaces and signatures
- encapsulate business logic
- Return structured predictions

**What it SHOULD NOT do**:
- Manage workflow state
- Route to other agents
- Handle persistence

#### Training Layer (GEPA)

**Responsibilities**:
- Optimize DSPy module prompts
- Evaluate performance metrics
- Manage training datasets
- Save/load optimized configurations

**What it SHOULD NOT do**:
- Access LangGraph state
- Modify routing logic
- Handle runtime orchestration

### Integration Pattern: API-Based Separation

```python
# ========== Orchestration Layer (LangGraph) ==========
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END

class AgentState(TypedDict):
    goal: str
    route: Literal["search", "calc", "answer"]
    data: dict
    error: str | None

def router(state: AgentState) -> str:
    """Deterministic routing - NO training logic here"""
    g = state["goal"].lower()
    if "sum" in g or "compute" in g:
        return "calc"
    if "find" in g or "search" in g:
        return "search"
    return "answer"

# DSPy agents are called as regular functions
def search_node(state: AgentState):
    from agentx.agents.search_agent import search_agent  # DSPy module
    result = search_agent(query=state["goal"])
    return {"data": {"search_result": result}}

# ========== Agent Layer (DSPy Module) ==========
import dspy

class SearchAgent(dspy.Module):
    """DSPy agent - pure business logic"""
    def forward(self, query: str) -> dspy.Prediction:
        # Implementation here
        return dspy.Prediction(result="...")

search_agent = SearchAgent()

# ========== Training Layer (GEPA) ==========
def optimize_search_agent(trainset, metric):
    """Run GEPA optimization - NO LangGraph dependencies"""
    from dspy import GEPA

    optimizer = GEPA(
        metric=metric,
        max_iterations=10,
        max_labeled_demos=5,
    )

    optimized_agent = optimizer.compile(
        search_agent,  # The DSPy module
        trainset=trainset,
    )

    # Save optimized agent
    optimized_agent.save("optimized_search_agent.json")

    return optimized_agent
```

---

## 3. Collecting Training Data from LangGraph Workflows

### Key Insight: Decoupled Data Collection

GEPA can work **without labeled training data** using gradient-free optimization. However, for best results, collect data from production LangGraph workflows.

### Data Collection Strategies

#### Strategy 1: Passive Logging (Recommended)

```python
from typing import TypedDict
from langgraph.graph import StateGraph
from agentx.infrastructure.logging import TrainingDataLogger
import json

class AgentState(TypedDict):
    query: str
    agent_name: str
    result: str
    metadata: dict

# Global training data logger
training_logger = TrainingDataLogger(log_dir="/var/log/agentx/training")

def agent_node(state: AgentState):
    """Wrap DSPy agent calls with logging"""
    from agentx.agents.search_agent import search_agent

    # Execute DSPy agent
    prediction = search_agent(query=state["query"])

    # Log interaction for training
    training_logger.log_interaction(
        agent_name=state["agent_name"],
        input_data={"query": state["query"]},
        output_data=prediction,
        metadata=state.get("metadata", {}),
        timestamp=time.time(),
    )

    return {"result": prediction.result}
```

#### Strategy 2: Active Sampling with Metrics

```python
def evaluate_agent_node(state: AgentState):
    """Collect labeled data with explicit metrics"""
    from agentx.agents.search_agent import search_agent

    prediction = search_agent(query=state["query"])

    # Define metric function
    def metric_fn(gold, pred, trace=None):
        """Custom metric for this task"""
        # Implementation specific to your use case
        return evaluate_quality(gold, pred)

    # Log with metric score
    training_logger.log_with_metric(
        agent_name=state["agent_name"],
        input_data={"query": state["query"]},
        output_data=prediction,
        gold_label=state.get("expected_answer"),
        metric_fn=metric_fn,
    )
```

### DSPy Example Format

From [DSPy Examples Documentation](https://dspy.ai/deep-dive/data-handling/examples/):

```python
import dspy

# Create training examples
trainset = [
    dspy.Example(
        question="What is the capital of France?",
        answer="Paris"
    ).with_inputs("question"),  # Mark "question" as input

    dspy.Example(
        question="Calculate 123 * 456",
        answer="56088"
    ).with_inputs("question"),
]

# Examples can have any field keys and value types
qa_pair = dspy.Example(
    question="This is a question?",
    answer="This is an answer."
)

# Access fields
print(qa_pair.question)  # "This is a question?"
print(qa_pair.answer)    # "This is an answer."

# Get only input fields
inputs_only = qa_pair.inputs()

# Get only label fields
labels_only = qa_pair.labels()
```

### Metric Definition Pattern

From [DSPy Metrics Documentation](https://dspy.ai/learn/evaluation/metrics/):

```python
def validate_answer(example, pred, trace=None):
    """Simple metric: exact match"""
    return example.answer.lower() == pred.answer.lower()

# More complex metric with multiple checks
def validate_context_and_answer(example, pred, trace=None):
    # Check answer matches
    answer_match = example.answer.lower() == pred.answer.lower()

    # Check answer comes from context
    context_match = any(
        (pred.answer.lower() in c)
        for c in pred.context
    )

    if trace is None:  # Evaluation/optimization mode
        return (answer_match + context_match) / 2.0
    else:  # Bootstrapping mode
        return answer_match and context_match
```

### Using AI Feedback for Metrics

```python
class Assess(dspy.Signature):
    """Assess the quality of output along specified dimension."""
    assessed_text = dspy.InputField()
    assessment_question = dspy.InputField()
    assessment_answer: bool = dspy.OutputField()

def metric_with_ai_feedback(gold, pred, trace=None):
    """Use LLM to evaluate output quality"""
    correct = f"Does `{pred.output}` correctly answer `{gold.question}`?"
    engaging = "Is the text engaging and well-structured?"

    correct_eval = dspy.Predict(Assess)(
        assessed_text=pred.output,
        assessment_question=correct
    )
    engaging_eval = dspy.Predict(Assess)(
        assessed_text=pred.output,
        assessment_question=engaging
    )

    correct, engaging = [
        m.assessment_answer
        for m in [correct_eval, engaging_eval]
    ]

    score = (correct + engaging) if correct else 0

    if trace is not None:
        return score >= 2
    return score / 2.0
```

### Converting LangGraph Logs to DSPy Training Data

```python
def convert_logs_to_trainset(log_file: str, agent_name: str):
    """Convert LangGraph execution logs to DSPy training set"""
    trainset = []

    with open(log_file, "r") as f:
        for line in f:
            log_entry = json.loads(line)

            if log_entry["agent_name"] == agent_name:
                # Create DSPy Example
                example = dspy.Example(
                    **log_entry["input_data"],
                    **log_entry["output_data"]
                ).with_inputs(*log_entry["input_data"].keys())

                trainset.append(example)

    return trainset
```

---

## 4. Updating DSPy Agents Without Breaking LangGraph State

### Key Principle: Versioned Agent Modules

From [8 LangGraph Agent Patterns That Don't Break Under Load](https://medium.com/@kaushalsinh73/8-langgraph-agent-patterns-that-dont-break-under-load-9ea885070f59):

> "Use deterministic routing so concurrency and retries stay predictable."

### Pattern 1: Semantic Versioning

```python
# agents/search_agent/__init__.py
from agentx.agents.search_agent.v1 import SearchAgentV1
from agentx.agents.search_agent.v2 import SearchAgentV2

# Version registry
AGENT_VERSIONS = {
    "search": {
        "v1": SearchAgentV1,
        "v2": SearchAgentV2,  # GEPA-optimized version
    }
}

def get_agent(agent_name: str, version: str = "v1"):
    """Factory function to get agent version"""
    return AGENT_VERSIONS[agent_name][version]()

# Usage in LangGraph
def search_node(state: AgentState):
    agent_version = state.get("agent_version", "v1")
    agent = get_agent("search", agent_version)

    result = agent(query=state["query"])
    return {"result": result}
```

### Pattern 2: Feature Flags

```python
# core/config.py
from pydantic_settings import BaseSettings

class AgentSettings(BaseSettings):
    use_optimized_search: bool = False
    use_optimized_calculator: bool = True

    class Config:
        env_file = ".env"

settings = AgentSettings()

# LangGraph node
def search_node(state: AgentState):
    if settings.use_optimized_search:
        from agentx.agents.search_agent.optimized import optimized_search_agent
        agent = optimized_search_agent
    else:
        from agentx.agents.search_agent.base import base_search_agent
        agent = base_search_agent

    result = agent(query=state["query"])
    return {"result": result}
```

### Pattern 3: Hot Reload with Checkpointing

From [LangGraph Persistence Documentation](https://docs.langchain.com/oss/python/langgraph/persistence):

```python
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import StateGraph

# Create checkpoint saver
checkpointer = SqliteSaver.from_conn_string("agent_state.db")

# Build graph with checkpointing
graph = StateGraph(AgentState)
graph.add_node("search", search_node)
graph.add_node("calc", calc_node)
graph.add_edge(START, "search")
graph.add_edge("search", "calc")
graph.add_edge("calc", END)

compiled = graph.compile(checkpointer=checkpointer)

# Reload agent without breaking state
def reload_agent(agent_name: str, new_version):
    """Reload agent module while preserving graph state"""
    import importlib

    # Reload module
    module = importlib.import_module(f"agentx.agents.{agent_name}")
    importlib.reload(module)

    # LangGraph state remains intact
    # Next execution will use new agent code
```

### Pattern 4: A/B Testing with GEPA

```python
def ab_test_search_node(state: AgentState):
    """Route to optimized or baseline based on A/B test"""
    import random

    user_id = state.get("user_id")
    bucket = hash(user_id) % 2

    if bucket == 0:
        # Control: baseline agent
        from agentx.agents.search_agent.base import search_agent
    else:
        # Treatment: GEPA-optimized agent
        from agentx.agents.search_agent.optimized import search_agent

    result = search_agent(query=state["query"])

    # Log which version was used
    result["agent_version"] = "optimized" if bucket == 1 else "baseline"

    return {"result": result}
```

### Saving and Loading Optimized Agents

From [DSPy Saving Tutorial](https://dspy.ai/tutorials/saving/):

```python
# After GEPA optimization
optimized_agent = optimizer.compile(
    search_agent,
    trainset=trainset
)

# Method 1: Save to JSON
optimized_agent.save("optimized_search_agent.json")

# Method 2: Save manually
import json

config = {
    "prompt": optimized_agent.prompt,
    "demos": optimized_agent.demos,
    "hyperparameters": optimized_agent.hyperparameters,
}

with open("optimized_search_agent.json", "w") as f:
    json.dump(config, f, indent=2)

# Load optimized agent
def load_optimized_agent(path: str):
    with open(path, "r") as f:
        config = json.load(f)

    agent = SearchAgent()
    agent.prompt = config["prompt"]
    agent.demos = config["demos"]
    agent.hyperparameters = config["hyperparameters"]

    return agent

# Use in LangGraph
optimized_search_agent = load_optimized_agent("optimized_search_agent.json")
```

---

## 5. Best Practices for Trainable DSPy Modules in LangGraph

### 5.1 Production-Grade Patterns

From [8 LangGraph Agent Patterns That Don't Break Under Load](https://medium.com/@kaushalsinh73/8-langgraph-agent-patterns-that-dont-break-under-load-9ea885070f59):

#### 1. Deterministic Routing

```python
def router(state: AgentState) -> str:
    """Explicit router - not LLM-based"""
    goal = state["goal"].lower()

    if "sum" in goal or "compute" in goal:
        return "calc"
    if "find" in goal or "search" in goal:
        return "search"
    return "answer"
```

**Why**: LLM-based routing is unpredictable. Explicit routers make training and debugging easier.

#### 2. Circuit Breakers

```python
from tenacity import retry, stop_after_attempt, retry_if_exception_type

@retry(
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type(Exception)
)
def resilient_agent_call(agent, state: AgentState):
    """Wrap DSPy agent with retry logic"""
    return agent(query=state["query"])
```

**Why**: Prevents cascading failures when GEPA-optimized agents have issues.

#### 3. Idempotent State

```python
def agent_node(state: AgentState):
    """Node should produce same output for same input"""
    agent = get_agent("search")

    result = agent(query=state["query"])

    # Return new state, don't mutate existing
    return {
        **state,
        "result": result,
        "last_agent": "search",
    }
```

**Why**: Enables safe retries and checkpoint rollback.

#### 4. Batching

```python
from typing import List

def batch_agent_node(state: AgentState):
    """Process multiple queries in batch"""
    agent = get_agent("search")
    queries = state["queries"]

    # Batch processing
    results = [agent(query=q) for q in queries]

    return {"results": results}
```

**Why**: Reduces API calls and improves throughput.

#### 5. Cache-First RAG

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_agent(query: str):
    """Cache agent responses"""
    agent = get_agent("search")
    return agent(query=query)
```

**Why**: Reduces redundant LLM calls during training and inference.

#### 6. Schema Guards

```python
from pydantic import BaseModel, validator

class SearchResult(BaseModel):
    result: str
    confidence: float

    @validator("confidence")
    def check_confidence(cls, v):
        if not 0 <= v <= 1:
            raise ValueError("Confidence must be 0-1")
        return v

def agent_node(state: AgentState):
    agent = get_agent("search")
    raw_result = agent(query=state["query"])

    # Validate output
    validated = SearchResult(**raw_result)

    return {"result": validated}
```

**Why**: Catches invalid outputs from GEPA-optimized agents early.

#### 7. Tracing

```python
from langfuse import Langfuse

langfuse = Langfuse()

def agent_node(state: AgentState):
    agent = get_agent("search")

    with langfuse.trace(
        name="search_agent",
        input={"query": state["query"]}
    ) as trace:
        result = agent(query=state["query"])

        trace.end(
            output={"result": result},
            status="success"
        )

    return {"result": result}
```

**Why**: Essential for collecting training data and debugging GEPA optimizations.

### 5.2 GEPA Training Best Practices

From [DSPy GEPA Documentation](https://dspy.ai/api/optimizers/GEPA/overview/):

#### Start Small

```python
# Use small, representative dataset first
sample_trainset = trainset[:100]

# Quick test run
optimizer = GEPA(
    metric=metric,
    max_iterations=3,  # Start with few iterations
)

optimized = optimizer.compile(
    agent,
    trainset=sample_trainset,
)
```

#### Define Clear Metrics

```python
def metric(example, pred, trace=None):
    """Metric should reflect real business value"""
    # Check multiple dimensions
    accuracy = check_accuracy(example, pred)
    relevance = check_relevance(example, pred)
    safety = check_safety(pred)

    # Weighted score
    return (accuracy * 0.5 + relevance * 0.3 + safety * 0.2)
```

#### Use Reflection LLM

From [Building Multi-Agent RAG with DSPy and GEPA](https://kargarisaac.medium.com/building-and-optimizing-multi-agent-rag-systems-with-dspy-and-gepa-2b88b5838ce2):

```python
optimizer = GEPA(
    metric=metric,
    max_iterations=10,
    teacher_settings=TeacherSettings(
        model="gpt-4o",  # Use stronger model for reflection
    ),
)
```

#### Save Intermediate Results

```python
for iteration in range(10):
    optimized = optimizer.compile(agent, trainset)

    # Save checkpoint
    optimized.save(f"checkpoints/agent_iter_{iteration}.json")

    # Evaluate
    score = evaluator(optimized, devset, metric)
    print(f"Iteration {iteration}: {score}")
```

### 5.3 LangGraph Integration Checklist

- [ ] **Separate concerns**: LangGraph for orchestration, DSPy for agents, GEPA for training
- [ ] **Version agents**: Use semantic versioning for trained agents
- [ ] **Feature flags**: Allow easy rollback to baseline agents
- [ ] **Checkpointing**: Enable state persistence for fault tolerance
- [ ] **Deterministic routing**: Avoid LLM-based routing in LangGraph
- [ ] **Circuit breakers**: Wrap agent calls with retry logic
- [ ] **Schema guards**: Validate agent outputs before state updates
- [ ] **Tracing**: Collect logs for training data and debugging
- [ ] **Idempotent state**: Nodes should not mutate state directly
- [ ] **A/B testing**: Test optimized agents against baseline in production

---

## 6. Complete Integration Example

### GEPA Training Pipeline

```python
# train_agents.py
import dspy
from dspy import GEPA

def train_search_agent():
    """Train search agent with GEPA"""
    # Load training data from LangGraph logs
    trainset = convert_logs_to_trainset(
        "logs/search_agent.jsonl",
        agent_name="search"
    )

    # Load dev set
    devset = convert_logs_to_trainset(
        "logs/search_agent_dev.jsonl",
        agent_name="search"
    )

    # Define metric
    def metric(example, pred, trace=None):
        return example.answer.lower() in pred.result.lower()

    # Load base agent
    from agentx.agents.search_agent.base import SearchAgent
    agent = SearchAgent()

    # Configure GEPA
    optimizer = GEPA(
        metric=metric,
        max_iterations=10,
        max_labeled_demos=5,
        teacher_settings=TeacherSettings(model="gpt-4o"),
    )

    # Optimize
    optimized = optimizer.compile(
        agent,
        trainset=trainset,
        valset=devset,
    )

    # Save optimized agent
    optimized.save("agentx/agents/search_agent/optimized.json")

    # Evaluate
    from dspy.evaluate import Evaluate

    evaluator = Evaluate(
        devset=devset,
        num_threads=4,
        display_progress=True,
    )

    score = evaluator(optimized, metric=metric)
    print(f"Optimized agent score: {score}")

    return optimized

if __name__ == "__main__":
    train_search_agent()
```

### LangGraph Workflow with Optimized Agents

```python
# workflows/research_workflow.py
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver

class ResearchState(TypedDict):
    query: str
    search_results: list
    analysis: str
    agent_version: str

def research_router(state: ResearchState) -> Literal["search", "end"]:
    """Deterministic routing"""
    if not state.get("search_results"):
        return "search"
    return "end"

def search_node(state: ResearchState):
    """Search node with versioned agent"""
    from agentx.agents.search_agent import get_search_agent

    # Get agent version (default to optimized)
    version = state.get("agent_version", "optimized")
    agent = get_search_agent(version=version)

    result = agent(query=state["query"])

    return {"search_results": [result]}

def analysis_node(state: ResearchState):
    """Analysis node with versioned agent"""
    from agentx.agents.analysis_agent import get_analysis_agent

    agent = get_analysis_agent(version="optimized")
    result = agent(context=state["search_results"])

    return {"analysis": result}

def build_research_graph():
    """Build research workflow graph"""
    graph = StateGraph(ResearchState)

    graph.add_node("search", search_node)
    graph.add_node("analysis", analysis_node)

    graph.add_conditional_edges(
        START,
        research_router,
        {
            "search": "search",
            "end": END,
        }
    )

    graph.add_edge("search", "analysis")
    graph.add_edge("analysis", END)

    # Add checkpointing
    checkpointer = SqliteSaver.from_conn_string("research_state.db")

    return graph.compile(checkpointer=checkpointer)
```

---

## 7. Key Takeaways

### 7.1 Architecture Principles

1. **Separation of Concerns**: LangGraph (orchestration) vs. DSPy (agents) vs. GEPA (training)
2. **API-Based Integration**: DSPy modules expose clean interfaces to LangGraph
3. **Versioning**: Always version trained agents for easy rollback
4. **State Independence**: Agent optimization doesn't affect LangGraph state management

### 7.2 GEPA Training Workflow

```
1. Collect data from LangGraph logs
2. Convert to DSPy Examples format
3. Define metric function
4. Run GEPA optimization (offline)
5. Save optimized agent
6. Deploy via feature flag or version switch
7. Monitor performance in production
8. Iterate
```

### 7.3 Production Readiness

- Use deterministic routing in LangGraph
- Enable checkpointing for fault tolerance
- Implement circuit breakers for agent calls
- Validate agent outputs with schema guards
- Collect comprehensive traces for debugging
- Support A/B testing for optimized agents

---

## 8. Resources

### Official Documentation

- [DSPy Examples Documentation](https://dspy.ai/deep-dive/data-handling/examples/) - Training data format
- [DSPy Metrics Documentation](https://dspy.ai/learn/evaluation/metrics/) - Metric definition patterns
- [DSPy GEPA API](https://dspy.ai/api/optimizers/GEPA/overview/) - GEPA optimizer reference
- [DSPy Saving Tutorial](https://dspy.ai/tutorials/saving/) - Save/load optimized programs
- [LangGraph Persistence](https://docs.langchain.com/oss/python/langgraph/persistence) - State checkpointing
- [LangGraph Time-Travel](https://docs.langchain.com/oss/python/langgraph/use-time-travel) - State manipulation

### Articles & Tutorials

- [LangGraph + DSPy + GEPA: Agentic Researcher](https://rajapatnaik.com/blog/2025/10/23/langgraph-dspy-gepa-researcher) - Real-world hybrid implementation
- [LangGraph & DSPy: Orchestrating Multi-Agent AI Workflows](https://medium.com/@akankshasinha247/langgraph-dspy-orchestrating-multi-agent-ai-workflows-with-declarative-prompting-93b2bd06e995) - Orchestration patterns
- [Building Multi-Agent RAG with DSPy and GEPA](https://kargarisaak.medium.com/building-and-optimizing-multi-agent-rag-systems-with-dspy-and-gepa-2b88b5838ce2) - GEPA optimization guide
- [8 LangGraph Agent Patterns That Don't Break Under Load](https://medium.com/@kaushalsinh73/8-langgraph-agent-patterns-that-dont-break-under-load-9ea885070f59) - Production patterns
- [DSPy 3 + GEPA: The Most Advanced RAG Framework Yet](https://gaodalie.substack.com/p/dspy-3-gepa-the-most-advanced-rag) - DSPy 3 with GEPA

### GitHub Repositories

- [GEPA Official Repository](https://github.com/gepa-ai/gepa) - GEPA implementation
- [LangGraph DSPy Course](https://github.com/Ronoh4/LangGraphDSPyCourse) - Integration examples

### Courses

- [AI Agents in LangGraph (DeepLearning.AI)](https://www.deeplearning.ai/short-courses/ai-agents-in-langgraph/) - State management and persistence

---

**Document Status**: Complete
**Last Updated**: 2026-02-04
**Next Steps**: Implement prototype integration with AGENTX codebase
