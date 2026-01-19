# AGENTX Sequence Diagrams

**Version**: 1.0.0
**Date**: 2026-01-19
**Status**: Draft
**Part of**: AGENTX HLD v1.0

---

## Table of Contents

1. [Ingest Flow](#1-ingest-flow)
2. [Query Flow](#2-query-flow)
3. [Plugin Lifecycle](#3-plugin-lifecycle)
4. [Memory Consolidation](#4-memory-consolidation)
5. [Voice Flow](#5-voice-flow)

---

## 1. Ingest Flow

### Overview

Data ingestion from plugins/API through canonicalization to vector storage.

### Sequence Diagram

```mermaid
sequenceDiagram
    actor User
    participant PWA as PWA Frontend
    participant API as FastAPI
    participant Ingest as Ingest Service
    participant PII as PII Detector
    participant Canon as Canonicalizer
    participant Temporal as Temporal Indexer
    participant Qdrant as Vector Store
    participant Audit as Audit Service

    User->>PWA: Submit data (text/file/audio)
    PWA->>API: POST /api/ingest
    API->>Ingest: Forward raw data

    Ingest->>PII: Scan for PII patterns
    PII-->>Ingest: PII markers

    Ingest->>Canon: Canonicalize data
    Canon->>Canon: Apply CanonicalDocument model
    Canon-->>Ingest: Canonical document

    Ingest->>Temporal: Add temporal metadata
    Temporal->>Temporal: Add timestamps, classify type
    Temporal->>Temporal: Chunk into 512-token pieces

    Temporal->>Temporal: Embed with ColBERTv2
    Temporal->>Qdrant: Store vectors with time partition

    Qdrant-->>Temporal: Vector IDs
    Temporal-->>Ingest: Ingestion complete

    Ingest->>Audit: Log ingest event
    Audit-->>Ingest: Logged

    Ingest-->>API: Success response
    API-->>PWA: 200 OK
    PWA-->>User: Confirmation
```

### Key States

| State | Description | Transition |
|-------|-------------|------------|
| **Received** | Raw data received | → Validating |
| **Validating** | Schema validation, PII detection | → Canonicalizing / Rejected |
| **Canonicalizing** | Apply canonical model | → Tagging |
| **Tagging** | Add temporal metadata | → Chunking |
| **Chunking** | Split into chunks | → Embedding |
| **Embedding** | Generate embeddings | → Indexing |
| **Indexing** | Store in Qdrant | → Complete |
| **Rejected** | Validation failed | → Error response |

---

## 2. Query Flow

### Overview

User query with temporal-aware retrieval and fact invalidation.

### Sequence Diagram

```mermaid
sequenceDiagram
    actor User
    participant PWA as PWA Frontend
    participant API as FastAPI
    participant Retriever as Temporal Retriever
    participant Qdrant as Vector Store
    participant Mem0AI as Memory Manager
    participant DSPy as ReAct Orchestrator
    participant Ollama as LLM Runtime
    participant Plugin as Plugin Host
    participant Audit as Audit Service

    User->>PWA: Enter query
    PWA->>API: POST /api/chat

    API->>Retriever: Search memories
    Retriever->>Retriever: Parse time_window, freshness_hint

    Retriever->>Qdrant: Time-aware vector search
    Qdrant-->>Retriever: Ranked results with provenance

    Retriever->>Retriever: Invalidate outdated facts
    Retriever->>Mem0AI: Get contextual memories
    Mem0AI-->>Retriever: Episodic/semantic memories

    Retriever-->>API: Retrieved context
    API->>DSPy: Process query with context

    DSPy->>DSPy: Analyze query, select tools

    alt Tool required
        DSPy->>Plugin: Execute tool
        Plugin-->>DSPy: Tool result
        DSPy->>DSPy: Update reasoning
    end

    DSPy->>Ollama: Generate response
    Ollama-->>DSPy: Streaming response

    DSPy->>API: Stream tokens
    API->>PWA: WebSocket stream

    DSPy->>Mem0AI: Store conversation turn
    Mem0AI-->>DSPy: Stored

    API->>Audit: Log query completion
    Audit-->>API: Logged

    API-->>PWA: Done
    PWA-->>User: Display response
```

### Query States

| State | Description | Timeout |
|-------|-------------|----------|
| **Receiving** | Accept query input | N/A |
| **Searching** | Temporal vector search | 500ms |
| **Invalidating** | Remove outdated facts | 100ms |
| **Reasoning** | DSPy ReAct planning | 2s (first token) |
| **Tool Execution** | Plugin tool calls | 30s per tool |
| **Generating** | LLM streaming response | 17s average (R013) |
| **Storing** | Save conversation turn | 100ms |

---

## 3. Plugin Lifecycle

### Overview

Plugin installation, activation, deactivation, and removal.

### Sequence Diagram

```mermaid
sequenceDiagram
    actor Admin
    participant Host as Plugin Host
    participant Manifest as Plugin Manifest
    participant Plugin as MCP Server
    participant Audit as Audit Service
    participant KMS as Local KMS

    Note over Admin,KMS: Installation Phase
    Admin->>Host: Install plugin (directory)
    Host->>Manifest: Load and validate manifest
    Manifest->>Manifest: Check capabilities, permissions
    Manifest->>Manifest: Verify GPG signature

    alt Signature invalid
        Manifest-->>Host: Signature verification failed
        Host-->>Admin: Error: Invalid signature
    end

    Manifest-->>Host: Valid manifest
    Host->>KMS: Generate plugin API key
    KMS-->>Host: API key
    Host->>Audit: Log plugin installed
    Host-->>Admin: Installation complete

    Note over Admin,KMS: Activation Phase
    Admin->>Host: Enable plugin
    Host->>Plugin: Start MCP server
    Plugin-->>Host: Server ready
    Host->>Host: Register capabilities

    Host->>Audit: Log plugin enabled
    Host-->>Admin: Plugin active

    Note over Admin,KMS: Operation Phase
    Host->>Plugin: Tool request
    Plugin-->>Host: Tool result

    alt Resource quota exceeded
        Host->>Plugin: Stop request
        Host-->>Plugin: Quota exceeded
        Host->>Audit: Log quota violation
    end

    alt Plugin crash
        Plugin->>Host: Crash signal
        Host->>Host: Isolate plugin
        Host->>Audit: Log plugin crash
    end

    Note over Admin,KMS: Deactivation Phase
    Admin->>Host: Disable plugin
    Host->>Plugin: Stop MCP server
    Host->>Audit: Log plugin disabled
    Host-->>Admin: Plugin disabled

    Note over Admin,KMS: Uninstallation Phase
    Admin->>Host: Uninstall plugin
    Host->>Host: Remove registration
    Host->>KMS: Revoke API key
    Host->>Audit: Log plugin uninstalled
    Host->>Host: Delete plugin data
    Host-->>Admin: Plugin removed
```

### Plugin States

| State | Description | Valid Transitions |
|-------|-------------|-------------------|
| **Installed** | Plugin files present, not active | → Activating, Uninstalling |
| **Activating** | Starting MCP server | → Active, Failed |
| **Active** | Server running, accepting requests | → Deactivating, Crashed |
| **Deactivating** | Stopping server | → Installed, Failed |
| **Crashed** | Server crashed, isolated | → Activating, Uninstalling |
| **Failed** | Operation failed | → Installed, Uninstalling |

---

## 4. Memory Consolidation

### Overview

Periodic consolidation of old memories into summarized form.

### Sequence Diagram

```mermaid
sequenceDiagram
    participant Scheduler as Cron Scheduler
    participant Consolidator as Memory Consolidator
    participant Qdrant as Vector Store
    participant Mem0AI as Memory Manager
    participant Ollama as LLM Runtime
    participant Audit as Audit Service

    Note over Scheduler,Audit: Nightly (2 AM UTC)
    Scheduler->>Consolidator: Trigger consolidation

    Consolidator->>Qdrant: Get memories older than 90 days
    Qdrant-->>Consolidator: Old memories (scroll)

    Consolidator->>Consolidator: Group by topic/entity

    loop For each topic
        Consolidator->>Mem0AI: Get topic context
        Mem0AI-->>Consolidator: Related memories

        Consolidator->>Ollama: Summarize topic
        Ollama-->>Consolidator: Consolidated summary

        Consolidator->>Qdrant: Store consolidated memory
        Qdrant-->>Consolidator: New memory ID

        Consolidator->>Qdrant: Mark old as consolidated
        Qdrant-->>Consolidator: Updated
    end

    Consolidator->>Audit: Log consolidation summary
    Audit-->>Consolidator: Logged

    Consolidator->>Scheduler: Consolidation complete
```

### Consolidation States

| State | Description | Transition |
|-------|-------------|------------|
| **Idle** | Waiting for schedule | → Scanning |
| **Scanning** | Finding old memories | → Grouping |
| **Grouping** | Grouping by topic | → Summarizing |
| **Summarizing** | LLM summarization | → Storing |
| **Storing** | Store consolidated | → Marking |
| **Marking** | Mark old as consolidated | → Complete |
| **Complete** | Ready for next run | → Idle |

---

## 5. Voice Flow

### Overview

Voice interaction pipeline (see kyutai_speech_integration_plan.md for full details).

### Sequence Diagram

```mermaid
sequenceDiagram
    actor User
    participant PWA as PWA Frontend
    participant Core as AGENTX Core
    participant STT as Kyutai unmute STT
    participant DSPy as ReAct Orchestrator
    participant TTS as Kyutai pocket-tts TTS
    participant Audit as Audit Service

    Note over User,TTS: Voice Pipeline (<300ms target)
    User->>PWA: Speak (audio stream)
    PWA->>Core: WebSocket audio chunks

    Core->>STT: Stream audio (24kHz Opus)
    STT->>STT: Semantic VAD (built-in)
    STT-->>Core: Transcription stream

    alt User interrupts
        User->>PWA: Interrupt signal
        PWA->>Core: Stop request
        Core->>TTS: Cancel generation
        TTS-->>Core: Cancelled
    end

    STT->>Core: Speech stopped (VAD)
    Core->>DSPy: Process transcription

    DSPy->>DSPy: ReAct reasoning
    DSPy->>DSPy: Tool calls (if needed)

    DSPy->>Core: Response text
    Core->>Audit: Log conversation turn
    Audit-->>Core: Logged

    Core->>TTS: Synthesize speech
    TTS-->>Core: Audio stream (24kHz WAV)

    Core->>PWA: Stream audio
    PWA->>User: Play speech
```

### Voice States

| State | Description | Timeout |
|-------|-------------|----------|
| **Listening** | Waiting for speech start | N/A |
| **Streaming** | Receiving audio chunks | 30s max |
| **Processing** | STT + LLM + TTS pipeline | <300ms target |
| **Speaking** | Playing TTS audio | Interruptible |
| **Interrupted** | User stopped playback | N/A |

### Latency Budget

| Component | Target | Actual (Kyutai) |
|-----------|--------|-----------------|
| **VAD** | 50ms | Built-in semantic VAD |
| **STT (streaming)** | 100ms | 500ms (1B model) |
| **LLM (first token)** | 50ms | 1.36s (DSPy + Ollama) |
| **TTS (first chunk)** | 100ms | 200ms (pocket-tts) |
| **Network** | 0ms | Local containers |
| **Total** | **300ms** | ~2.2s (voice-only) |

---

## Appendix: Error Handling

### Common Error Scenarios

| Scenario | Detection | Response | Recovery |
|----------|-----------|----------|----------|
| **Invalid PII** | PII detector | Reject with reason | User resubmits |
| **Qdrant timeout** | 5s elapsed | In-memory fallback | Retry in background |
| **Plugin crash** | Process exit | Isolate plugin | Restart plugin |
| **LLM timeout** | 10s elapsed | Cached response | User retries |
| **Audio timeout** | 30s silence | End listening | Ready for next |

---

**This document is part of AGENTX HLD v1.0. See [HLD.md](HLD.md) for complete architecture.**
