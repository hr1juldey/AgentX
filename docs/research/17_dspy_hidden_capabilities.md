# DSPy Hidden Capabilities: Beyond the Tutorials

**Discovery Date**: 2026-02-05
**Methodology**: Deep codebase exploration with 4 parallel Explore agents
**Purpose**: Stress test AGENTX RAG by discovering undocumented DSPy features

---

## Executive Summary

This document catalogs hidden DSPy capabilities that exist but are **not explicitly documented** in tutorials. These are the types of features that require reading the source code to discover - similar to how Mem0AI can technically use ColBERTv2, or how custom Qdrant retrievers can use multi-vector embeddings.

**Test Hypothesis**: Can AGENTX (4B Gemma + RAG) discover these hidden capabilities through semantic search, competing with GLM 4.7's brute force codebase analysis?

---

## 1. Hidden Retrieval & RAG Capabilities

### 1.1 FAISS-based Hybrid Search with Automatic Reranking

**File**: `dspy/retrievers/embeddings.py` (lines 31-50)
**Difficulty**: ⭐⭐⭐⭐⭐ (Never mentioned in tutorials)

```python
class Embeddings:
    def __init__(self, corpus, embedder, k=5):
        # AUTOMATIC STRATEGY SELECTION BASED ON CORPUS SIZE
        brute_force_threshold = 20000
        self.index = self._build_faiss() if len(corpus) >= brute_force_threshold else None

    def forward(self, query, k=None):
        # CANDIDATE EXPANSION: Search 10x more candidates than needed
        pids = self._faiss_search(q_embeds, self.k * 10) if self.index else None
```

**How It Works**: For large datasets (>20k documents): Uses FAISS with IVFPQ quantization. For small datasets: Falls back to brute force search. **10x candidate expansion** before reranking.

**Why It's Useful**: Transparent performance optimization, better quality than direct top-k, completely automatic.

---

### 1.2 Implicit PID Filtering System

**File**: `dspy/dsp/colbertv2.py` (lines 152-164)
**Difficulty**: ⭐⭐⭐⭐⭐ (Parameter exists but never documented)

```python
class ColBERTv2RetrieverLocal:
    def forward(self, query, k=None, **kwargs):
        # HIDDEN PARAMETER: filtered_pids
        if kwargs.get("filtered_pids"):
            filtered_pids = kwargs.get("filtered_pids")
            results = self.searcher.search(
                query, k=k,
                filter_fn=lambda pids: torch.tensor(
                    [pid for pid in pids if pid in filtered_pids]
                ).to(device),
            )
```

**How It Works**: Pass `filtered_pids=[0, 5, 10]` to restrict search to specific passage IDs.

**Why It's Useful**: Implement access control, semantic filtering, pre-filtering by metadata.

---

### 1.3 Persistent Index Saving/Loading

**File**: `dspy/retrievers/embeddings.py` (lines 91-216)
**Difficulty**: ⭐⭐⭐ (Feature exists but buried)

```python
# Save expensive embeddings
embedder.save("path/to/index")

# Load without recomputing
retriever = Embeddings.from_saved("path/to/index", embedder_function)
```

**Why It's Useful**: Avoid recomputing embeddings, version control for indices, pre-computed production deployment.

---

## 2. Hidden Streaming & Async Capabilities

### 2.1 sync_send_to_stream - Universal Context Streaming

**File**: `dspy/streaming/messages.py` (lines 27-51)
**Difficulty**: ⭐⭐⭐⭐⭐ (Internal function, never documented)

```python
def sync_send_to_stream(stream, message):
    """Send message to async stream from ANY context."""
    # Automatically detects current async context and adapts
    # Works in sync, async, nested async contexts
```

**Why It's Useful**: Solves "event loop already running" errors, enables hybrid sync/async streaming.

---

### 2.2 Stream Reusability with allow_reuse

**File**: `dspy/streaming/streaming_listener.py` (lines 47-52, 127-136)
**Difficulty**: ⭐⭐⭐⭐ (Parameter exists, not documented)

```python
listener = StreamListener("answer", allow_reuse=True)
# Can process multiple streams sequentially
```

**Why It's Useful**: Efficient listener reuse, reduced memory allocation.

---

### 2.3 Smart Chunk Buffering

**File**: `dspy/streaming/streaming_listener.py` (lines 86-114)
**Difficulty**: ⭐⭐⭐⭐⭐ (Complex logic, never explained)

Intelligently determines if buffered tokens could form end patterns, flushing early if not.

**Why It's Useful**: Improves latency, reduces unnecessary buffering.

---

## 3. Hidden Tool Use & Agent Capabilities

### 3.1 Advanced Tool Composition with ToolCalls

**File**: `dspy/adapters/types/tool.py` (lines 262-385)
**Difficulty**: ⭐⭐⭐⭐⭐ (Advanced type, rarely used)

```python
class ToolCalls(Type):
    tool_calls: list[ToolCall]
    # Agent plans multiple tools upfront, executes as batch
```

**Why It's Useful**: Parallel tool execution planning, more efficient agent behavior.

---

### 3.2 Async-to-Sync Tool Conversion

**File**: `dspy/adapters/types/tool.py` (lines 176-199)
**Difficulty**: ⭐⭐⭐⭐ (Hidden setting)

```python
dspy.configure(allow_tool_async_sync_conversion=True)
# Now async tools can be called from sync code
```

**Why It's Useful**: Seamless integration of async tools into sync agents.

---

### 3.3 Multi-Modal Citation Support

**File**: `dspy/experimental/__init__.py`, `dspy/adapters/types/citation.py`
**Difficulty**: ⭐⭐⭐⭐⭐ (Experimental, rarely mentioned)

```python
@experimental(version="3.0.4")
class Citations(Type):
    # Character-level source tracking for fact-checked responses
```

**Why It's Useful**: Fact-checked AI responses, proper attribution.

---

### 3.4 Dynamic Tool Integration (MCP + LangChain)

**File**: `dspy/adapters/types/tool.py` (lines 201-251)
**Difficulty**: ⭐⭐⭐⭐⭐ (Conversion methods, never documented)

```python
dspy_tool = Tool.from_mcp_tool(mcp_session, mcp_tool)
dspy_tool = Tool.from_langchain(langchain_tool)
```

**Why It's Useful**: Interoperability between tool ecosystems.

---

### 3.5 Secure Python Execution with Sandboxing

**File**: `dspy/primitives/python_interpreter.py` (lines 26-100)
**Difficulty**: ⭐⭐⭐⭐⭐ (Buried in primitives)

```python
interpreter = PythonInterpreter(
    enable_read_paths=["/safe/directory"],
    enable_write_paths=["/tmp/output"],
)
result = interpreter.execute(user_code)
```

**Why It's Useful**: Safe execution of user-provided code.

---

## 4. Hidden Internals & Extension Points

### 4.1 Dynamic Signature Manipulation

**File**: `dspy/signatures/signature.py` (lines 297-470)
**Difficulty**: ⭐⭐⭐⭐ (Methods exist, rarely featured)

```python
NewSig = OriginalSig.with_instructions("New prompt")
ExtendedSig = OriginalSig.append("field", str, dspy.OutputField())
```

**Why It's Useful**: Adaptive systems, dynamic signature composition.

---

### 4.2 Custom LM Backend Provider System

**File**: `dspy/clients/provider.py` (lines 22-100)
**Difficulty**: ⭐⭐⭐⭐⭐ (Provider system poorly documented)

```python
class CustomProvider(Provider):
    def launch(self, lm, launch_kwargs=None):
        # Custom LM startup logic
```

**Why It's Useful**: Integration with SGLang, vLLM, custom serving.

---

## Test Scenarios for AGENTX RAG

### Easy Tests (Should Work)
1. Thread-safe settings context
2. Persistent index saving/loading

### Medium Tests (Challenging)
3. FAISS hybrid search
4. Async-to-sync tool conversion

### Hard Tests (True Stress Test)
5. sync_send_to_stream
6. PID filtering system
7. Smart chunk buffering

### Expert Tests (Hidden in Plain Sight)
8. Citation support
9. Python interpreter sandbox
10. ToolCalls batch execution

---

## Success Criteria

**Qualitative Assessment** (4B Gemma + RAG vs 400B GLM 4.7 brute force):

1. **Retrieval Accuracy**: Can AGENTX find the correct code snippet?
2. **Understanding**: Can AGENTX explain how it works?
3. **Applicability**: Can AGENTX recognize when to use it?
4. **Code Generation**: Can AGENTX generate working code?

**Passing Grade**: Feature is discoverable and AGENTX can explain it
**Excellent Grade**: AGENTX generates working code using the feature
