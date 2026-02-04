# Spec: Differentiation Pattern

## ADDED Requirements

### Requirement: Stem Cell Agent Base Class
The system SHALL provide a base `StemCellAgent` class in `application/agents/stem_cell.py` that implements pluripotent agent behavior.

#### Scenario: Default pluripotent signature
- **WHEN** StemCellAgent is instantiated without signature parameter
- **THEN** agent SHALL use default signature `"context, question -> answer, reasoning"`

#### Scenario: Custom signature injection
- **WHEN** StemCellAgent is instantiated with custom signature
- **THEN** agent SHALL use the provided signature instead of default

#### Scenario: Extending dspy.Module
- **WHEN** StemCellAgent is defined
- **THEN** it SHALL extend `dspy.Module` for DSPy compatibility

---

### Requirement: Signature-Based Differentiation
Agent differentiation SHALL occur primarily through DSPy signature changes, not module overexpression.

#### Scenario: Differentiated agent signature
- **WHEN** specialized agent extends StemCellAgent
- **THEN** agent SHALL define custom signature in `__init__` and pass to parent class

#### Scenario: Signature defines agent DNA
- **WHEN** agent signature is set
- **THEN** signature SHALL define input/output contract (the agent's behavior pattern)

#### Scenario: Signature change at runtime
- **WHEN** agent needs to change behavior dynamically
- **THEN** agent SHALL call `set_signature()` method to update signature

---

### Requirement: Module Overexpression as Secondary Differentiation
Agents MAY use module overexpression (adding DSPy modules/tools) as a secondary differentiation mechanism.

#### Scenario: Adding specialized module
- **WHEN** agent needs additional processing capability
- **THEN** agent MAY add DSPy module in `__init__` (e.g., `self.data_judgment = dspy.ChainOfThought(...)`)

#### Scenario: Tool mounting
- **WHEN** agent needs external capabilities
- **THEN** agent SHALL mount tools via `self.add_tool(tool)` method

#### Scenario: Overexpression is optional
- **WHEN** agent signature is sufficient for desired behavior
- **THEN** module overexpression is NOT required

---

### Requirement: Per-Agent Mem0AI Injection
Each agent SHALL receive Mem0AI client and user_id for user-scoped memory, while LM and RM are globally configured.

#### Scenario: Mem0AI singleton access
- **WHEN** agent is instantiated
- **THEN** agent SHALL call `get_mem0_client()` to retrieve singleton Mem0AI client

#### Scenario: User-specific memory isolation
- **WHEN** agent is instantiated with user_id
- **THEN** agent SHALL store `mem0_user_id` for memory operations scoped to that user

#### Scenario: Global DSPy LM/RM
- **WHEN** agent is instantiated
- **THEN** agent SHALL NOT configure LM or RM (uses global DSPy configuration)

---

### Requirement: Memory Search Before Execution
Agents SHALL search Mem0AI for relevant context before executing their primary reasoning.

#### Scenario: Memory search on forward
- **WHEN** agent `forward()` method is called
- **THEN** agent SHALL first search Mem0AI with the input query

#### Scenario: Context injection into reasoning
- **WHEN** Mem0AI returns relevant memories
- **THEN** agent SHALL inject memory context into reasoning input

#### Scenario: Graceful degradation on memory failure
- **WHEN** Mem0AI search fails or times out
- **THEN** agent SHALL continue execution without memory context

---

### Requirement: Memory Storage After Execution
Agents SHALL store interaction results in Mem0AI after successful execution.

#### Scenario: Storing user message
- **WHEN** agent receives input
- **THEN** agent SHALL store user message with role "user" in Mem0AI

#### Scenario: Storing assistant response
- **WHEN** agent produces output
- **THEN** agent SHALL store assistant response with role "assistant" in Mem0AI

#### Scenario: Batch storage
- **WHEN** execution completes
- **THEN** agent SHALL store interaction as batch: `[{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]`

---

### Requirement: Specialized Agent Subclassing
Permanent differentiated cell types SHALL be created as subclasses of StemCellAgent.

#### Scenario: Creating AnalystAgent
- **WHEN** developer needs analysis-specialized agent
- **THEN** agent SHALL be created as `class AnalystAgent(StemCellAgent)` in `application/agents/analyst.py`

#### Scenario: AnalystAgent signature
- **WHEN** AnalystAgent is instantiated
- **THEN** it SHALL use signature `"query, memory_context, knowledge_context -> context_summary, goals, is_sufficient, confidence"`

#### Scenario: Creating ResearcherAgent
- **WHEN** developer needs research-specialized agent
- **THEN** agent SHALL be created as `class ResearcherAgent(StemCellAgent)` in `application/agents/researcher.py`

#### Scenario: ResearcherAgent signature
- **WHEN** ResearcherAgent is instantiated
- **THEN** it SHALL use signature `"query, context -> answer, reasoning, citations"`

---

### Requirement: Pluripotent Agent Capabilities
The base StemCellAgent SHALL be pluripotent - capable of handling general queries without specialization.

#### Scenario: General query handling
- **WHEN** StemCellAgent receives query without specialized context
- **THEN** agent SHALL process query using default signature

#### Scenario: Minimal default behavior
- **WHEN** StemCellAgent is used without customization
- **THEN** agent SHALL provide reasoning and answer but no specialized outputs

#### Scenario: Stem cell as starting point
- **WHEN** developer needs new agent type
- **THEN** StemCellAgent SHALL be extended rather than creating new base class

---

### Requirement: Agent Registry for Graph Compilation
The system SHALL maintain an agent registry for LangGraph graph compilation.

#### Scenario: Registering agent type
- **WHEN** agent class is defined
- **THEN** agent SHALL be registered in agent registry with unique identifier

#### Scenario: Retrieving agent from registry
- **WHEN** GraphCompiler builds LangGraph
- **THEN** compiler SHALL retrieve agent instances from registry by identifier

#### Scenario: Registry as singleton
- **WHEN** application needs agent registry
- **THEN** registry SHALL be accessed via getter function from `core/dependencies.py`

---

### Requirement: Differentiation Validation
Agent differentiation SHALL be validated at agent initialization time (fail fast).

#### Scenario: Signature validation
- **WHEN** agent is instantiated with custom signature
- **THEN** signature SHALL be validated to have at least one input and one output field

#### Scenario: Tool validation
- **WHEN** agent calls `add_tool(tool)`
- **THEN** tool SHALL be validated to be callable or dspy.Tool instance

#### Scenario: User ID validation
- **WHEN** agent is instantiated
- **THEN** user_id SHALL be validated to be non-empty string

---

### Requirement: Reversible Differentiation
Agents MAY change their signature at runtime, enabling reversible differentiation.

#### Scenario: Changing signature
- **WHEN** agent needs to handle different type of query
- **THEN** agent MAY call `set_signature(new_signature)` to change behavior

#### Scenario: Resetting to pluripotent state
- **WHEN** agent needs to return to general-purpose behavior
- **THEN** agent MAY call `reset_signature()` to restore default pluripotent signature

#### Scenario: Signature change persists
- **WHEN** agent signature is changed
- **THEN** new signature SHALL be used for all subsequent forward() calls
