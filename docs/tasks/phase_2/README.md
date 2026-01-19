# Phase 2 Tasks: Main DSPy Agent

**Phase**: 2
**Estimated Time**: 2-3 hours
**Dependencies**: Phase 0 (T001-T009), Phase 1 (T100-T104)
**Status**: Ready for Execution

---

## Phase Overview

Phase 2 implements the main DSPy ReAct agent with basic tools. This enables the AI assistant to answer questions, perform calculations, search the web, and get weather information.

### What's Implemented

- **DSPy Signatures**: MainAgent, ToolSelection, ConfidenceScoring
- **DSPy Tools**: Calculator (safe), Search (SearXNG), Weather (mock)
- **Main Agent**: Multi-signature ReAct pattern with confidence scoring
- **Use Cases**: ExecuteAgentQueryUseCase for orchestration
- **Testing**: Integration tests for agent layer

### What's Stubbed

- UI descriptors (Pydantic models) - Phase 3
- UI DSPy agent - Phase 3
- WebSocket streaming - Phase 3
- LangGraph state machines - Phase 4
- RAG integration - Phase 5

---

## Task List

### T200: Create DSPy Signatures (30 minutes)

**File**: `T200_create_dspy_signatures.md`

**Creates**:
- `agentx/agent/dspy_signatures/main_signatures.py`
  - MainAgentSignature - Core reasoning signature
  - ToolSelectionSignature - Tool selection logic
  - ConfidenceScoringSignature - Confidence evaluation

**Locked APIs**:
- All signature class names
- All signature field names and types

---

### T201: Create DSPy Tools (40 minutes)

**File**: `T201_create_dspy_tools.md`

**Creates**:
- `agentx/agent/tools/calculator.py` - Safe math evaluation with AST
- `agentx/agent/tools/search.py` - SearXNG web search
- `agentx/agent/tools/weather.py` - Mock weather service
- `agentx/agent/tools/main_tools.py` - dspy.Tool wrappers

**Locked APIs**:
- All tool function names and signatures

---

### T202: Create Main DSPy ReAct Agent (45 minutes)

**File**: `T202_create_dspy_agent.md`

**Creates**:
- `agentx/agent/dspy_agents/main_react_agent.py`
  - MainDSPyReActAgent - Multi-signature ReAct pattern
  - AgentFactory - Singleton with warmup
  - get_main_agent() - Factory function

**Features**:
- Tool selection before reasoning
- Step-by-step ReAct reasoning
- Confidence scoring with threshold
- Singleton pattern for performance

---

### T203: Create Agent Use Cases (35 minutes)

**File**: `T203_agent_use_cases.md`

**Creates**:
- `agentx/application/dtos/agent_dtos.py`
  - ExecuteAgentQueryCommand
  - ExecuteAgentQueryResponse
  - ToolCallDTO
  - ReasoningStepDTO
- `agentx/application/use_cases/execute_agent_query_use_case.py`

**Locked APIs**:
- ExecuteAgentQueryUseCase class name
- All DTO class names and field definitions

---

### T204: Create Phase 2 Integration Tests (45 minutes)

**File**: `T204_phase2_integration_tests.md`

**Creates**:
- `tests/integration/phase2/test_signatures.py`
- `tests/integration/phase2/test_tools.py`
- `tests/integration/phase2/test_main_agent.py`
- `tests/integration/phase2/test_use_cases.py`

**Test Categories**:
- Signature field definitions
- Calculator safety (no eval)
- Agent initialization (mocked, optional real tests)
- Use case validation

---

## Running Phase 2

### Prerequisites

1. **Phase 0 Complete**: T001-T009
2. **Phase 1 Complete**: T100-T104
3. **Dependencies Installed**:
   ```bash
   uv pip install dspy-ai==2.5.0
   ```

### Optional Services (for full testing)

- **Ollama**: `ollama serve && ollama pull gemma3:4b`
- **SearXNG**: `sudo systemctl start searxng-docker`

### Execution Order

```bash
# T200: DSPy Signatures
cd /home/riju279/Documents/Code/XRIG/AgentX/prototypes/R013_travel_planning_stream/backend
# Follow T200_create_dspy_signatures.md

# T201: DSPy Tools
# Follow T201_create_dspy_tools.md

# T202: Main DSPy Agent
# Follow T202_create_dspy_agent.md

# T203: Agent Use Cases
# Follow T203_agent_use_cases.md

# T204: Phase 2 Tests
# Follow T204_phase2_integration_tests.md
```

### Verification (End of Phase 2)

```bash
cd /home/riju279/Documents/Code/XRIG/AgentX/prototypes/R013_travel_planning_stream/backend

# Verify DSPy signatures
python3 -c "from agentx.agent.dspy_signatures import MainAgentSignature; print('Signatures OK')"

# Verify tools
python3 -c "from agentx.agent.tools import calculator, search; print('Tools OK')"

# Verify agent
python3 -c "from agentx.agent.dspy_agents import get_main_agent; print('Agent OK')"

# Verify use cases
python3 -c "from agentx.application.use_cases import ExecuteAgentQueryUseCase; print('Use cases OK')"

# Run tests
pytest tests/integration/phase2/ -v
```

---

## Phase 2 Deliverables

### Agent Layer

**Signatures** (1 file):
- ✅ `main_signatures.py` - MainAgent, ToolSelection, Confidence

**Tools** (4 files):
- ✅ `calculator.py` - Safe AST-based calculator
- ✅ `search.py` - SearXNG integration
- ✅ `weather.py` - Mock weather service
- ✅ `main_tools.py` - dspy.Tool wrappers

**DSPy Agents** (1 file):
- ✅ `main_react_agent.py` - Multi-signature ReAct agent

### Application Layer

**DTOs** (1 file):
- ✅ `agent_dtos.py` - Command, Response, ToolCall, ReasoningStep DTOs

**Use Cases** (1 file):
- ✅ `execute_agent_query_use_case.py` - Query orchestration

### Testing

**Integration Tests** (4 files):
- ✅ `test_signatures.py` - Signature tests
- ✅ `test_tools.py` - Tool tests with safety checks
- ✅ `test_main_agent.py` - Agent tests (mocked + optional real)
- ✅ `test_use_cases.py` - Use case tests

**Total**: 12 files created in Phase 2

---

## Key Features

### Multi-Signature Pattern

```
User Query
    ↓
Tool Selection (Which tools?)
    ↓
ReAct Reasoning (Step-by-step + Tool Use)
    ↓
Confidence Scoring (How confident?)
    ↓
Final Answer + Reasoning + Tool Calls
```

### Safe Calculator

- Uses AST parsing (NOT eval/exec)
- Whitelisted operators only: +, -, *, /, **, %
- Whitelisted functions: abs, round, min, max, sum
- No access to __builtins__ or unsafe operations

### Singleton Agent Factory

- Lazy initialization on first use
- Warmup for DSPy compilation
- Thread-safe singleton pattern
- Reset function for testing

---

## Next Phase: Phase 3 - UI DSPy Agent + Descriptors

**Phase 3 Tasks** (T300-T304):
- T300: Create UI Descriptor Schemas
- T301: Create UI DSPy Signatures
- T302: Create UI DSPy Agent
- T303: Create WebSocket Streaming
- T304: Create Phase 3 Tests

**Phase 3 Deliverables**:
- 7 core UI descriptor types (Markdown, Card, Form, Progress, Action, Confirmation, Voice)
- UI DSPy signatures (SelectWidget, ConfigureForm, etc.)
- UI DSPy agent for widget generation
- WebSocket streaming endpoints
- Integration tests for UI layer

---

**Phase 2 Status**: ✅ READY FOR EXECUTION

**All task files created**: T200-T204

**Total Estimated Time**: 2-3 hours
