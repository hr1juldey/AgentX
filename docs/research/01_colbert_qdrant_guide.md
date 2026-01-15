# ColBERTv2 + Qdrant Integration Guide

## Overview

ColBERT (Contextual Late Interaction over BERT) is a late interaction model that produces multi-vector representations of text, enabling more nuanced semantic matching than single-vector embeddings.

## Why ColBERTv2?

### Advantages
- **Token-level granularity** - Preserves fine-grained semantic information
- **Late interaction** - Efficient retrieval without early query-document mixing
- **MaxSim operation** - Finds maximum similarity for each query token
- **State-of-the-art retrieval** - Outperforms dense embeddings on benchmarks
- **Residual compression** - Reduced storage footprint (ColBERTv2)

### Trade-offs
- **Memory overhead** - More vectors per document vs single-vector
- **Slower retrieval** - More computation per query
- **Best for reranking** - Use with two-stage pipeline

## Architecture

### Late Interaction Mechanism

```
Query: "A movie for kids with fantasy elements"
├── Tokenize → [A, movie, for, kids, with, fantasy, elements]
├── Embed per token → [v1, v2, v3, v4, v5, v6, v7]
└── Multi-vector: 7 × 128 = 896 dimensions

Document: "Kubo and the Two Strings..."
├── Tokenize → [Kubo, and, the, Two, Strings, ...]
├── Embed per token → [w1, w2, w3, w4, w5, ...]
└── Multi-vector: 48 × 128 = 6144 dimensions

Scoring: MaxSim(query, doc) = Σ max(sim(vi, wj))
For each query token, find max similarity with any document token
```

### FastEmbed Models Supported

| Model | Dimensions | Size | Description |
|-------|-----------|------|-------------|
| colbert-ir/colbertv2.0 | 128 | 0.44 GB | Original ColBERTv2 |
| answerdotai/answerai-colbert-small-v1 | 96 | 0.13 GB | Multilingual |
| jinaai/jina-colbert-v2 | 128 | 2.24 GB | Enhanced capabilities |

## Implementation

### Installation

```bash
pip install "fastembed>=0.7.4" "qdrant-client>=1.16.2"
```

### Basic Setup

```python
from fastembed import LateInteractionTextEmbedding
from qdrant_client import QdrantClient, models

# Initialize ColBERT model
model_name = "colbert-ir/colbertv2.0"
embedding_model = LateInteractionTextEmbedding(model_name)

# Initialize Qdrant (in-memory for development)
qdrant_client = QdrantClient(":memory:")

# Production: use persistent storage
# qdrant_client = QdrantClient(url="http://localhost:6333")
```

### Create Collection with Multivector Support

```python
qdrant_client.create_collection(
    collection_name="agentx_memory",
    vectors_config=models.VectorParams(
        size=128,  # ColBERT vector dimension
        distance=models.Distance.COSINE,
        multivector_config=models.MultiVectorConfig(
            comparator=models.MultiVectorComparator.MAX_SIM
        )
    )
)
```

### Embed Documents

```python
documents = [
    "User prefers Italian food, especially pasta carbonara",
    "User likes to exercise in the morning around 7 AM",
    "User enjoys hiking on weekends",
]

# Generate embeddings (generator)
embeddings = list(embedding_model.embed(documents))

# Check shape: (num_tokens, 128)
print(f"First doc: {embeddings[0].shape}")
# Output: (9, 128) - 9 tokens, 128 dimensions each
```

### Upload to Qdrant

```python
from qdrant_client.models import PointStruct

points = [
    PointStruct(
        id=idx,
        vector=embedding,  # Multi-vector
        payload={
            "text": doc,
            "timestamp": "2025-01-15T10:00:00Z",
            "user_id": "user_123",
            "category": "preference"
        }
    )
    for idx, (doc, embedding) in enumerate(zip(documents, embeddings))
]

qdrant_client.upsert(
    collection_name="agentx_memory",
    points=points
)
```

### Querying

```python
query = "What are the user's exercise preferences?"
query_embedding = list(embedding_model.query_embed(query))[0]

results = qdrant_client.query_points(
    collection_name="agentx_memory",
    query=query_embedding,
    limit=3,
    with_payload=True
)

for result in.results:
    print(f"Score: {result.score:.4f}")
    print(f"Text: {result.payload['text']}")
    print()
```

### Temporal Filtering

```python
from datetime import datetime, timedelta

# Last 7 days only
time_filter = models.Filter(
    must=[
        models.FieldCondition(
            key="timestamp",
            range=models.DateTimeRange(
                gte=datetime.now() - timedelta(days=7)
            )
        )
    ]
)

results = qdrant_client.query_points(
    collection_name="agentx_memory",
    query=query_embedding,
    limit=10,
    query_filter=time_filter
)
```

## Two-Stage Retrieval Pipeline

### Stage 1: Dense Retrieval (Fast)

```python
from fastembed import TextEmbedding

# Use faster single-vector model for initial retrieval
dense_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
query_dense = list(dense_model.embed(query))[0]

# Retrieve top 100 candidates
candidates = qdrant_client.search(
    collection_name="agentx_memory",
    query_vector=query_dense,
    limit=100
)
candidate_ids = [point.id for point in candidates]
```

### Stage 2: ColBERT Reranking (Precise)

```python
# Rerank with ColBERT
query_colbert = list(embedding_model.query_embed(query))[0]

# Retrieve only candidates
from qdrant_client.models import Filter

rerank_filter = Filter(
    must=[models.HasIdCondition(has_id=candidate_ids)]
)

results = qdrant_client.query_points(
    collection_name="agentx_memory",
    query=query_colbert,
    query_filter=rerank_filter,
    limit=10
)
```

## Performance Optimization

### GPU Acceleration

```python
# Enable CUDA (if available)
embedding_model = LateInteractionTextEmbedding(
    model_name,
    providers=["CUDAExecutionProvider"]  # ONNX GPU provider
)
```

### Batch Processing

```python
# Process in parallel
embeddings = list(
    embedding_model.embed(
        documents,
        batch_size=32,  # Process 32 docs at once
        parallel=0      # Use all CPU cores
    )
)
```

### Quantization (Qdrant)

```python
# Create collection with scalar quantization
qdrant_client.create_collection(
    collection_name="agentx_memory",
    vectors_config=models.VectorParams(
        size=128,
        distance=models.Distance.COSINE,
        multivector_config=models.MultiVectorConfig(
            comparator=models.MultiVectorComparator.MAX_SIM
        ),
        quantization_config=models.ScalarQuantization(
            scalar=models.ScalarQuantizationConfig(
                type=models.ScalarType.INT8,
                quantile=0.99
            )
        )
    )
)
```

## Best Practices

### 1. Chunk Size Optimization
```python
# ColBERT works best with 200-400 tokens per chunk
# Too short: Not enough context
# Too long: Too many vectors, slower retrieval

def chunk_text(text, max_tokens=256):
    # Use sentence-based chunking
    sentences = text.split('. ')
    chunks = []
    current = []
    current_len = 0

    for sent in sentences:
        sent_len = len(sent.split())
        if current_len + sent_len > max_tokens:
            chunks.append('. '.join(current))
            current = [sent]
            current_len = sent_len
        else:
            current.append(sent)
            current_len += sent_len

    if current:
        chunks.append('. '.join(current))
    return chunks
```

### 2. Metadata Enrichment
```python
payload = {
    "text": chunk,
    # Temporal information
    "created_at": datetime.now().isoformat(),
    "modified_at": datetime.now().isoformat(),

    # User context
    "user_id": user_id,
    "session_id": session_id,

    # Content classification
    "category": classify_content(chunk),
    "importance": score_importance(chunk),

    # Relationships
    "conversation_id": conversation_id,
    "parent_chunk_id": parent_id,
}
```

### 3. Hybrid Search
```python
# Combine sparse (BM25) and dense (ColBERT)
# for better exact+semantic matching

from qdrant_client.models import SearchRequest

search_requests = [
    # Dense search with ColBERT
    SearchRequest(
        vector=query_colbert,
        limit=10,
        with_payload=True,
    ),

    # Sparse search (if using BM25)
    SearchRequest(
        vector=...,  # BM25 sparse vector
        limit=10,
        with_payload=True,
    )
]

# Merge results with Reciprocal Rank Fusion (RRF)
results = qdrant_client.search_batch(
    collection_name="agentx_memory",
    requests=search_requests
)
```

## Troubleshooting

### Issue: High Memory Usage
```python
# Solution: Use streaming for large datasets
for embedding in embedding_model.embed(large_document_list):
    # Process one at a time
    pass
```

### Issue: Slow Query Performance
```python
# Solution: Reduce candidate set with two-stage pipeline
# See "Two-Stage Retrieval Pipeline" above
```

### Issue: Poor Retrieval Quality
```python
# Solution: Tune chunk size and overlap
# Solution: Add query expansion
# Solution: Use hybrid search (dense + sparse)
```

## References

- [Qdrant ColBERT Documentation](https://qdrant.tech/documentation/fastembed/fastembed-colbert/)
- [ColBERTv2 Paper](https://arxiv.org/abs/2112.01488)
- [FastEmbed Supported Models](https://qdrant.github.io/fastembed/examples/Supported_Models)
