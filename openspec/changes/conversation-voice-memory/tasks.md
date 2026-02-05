# Tasks: Voice Conversation with DSPy Stem Cell Agent and Memory

Implementation tasks organized by phase as defined in design.md.

## Phase 1: Core Conversation Flow (Minimal Viable)

### 1. Core Layer - Dependencies and Configuration

- [x] 1.1 Add Ollama health check in `ensure_dspy_configured()`
  - Verify Ollama is running on `http://localhost:11434`
  - Fail fast with clear error message if unavailable
  - Add connection timeout (600 seconds)

- [x] 1.2 Add `get_session_manager()` singleton function
  - Create in-memory session state storage: `dict[str, SessionState]`
  - Implement `get_or_create_session(session_id: str)` function
  - Add session cleanup task for expired sessions

### 2. Domain Layer - Signatures

- [x] 2.1 Create `ConversationSignature` class
  - File: `agentx/domain/signatures/conversation_signature.py`
  - Inherit from `dspy.Signature`
  - Define fields: `question: str = dspy.InputField(desc="User's question")`
  - Define fields: `history: dspy.History = dspy.InputField(desc="Conversation history")`
  - Define fields: `answer: str = dspy.OutputField(desc="Agent's response")`
  - NO inline string signatures

### 3. Application Layer - Agents

- [x] 3.1 Implement `StemCellAgent.forward()` (sync version)
  - File: `agentx/application/agents/stem_cell.py`
  - Implement DSPy History management: initialize, append, pass to reasoning
  - Create `self._history: dspy.History` instance attribute
  - Execute `self.reasoning(question=question, context=context)`
  - Return `dspy.Prediction`

- [x] 3.2 Update `ConversationAgent` to use `ConversationSignature`
  - File: `agentx/application/agents/conversation.py`
  - Pass `ConversationSignature` to parent `__init__`
  - Initialize `self._history = dspy.History(messages=[])`
  - Implement `get_history()` and `set_history()` methods

### 4. Infrastructure Layer - Voice

- [x] 4.1 Implement `VoiceSDKAdapter.handle_session()`
  - File: `agentx/infrastructure/voice/voice_adapter.py`
  - Import `VoiceClient` from `libs/voice_client/`
  - Implement STT buffering: collect audio chunks until Eos
  - Implement TTS streaming: send text to TTS, stream audio back
  - Add error handling for STT/TTS failures

- [x] 4.2 Implement `VoiceGatewayService`
  - File: `agentx/infrastructure/voice/voice_gateway.py`
  - Create `handle_session(websocket, session_id)` method
  - Get or create agent from session manager
  - Route messages: Audio (buffer), Eos (transcribe), Text (send to agent)
  - Send agent response to TTS

- [x] 4.3 Create `TextPreprocessor` service
  - File: `agentx/application/services/text_preprocessor.py`
  - Implement `preprocess_stt(text: str) -> str`: remove filler words
  - Implement `preprocess_tts(text: str) -> str`: add punctuation, break sentences
  - Keep it simple for Phase 1 (rule-based, not LLM-based)

- [x] 4.4 Create `SessionStateManager` service
  - File: `agentx/infrastructure/memory/session_state_manager.py`
  - Create `SessionState` dataclass: session_id, history, agent, metadata
  - Implement `get_or_create_session(session_id: str) -> SessionState`
  - Implement `add_user_message()` and `add_assistant_message()`
  - Implement `get_history()` method

### 5. Presentation Layer - API Routes

- [x] 5.1 Create WebSocket voice endpoint
  - File: `agentx/presentation/api/v1/voice/routes.py`
  - Create `@router.websocket("/ws/voice")` endpoint
  - Accept WebSocket, extract session_id from query params
  - Delegate to `VoiceGatewayService.handle_session()`
  - Handle WebSocket disconnect gracefully

### 6. Main Application

- [x] 6.1 Update `main.py` lifespan to initialize session manager
  - Import `get_session_manager` and call during startup
  - Add background task for session cleanup

---

## Phase 2: Persistent Memory (Mem0AI)

### 7. Core Layer - Mem0AI Dependencies

- [x] 7.1 Add Mem0AI client initialization
  - File: `agentx/core/dependencies.py`
  - Implement `get_mem0_client()` singleton function
  - Create `Mem0` client with local Ollama + Qdrant (no API key)
  - Add health check with try-except, return None if unavailable
  - Add graceful degradation (continue without memory if unavailable)

- [x] 7.2 Add Mem0AI to requirements-core.txt
  - Add `mem0ai==1.0.3` package (in pyproject.toml)
  - Run `uv pip install -r requirements-core.txt`

### 8. Infrastructure Layer - Memory Client

- [x] 8.1 Create `Mem0Client` wrapper
  - File: `agentx/infrastructure/memory/mem0_client.py`
  - Wrap Mem0AI client with AGENTX-specific methods
  - Implement `search_memory(query: str, user_id: str, limit: int) -> list[str]`
  - Implement `store_memory(text: str, user_id: str, metadata: dict) -> None`
  - Add error handling and logging

### 9. Application Layer - Integrate Memory into StemCellAgent

- [x] 9.1 Add memory search to `StemCellAgent.forward()`
  - Before executing reasoning, call `memory_manager.search_memory(context, question)`
  - Concatenate memory results to context
  - Handle case where Mem0AI is unavailable (continue with empty context)

- [x] 9.2 Add memory storage to `StemCellAgent.forward()`
  - After executing reasoning, format interaction as string
  - Call `memory_manager.store_interaction(question, result)`
  - Store asynchronously (don't block response)

### 10. Testing

- [x] 10.1 Test memory persistence across sessions
  - Test file: `agentx/tests/integration/test_memory_persistence.py`
  - Start conversation, add facts
  - Disconnect and reconnect with same session_id
  - Verify agent remembers previous context
  - **Test passes**: Agent 2 correctly retrieved "Alice" and "hiking" memories

---

## Phase 3: Multivector Memory (Qdrant)

### 11. Core Layer - Qdrant Dependencies

- [x] 11.1 Add Qdrant client initialization
  - File: `agentx/core/dependencies.py`
  - Implement `get_qdrant_client()` singleton function
  - Create `QdrantClient` pointing to `http://localhost:6335`
  - Verify connection with health check
  - Returns `QdrantClient` or `None` if unavailable

- [x] 11.2 Add Qdrant to requirements-core.txt
  - Add `qdrant-client>=1.13.2` to `pyproject.toml`
  - Also added `fastembed` for ColBERT support

### 12. Infrastructure Layer - Vector Embedding

- [x] 12.1 Create `DenseVectorizer` service
  - File: `agentx/infrastructure/retrieval/dense_vectorizer.py`
  - Uses Ollama `mxbai-embed-large:latest` for local embeddings
  - Implements `embed(text: str) -> list[float]`
  - Fallback to sentence-transformers if Ollama unavailable

- [x] 12.2 Create `ColBERTVectorizer` service
  - File: `agentx/infrastructure/retrieval/colbert_vectorizer.py`
  - Uses FastEmbed `LateInteractionTextEmbedding("colbert-ir/colbertv2.0")`
  - Implements `embed(text: str) -> list[list[float]]` (multi-vector)
  - Graceful degradation when FastEmbed unavailable

### 13. Infrastructure Layer - Qdrant Retriever

- [x] 13.1 Implement `PrefetchRM` (DSPy Retriever)
  - File: `agentx/infrastructure/retrieval/prefetch_rm.py`
  - Inherits from `dspy.retrievers.Retrieve`
  - Implements `forward(query: str, k: int | None = None) -> dspy.Prediction`
  - Uses Qdrant prefetch pattern: dense → top-100 → ColBERT → final-k
  - Returns DSPy-compatible `Prediction` object with `passages` attribute

- [x] 13.2 Implement Qdrant collection management
  - File: `agentx/infrastructure/retrieval/qdrant_collection_manager.py`
  - Creates collection with named vectors: "dense" and "colbert"
  - Configures `MultiVectorConfig` with `MAX_SIM` comparator
  - Sets `HnswConfigDiff(m=0)` for ColBERT (no indexing for reranker)
  - Implements `search_with_prefetch()` using Qdrant's `query_points` API

### 14. Integration

- [x] 14.1 Configure Mem0AI to use Qdrant as backend
  - Mem0AI uses Qdrant directly (configured in `mem0_client.py`)
  - **Implementation**:
    - `qdrant-client>=1.13.2` added to `pyproject.toml` dependencies
    - Mem0AI config in `mem0_client.py`: `vector_store.provider = "qdrant"`
    - Collection: `agentx_memories` at `localhost:6335`
    - Uses Ollama embedder for local embeddings
  - **Note**: PrefetchRM is a separate knowledge base system (different collection)

- [ ] 14.2 Test multivector retrieval accuracy
  - Compare dense-only vs multivector results
  - Verify prefetch pattern improves accuracy

---

## Phase 4: Async Streaming

### 15. Application Layer - Async Forward

- [ ] 15.1 Implement `ConversationAgent.aforward()`
  - File: `agentx/application/agents/conversation.py`
  - Change to `async def aforward(self, question: str, history: dspy.History) -> dspy.Prediction`
  - Use `await self.reasoning.acall(question=question, history=history)`
  - Return `dspy.Prediction`

### 16. Application Layer - Streaming Wrapper

- [ ] 16.1 Create streaming wrapper for ConversationAgent
  - File: `agentx/application/agents/conversation.py`
  - Implement `create_streaming_agent()` function
  - Wrap agent with `dspy.streamify(agent, stream_listeners=[...])`
  - Create `StreamListener(signature_field_name="answer")`

### 17. Infrastructure Layer - Streaming WebSocket Handler

- [ ] 17.1 Update `VoiceGatewayService` to handle streaming
  - File: `agentx/infrastructure/voice/voice_gateway.py`
  - Use streaming agent instead of sync agent
  - Iterate over stream: `async for chunk in stream_agent(...)`
  - Handle both `StreamResponse` (tokens) and `Prediction` (final)
  - Send tokens to WebSocket as they arrive
  - Store final Prediction in memory

### 18. Testing

- [ ] 18.1 Test streaming performance
  - Measure time-to-first-token latency
  - Verify tokens arrive in order
  - Test with long responses

- [ ] 18.2 Test streaming error handling
  - Disconnect mid-stream
  - Verify graceful cleanup

---

## Post-Implementation

### 19. Quality Checks

- [ ] 19.1 Run ruff checks

  ```bash
  ruff check agentx/ --fix
  ruff format agentx/
  ```

- [ ] 19.2 Run pyrefly type checking

  ```bash
  pyrefly check agentx/ --summarize-errors
  ```

- [ ] 19.3 Fix any remaining errors
  - Address ruff violations
  - Address pyrefly type errors
  - Ensure all checks pass

### 20. Documentation

- [ ] 20.1 Update CLAUDE.md with voice conversation patterns
- [ ] 20.2 Add README for running voice conversation
- [ ] 20.3 Document environment variables (.env.example)

### 21. Deployment Verification

- [ ] 21.1 Start all services: Ollama, Qdrant (docker-compose), Kyutai voice-server
- [ ] 21.2 Run agentx backend: `python agentx/main.py`
- [ ] 21.3 Test voice conversation end-to-end
- [ ] 21.4 Verify memory persistence across sessions
