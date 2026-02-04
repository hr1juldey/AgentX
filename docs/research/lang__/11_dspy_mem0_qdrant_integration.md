# DSPy Retrieve + Mem0AI + Qdrant Integration Guide

**Research Date:** 2025-02-04
**Purpose:** How to integrate `dspy.Retrieve` with Mem0AI when both use Qdrant

---

## Executive Summary

**DSPy Retrieve** and **Mem0AI** can coexist in the same Qdrant instance by using **separate collections** with distinct purposes:

| System | Collection Pattern | Purpose | Data Type |
|--------|-------------------|---------|-----------|
| **Mem0AI** | `agentx_memories` or `{agent_name}_collection` | Conversational memory | User interactions, preferences |
| **DSPy Retrieve (QdrantRM)** | `agentx_documents` or `agentx_rag` | Document retrieval (RAG) | Clean, curated knowledge base |
| **ColBERTv2** | `agentx_web_search` | Large-scale web search | Researcher/MemoryDump data |

---

## 1. QdrantRM Installation

DSPy's Qdrant integration is a separate package:

```bash
pip install dspy-ai dspy-qdrant fastembed qdrant-client
```

**Note:** `dspy-qdrant` provides `QdrantRM` class that implements DSPy's retrieval interface.

---

## 2. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      Qdrant Instance                            │
│                     (localhost:6333)                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────┐  ┌──────────────────────┐            │
│  │ Collection:          │  │ Collection:          │            │
│  │ agentx_memories      │  │ agentx_documents     │            │
│  │                      │  │                      │            │
│  │ - Conversational     │  │ - Document chunks    │            │
│  │   memory (Mem0AI)    │  │ - Knowledge base     │            │
│  │ - User preferences   │  │ - Curated content    │            │
│  │ - Interaction history│  │ - FAQ, docs          │            │
│  │                      │  │                      │            │
│  │ Embedder: Ollama     │  │ Embedder: FastEmbed  │            │
│  │ (nomic-embed-text)   │  │ (or ColBERTv2)       │            │
│  └──────────────────────┘  └──────────────────────┘            │
│                                                                   │
│  ┌──────────────────────┐  ┌──────────────────────┐            │
│  │ Collection:          │  │ Collection:          │            │
│  │ conversation_        │  │ researcher_          │            │
│  │ agent_collection     │  │ collection           │            │
│  │                      │  │                      │            │
│  │ Per-agent memory     │  │ Web search results   │            │
│  │ (DSPy Mem0 tools)    │  │ (ColBERTv2)          │            │
│  └──────────────────────┘  └──────────────────────┘            │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Mem0AI Configuration

Mem0AI stores conversational memories in Qdrant:

```python
from mem0 import Memory

# Mem0AI configuration for AGENTX
mem0_config = {
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": "localhost",
            "port": 6333,
            "collection_name": "agentx_memories"  # Main conversational memory
        },
    },
    "llm": {
        "provider": "ollama",
        "config": {
            "model": "gemma3:4b",
            "host": "http://localhost:11434",
            "temperature": 0.7
        },
    },
    "embedder": {
        "provider": "ollama",
        "config": {
            "model": "nomic-embed-text",
            "host": "http://localhost:11434"
        },
    },
}

# Create Mem0AI instance
memory = Memory.from_config(mem0_config)

# Usage
memory.add(["User prefers Python over JavaScript"], user_id="user123")
results = memory.search("programming preference", user_id="user123")
```

**Collection created by Mem0AI:** `agentx_memories`

---

## 4. DSPy QdrantRM Configuration

DSPy Retrieve uses QdrantRM for document retrieval (RAG):

```python
import os
import dspy
from dspy_qdrant import QdrantRM
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

# Configure LLM
lm = dspy.LM(
    "ollama_chat/gemma3:4b",
    api_base="http://localhost:11434",
    api_key=""
)

# Create Qdrant client
qdrant_client = QdrantClient(url="http://localhost:6333")

# Collection name for DSPy Retrieve (SEPARATE from Mem0AI)
DSPY_COLLECTION = "agentx_documents"

# Create collection if not exists
if not qdrant_client.collection_exists(DSPY_COLLECTION):
    qdrant_client.create_collection(
        collection_name=DSPY_COLLECTION,
        vectors_config={
            "dense": VectorParams(size=384, distance=Distance.COSINE)  # nomic-embed-text dimension
        }
    )

# Configure QdrantRM
rm = QdrantRM(
    qdrant_collection_name=DSPY_COLLECTION,
    qdrant_client=qdrant_client,
    vector_name="dense",            # Matches vector config
    document_field="passage_text",  # Payload field containing text
    k=5
)

# Configure DSPy
dspy.settings.configure(lm=lm, rm=rm)
```

---

## 5. DSPy Retrieve Module

Create a DSPy module that uses `dspy.Retrieve`:

```python
import dspy

class RAGSignature(dspy.Signature):
    """Signature for RAG QA."""
    context = dspy.InputField(desc="Retrieved context passages")
    question = dspy.InputField(desc="User question")
    answer = dspy.OutputField(desc="Answer to the question")

class SimpleRAG(dspy.Module):
    def __init__(self, num_passages=5):
        super().__init__()
        self.retrieve = dspy.Retrieve(k=num_passages)
        self.generate_answer = dspy.ChainOfThought(RAGSignature)

    def forward(self, question):
        # Retrieve relevant passages
        retrieved = self.retrieve(question)
        context = retrieved.passages

        # Generate answer with context
        pred = self.generate_answer(context=context, question=question)
        return dspy.Prediction(context=context, answer=pred.answer)

# Usage
rag = SimpleRAG(num_passages=3)
result = rag(question="What is the capital of France?")
print(result.answer)
```

---

## 6. Combined Usage Pattern

Here's how to use both Mem0AI and DSPy Retrieve together:

```python
import dspy
from mem0 import Memory
from dspy_qdrant import QdrantRM
from qdrant_client import QdrantClient

# Initialize Qdrant client
qdrant_client = QdrantClient(url="http://localhost:6333")

# Initialize Mem0AI for conversational memory
memory = Memory.from_config({
    "vector_store": {
        "provider": "qdrant",
        "config": {"host": "localhost", "port": 6333, "collection_name": "agentx_memories"}
    },
    "llm": {"provider": "ollama", "config": {"model": "gemma3:4b", "host": "http://localhost:11434"}},
    "embedder": {"provider": "ollama", "config": {"model": "nomic-embed-text", "host": "http://localhost:11434"}}
})

# Initialize DSPy with QdrantRM for document retrieval
lm = dspy.LM("ollama_chat/gemma3:4b", api_base="http://localhost:11434")
rm = QdrantRM(
    qdrant_collection_name="agentx_documents",  # Different collection!
    qdrant_client=qdrant_client,
    vector_name="dense",
    document_field="passage_text",
    k=5
)
dspy.settings.configure(lm=lm, rm=rm)

class AgentXModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.retrieve = dspy.Retrieve(k=3)
        self.react = dspy.ReAct("question->answer", tools=[])

    def forward(self, question, user_id):
        # 1. Get conversational context from Mem0AI
        memories = memory.search(question, user_id=user_id)
        memory_context = "\n".join([m['memory'] for m in memories.get('results', [])])

        # 2. Get document context from DSPy Retrieve
        doc_context = self.retrieve(question).passages

        # 3. Combine contexts
        full_context = f"""User Memory:
{memory_context}

Document Context:
{' '.join(doc_context)}"""

        # 4. Generate response
        result = self.react(question=f"{question}\n\n{full_context}")

        # 5. Store interaction in Mem0AI
        memory.add(
            [{"role": "user", "content": question}, {"role": "assistant", "content": result.answer}],
            user_id=user_id
        )

        return result

# Usage
agent = AgentXModule()
response = agent.forward("What did we discuss about Python?", user_id="user123")
```

---

## 7. Collection Naming Strategy

### Recommended Collection Names

| Purpose | Collection Name | Access Pattern |
|---------|----------------|----------------|
| Main conversational memory | `agentx_memories` | Mem0AI API |
| Document/RAG knowledge | `agentx_documents` | DSPy QdrantRM |
| Per-agent memory | `{agent_name}_collection` | DSPy Mem0 tools |
| Web search cache | `agentx_web_search` | ColBERTv2 |

### Per-Environment Namespacing

```python
import os

ENV = os.getenv("AGENTX_ENV", "dev")

# Environment-prefixed collections
MEM0_COLLECTION = f"{ENV}_agentx_memories"     # dev_agentx_memories
DOC_COLLECTION = f"{ENV}_agentx_documents"     # dev_agentx_documents
WEB_COLLECTION = f"{ENV}_agentx_web_search"    # dev_agentx_web_search
```

---

## 8. Data Ingestion for DSPy Retrieve

To populate the `agentx_documents` collection:

```python
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

client = QdrantClient(url="http://localhost:6333")

# Sample documents
documents = [
    {"id": 1, "text": "Python is a high-level programming language."},
    {"id": 2, "text": "JavaScript is used for web development."},
    {"id": 3, "text": "Rust is a systems programming language."},
]

# Upsert documents
client.upsert(
    collection_name="agentx_documents",
    points=[
        PointStruct(
            id=doc["id"],
            vector={},  # Qdrant will use the default vector (from FastEmbed/Ollama)
            payload={"passage_text": doc["text"]}  # Must match document_field in QdrantRM
        )
        for doc in documents
    ]
)
```

**Note:** Use FastEmbed or Ollama embeddings for vectorization:

```python
from fastembed import TextEmbedding

embedder = TextEmbedding(model_name="nomic-ai/nomic-embed-text-v1.5")

for doc in documents:
    vector = list(embedder.embed([doc["text"]]))[0]
    client.upsert(
        collection_name="agentx_documents",
        points=[
            PointStruct(
                id=doc["id"],
                vector=vector,
                payload={"passage_text": doc["text"]}
            )
        ]
    )
```

---

## 9. DSPy Mem0 Tools Integration

DSPy's Mem0 ReAct agent uses memory tools that store in Qdrant:

```python
import dspy
from dspy.mem0 import MemoryTools

# Create memory tools
memory_tools = MemoryTools(
    memory=memory,  # Mem0AI instance
    user_id="user123"
)

# ReAct agent with memory
react = dspy.ReAct(
    "question->answer",
    tools=[
        dspy.Tool(memory_tools.add_memory, name="add_memory"),
        dspy.Tool(memory_tools.search_memory, name="search_memory"),
        # ... other tools
    ]
)

# The agent will automatically store memories in:
# Collection: {agent_name}_collection
```

**Collection created:** `{agent_name}_collection` (e.g., `conversation_agent_collection`)

---

## 10. ColBERTv2 Integration (Researcher Agent)

For large-scale web search retrieval:

```python
import dspy

# ColBERTv2 for web-scale retrieval
colbert_rm = dspy.ColBERTv2(
    url="http://20.102.90.50:2017/wiki17_abstracts"  # Or local ColBERTv2 server
)

# Configure separate retriever for Researcher agent
class ResearcherAgent(dspy.Module):
    def __init__(self):
        super().__init__()
        # Use ColBERTv2 for large-scale retrieval
        self.web_retrieve = dspy.Retrieve(k=10)
        self.react = dspy.ReAct("query->answer", tools=[web_search_tool])

    def forward(self, query):
        # ColBERTv2 retrieves from massive corpus
        context = self.web_retrieve(query).passages
        return self.react(query=f"{query}\n\nContext: {context}")

# Configure with ColBERTv2
dspy.configure(lm=lm, rm=colbert_rm)
researcher = ResearcherAgent()
```

---

## 11. Summary: Integration Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         AGENTX Agent                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────────┐    ┌─────────────────────┐            │
│  │  Conversation       │    │   Researcher        │            │
│  │  Agent              │    │   Agent             │            │
│  │                     │    │                     │            │
│  │  ┌──────────────┐   │    │   ┌──────────────┐ │            │
│  │  │ Mem0AI       │   │    │   │ ColBERTv2    │ │            │
│  │  │ (QdrantRM)   │   │    │   │ (Web Search) │ │            │
│  │  └──────────────┘   │    │   └──────────────┘ │            │
│  │         │           │    │           │         │            │
│  │         ▼           │    │           ▼         │            │
│  │  agentx_memories    │    │  agentx_web_search  │            │
│  └─────────────────────┘    └─────────────────────┘            │
│                                                                   │
│  ┌─────────────────────┐    ┌─────────────────────┐            │
│  │   RAG Agent         │    │  All Agents         │            │
│  │                     │    │  (Common)           │            │
│  │  ┌──────────────┐   │    │   ┌──────────────┐ │            │
│  │  │ DSPy         │   │    │   │ Mem0AI       │ │            │
│  │  │ Retrieve     │   │    │   │ Per-Agent    │ │            │
│  │  └──────────────┘   │    │   │ Memory       │ │            │
│  │         │           │    │   └──────────────┘ │            │
│  │         ▼           │    │           │         │            │
│  │  agentx_documents    │    │  {agent}_collection │            │
│  └─────────────────────┘    └─────────────────────┘            │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Qdrant (localhost:6333)                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Collections:                                                    │
│  - agentx_memories        (Mem0AI main)                          │
│  - agentx_documents       (DSPy RAG knowledge)                   │
│  - agentx_web_search      (ColBERTv2 cache)                      │
│  - {agent_name}_collection (Per-agent DSPy Mem0 tools)           │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 12. Configuration File Template

```yaml
# config/agentx_memory.yaml

# Mem0AI Configuration (Conversational Memory)
mem0:
  vector_store:
    provider: qdrant
    config:
      host: localhost
      port: 6333
      collection_name: agentx_memories
  llm:
    provider: ollama
    config:
      model: gemma3:4b
      host: http://localhost:11434
  embedder:
    provider: ollama
    config:
      model: nomic-embed-text
      host: http://localhost:11434

# DSPy QdrantRM Configuration (Document Retrieval)
dspy_retrieve:
  collection_name: agentx_documents
  vector_name: dense
  document_field: passage_text
  k: 5

# ColBERTv2 Configuration (Web Search)
colbert:
  url: http://20.102.90.50:2017/wiki17_abstracts
  # Or local: http://localhost:2017/my_colbert_index
```

---

## 13. Key Takeaways

1. **Separate Collections**: Mem0AI and DSPy Retrieve use different Qdrant collections
2. **QdrantRM Package**: Install `dspy-qdrant` for DSPy integration with Qdrant
3. **Collection Naming**: Use `{prefix}_agentx_*` pattern for clarity
4. **Embedder Choice**: Use Ollama embeddings for both systems to maintain compatibility
5. **Per-Agent Memory**: DSPy Mem0 tools create `{agent_name}_collection` per agent
6. **ColBERTv2 Separate**: Use ColBERTv2 for large-scale web search, not QdrantRM

---

## 14. Quick Reference

```python
# Mem0AI (Conversational Memory)
memory = Memory.from_config(config)
memory.add(["User prefers Python"], user_id="user123")
results = memory.search("preference", user_id="user123")

# DSPy Retrieve (Document RAG)
from dspy_qdrant import QdrantRM
rm = QdrantRM("agentx_documents", qdrant_client, "dense", "passage_text", k=5)
dspy.settings.configure(lm=lm, rm=rm)
retriever = dspy.Retrieve(k=3)
passages = retriever(question).passages

# DSPy Mem0 Tools (Per-Agent Memory)
from dspy.mem0 import MemoryTools
tools = MemoryTools(memory=memory, user_id="user123")
react = dspy.ReAct("question->answer", tools=[tools.add_memory, tools.search_memory])

# ColBERTv2 (Large-Scale Web Search)
colbert_rm = dspy.ColBERTv2(url="http://localhost:2017/index")
dspy.settings.configure(lm=lm, rm=colbert_rm)
```

---

## Sources

- [Qdrant DSPy Integration](https://qdrant.tech/documentation/frameworks/dspy/)
- [DSPy Retrieve Documentation](https://github.com/stanfordnlp/dspy/blob/main/dspy/retrieve/qdrant_rm.py)
- [Mem0AI Configuration](https://docs.mem0.ai/open-source/configuration)
- [Mem0AI LangGraph Integration](https://docs.mem0.ai/integrations/langgraph)
- [Qdrant FastEmbed ColBERTv2](https://qdrant.tech/documentation/fastembed/fastembed-colbert/)

---

**Next Steps:**
- Update `docs/engineering/PRD.md` Retrieval Architecture section
- Create Qdrant initialization script for all collections
- Implement unified MemoryService that wraps both Mem0AI and QdrantRM
