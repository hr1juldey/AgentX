# Spec: Stem Cell Conversation Differentiation

Stem cell to conversation agent specialization using signature-based differentiation.

## ADDED Requirements

### Requirement: Conversation signature definition

The system SHALL define a proper DSPy signature class for conversational interactions with typed fields.

#### Scenario: Signature class with History field

- **WHEN** defining ConversationSignature
- **THEN** system creates class inheriting from `dspy.Signature`
- **AND** system includes `question: str = dspy.InputField(desc="User's question")`
- **AND** system includes `history: dspy.History = dspy.InputField(desc="Conversation history")`
- **AND** system includes `answer: str = dspy.OutputField(desc="Agent's response")`

#### Scenario: No inline signatures

- **WHEN** creating any agent signature
- **THEN** system MUST define as a class (not inline string)
- **AND** system MUST use typed field definitions
- **AND** system MUST include field descriptions

---

### Requirement: Stem cell pluripotency preservation

The system SHALL preserve the pluripotent base StemCellAgent while differentiating into ConversationAgent.

#### Scenario: ConversationAgent inherits StemCellAgent

- **WHEN** creating ConversationAgent
- **THEN** system inherits from StemCellAgent
- **AND** system passes custom signature to parent **init**
- **AND** system does not modify parent behavior

#### Scenario: Stem cell can differentiate into other agents

- **WHEN** StemCellAgent exists
- **THEN** system can create ResearcherAgent with different signature
- **AND** system can create AnalystAgent with different signature
- **AND** base StemCellAgent remains unchanged

---

### Requirement: DSPy History management

The system SHALL use DSPy's native `dspy.History` for conversation context management.

#### Scenario: Initialize history on session start

- **WHEN** voice session begins
- **THEN** system creates `dspy.History(messages=[])`
- **AND** system stores history in session state

#### Scenario: Append to history after each turn

- **WHEN** agent completes query execution
- **THEN** system appends `{"question": <input>, **result}` to history.messages
- **AND** system preserves history for next query

#### Scenario: History passed to agent

- **WHEN** executing agent query
- **THEN** system passes current history as parameter
- **AND** agent uses history for context

---

### Requirement: Signature-based differentiation

The system SHALL differentiate agents by changing their DSPy signature.

#### Scenario: Pluripotent signature

- **WHEN** StemCellAgent is created without signature
- **THEN** system uses default ReasoningSignature
- **AND** system handles general reasoning tasks

#### Scenario: Conversation signature

- **WHEN** ConversationAgent is created
- **THEN** system uses ConversationSignature with History field
- **AND** system specializes in dialogue tasks

#### Scenario: Research signature

- **WHEN** ResearcherAgent is created
- **THEN** system uses ResearchSignature with citations field
- **AND** system specializes in research tasks

---

### Requirement: Agent execution flow

The system SHALL execute agent with proper DSPy patterns.

#### Scenario: Sync execution

- **WHEN** calling agent.forward(question="...", history=...)
- **THEN** system executes synchronously
- **AND** system returns dspy.Prediction

#### Scenario: Async execution

- **WHEN** calling agent.acall(question="...", history=...)
- **THEN** system executes asynchronously
- **AND** system awaits result
- **AND** system returns dspy.Prediction
