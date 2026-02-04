# Proposal: Voice Conversation with DSPy Stem Cell Agent and Memory

## Why

The AGENTX backend skeleton exists but cannot yet hold real-time voice conversations with users. We need to implement a fast, async, streaming voice conversation system where the stem cell agent differentiates into a specialized conversation agent that talks to users while maintaining persistent memory across sessions.

## What Changes

- **Implement voice conversation flow**: STT → ConversationAgent → TTS pipeline with WebSocket handling
- **Add text preprocessing layer**: STT-to-query formatter and TTS-to-speakable-phrase converter with proper punctuation and dialogue formatting
- **Implement stem cell differentiation**: StemCellAgent differentiates into ConversationAgent while preserving pluripotent base
- **Add async streaming support**: ConversationAgent uses DSPy streaming with async handlers for fast, real-time responses
- **Implement Qdrant multivector memory**: Single collection with dense (fast) + ColBERT (accurate) vectors using prefetch pattern
- **Add Mem0AI integration**: Persistent memory storage and retrieval across conversation sessions

## Capabilities

### New Capabilities

- **voice-conversation-flow**: End-to-end voice interaction pipeline from WebSocket to agent response
  - STT audio transcription handling
  - Agent query execution with memory context
  - TTS audio synthesis and streaming
  - Session management and state tracking

- **text-preprocessing**: Text normalization for speech interfaces
  - STT output → clean query formatter (remove filler words, fix grammar)
  - Agent response → speakable phrase converter (add punctuation, format dialogue, break into sentences)
  - Context-aware text transformation (conversational style, natural pauses)

- **stem-cell-conversation-differentiation**: Stem cell to conversation agent specialization
  - Signature-based differentiation from pluripotent stem cell
  - Conversation-specific DSPy signature class with typed fields (no inline string signatures)
  - Use `dspy.History` field type for conversation context management
  - Preserve stem cell pluripotency (can differentiate into other agents)

- **async-streaming-agent**: Fast, real-time agent execution
  - DSPy `dspy.streamify()` with `StreamListener` for token-level streaming
  - Implement `aforward()` method for async execution (use `acall()` on built-in modules)
  - Handle both `StreamResponse` (tokens) and `Prediction` (final output) in streaming loop

- **multivector-memory**: Qdrant hybrid vector storage
  - Dense vectors (fast retrieval) + ColBERT vectors (accurate reranking)
  - Prefetch pattern: dense → top-100 → ColBERT rerank → final-k
  - Single collection with named vectors ("dense", "colbert")

### Modified Capabilities

- None (this is new functionality)

## Impact

### Code Changes

- `agentx/application/agents/stem_cell.py`: Implement `forward()` with Mem0AI memory search/store
- `agentx/application/agents/conversation.py`: Implement async streaming conversation agent
- `agentx/infrastructure/voice/`: Complete voice gateway, SDK adapter, text stream handler
- `agentx/infrastructure/retrieval/`: Implement PrefetchRM with Qdrant multivector support
- `agentx/infrastructure/memory/`: Implement Mem0AI client wrapper
- `agentx/core/dependencies.py`: Add Mem0AI and Qdrant client initialization
- `agentx/presentation/api/v1/voice/routes.py`: WebSocket endpoint for voice sessions

### API Changes

- New WebSocket endpoint: `WS /api/v1/voice/ws?session_id={id}`
- New REST endpoints:
  - `GET /api/v1/voice/conversation/history` - Get conversation history
  - `POST /api/v1/voice/conversation/context` - Update conversation context
  - `POST /api/v1/agents/execute` - Execute agent with text query

### Dependencies

- **Existing** (already in requirements-core.txt): `dspy-ai`, `fastapi`, `websockets`
- **New**: `mem0ai` (Mem0AI client), `qdrant-client` (Qdrant Python client)
- **External services**: Ollama (LLM), Qdrant (vector DB), Mem0AI server (memory), Kyutai voice-server (STT/TTS)

### Systems

- **Ollama**: Must be running on `http://localhost:11434` with `gemma3:4b` model
- **Qdrant**: Must be running on `http://localhost:6335` (via docker-compose)
- **Mem0AI**: Optional for now (can be stubbed if not running)
- **Kyutai voice-server**: Must be running on `ws://localhost:16000` for STT/TTS
