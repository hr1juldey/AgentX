# Design: Voice Conversation with DSPy Stem Cell Agent and Memory

## Context

**Current State:**
- AGENTX backend skeleton exists with 5-layer Clean Architecture
- DSPy configured globally with Ollama LM (`gemma3:4b`)
- Qdrant running in Docker (port 6335) for vector storage
- Kyutai voice-server available for STT/TTS (port 16000)
- Skeleton files raise `NotImplementedError`

**Constraints:**
- Must use absolute imports only (CLAUDE_POLICY.md)
- File size limit: 100 lines executable + 50 lines overhead
- No inline DSPy signatures (must use typed signature classes)
- Ollama is local (not cloud), must handle connection failures gracefully
- Frontend already has voice UI and WebSocket client (no changes needed)

**Stakeholders:**
- User: Wants fast, natural voice conversations with memory
- Developer: Needs clean, maintainable code following DSPy best practices

---

## Goals / Non-Goals

**Goals:**
1. Enable real-time voice conversation with async streaming responses
2. Maintain conversation context using DSPy's native `dspy.History`
3. Store and retrieve long-term memories across sessions using Mem0AI
4. Use Qdrant multivector (dense + ColBERT) for accurate semantic search
5. Differentiate StemCellAgent into ConversationAgent via signature change

**Non-Goals:**
- UI changes (frontend already complete)
- Multiple concurrent users (single-user focused for v0.1)
- Voice activity detection (handled by Kyutai server)
- Fallback to internal Silero services (using external Kyutai only)

---

## Memory Architecture (Three Layers)

### Layer 1: DSPy History (In-Memory, Short-Term)
**Purpose:** Maintain conversation context within a single session

**Pattern:**
```python
class ConversationSignature(dspy.Signature):
    """Signature for conversational interactions."""
    question: str = dspy.InputField(desc="User's question")
    history: dspy.History = dspy.InputField(desc="Conversation history")
    answer: str = dspy.OutputField(desc="Agent's response")

# Usage
history = dspy.History(messages=[])
result = await agent.acall(question="Hello", history=history)
history.messages.append({"question": "Hello", **result})
```

**Lifecycle:** Exists only during session, lost on disconnect

---

### Layer 2: Mem0AI (Persistent, Long-Term)
**Purpose:** Store and retrieve memories across sessions

**Pattern:**
```python
# Before query: Search for relevant context
memories = mem0_client.search(
    query=question,
    user_id=user_id,
    limit=5
)
context = "\n".join([m["memory"] for m in memories])

# After query: Store interaction
mem0_client.add(
    memory=f"User: {question}\nAssistant: {answer}",
    user_id=user_id,
    metadata={"timestamp": now()}
)
```

**Lifecycle:** Persists across sessions, stored in Mem0AI backend

---

### Layer 3: Qdrant (Vector Index for Mem0AI)
**Purpose:** Fast semantic search with multivector reranking

**Pattern:**
```python
# Prefetch: Dense (fast) → Top-100 → ColBERT (accurate) → Final-k
results = qdrant_client.query_points(
    collection_name="agentx_memory",
    prefetch=[
        models.Prefetch(
            query=dense_vector,
            using="dense",
            limit=100
        )
    ],
    query=colbert_vector,
    using="colbert",
    limit=k
)
```

**Lifecycle:** Vectors stored in Qdrant, managed by Mem0AI or directly

---

## Decisions

### Decision 1: Use Three-Layer Memory Architecture

**Choice:** DSPy History (session) → Mem0AI (persistent) → Qdrant (vector index)

**Rationale:**
- DSPy History: Native conversation context, no custom implementation needed
- Mem0AI: Purpose-built for LLM memory with deduplication and importance scoring
- Qdrant: Multivector (dense + ColBERT) for fast + accurate retrieval

**Alternatives Considered:**
- **Only DSPy History:** Loses memories after session (unacceptable)
- **Only Qdrant directly:** No memory importance scoring, no deduplication
- **Custom memory system:** Reinventing the wheel, maintenance burden

---

### Decision 2: Mem0AI as Primary Memory Interface

**Choice:** Use Mem0AI Python client as main memory interface, Qdrant as backend

**Rationale:**
- Mem0AI handles memory importance scoring, deduplication, TTL
- Supports multiple memory types: episodic, semantic, procedural
- Can use Qdrant as vector backend (or its own internal storage)
- Simpler API than raw Qdrant for memory operations

**Alternatives Considered:**
- **Raw Qdrant only:** More control, but must implement scoring/dedup manually
- **Redis only:** No vector search, would need separate vector DB
- **DSPy RM only:** DSPy's retriever module is for RAG, not long-term memory

---

### Decision 3: Hybrid Adapter Pattern for Voice

**Choice:** Create `VoiceSDKAdapter` that wraps `libs/voice_client/` SDK with fallback to direct WebSocket

**Rationale:**
- SDK already implements complex STT/TTS protocol (auto-reconnect, message handling)
- Thin wrapper keeps AGENTX code decoupled from SDK changes
- Fallback to direct WebSocket if SDK fails (defensive programming)

**Alternatives Considered:**
- **Direct WebSocket only:** Must re-implement protocol handling (error-prone)
- **SDK only:** No fallback if SDK has issues
- **Internal Silero:** Deprecated, external Kyutai is better quality

---

### Decision 4: Signature Classes Only (No Inline Strings)

**Choice:** Define DSPy signatures as classes with typed fields

**Rationale:**
- Type safety and IDE autocomplete
- Clear field descriptions via `desc` parameter
- Consistent with DSPy best practices
- Required by CLAUDE_POLICY.md

**Example:**
```python
# CORRECT: Typed signature class
class ConversationSignature(dspy.Signature):
    """Signature for conversational interactions."""
    question: str = dspy.InputField(desc="User's question")
    history: dspy.History = dspy.InputField(desc="Conversation history")
    answer: str = dspy.OutputField(desc="Agent's response")

# WRONG: Inline string signature
conversation_signature = dspy.Signature("question, history -> answer")
```

---

### Decision 5: Async with `aforward()`, Stream with `dspy.streamify()`

**Choice:** Implement `aforward()` for async execution, wrap with `dspy.streamify()` for token streaming

**Rationale:**
- Async: Non-blocking I/O for concurrent requests
- Streaming: Real-time token generation for fast perceived response time
- Separation: Core logic in `aforward()`, streaming is wrapper

**Pattern:**
```python
class ConversationAgent(StemCellAgent):
    async def aforward(self, question: str, history: dspy.History) -> dspy.Prediction:
        # Core async logic
        result = await self.reasoning.acall(question=question, history=history)
        return result

# Wrap with streaming
stream_agent = dspy.streamify(
    agent,
    stream_listeners=[
        dspy.streaming.StreamListener(signature_field_name="answer")
    ]
)

# Consume stream
async for chunk in stream_agent(question="Hello", history=history):
    if isinstance(chunk, dspy.streaming.StreamResponse):
        print(f"Token: {chunk.chunk}")
    elif isinstance(chunk, dspy.Prediction):
        print(f"Final: {chunk.answer}")
```

**Alternatives Considered:**
- **Sync only:** Blocks during LM calls, poor UX for voice
- **Streaming only without async:** Still blocks on I/O
- **Callbacks:** More complex, less Pythonic than async/await

---

### Decision 6: Text Preprocessing for Speech Interfaces

**Choice:** Create `TextPreprocessor` service with two methods:
- `preprocess_stt()`: Clean STT output (remove filler words, fix grammar)
- `preprocess_tts()`: Format TTS input (add punctuation, break into sentences)

**Rationale:**
- STT output often has filler words ("um", "uh") and lacks punctuation
- TTS needs punctuation for natural pauses and intonation
- LLM outputs can be long sentences; breaking them improves TTS quality

**Alternatives Considered:**
- **No preprocessing:** STT → LLM → TTS (pass-through) - less natural
- **Preprocessing in LLM prompt:** Adds token overhead, inconsistent results
- **External NLP service:** Another dependency, overkill for this use case

---

## Risks / Trade-offs

### Risk 1: Mem0AI Server Not Running
**Impact:** Memory search/storage fails, degrades to stateless conversation

**Mitigation:**
- Wrap Mem0AI calls in try-except, log warnings
- Graceful degradation: Continue without memory if unavailable
- Health check endpoint to monitor Mem0AI status

---

### Risk 2: Ollama Connection Timeout
**Impact:** Agent cannot generate responses, conversation hangs

**Mitigation:**
- Connection timeout with retry logic
- Fallback error message: "Sorry, I'm having trouble connecting. Please try again."
- Health check on startup, fail fast if Ollama unavailable

---

### Risk 3: Streaming Complexity
**Impact:** More complex code, potential bugs in stream handling

**Mitigation:**
- Start with sync `forward()`, add async `aforward()` after core logic works
- Add comprehensive tests for streaming edge cases
- Use `async_streaming=False` flag for simpler sync streaming during development

---

### Risk 4: Qdrant Multivector Setup Complexity
**Impact:** ColBERT vectorization requires additional setup and dependencies

**Mitigation:**
- Phase 1: Use dense-only vectors (simpler, faster)
- Phase 2: Add ColBERT reranking once dense vectors work
- Provide clear setup documentation for ColBERT dependencies

---

### Trade-off 1: Latency vs Accuracy
**Choice:** Prefetch pattern (dense → ColBERT rerank)

**Why:** Dense vectors are fast (~10ms), ColBERT is accurate but slower (~100ms)
**Trade-off:** Slightly higher latency for much better retrieval accuracy

---

### Trade-off 2: Memory Storage Speed vs Completeness
**Choice:** Store memory asynchronously after response sent

**Why:** Don't block response waiting for memory storage
**Trade-off:** If storage fails, memory is lost but conversation continues

---

## Migration Plan

### Phase 1: Core Conversation Flow (Minimal Viable)
1. Implement `StemCellAgent.forward()` with DSPy History only
2. Implement `ConversationAgent` with `ConversationSignature`
3. Implement `VoiceSDKAdapter.handle_session()` (STT → Agent → TTS)
4. Implement WebSocket endpoint `/ws/voice`
5. Test basic voice conversation (no persistent memory)

### Phase 2: Persistent Memory
1. Implement Mem0AI client wrapper in `infrastructure/memory/`
2. Add memory search before query in `StemCellAgent.forward()`
3. Add memory storage after response in `StemCellAgent.forward()`
4. Test conversation persistence across sessions

### Phase 3: Multivector Memory
1. Implement Qdrant client initialization
2. Create `PrefetchRM` with dense + ColBERT support
3. Configure Mem0AI to use Qdrant as vector backend (or use directly)
4. Test retrieval accuracy with multivector

### Phase 4: Async Streaming
1. Implement `ConversationAgent.aforward()` with async execution
2. Wrap agent with `dspy.streamify()` for token streaming
3. Update WebSocket handler to send streaming tokens
4. Test streaming performance and latency

### Rollback Strategy
- Each phase is independently deployable
- Can revert to previous phase if issues arise
- Git tags for each phase: `v0.1-phase1`, `v0.1-phase2`, etc.

---

## Open Questions

1. **Mem0AI Integration:** Should Mem0AI use Qdrant as backend, or should we use Qdrant directly with Mem0AI-like features?
   - **Resolution:** Evaluate Mem0AI's Qdrant integration capabilities in Phase 2

2. **ColBERT Dependencies:** What are the exact dependencies for ColBERT vectorization in Python?
   - **Resolution:** Research in Phase 3, may require `colbert-ai` or similar package

3. **Session Management:** How should sessions be identified and managed across WebSocket disconnections?
   - **Resolution:** Use UUID session IDs, store in-memory session state (Phase 1)

4. **Text Preprocessing Quality:** Should we use a simple LLM call or a dedicated NLP library for preprocessing?
   - **Resolution:** Start with simple rule-based preprocessing, upgrade to LLM if needed
