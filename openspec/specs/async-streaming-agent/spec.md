# Spec: Async Streaming Agent

Fast, real-time agent execution with async and streaming capabilities.

## Purpose

Enable real-time AI agent interactions with async execution and token-level streaming for responsive voice and chat interfaces.

## Requirements

### Requirement: Async forward method
The system SHALL implement `aforward()` method for asynchronous agent execution.

#### Scenario: Implement aforward in ConversationAgent
- **WHEN** creating ConversationAgent
- **THEN** system defines `async def aforward(self, question: str, history: dspy.History) -> dspy.Prediction`
- **AND** system uses `await self.reasoning.acall(...)` for async LM calls
- **AND** system returns dspy.Prediction

#### Scenario: Async memory operations
- **WHEN** executing agent asynchronously
- **THEN** system uses `await` for Mem0AI search
- **AND** system uses `await` for Mem0AI storage
- **AND** system does not block event loop

---

### Requirement: Token-level streaming
The system SHALL support token-level streaming using `dspy.streamify()`.

#### Scenario: Wrap agent with streamify
- **WHEN** creating streaming agent
- **THEN** system wraps with `dspy.streamify(agent, stream_listeners=[...])`
- **AND** system creates `StreamListener(signature_field_name="answer")`
- **AND** system returns async generator

#### Scenario: Consume streaming output
- **WHEN** consuming stream
- **THEN** system iterates with `async for chunk in stream_agent(...)`
- **AND** system checks `isinstance(chunk, dspy.streaming.StreamResponse)` for tokens
- **AND** system checks `isinstance(chunk, dspy.Prediction)` for final output

---

### Requirement: StreamResponse handling
The system SHALL properly handle StreamResponse objects with correct field access.

#### Scenario: Access stream chunks
- **WHEN** receiving StreamResponse
- **THEN** system accesses `chunk.chunk` for token text
- **AND** system accesses `chunk.signature_field_name` for field name
- **AND** system accesses `chunk.predict_name` for predictor name

#### Scenario: Send tokens to WebSocket
- **WHEN** streaming tokens to voice client
- **THEN** system sends each chunk as separate message
- **AND** system maintains message order
- **AND** system handles final Prediction separately

---

### Requirement: Prediction finalization
The system SHALL handle final Prediction object after streaming completes.

#### Scenario: Final Prediction received
- **WHEN** stream yields dspy.Prediction
- **THEN** system extracts final answer from `prediction.answer`
- **AND** system stores interaction in memory
- **AND** system appends to DSPy history

#### Scenario: Cache hit behavior
- **WHEN** result is served from cache
- **THEN** system yields only Prediction (no StreamResponse)
- **AND** system handles this case gracefully

---

### Requirement: Sync streaming fallback
The system SHALL support sync streaming with `async_streaming=False` flag.

#### Scenario: Sync streaming for development
- **WHEN** `async_streaming=False` is set
- **THEN** system returns sync generator (not async)
- **AND** system can iterate with `for chunk in stream_agent(...)`

---

### Requirement: Streaming error handling
The system SHALL handle streaming errors without crashing.

#### Scenario: Stream interruption
- **WHEN** stream is interrupted by client disconnect
- **THEN** system gracefully stops streaming
- **AND** system cleans up resources

#### Scenario: Partial stream failure
- **WHEN** LM fails mid-stream
- **THEN** system catches exception
- **AND** system sends error message to client
- **AND** system preserves conversation history
