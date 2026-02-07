# Spec: LangGraph Conversation Orchestration

LangGraph-based conversation orchestration layer that processes both text chat and voice (after STT transcription) through a unified multi-node graph, with intelligent routing for text vs audio output paths.

## Purpose

Provide a unified conversation orchestration layer using LangGraph that handles both text chat and voice interactions through a multi-node graph with proper state management, memory persistence, and input mode routing.

## Requirements

### Requirement: LangGraph StateGraph with TypedDict state schema
The system SHALL implement a LangGraph StateGraph for conversation processing using TypedDict state schema.

#### Scenario: State schema definition
- **WHEN** defining conversation state
- **THEN** system uses TypedDict (not Pydantic BaseModel) following codebase patterns
- **AND** state includes: query, user_id, session_id, conversation_history, agent_response, formatted_response, error, input_mode
- **AND** conversation_history is of type `Optional[dspy.History]`
- **AND** input_mode indicates source: "text" for chat, "voice" for STT pathway

#### Scenario: State initialization
- **WHEN** graph is invoked with initial state
- **THEN** system accepts query, user_id, session_id, and input_mode as required fields
- **AND** optional fields (conversation_history) default to None

---

### Requirement: Multi-node conversation graph
The system SHALL implement a multi-node LangGraph graph with sequential processing: validate_input → conversation_agent → format_output.

#### Scenario: Input validation node
- **WHEN** query enters the graph
- **THEN** validate_input node processes the query
- **AND** system applies format_stt_query() to remove filler words and clean text
- **AND** system validates query is non-empty
- **AND** system returns cleaned query or error state

#### Scenario: Conversation agent node
- **WHEN** validated query reaches conversation_agent node
- **THEN** system gets or creates session via SessionStateManager
- **AND** system calls ConversationAgent as callable: `result = agent(query=query)` (CORRECT DSPy pattern)
- **AND** system NEVER calls `.forward()` directly (this is a DSPy anti-pattern/"crime")
- **AND** system stores interaction in session history
- **AND** system retrieves Mem0 memories if needed
- **AND** system returns agent_response and updated conversation_history

#### Scenario: Output formatting node
- **WHEN** agent response reaches format_output node
- **THEN** system applies format_tts_phrase() to remove markdown and add punctuation
- **AND** system returns formatted_response for output
- **AND** system handles error state if present

---

### Requirement: ConversationAgent as LangGraph node
The system SHALL wrap ConversationAgent as a LangGraph node function using proper DSPy calling conventions.

#### Scenario: Agent node function signature
- **WHEN** defining conversation_agent node
- **THEN** function accepts TypedDict state parameter
- **AND** function returns dict with partial state updates
- **AND** returned dict includes agent_response and conversation_history keys

#### Scenario: DSPy module calling (NOT .forward())
- **WHEN** calling ConversationAgent
- **THEN** system calls agent as function: `result = agent(query=query)` (correct DSPy pattern)
- **AND** system NEVER calls `.forward()` directly (DSPy anti-pattern)
- **AND** DSPy internally calls the module's `forward()` method

#### Scenario: DSPy History integration
- **WHEN** calling ConversationAgent
- **THEN** system passes agent.get_history() via ConversationSignature
- **AND** agent receives conversation history for context
- **AND** agent updates internal DSPy History after each turn

---

### Requirement: MemorySaver checkpointer for session persistence
The system SHALL use LangGraph MemorySaver for in-memory checkpointing across WebSocket reconnections.

#### Scenario: Checkpointer configuration
- **WHEN** compiling the conversation graph
- **THEN** system creates MemorySaver instance
- **AND** system compiles graph with checkpointer parameter

#### Scenario: Thread-based session isolation
- **WHEN** invoking graph with session_id
- **THEN** system passes thread_id in config: {"configurable": {"thread_id": session_id}}
- **AND** system maintains separate state per thread_id
- **AND** system can resume conversation on reconnection with same session_id

#### Scenario: State persistence
- **WHEN** conversation turn completes
- **THEN** checkpointer saves final state
- **AND** subsequent invocations with same thread_id load previous state
- **AND** conversation_history persists across WebSocket disconnections

---

### Requirement: Input mode routing (voice vs text)
The system SHALL route inputs to appropriate output paths based on input_mode.

#### Scenario: Chat mode routing
- **WHEN** input_mode is "text" (from `/ws/chat` WebSocket)
- **THEN** system sends formatted_response as text message back to chat WebSocket
- **AND** system does NOT invoke TTS for audio output

#### Scenario: Voice mode routing
- **WHEN** input_mode is "voice" (from voice gateway after STT)
- **THEN** system sends formatted_response to TTS service for audio synthesis
- **AND** system streams audio chunks back to voice WebSocket
- **AND** system does NOT send text response to voice WebSocket

---

### Requirement: WebSocket chat endpoint integration
The system SHALL integrate the LangGraph graph with the `/ws/chat` WebSocket endpoint.

#### Scenario: Chat message processing
- **WHEN** client sends message with message_type="query"
- **THEN** system extracts query text from message data
- **AND** system invokes conversation graph with query, user_id, session_id, input_mode="text"
- **AND** system sends formatted_response back to client as text

#### Scenario: Session ID handling
- **WHEN** WebSocket connects with session_id query parameter
- **THEN** system uses provided session_id for graph thread_id
- **WHEN** WebSocket connects without session_id
- **THEN** system generates new UUID for session_id

---

### Requirement: Voice gateway integration
The system SHALL integrate the LangGraph graph with the voice gateway for STT-processed text.

#### Scenario: Voice input processing
- **WHEN** voice gateway receives STT transcription
- **THEN** system passes transcription to format_stt_query() for cleaning
- **AND** system invokes conversation graph with cleaned query, user_id, session_id, input_mode="voice"
- **AND** system receives formatted_response from graph

#### Scenario: Voice output routing
- **WHEN** graph returns formatted_response with input_mode="voice"
- **THEN** voice gateway sends formatted_response to TTS service
- **AND** system streams audio chunks back to client
- **AND** system maintains same session_id for memory continuity

---

### Requirement: Unified memory across modes
The system SHALL maintain unified memory across voice and text modes, allowing bidirectional switching within the same session.

#### Scenario: Cross-mode memory access
- **WHEN** user switches between voice and text modes
- **THEN** both modes access same conversation history via DSPy History
- **AND** both modes access same Mem0AI memory via user_id
- **AND** agent maintains context across mode switches

#### Scenario: Voice to text switching (within same session)
- **WHEN** user starts conversation in voice mode (session_id="abc")
- **AND** then switches to text mode with same session_id
- **THEN** text mode continues same session
- **AND** agent remembers context from voice interactions
- **AND** user sees previous conversation in chat interface

#### Scenario: Text to voice switching (within same session)
- **WHEN** user starts conversation in text mode (session_id="xyz")
- **AND** then switches to voice mode with same session_id
- **THEN** voice mode continues same session
- **AND** agent remembers context from text interactions
- **AND** agent responds appropriately with voice context

#### Scenario: Multiple mode switches (bidirectional, same session)
- **WHEN** user switches modes multiple times: text → voice → text → voice
- **THEN** all interactions maintain same session_id
- **AND** agent maintains continuous context across all switches
- **AND** DSPy History accumulates all interactions regardless of mode

---

### Requirement: Error handling and recovery
The system SHALL handle errors gracefully in the LangGraph graph execution.

#### Scenario: Graph recursion error
- **WHEN** graph execution exceeds recursion limit
- **THEN** system catches GraphRecursionError
- **AND** system sends error message to client
- **AND** system keeps WebSocket open for retry

#### Scenario: Agent execution error
- **WHEN** ConversationAgent callable raises exception
- **THEN** system logs error with stack trace
- **AND** system returns error state to format_output node
- **AND** format_output node returns error message to client

#### Scenario: Empty query handling
- **WHEN** validate_input node receives empty query
- **THEN** system returns error state: {"error": "Empty query"}
- **AND** format_output node formats error message for client

---

### Requirement: Integration with existing services
The system SHALL integrate with existing SessionStateManager, text preprocessing services, and DSPy infrastructure.

#### Scenario: SessionManager integration
- **WHEN** conversation_agent node executes
- **THEN** system calls get_session_manager() singleton
- **AND** system calls get_or_create_session(session_id, user_id)
- **AND** system accesses session.agent for ConversationAgent instance

#### Scenario: Text preprocessing integration
- **WHEN** validate_input node processes query
- **THEN** system calls format_stt_query() for input cleaning
- **WHEN** format_output node processes response
- **THEN** system calls format_tts_phrase() for output formatting

#### Scenario: DSPy LM/RM configuration
- **WHEN** ConversationAgent executes
- **THEN** agent uses globally configured DSPy LM (from get_lm())
- **AND** agent uses globally configured DSPy RM if available
