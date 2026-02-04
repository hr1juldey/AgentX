# Spec: Multivector Memory

Qdrant hybrid vector storage with dense (fast) + ColBERT (accurate) vectors using prefetch pattern.

## ADDED Requirements

### Requirement: Qdrant client initialization
The system SHALL initialize Qdrant client with connection to local Qdrant instance.

#### Scenario: Connect to Qdrant
- **WHEN** system starts
- **THEN** system creates QdrantClient pointing to `http://localhost:6335`
- **AND** system verifies connection with health check
- **AND** system logs connection status

#### Scenario: Create collection with named vectors
- **WHEN** initializing for the first time
- **THEN** system creates collection "agentx_memory"
- **AND** system configures named vectors: "dense" and "colbert"
- **AND** system sets appropriate parameters for each vector type

---

### Requirement: Dense vector embedding
The system SHALL generate dense vectors for fast retrieval.

#### Scenario: Generate dense embedding
- **WHEN** storing memory in Qdrant
- **THEN** system generates dense vector using sentence transformer
- **AND** system stores with vector name "dense"
- **AND** system stores text in payload

#### Scenario: Dense vector query
- **WHEN** searching with dense-only mode
- **THEN** system generates query embedding
- **AND** system queries Qdrant with dense vector
- **AND** system returns top-k results

---

### Requirement: ColBERT vector embedding
The system SHALL generate ColBERT multi-vector embeddings for accurate reranking.

#### Scenario: Generate ColBERT embedding
- **WHEN** storing memory with ColBERT
- **THEN** system generates ColBERT multi-vector representation
- **AND** system stores with vector name "colbert"
- **AND** system stores alongside dense vector

#### Scenario: ColBERT query
- **WHEN** searching with ColBERT
- **THEN** system generates ColBERT query embedding
- **AND** system queries Qdrant with ColBERT vector
- **AND** system returns reranked results

---

### Requirement: Prefetch pattern (dense → ColBERT)
The system SHALL implement prefetch pattern for fast + accurate retrieval.

#### Scenario: Prefetch query
- **WHEN** searching with multivector mode
- **THEN** system generates dense and ColBERT query embeddings
- **AND** system executes prefetch: dense query → top-100 candidates
- **AND** system reranks with ColBERT → final-k results

#### Scenario: Prefetch configuration
- **WHEN** configuring prefetch
- **THEN** system sets prefetch limit to 100 (or configurable)
- **AND** system sets final limit to k (default 5)
- **AND** system uses "dense" for prefetch, "colbert" for final query

---

### Requirement: Custom Retriever implementation
The system SHALL implement custom DSPy Retriever class for Qdrant multivector.

#### Scenario: PrefetchRM class
- **WHEN** creating retriever
- **THEN** system creates class inheriting from `dspy.retrieve.retrieve.Retrieve`
- **AND** system implements `forward(self, query: str, k: int) -> list[str]`
- **AND** system uses Qdrant prefetch pattern

#### Scenario: Retriever integration
- **WHEN** using retriever in DSPy
- **THEN** system can pass retriever to DSPy configure
- **AND** system can use in dspy.Retrieve modules

---

### Requirement: Memory storage with vectors
The system SHALL store memories with both dense and ColBERT vectors.

#### Scenario: Store with multivector
- **WHEN** storing memory
- **THEN** system generates both dense and ColBERT vectors
- **AND** system upserts to Qdrant with named vectors
- **AND** system stores metadata in payload

#### Scenario: Retrieve and decode
- **WHEN** retrieving memories
- **THEN** system queries Qdrant with prefetch
- **AND** system extracts text from payload
- **AND** system returns list of document contents

---

### Requirement: Graceful degradation
The system SHALL degrade gracefully if Qdrant is unavailable.

#### Scenario: Qdrant unavailable
- **WHEN** Qdrant connection fails
- **THEN** system logs error
- **AND** system continues without vector search
- **AND** system may use keyword search as fallback

#### Scenario: ColBERT unavailable
- **WHEN** ColBERT embedding fails
- **THEN** system falls back to dense-only search
- **AND** system logs warning about missing accuracy
