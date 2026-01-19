# T200: Create DSPy Signatures

**Phase**: 2
**Estimated Time**: 30 minutes
**Dependencies**: T001
**Blocked By**: None

---

## Context

**LLD References**:
- `lld/agent_runtime.md` - DSPy signature definitions
- `lld/incremental_release_plan.md` - Phase 2: Main agent signatures

**Description**:
Creates all DSPy signatures for the main agent. Signatures define input/output contracts for DSPy modules.

---

## Acceptance Criteria

**Passing Criteria**:
- agent/dspy_signatures/ directory exists
- MainAgentSignature defined
- ToolSelectionSignature defined
- ConfidenceScoringSignature defined
- All signatures use dspy.InputField and dspy.OutputField
- All signatures can be imported

**Verification Commands**:
```bash
cd /home/riju279/Documents/Code/XRIG/AgentX/prototypes/R013_travel_planning_stream/backend

# Verify directory exists
test -d agentx/agent/dspy_signatures && echo "dspy_signatures directory exists"

# Verify signatures can be imported
python3 -c "from agentx.agent.dspy_signatures.main_signatures import MainAgentSignature; print('MainAgentSignature OK')"
```

---

## Implementation Steps

### Step 1: Create main signatures file

Create file `agentx/agent/dspy_signatures/main_signatures.py`:

```python
"""Main agent DSPy signatures."""

import dspy


class MainAgentSignature(dspy.Signature):
    """Main agent reasoning signature for handling user queries.

    This signature defines the core reasoning pattern for the AGENTX assistant.
    It takes user query, conversation history, and retrieved context to produce
    step-by-step reasoning and a final answer.
    """

    user_query: str = dspy.InputField(desc="User's query or request")
    conversation_history: str = dspy.InputField(desc="Formatted conversation history")
    retrieved_context: str = dspy.InputField(desc="Retrieved context from RAG or memory", default="")
    reasoning: str = dspy.OutputField(desc="Step-by-step reasoning process")
    final_answer: str = dspy.OutputField(desc="Final response to user")


class ToolSelectionSignature(dspy.Signature):
    """Select appropriate tools based on query analysis.

    This signature analyzes the user query and determines which tools
    should be used to answer it.
    """

    query_analysis: str = dspy.InputField(desc="Analysis of what the user is asking for")
    available_tools: str = dspy.InputField(desc="Comma-separated list of available tool names")
    selected_tools: str = dspy.OutputField(desc="Comma-separated list of tools to use")
    tool_rationale: str = dspy.OutputField(desc="Explanation for why these tools were selected")


class ConfidenceScoringSignature(dspy.Signature):
    """Score confidence in the generated response.

    This signature evaluates how confident the agent is in its answer.
    Low confidence triggers clarification or tool use.
    """

    response: str = dspy.InputField(desc="Generated response to evaluate")
    query_context: str = dspy.InputField(desc="Original query context", default="")
    confidence_score: float = dspy.OutputField(desc="Confidence from 0.0 to 1.0")
    confidence_reasoning: str = dspy.OutputField(desc="Explanation of confidence score")
```

### Step 2: Create __init__.py for dspy_signatures

Create file `agentx/agent/dspy_signatures/__init__.py`:

```python
"""DSPy signatures for AGENTX agents."""

from agentx.agent.dspy_signatures.main_signatures import (
    MainAgentSignature,
    ToolSelectionSignature,
    ConfidenceScoringSignature,
)

__all__ = [
    "MainAgentSignature",
    "ToolSelectionSignature",
    "ConfidenceScoringSignature",
]
```

---

## Expected Failures & Countermeasures

### Failure: dspy not installed

**Likelihood**: Medium
**Symptoms**: `ModuleNotFoundError: No module named 'dspy'`

**Countermeasures**:
1. Install DSPy: `uv pip install dspy-ai`
2. Check requirements.txt includes dspy-ai
3. Verify installation: `python3 -c "import dspy; print(dspy.__version__)"`

**Recovery Time**: 3 minutes

### Failure: DSPy API changed

**Likelihood**: Low
**Symptoms**: `AttributeError: module 'dspy' has no attribute 'InputField'`

**Countermeasures**:
1. Check DSPy version: Ensure using dspy-ai 2.5.0+
2. Refer to DSPy docs at `/home/riju279/Downloads/dspy-main/dspy-main/docs/`
3. Update signature syntax if needed

**Recovery Time**: 10 minutes

---

## Retroactive Measures

### Upstream Drift Recovery

**Scenario**: T001 directory structure changed
**Detection**: agentx/agent/dspy_signatures/ directory missing
**Action**: Re-run T001 to ensure all directories exist

**Recovery Time**: 5 minutes

### Downstream Impact

**Scenario**: Signature field names change
**Prevention**: All signature field names are LOCKED
**Mitigation**: Update all DSPy modules using these signatures
**Affected Tasks**: T202 (Main DSPy Agent), T203 (Agent Use Cases)

---

## Artifacts

**Files Created**:
- `agentx/agent/dspy_signatures/main_signatures.py` (Signatures, LOCKED)
- `agentx/agent/dspy_signatures/__init__.py` (Package marker, not locked)

**Locked APIs**:
- `MainAgentSignature` class name
- All signature field names and types
- Field descriptions (affects LLM behavior)

---

## Quality Gates

**Quality Checks**:
- **Check**: Directory and files exist
  - Command: `test -d agentx/agent/dspy_signatures && test -f agentx/agent/dspy_signatures/main_signatures.py && echo "OK"`
  - Expected: `OK`
  - Required: Yes

- **Check**: Signatures can be imported
  - Command: `python3 -c "from agentx.agent.dspy_signatures import MainAgentSignature; print('OK')"`
  - Expected: `OK`
  - Required: Yes

---

## Notes

1. DSPy signatures define LLM input/output contracts
2. Field descriptions are critical for LLM behavior
3. default="" for optional context fields
4. confidence_score as float for numeric confidence
5. All signatures use dspy.InputField and dspy.OutputField

---

## Completion Checklist

- [ ] agentx/agent/dspy_signatures/ directory created
- [ ] main_signatures.py created with all signatures
- [ ] __init__.py exports all signatures
- [ ] All signatures can be imported
- [ ] Ready for T201 (Create DSPy Tools)

---

**Task T200 is part of Phase 2: Main DSPy Agent**
**Locked APIs**: All signature class names, field names, and types
