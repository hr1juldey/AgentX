# ColBERTv2 Integration: DSPy + Qdrant + FastEmbed

**Research Date:** 2025-02-04
**Purpose:** How ColBERTv2 works with DSPy and Qdrant for AGENTX

---

## Executive Summary

**ColBERTv2 is NOT a server** - it's a **late interaction embedding model** that produces multivectors (one vector per token).

**The recommended pattern for AGENTX** (based on Qdrant medical bot example) is:
- **ONE collection** with **TWO named vectors**: "dense" (fast) + "colbert" (accurate)
- **Prefetch pattern**: retrieve with dense, rerank with ColBERT in a single query
- ColBERT has **no indexing** (`hnsw_config(m=0)`) - used only for reranking

```
agentx_knowledge (ONE collection)
├── dense vector (384 dims, indexed) → Fast retrieval
└── colbert multivector (N×128 dims, not indexed) → Accurate reranking
```

---

## 1. Understanding ColBERTv2

### What is ColBERTv2?

**ColBERTv2** is a **late interaction** retrieval model that produces **multivector** embeddings:

```python
# Traditional Dense Embedding (single vector)
"capital of France" → [0.1, 0.2, -0.3, ..., 0.5]  # Shape: (384,)

# ColBERTv2 Multivector (one vector per token)
"capital of France" → [
  [0.1, 0.2, ...],  # Token 1: "capital" (128 dims)
  [-0.1, 0.5, ...], # Token 2: "of"      (128 dims)
  [0.3, -0.2, ...], # Token 3: "France"  (128 dims)
]  # Shape: (3 tokens × 128 dims)
```

### Late Interaction Mechanism

```
Cross-Encoder (Early Interaction):
Query + Document → [Model processes together] → Score

Late Interaction (ColBERT):
Query → [Model] → Query Vectors (matrix)
Document → [Model] → Document Vectors (matrix)

Query Vectors × Document Vectors → Score (computed OUTSIDE model)

Scoring: MAX_SIM (Maximum Similarity)
- For each query token, find max similarity with ALL document tokens
- Sum across all query tokens for final score
```

### Why Late Interaction?

| Aspect | Late Interaction (ColBERT) | Cross-Encoder |
|--------|----------------------------|---------------|
| Speed | Fast (embeddings pre-computed) | Slow (processes query+doc together) |
| Storage | Larger (multivectors) | Smaller (no storage) |
| Accuracy | High (token-level matching) | Highest (full interaction) |
| Use case | First-stage retrieval | Reranking |

---

## 2. FastEmbed: Universal Vectorizer

**FastEmbed** is the key - it supports BOTH dense and late interaction embeddings:

```python
from fastembed import TextEmbedding, LateInteractionTextEmbedding

# Dense embedding (single vector)
dense_model = TextEmbedding("BAAI/bge-small-en-v1.5")
dense_embedding = list(dense_model.embed(["text"]))[0]
# Shape: (384,) - single vector

# Late interaction embedding (multivector)
late_model = LateInteractionTextEmbedding("colbert-ir/colbertv2.0")
doc_embedding = list(late_model.embed(["text"]))[0]
# Shape: (N tokens, 128 dims) - matrix
query_embedding = list(late_model.query_embed(["query"]))[0]
# Shape: (M tokens, 128 dims) - matrix

# List supported models
LateInteractionTextEmbedding.list_supported_models()
# Output:
# [
#   {'model': 'colbert-ir/colbertv2.0', 'dim': 128, 'size_in_GB': 0.44},
#   {'model': 'answerdotai/answerai-colbert-small-v1', 'dim': 96, 'size_in_GB': 0.13}
# ]
```

### What About the DSPy ColBERT URL?

```python
# This is NOT a ColBERT-specific server!
colbert_rm = dspy.ColBERTv2(url="http://20.102.90.50:2017/wiki17_abstracts")
```

**Clarification:**
- The URL is a **hosted retrieval server** that happens to use ColBERTv2
- The server has pre-indexed documents using ColBERT embeddings
- DSPy sends HTTP requests to this server
- The server does retrieval and returns results

**This is different from using ColBERT directly with Qdrant:**
- Remote server: External infrastructure, pre-indexed corpus
- Qdrant + ColBERT: Local, flexible, you control the data

---

## 3. Qdrant Multi-Vector Collection (Dense + ColBERT)

Based on the Qdrant medical bot example, the **recommended pattern** is:

### Single Collection with Two Named Vectors

```python
from qdrant_client import QdrantClient, models
from fastembed import TextEmbedding, LateInteractionTextEmbedding

# Qdrant port from docker-compose.yaml: 6335
qdrant_client = QdrantClient(url="http://localhost:6335")

collection_name = "agentx_knowledge"

# Create collection with BOTH dense and ColBERT vectors
if not qdrant_client.collection_exists(collection_name):
    qdrant_client.create_collection(
        collection_name=collection_name,
        vectors_config={
            # Dense vector for fast retrieval (indexed)
            "dense": models.VectorParams(
                size=384,  # BAAI/bge-small-en dimension
                distance=models.Distance.COSINE
            ),
            # ColBERT multivector for reranking (NOT indexed)
            "colbert": models.VectorParams(
                size=128,
                distance=models.Distance.COSINE,
                multivector_config=models.MultiVectorConfig(
                    comparator=models.MultiVectorComparator.MAX_SIM
                ),
                hnsw_config=models.HnswConfigDiff(m=0),  # No indexing for reranker!
            ),
        },
    )
```

### Indexing Documents (Index Time)

```python
# Load both embedders
dense_model = TextEmbedding("BAAI/bge-small-en")
colbert_model = LateInteractionTextEmbedding("colbert-ir/colbertv2.0")

documents = ["Python is a programming language", "JavaScript for web development"]

# Create documents with BOTH embeddings
dense_documents = [models.Document(text=doc, model="BAAI/bge-small-en") for doc in documents]
colbert_documents = [models.Document(text=doc, model="colbert-ir/colbertv2.0") for doc in documents]

# Upload with both vectors in ONE point
points = [
    models.PointStruct(
        id=i,
        vector={"dense": dense_documents[i], "colbert": colbert_documents[i]},
        payload={"text": doc}
    )
    for i, doc in enumerate(documents)
]

qdrant_client.upsert(collection_name=collection_name, points=points)
```

### Prefetch Pattern (Query Time) - THE KEY PATTERN

```python
def search_with_reranking(query_text: str):
    """Retrieve with dense, rerank with ColBERT in ONE query."""
    # Embed query with BOTH models
    dense_query = list(dense_model.embed([query_text]))[0]
    colbert_query = list(colbert_model.embed([query_text]))[0]

    # Prefetch pattern: retrieve with dense, rerank with colbert
    results = qdrant_client.query_points(
        collection_name=collection_name,
        prefetch=models.Prefetch(
            query=dense_query,    # First: retrieve candidates using dense
            using="dense"          # Fast indexed search
        ),
        query=colbert_query,       # Second: rerank using ColBERT
        using="colbert",           # Accurate late interaction
        limit=5,
        with_payload=True
    )

    return [r.payload["text"] for r in results.points]
```

### How Prefetch Works

```
Query → [Dense Embedding] → Top 100 candidates (fast, indexed)
                            ↓
                       Prefetch pass
                            ↓
Query → [ColBERT Embedding] → Rerank top 100 → Top 5 results (accurate)
```

---

## 4. DSPy 3.1+ API Update

**Note:** DSPy 3.1+ has a unified API. See **file 13** for complete documentation.

```python
# New unified LLM API
lm = dspy.LM("ollama_chat/gemma3:4b", api_base="http://localhost:11434", api_key="")

# New unified Embedder API
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("sentence-transformers/static-retrieval-mrl-en-v1")
embedder = dspy.Embedder(model.encode)
dspy.configure(lm=lm, embedder=embedder)
```

## 5. dspy-qdrant with FastEmbed

The `dspy-qdrant` package uses **FastEmbed** for vectorization:

```python
from dspy_qdrant import QdrantRM
from qdrant_client import QdrantClient
from fastembed import LateInteractionTextEmbedding
import dspy

# Qdrant port: 6335 (from docker-compose.yaml)
qdrant_client = QdrantClient(url="http://localhost:6335")

# Create ColBERT vectorizer
colbert_vectorizer = LateInteractionTextEmbedding("colbert-ir/colbertv2.0")

# Configure QdrantRM with ColBERT
rm = QdrantRM(
    qdrant_collection_name="agentx_web_search",
    qdrant_client=qdrant_client,
    vectorizer=colbert_vectorizer,  # FastEmbed vectorizer
    vector_name="dense",
    document_field="text",
    k=5
)

# Configure DSPy
lm = dspy.LM("ollama_chat/gemma3:4b", api_base="http://localhost:11434")
dspy.settings.configure(lm=lm, rm=rm)

# Use in DSPy modules
class ResearcherAgent(dspy.Module):
    def __init__(self):
        super().__init__()
        self.retrieve = dspy.Retrieve(k=5)

    def forward(self, query):
        passages = self.retrieve(query).passages
        return self.generate_answer(context=passages, question=query)
```

### How QdrantRM Works with ColBERT

```python
# QdrantRM internals (simplified)
class QdrantRM:
    def __init__(
        self,
        qdrant_collection_name: str,
        qdrant_client: QdrantClient,
        vectorizer: BaseSentenceVectorizer = None,
        k: int = 3,
    ):
        if vectorizer is None:
            # Default: FastEmbed dense vectorizer
            from fastembed import TextEmbedding
            vectorizer = FastEmbedVectorizer()  # BGE-small

        self.vectorizer = vectorizer

    def forward(self, query: str, k: int = None):
        # Embed query based on vectorizer type
        if isinstance(self.vectorizer, FastEmbedVectorizer):
            # Dense: single vector
            query_vector = list(self.vectorizer.embed([query]))[0]
        elif isinstance(self.vectorizer, LateInteractionTextEmbedding):
            # ColBERT: multivector (matrix)
            query_vector = list(self.vectorizer.query_embed([query]))[0]

        # Search Qdrant
        results = self.qdrant_client.query_points(
            collection_name=self.qdrant_collection_name,
            query=query_vector,
            limit=k or self.k,
        )

        return [r.payload[self.document_field] for r in results.points]
```

---

## 5. Mem0AI with FastEmbed

Mem0AI can also use FastEmbed (supports ColBERT):

```python
from mem0 import Memory

# Mem0AI configuration with FastEmbed
config = {
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": "localhost",
            "port": 6335,  # From docker-compose.yaml
            "collection_name": "agentx_memories"
        },
    },
    "llm": {
        "provider": "ollama",
        "config": {
            "model": "gemma3:4b",
            "host": "http://localhost:11434"
        },
    },
    "embedder": {
        "provider": "ollama",  # Or "fastembed" for ColBERT
        "config": {
            "model": "nomic-embed-text",
            "host": "http://localhost:11434"
        },
    },
}

memory = Memory.from_config(config)
```

---

## 6. AGENTX Architecture (Recommended Pattern)

### Collection Strategy

Based on the Qdrant medical bot example, the **recommended pattern** is:

```
Qdrant (localhost:6335)
│
├── agentx_memories
│   │ Type: Dense vectors only
│   │ Model: Ollama (nomic-embed-text)
│   │ Size: 384 dims
│   │ Purpose: Mem0AI conversational memory (ALL agents)
│   │
│
└── agentx_knowledge
    │ Type: TWO named vectors in ONE collection
    │   ├── dense: BGE-small (384 dims, indexed) → Fast retrieval
    │   └── colbert: ColBERTv2 (N×128 dims, NOT indexed) → Accurate reranking
    │ Purpose: RAG + Research with prefetch pattern
```

### Configuration Summary

| Collection | Vectors | Purpose |
|------------|---------|---------|
| `agentx_memories` | dense (384) | Mem0AI conversational memory |
| `agentx_knowledge` | dense (384) + colbert (N×128) | RAG + Research with prefetch reranking |

### Why This Pattern?

- **Mem0AI**: Simple conversational memory → dense vectors only
- **agentx_knowledge**: Complex retrieval with reranking → dense + ColBERT with prefetch
- **One collection** for knowledge base (not three separate ones) → simpler management

---

## 7. Complete Implementation: Prefetch Pattern

**This is the recommended pattern from the Qdrant medical bot example: ONE collection with TWO named vectors.**

### Collection Setup

```python
import dspy
from dspy_qdrant import QdrantRM
from fastembed import TextEmbedding, LateInteractionTextEmbedding
from qdrant_client import QdrantClient, models

# Qdrant client (port 6335 from docker-compose.yaml)
qdrant_client = QdrantClient(url="http://localhost:6335")

# Create collection with BOTH vectors (medical bot pattern)
COLLECTION = "agentx_knowledge"

if not qdrant_client.collection_exists(COLLECTION):
    qdrant_client.create_collection(
        collection_name=COLLECTION,
        vectors_config={
            # Dense: for fast initial retrieval (indexed)
            "dense": models.VectorParams(
                size=384,
                distance=models.Distance.COSINE,
                # HNSW indexing by default (fast)
            ),
            # ColBERT: for accurate reranking (NOT indexed)
            "colbert": models.VectorParams(
                size=128,
                distance=models.Distance.COSINE,
                multivector_config=models.MultiVectorConfig(
                    comparator=models.MultiVectorComparator.MAX_SIM
                ),
                hnsw_config=models.HnswConfigDiff(m=0),  # NO indexing!
            ),
        },
    )

# Initialize vectorizers
dense_vectorizer = TextEmbedding("BAAI/bge-small-en-v1.5")
colbert_vectorizer = LateInteractionTextEmbedding("colbert-ir/colbertv2.0")

# Configure DSPy
lm = dspy.LM("ollama_chat/gemma3:4b", api_base="http://localhost:11434")
dspy.settings.configure(lm=lm)
```

### Prefetch Query Pattern

```python
from fastembed import TextEmbedding, LateInteractionTextEmbedding

def prefetch_search(query: str, top_k: int = 5):
    """
    Prefetch pattern: retrieve with dense, rerank with ColBERT.
    This is the Qdrant medical bot pattern.
    """
    # Step 1: Create dense query for initial retrieval
    dense_query = list(dense_vectorizer.query_embed([query]))[0]

    # Step 2: Create ColBERT query for reranking
    colbert_query = list(colbert_vectorizer.query_embed([query]))[0]

    # Step 3: Prefetch search (dense → ColBERT rerank)
    results = qdrant_client.query_points(
        collection_name=COLLECTION,
        prefetch=[
            # First: retrieve top 100 with dense (fast, indexed)
            models.Prefetch(
                query=dense_query,
                using="dense",
                limit=100,
            )
        ],
        # Then: rerank with ColBERT (accurate)
        query=colbert_query,
        using="colbert",
        limit=top_k,
        with_payload=True
    )

    return [r.payload["text"] for r in results.points]

# Usage
results = prefetch_search("Latest quantum computing breakthroughs", top_k=5)
```

### DSPy Agent with Prefetch

```python
# Researcher Agent with prefetch pattern
class ResearcherAgent(dspy.Module):
    def __init__(self, num_passages=5):
        super().__init__()
        self.num_passages = num_passages
        self.react = dspy.ReAct(
            "query->answer",
            tools=[web_search_tool, searxng_search_tool]
        )

    def forward(self, query: str):
        # Use prefetch pattern (bypass dspy.Retrieve for now)
        context = prefetch_search(query, top_k=self.num_passages)

        # Use ReAct with context
        result = self.react(
            query=f"{query}\n\nContext:\n{' '.join(context)}"
        )

        return dspy.Prediction(
            answer=result.answer,
            context=context,
            retrieved_count=len(context)
        )

researcher = ResearcherAgent()
result = researcher.forward("Latest quantum computing breakthroughs")
```

---

## 8. Data Ingestion: Web Search to Multi-Vector Collection

**Ingest data with BOTH dense and ColBERT vectors into a single collection:**

```python
from fastembed import TextEmbedding, LateInteractionTextEmbedding
from qdrant_client import QdrantClient, models

# Initialize (port 6335 from docker-compose.yaml)
qdrant_client = QdrantClient(url="http://localhost:6335")
dense_vectorizer = TextEmbedding("BAAI/bge-small-en-v1.5")
colbert_vectorizer = LateInteractionTextEmbedding("colbert-ir/colbertv2.0")

# Web search results from SearXNG
search_results = [
    {"url": "https://example.com/1", "title": "Python 3.12 Released", "text": "..."},
    {"url": "https://example.com/2", "title": "JavaScript ES2024", "text": "..."},
]

# Batch ingestion with BOTH vectors
points = []
for i, result in enumerate(search_results):
    # Step 1: Create dense vector (for fast retrieval)
    dense_vector = list(dense_vectorizer.embed([result["text"]]))[0]

    # Step 2: Create ColBERT multivector (for accurate reranking)
    colbert_vector = list(colbert_vectorizer.embed([result["text"]]))[0]

    # Step 3: Store BOTH vectors with named keys
    points.append(
        models.PointStruct(
            id=i,
            vector={
                "dense": dense_vector,      # Shape: (384,)
                "colbert": colbert_vector,  # Shape: (N, 128)
            },
            payload={
                "text": result["text"],
                "title": result["title"],
                "url": result["url"]
            }
        )
    )

# Upload to Qdrant (agentx_knowledge collection)
qdrant_client.upsert(
    collection_name="agentx_knowledge",
    points=points
)
```

---

## 9. Hybrid: Prefetch Pattern vs. Separate Collections

**Note: The prefetch pattern (ONE collection with TWO vectors) is recommended.**

### Option A: Prefetch Pattern (Recommended)

See section 7 for complete implementation. The prefetch pattern is:

```
Query → [Dense] → Top 100 (fast, indexed)
         ↓ Prefetch pass
Query → [ColBERT] → Rerank → Top 5 (accurate)
```

### Option B: Separate Collections (Alternative)

If you need separate collections for some reason:

```python
from dspy_qdrant import QdrantRM
from fastembed import TextEmbedding, LateInteractionTextEmbedding

# Collection 1: agentx_documents (dense only)
dense_rm = QdrantRM(
    qdrant_collection_name="agentx_documents",
    qdrant_client=qdrant_client,
    vectorizer=TextEmbedding("BAAI/bge-small-en-v1.5"),
    k=100  # Retrieve 100 candidates
)

# Collection 2: agentx_colbert (ColBERT only, for reranking)
colbert_rm = QdrantRM(
    qdrant_collection_name="agentx_colbert",
    qdrant_client=qdrant_client,
    vectorizer=LateInteractionTextEmbedding("colbert-ir/colbertv2.0"),
    k=5  # Rerank top 5
)

class HybridRAGAgent(dspy.Module):
    def __init__(self):
        super().__init__()
        self.dense_retrieve = dspy.Retrieve(k=100)
        self.colbert_retrieve = dspy.Retrieve(k=5)
        self.generate = dspy.ChainOfThought("context, question->answer")

    def forward(self, question):
        # Stage 1: Dense retrieval
        dspy.settings.configure(rm=dense_rm)
        candidates = self.dense_retrieve(question).passages

        # Stage 2: ColBERT reranking
        dspy.settings.configure(rm=colbert_rm)
        top_context = self.colbert_retrieve(question).passages

        answer = self.generate(context=top_context, question=question)
        return answer
```

**Recommendation**: Use Option A (prefetch pattern) for better performance and simpler management.

---

## 10. Performance Comparison

| Collection | Vectors | Storage | Query Speed | Accuracy |
|------------|---------|---------|-------------|----------|
| agentx_memories | dense (384) | Low | Very Fast | Good |
| agentx_knowledge | dense (384) + colbert (N×128) | High | Fast + Accurate | Excellent |

**Prefetch Pattern Benefits:**
- Dense (indexed) → Fast retrieval of top 100 candidates
- ColBERT (not indexed) → Accurate reranking to top 5 results
- One collection → Simpler management than separate collections

**Recommendations:**

- Use `agentx_memories` (dense only) for Mem0AI conversational memory
- Use `agentx_knowledge` (dense + ColBERT with prefetch) for RAG + Research
- The prefetch pattern gives you the best of both worlds: speed + accuracy

---

## 11. Installation

```bash
# Core dependencies
pip install dspy-ai dspy-qdrant fastembed qdrant-client

# For Mem0AI
pip install mem0ai

# Start Qdrant (from docker-compose.yaml)
cd agentx
docker-compose up -d
```

---

## 12. Quick Reference

```python
# Dense retrieval
from fastembed import TextEmbedding
model = TextEmbedding("BAAI/bge-small-en-v1.5")
emb = list(model.embed(["text"]))[0]  # Shape: (384,)

# ColBERT retrieval
from fastembed import LateInteractionTextEmbedding
model = LateInteractionTextEmbedding("colbert-ir/colbertv2.0")
doc_emb = list(model.embed(["text"]))[0]      # Shape: (N, 128)
query_emb = list(model.query_embed(["q"]))[0]  # Shape: (M, 128)

# Qdrant multivector collection
from qdrant_client import QdrantClient, models
client = QdrantClient(url="http://localhost:6335")
client.create_collection(
    collection_name="my_colbert",
    vectors_config=models.VectorParams(
        size=128,
        distance=models.Distance.COSINE,
        multivector_config=models.MultiVectorConfig(
            comparator=models.MultiVectorComparator.MAX_SIM
        ),
    ),
)

# DSPy with ColBERT
from dspy_qdrant import QdrantRM
rm = QdrantRM(
    qdrant_collection_name="my_colbert",
    qdrant_client=client,
    vectorizer=LateInteractionTextEmbedding("colbert-ir/colbertv2.0"),
    k=5
)
dspy.settings.configure(lm=lm, rm=rm)
```

---

## Sources

- [Qdrant FastEmbed ColBERT](https://qdrant.tech/documentation/fastembed/fastembed-colbert/)
- [dspy-qdrant PyPI](https://pypi.org/project/dspy-qdrant/)
- [FastEmbed GitHub](https://github.com/qdrant/fastembed)
- [Mem0AI Configuration](https://docs.mem0.ai/open-source/configuration)
- [DSPy Source Code](/home/riju279/Downloads/dspy-main/dspy-main/)
- [AGENTX docker-compose.yaml](/home/riju279/Documents/Code/XRIG/AgentX/agentx/docker-compose.yaml)

---

**Key Takeaways:**

1. **ColBERTv2 is an embedding model**, not a server
2. **FastEmbed is the universal vectorizer** for all systems (Mem0AI, Qdrant, dspy-qdrant)
3. **Qdrant has native multivector support** - no external ColBERT server needed
4. **Port is 6335** (from docker-compose.yaml)
5. **All systems can use ColBERT** via FastEmbed's `LateInteractionTextEmbedding`
