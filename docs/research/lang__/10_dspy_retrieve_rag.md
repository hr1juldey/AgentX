# DSPy Retrieve (RAG) Integration with LangGraph

**Research Date**: 2026-02-04
**Status**: Comprehensive research on hybrid RAG patterns combining DSPy retrieval with LangGraph orchestration

## Executive Summary

DSPy provides first-class retrieval modules (`dspy.Retrieve`, `dspy.Predict`, `dspy.ChainOfThought`) that can be integrated into LangGraph's typed state and node orchestration model for production RAG workflows. The key integration points are:

- **DSPy-side**: Configure retrievers (ColBERTv2, Qdrant) via `dspy.settings.configure(rm=...)`, use `dspy.Retrieve(k=num_passages)` in RAG modules
- **LangGraph-side**: Create nodes that call DSPy retrieval, map passages to state fields, use `RetryPolicy` for resilience, `Send` for parallel retrieval
- **State mapping**: Store raw passages, provenance, scores in typed state (`search_results`, `provenance`, `draft_response`)

**Sources**:
- [DSPy Cheatsheet](https://dspy.ai/cheatsheet/)
- [DSPy Async Tutorial](https://dspy.ai/tutorials/async/)
- [DSPy RAG Implementation Guide](https://cobusgreyling.substack.com/p/using-dspy-for-a-rag-implementation)
- [LangGraph Thinking Guide](https://docs.langchain.com/oss/python/langgraph/thinking-in-langgraph)
- [LangGraph Graph API](https://docs.langchain.com/oss/python/langgraph/graph-api)
- [Production AI Agents Guide](https://www.firebird-technologies.com/p/building-production-ready-ai-agents)
- [LangGraph + DSPy GitHub](https://github.com/ahmedsamymohamad/Langgraph_dspy)
- [Qdrant DSPy Documentation](https://qdrant.tech/documentation/frameworks/dspy/)

---

## 1. Using dspy.retrieve Within LangGraph Nodes

### Overview

DSPy exposes retrieval as a module accessible via `dspy.Retrieve(k=num_passages)`. LangGraph nodes are ordinary Python functions that accept the graph state and return state updates.

### Synchronous vs Asynchronous Invocation

**DSPy supports native async** via `module.acall()` and `dspy.asyncify`:

```python
import dspy
import asyncio

# Async DSPy call
async def retrieval_node_async(state: dict, config, runtime):
    rag = RAG(num_passages=6)
    # Use acall for async DSPy modules
    res = await rag.acall(state["query"])
    return {"search_results": res.passages}

# Or wrap sync code
async def retrieval_node_wrapped(state: dict, config, runtime):
    rag = RAG(num_passages=6)
    # Wrap synchronous DSPy for async execution
    res = await dspy.asyncify(rag)(state["query"])
    return {"search_results": res.passages}
```

**Within LangGraph, use `asyncio.to_thread`** for long-running synchronous I/O:

```python
async def retrieval_node_nonblocking(state: dict, config, runtime):
    rag = RAG(num_passages=6)
    # Avoid blocking event loop for long sync calls
    res = await asyncio.to_thread(rag, state["query"])
    return {"search_results": res.passages}
```

**Recommendation**: Start with synchronous integration; profile and switch to async only when needed.

### Retries, Timeouts, and Failure Handling

**Layered retry strategy**:

```python
from langgraph.policies import RetryPolicy

# LangGraph-level retries for node failures
retry_config = RetryPolicy(max_attempts=3)

# DSPy-level retries for LM calls
lm = dspy.LM("openai/gpt-4o-mini", num_retries=3)

dspy.settings.configure(lm=lm)
```

**Failure modes**:
- **Transient network timeouts**: Use `RetryPolicy` at LangGraph level
- **Authentication failures (401)**: DSPy MCP security wrapper implements token refresh
- **Rate limiting (429)**: DSPy wrapper waits for `Retry-After` header
- **Blocking calls**: Use `asyncio.to_thread` or `dspy.asyncify`

### Batching

DSPy modules expose `batch()` methods for parallelizing requests:

```python
# Batch multiple retrieval requests
rag = RAG(num_passages=6)
queries = ["question 1", "question 2", "question 3"]
results = rag.batch(queries)

# Or use LangGraph Send for fan-out
from langgraph.constants import Send

# Parallel queries via LangGraph
def fan_out_retrieval(state):
    return [Send("retrieval_node", {"query": q}) for q in state["queries"]]
```

### Concrete Python Pattern

```python
import dspy
from typing import TypedDict

# DSPy RAG module
class RAG(dspy.Module):
    def __init__(self, num_passages=4):
        super().__init__()
        self.retrieve = dspy.Retrieve(k=num_passages)
        self.generate = dspy.ChainOfThought("question, context -> answer")

    def forward(self, question: str):
        passages = self.retrieve(question).passages
        return self.generate(question=question, context=passages)

# LangGraph state schema
class RAGState(TypedDict):
    query: str
    search_results: list[str] | None
    draft_response: str | None
    provenance: list[dict] | None

# LangGraph retrieval node
def retrieval_node(state: RAGState, config, runtime) -> dict:
    rag = RAG(num_passages=6)
    res = rag(state["query"])

    # Map DSPy outputs to LangGraph state
    return {
        "search_results": res.passages,
        "draft_response": res.answer
    }
```

### ASCII Call Flow

```
User query
    -> LangGraph retrieval_node
    -> DSPy dspy.Retrieve(question)
    -> DSPy returns passages
    -> LangGraph updates state with passages
    -> Downstream generator node calls DSPy generate
    -> Answer written to state
```

---

## 2. Qdrant Integration Patterns with LangGraph State

### Configuration

Install dependencies:

```bash
pip install dspy-ai dspy-qdrant fastembed qdrant-client
```

Configure Qdrant as DSPy retriever:

```python
import os
import dspy
from dspy_qdrant import QdrantRM
from qdrant_client import QdrantClient

# Configure LM
lm = dspy.LM("gpt-4o-mini", max_tokens=512, api_key=os.environ.get("OPENAI_API_KEY"))

# Configure Qdrant client
client = QdrantClient(
    url=os.environ.get("QDRANT_CLOUD_URL"),
    api_key=os.environ.get("QDRANT_API_KEY")
)

# Configure retriever
rm = QdrantRM(
    qdrant_collection_name="collection_name",
    qdrant_client=client,
    vector_name="dense",        # Matches your vector name
    document_field="passage_text",  # Matches your payload field
    k=20
)

# Configure DSPy settings
dspy.settings.configure(lm=lm, rm=rm)
```

### Basic Usage

```python
# Using the retriever
retrieve = dspy.Retrieve(k=3)
question = "Some question about my data"
topK_passages = retrieve(question).passages

print(f"Top {retrieve.k} passages for question: {question}\n")
for idx, passage in enumerate(topK_passages):
    print(f"{idx+1}]", passage, "\n")
```

### RAG Module with Qdrant

```python
class RAG(dspy.Module):
    def __init__(self, num_passages=3):
        super().__init__()
        self.retrieve = dspy.Retrieve(k=num_passages)
        self.generate = dspy.ChainOfThought("question, context -> answer")

    def forward(self, question):
        context = self.retrieve(question).passages
        return self.generate(question=question, context=context)
```

### LangGraph State Integration

Encapsulate Qdrant operations in LangGraph tools:

```python
from langgraph.prebuilt import ToolNode

def qdrant_search_tool(query: str) -> dict:
    """Search Qdrant collection for relevant passages."""
    retrieve = dspy.Retrieve(k=5)
    result = retrieve(query)

    return {
        "passages": result.passages,
        "k": retrieve.k,
        "provenance": []  # Add provenance if available
    }

tools = [qdrant_search_tool]
tool_node = ToolNode(tools)

# State should store raw DB responses
def update_state_from_qdrant(state: dict, search_result: dict):
    state["search_results"] = search_result["passages"]
    state["provenance"] = search_result.get("provenance", [])
    return state
```

### Caching with LangGraph CachePolicy

```python
from langgraph.policies import CachePolicy

# Cache retrieval results with TTL
cache_policy = CachePolicy(ttl=300)  # 5 minutes

def cached_retrieval_node(state: dict, config, runtime):
    # Check cache first
    cached = runtime.cache.get(state["query"])
    if cached:
        return {"search_results": cached}

    # Perform retrieval
    retrieve = dspy.Retrieve(k=5)
    result = retrieve(state["query"])

    # Cache result
    runtime.cache.set(state["query"], result.passages, ttl=300)

    return {"search_results": result.passages}
```

---

## 3. ColBERTv2 Retriever Configuration

### Basic Configuration

```python
import dspy

# Configure ColBERTv2 as retrieval model
dspy.settings.configure(
    lm=dspy.LM("openai/gpt-4o-mini"),
    rm="colbertv2_wiki17_abstracts"  # Or your ColBERTv2 endpoint
)

# Create retrieve module with k passages
retrieve = dspy.Retrieve(k=num_passages)
```

### Remote ColBERTv2 Server

```python
from dspy.dsp.colbertv2 import ColBERTv2

# Connect to remote ColBERTv2 server
colbertv2 = ColBERTv2(
    url="http://20.102.90.50:2017/wiki17_abstracts",
    port=None  # Included in URL
)

# Use in retrieval
results = colbertv2(query="What is ColBERT?", k=10, simplify=True)
# results: list[str] of passages
```

### Local ColBERTv2 Index

```python
from colbert.infra.config import ColBERTConfig
from dspy.dsp.colbertv2 import ColBERTv2RetrieverLocal

# Configure ColBERT
colbert_config = ColBERTConfig(
    checkpoint="colbert-ir/colbertv2.0",
    index_name="my_index",
    experiment="my_experiment",
    nranks=1
)

# Create local retriever
retriever = ColBERTv2RetrieverLocal(
    passages=corpus,
    colbert_config=colbert_config,
    load_only=False  # Set True to load existing index
)

# Use for retrieval
results = retriever(query="search query", k=7)
```

### Evaluation

Use DSPy's built-in evaluation to validate retrieval quality:

```python
from dspy.evaluate import Evaluate
from dspy.datasets import HotPotQA

# Load dataset
dataset = HotPotQA(train_seed=1, eval_seed=2023)
trainset, devset, testset = dataset[:100], dataset[100:200], dataset[200:]

# Define metric
def retrieval_metric(example, pred, trace=None):
    gold_passages = example.passages
    retrieved_passages = pred.passages
    # Calculate recall/precision
    return len(set(gold) & set(retrieved)) / len(gold)

# Evaluate
evaluate = Evaluate(devset=devset, metric=retrieval_metric, num_threads=4)
evaluate(retriever)
```

---

## 4. Passing Retrieved Context Between DSPy and LangGraph

### State Schema Design

LangGraph state should store **raw data only** (no prompt templates):

```python
from typing import TypedDict

class RAGState(TypedDict):
    # Input
    query: str

    # Retrieval results
    search_results: list[str] | None
    provenance: list[dict] | None  # Source id, offset, score

    # Generated output
    draft_response: str | None

    # Error tracking
    error_log: list[str] | None
```

### Serialization Format

```python
def retrieval_node(state: RAGState, config, runtime) -> dict:
    rag = RAG(num_passages=6)
    res = rag(state["query"])

    return {
        "search_results": res.passages,
        "provenance": [  # If retriever provides scores
            {
                "pid": r.pid,
                "score": r.score,
                "source": r.get("source", "unknown")
            }
            for r in res.retrieve_results
        ],
        "draft_response": res.answer
    }
```

### Streaming Context Transfer

DSPy supports streaming via `dspy.streamify`:

```python
import dspy

# Wrap module for streaming
stream_rag = dspy.streamify(
    RAG(),
    stream_listeners=[
        dspy.streaming.StreamListener(
            signature_field_name="answer",
            allow_reuse=True
        )
    ]
)

# Use in async LangGraph node
async def streaming_retrieval_node(state: dict):
    chunks = []
    async for chunk in stream_rag.astream(state["query"]):
        chunks.append(chunk)
        # Yield intermediate results if needed

    return {"draft_response": "".join(chunks)}
```

### Caching Recent Retrievals

```python
from functools import lru_cache
from typing import Optional

@lru_cache(maxsize=128)
def cached_retrieve(query: str, k: int = 5) -> list[str]:
    """Cache retrieval results."""
    retrieve = dspy.Retrieve(k=k)
    result = retrieve(query)
    return result.passages

def cached_retrieval_node(state: dict) -> dict:
    passages = cached_retrieve(state["query"], k=5)
    return {"search_results": passages}
```

---

## 5. Hybrid RAG Patterns: DSPy Retrieval + LangGraph Routing

### Router-First Architecture

LangGraph routes queries to appropriate pipelines (RAG/SQL/hybrid):

```python
from typing import Literal

def route_query(state: dict) -> Literal["rag", "sql", "hybrid"]:
    """Classify query and route to appropriate pipeline."""
    # Use DSPy classifier
    classifier = dspy.Predict("query -> route: Literal['rag', 'sql', 'hybrid']")
    result = classifier(query=state["query"])
    return result.route

# LangGraph with routing
from langgraph.graph import StateGraph

graph = StateGraph(RAGState)
graph.add_node("router", route_query)
graph.add_node("rag_node", rag_retrieval_node)
graph.add_node("sql_node", sql_query_node)
graph.add_node("hybrid_node", hybrid_node)
graph.add_node("synthesizer", synthesis_node)

# Conditional routing
graph.add_conditional_edges(
    "router",
    {
        "rag": "rag_node",
        "sql": "sql_node",
        "hybrid": "hybrid_node"
    }
)
```

### Multi-Retriever Fanout

Use LangGraph `Send` for parallel retrievals:

```python
from langgraph.constants import Send

def fan_out_retrieval(state: dict):
    """Fan out to multiple retrievers."""
    queries = [
        {"query": state["query"], "retriever": "colbert"},
        {"query": state["query"], "retriever": "qdrant"},
        {"query": state["query"], "retriever": "bm25"}
    ]
    return [Send("retrieve", q) for q in queries]

def retrieve(state: dict):
    """Single retrieval node."""
    if state["retriever"] == "colbert":
        retriever = colbert_retriever
    elif state["retriever"] == "qdrant":
        retriever = qdrant_retriever
    else:
        retriever = bm25_retriever

    result = retriever(state["query"])
    return {"search_results": result.passages}

# Merge results from parallel branches
def merge_retrievals(state: dict):
    """Merge results from multiple retrievers."""
    # Deduplicate and rerank
    merged = merge_and_rerank(state["search_results"])
    return {"search_results": merged}
```

### Reranking and Fallback

```python
def rerank_node(state: dict):
    """Rerank retrieved passages."""
    if len(state.get("search_results", [])) == 0:
        # Fallback to no-RAG
        return {"fallback_mode": True}

    # Use DSPy reranker
    reranker = dspy.ChainOfThought("query, passages -> reranked_passages: list[str]")
    result = reranker(query=state["query"], passages=state["search_results"])

    return {"search_results": result.reranked_passages}

def synthesis_node_with_fallback(state: dict):
    """Generate answer with fallback."""
    if state.get("fallback_mode"):
        # Direct LLM call without RAG
        generate = dspy.Predict("query -> answer")
        result = generate(query=state["query"])
    else:
        # RAG generation
        rag = RAG(num_passages=5)
        result = rag(state["query"])

    return {"draft_response": result.answer}
```

### Complete Hybrid Flow

```python
# Based on https://github.com/ahmedsamymohamad/Langgraph_dspy

def build_hybrid_rag_graph():
    graph = StateGraph(RAGState)

    # Add nodes
    graph.add_node("classifier", classifier_node)
    graph.add_node("retriever", retrieval_node)
    graph.add_node("planner", planner_node)
    graph.add_node("sql_generator", sql_generator_node)
    graph.add_node("sql_executor", sql_executor_node)
    graph.add_node("synthesizer", synthesizer_node)

    # Add edges
    graph.set_entry_point("classifier")

    # Conditional routing based on classification
    graph.add_conditional_edges(
        "classifier",
        lambda s: s["route"],
        {
            "rag": "retriever",
            "sql": "planner",
            "hybrid": "retriever"  # Then to planner
        }
    )

    # RAG path
    graph.add_edge("retriever", "synthesizer")

    # SQL path
    graph.add_edge("planner", "sql_generator")
    graph.add_edge("sql_generator", "sql_executor")
    graph.add_edge("sql_executor", "synthesizer")

    # Hybrid path (retrieval + SQL)
    graph.add_edge("retriever", "planner")

    # End
    graph.set_finish_point("synthesizer")

    return graph.compile()
```

---

## 6. State Management Best Practices

### Typed State Schema

```python
from typing import TypedDict, Optional, List, Dict

class AgentState(TypedDict):
    # Input fields
    query: str

    # Retrieval results
    search_results: Optional[List[str]]
    provenance: Optional[List[Dict]]  # {pid, score, source}

    # Generated content
    draft_response: Optional[str]

    # Error tracking
    error_log: Optional[List[str]]
    retry_count: int

    # Metadata
    timestamp: float
    retrieval_k: int
```

### State Update Pattern

```python
def retrieval_node_with_provenance(state: AgentState) -> dict:
    """Retrieval node with provenance tracking."""
    try:
        rag = RAG(num_passages=state.get("retrieval_k", 5))
        res = rag(state["query"])

        # Extract provenance if available
        provenance = []
        if hasattr(res, "retrieve_results"):
            for r in res.retrieve_results:
                provenance.append({
                    "pid": getattr(r, "pid", -1),
                    "score": getattr(r, "score", 0.0),
                    "source": getattr(r, "source", "unknown")
                })

        return {
            "search_results": res.passages,
            "provenance": provenance,
            "draft_response": res.answer,
            "timestamp": time.time(),
            "retry_count": 0
        }

    except Exception as e:
        return {
            "error_log": [str(e)],
            "retry_count": state.get("retry_count", 0) + 1
        }
```

### Cacheable State Design

```python
class CacheableState(TypedDict):
    # Cacheable retrieval results
    cached_results: Dict[str, dict]  # query -> {passages, timestamp}

    # TTL configuration
    cache_ttl: int  # seconds

def check_cache(state: CacheableState, query: str) -> Optional[dict]:
    """Check if query result is cached and fresh."""
    if query in state["cached_results"]:
        cached = state["cached_results"][query]
        age = time.time() - cached["timestamp"]
        if age < state["cache_ttl"]:
            return cached["passages"]
    return None

def update_cache(state: CacheableState, query: str, passages: list) -> dict:
    """Update cache with new retrieval result."""
    state["cached_results"][query] = {
        "passages": passages,
        "timestamp": time.time()
    }
    return state
```

---

## 7. Operational Concerns

### Monitoring and Observability

```python
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("rag_pipeline")

def monitored_retrieval_node(state: dict):
    """Retrieval node with logging."""
    logger.info(f"Starting retrieval for query: {state['query']}")
    start_time = time.time()

    try:
        rag = RAG(num_passages=5)
        res = rag(state["query"])

        elapsed = time.time() - start_time
        logger.info(f"Retrieval completed in {elapsed:.2f}s")
        logger.info(f"Retrieved {len(res.passages)} passages")

        return {
            "search_results": res.passages,
            "draft_response": res.answer
        }

    except Exception as e:
        logger.error(f"Retrieval failed: {str(e)}")
        return {"error_log": [str(e)]}
```

### Security Patterns

DSPy's MCP security wrapper handles authentication:

```python
from dspy.mcp import security_wrapper

@security_wrapper
def secure_retrieval(state: dict):
    """Secure retrieval with token refresh."""
    # Wrapper handles 401 token refresh
    # and 429 rate limiting automatically
    rag = RAG(num_passages=5)
    return rag(state["query"])
```

### Testing and Evaluation

```python
from dspy.evaluate import Evaluate

# Define evaluation metrics
def answer_em_metric(example, pred, trace=None):
    """Exact match metric for answers."""
    return example.answer.lower() == pred.answer.lower()

def retrieval_recall_metric(example, pred, trace=None):
    """Recall metric for retrieval."""
    gold_docs = set(example.gold_doc_ids)
    retrieved_docs = set(pred.get("provenance", []))
    return len(gold_docs & retrieved_docs) / len(gold_docs)

# Create evaluator
evaluator = Evaluate(
    devset=devset,
    metric=lambda g, p, t: answer_em_metric(g, p, t) * 0.5 + retrieval_recall_metric(g, p, t) * 0.5,
    num_threads=4,
    display_progress=True
)

# Evaluate
result = evaluator(rag_module)
print(f"Score: {result.score:.2%}")
```

---

## 8. Complete End-to-End Pipeline Example

```python
import dspy
from typing import TypedDict, Literal
from langgraph.graph import StateGraph

# 1. Configure DSPy
dspy.settings.configure(
    lm=dspy.LM("ollama_chat/gemma3:4b", api_base="http://localhost:11434"),
    rm=QdrantRM(...)  # Or ColBERTv2
)

# 2. Define DSPy RAG module
class RAG(dspy.Module):
    def __init__(self, num_passages=4):
        super().__init__()
        self.retrieve = dspy.Retrieve(k=num_passages)
        self.generate = dspy.ChainOfThought("question, context -> answer")

    def forward(self, question: str):
        passages = self.retrieve(question).passages
        return self.generate(question=question, context=passages)

# 3. Define LangGraph state
class PipelineState(TypedDict):
    query: str
    search_results: list[str] | None
    draft_response: str | None
    route: Literal["rag", "direct"]

# 4. Define LangGraph nodes
def route_node(state: PipelineState) -> dict:
    """Route to RAG or direct LLM."""
    # Simple routing logic
    if "database" in state["query"].lower() or "search" in state["query"].lower():
        return {"route": "rag"}
    return {"route": "direct"}

def rag_node(state: PipelineState) -> dict:
    """RAG retrieval + generation."""
    rag = RAG(num_passages=5)
    res = rag(state["query"])
    return {
        "search_results": res.passages,
        "draft_response": res.answer
    }

def direct_node(state: PipelineState) -> dict:
    """Direct LLM call without RAG."""
    generate = dspy.Predict("query -> answer")
    res = generate(query=state["query"])
    return {"draft_response": res.answer}

# 5. Build LangGraph
graph = StateGraph(PipelineState)
graph.add_node("router", route_node)
graph.add_node("rag", rag_node)
graph.add_node("direct", direct_node)

graph.set_entry_point("router")

graph.add_conditional_edges(
    "router",
    lambda s: s["route"],
    {
        "rag": "rag",
        "direct": "direct"
    }
)

graph.set_finish_point("rag")
graph.set_finish_point("direct")

# 6. Compile and run
app = graph.compile()

# Invoke
result = app.invoke({"query": "What is RAG?"})
print(result["draft_response"])
```

---

## 9. Evidence Gaps

The following details are **not covered** in the available evidence and must be sourced from official documentation:

### Qdrant-Specific
- QdrantRM client connection/authentication details
- Collection schema design (distance metrics, shard/replica settings)
- Connection pooling, failover, throughput tuning
- Write-through vs write-back consistency strategies

### ColBERTv2 Low-Level
- Tokenization choices, max doc/query length, stride
- Index build parameters
- Deployment/hosting recommendations (local vs managed)
- Retrieval vs rerank thresholds and tuning

### LangGraph Persistence
- Canonical serialization formats for embeddings/timestamps
- Persistence APIs for external stores
- Explicit token-budgeting/truncation heuristics

### Performance Benchmarks
- Quantitative tradeoffs (latency vs recall)
- Recommended numeric thresholds
- Performance tuning guides

---

## 10. Key Takeaways

1. **DSPy provides modular retrieval** via `dspy.Retrieve(k)` that integrates cleanly with LangGraph nodes
2. **Qdrant integration** uses `dspy-qdrant` package with `QdrantRM` retriever model
3. **ColBERTv2** supports both remote server and local index configurations
4. **State mapping** stores raw passages and provenance in typed LangGraph state
5. **Hybrid patterns** enable routing between RAG/SQL/direct LLM based on query classification
6. **Resilience** uses layered retries: DSPy LM retries + LangGraph RetryPolicy
7. **Performance** uses DSPy batching + LangGraph Send for parallel retrieval
8. **Caching** leverages LangGraph CachePolicy for expensive retrievals
9. **Async patterns** use `dspy.asyncify` or `module.acall()` when profiling justifies complexity
10. **Evaluation** uses DSPy's built-in metrics and datasets (HotPotQA) for validation

---

## References

### DSPy Documentation
- [DSPy Cheatsheet](https://dspy.ai/cheatsheet/)
- [DSPy Async Tutorial](https://dspy.ai/tutorials/async/)
- [DSPy API: asyncify](https://dspy.ai/api/utils/asyncify/)

### Integration Guides
- [Using DSPy for RAG Implementation](https://cobusgreyling.substack.com/p/using-dspy-for-a-rag-implementation)
- [Qdrant DSPy Integration](https://qdrant.tech/documentation/frameworks/dspy/)

### LangGraph Documentation
- [Thinking in LangGraph](https://docs.langchain.com/oss/python/langgraph/thinking-in-langgraph)
- [LangGraph Graph API](https://docs.langchain.com/oss/python/langgraph/graph-api)

### GitHub Repositories
- [Langgraph_dspy (Production Example)](https://github.com/ahmedsamymohamad/Langgraph_dspy)
- [DSPy Main Repository](https://github.com/stanfordnlp/dspy)

### Articles and Tutorials
- [Production Ready AI Agents](https://www.firebird-technologies.com/p/building-production-ready-ai-agents)
- [LangGraph + DSPy GEPA Researcher](https://rajapatnaik.com/blog/2025/10/23/langgraph-dspy-gepa-researcher)
- [Handling Errors in LangGraph with Retry Policies](https://dev.to/aiengineering/a-beginners-guide-to-handling-errors-in-langgraph-with-retry-policies-h22)

### Additional Resources
- [Leoniemonigatti DSPy Blog](https://www.leoniemonigatti.com/blog/dspy.html)
- [Zemoso Labs: LangChain and DSPy with Llama 3.1](https://www.zemosolabs.com/blog/insights-langchain-and-dspy-with-llama-3-1)
- [LangFuse LangGraph Agents Guide](https://langfuse.com/guides/cookbook/example_langgraph_agents)
