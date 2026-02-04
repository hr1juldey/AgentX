# Tasks: AGENTX Layer-Based Folder Structure

## 1. Setup - Create Folder Skeleton

- [ ] 1.1 Create `agentx/core/` directory with `__init__.py`
- [ ] 1.2 Create `agentx/core/middleware/` directory with `__init__.py`
- [ ] 1.3 Create `agentx/domain/` directory with `__init__.py`
- [ ] 1.4 Create `agentx/domain/entities/` directory with `__init__.py`
- [ ] 1.5 Create `agentx/domain/signatures/` directory with `__init__.py`
- [ ] 1.6 Create `agentx/domain/services/` directory with `__init__.py`
- [ ] 1.7 Create `agentx/domain/value_objects/` directory with `__init__.py`
- [ ] 1.8 Create `agentx/application/` directory with `__init__.py`
- [ ] 1.9 Create `agentx/application/agents/` directory with `__init__.py`
- [ ] 1.10 Create `agentx/application/graphs/` directory with `__init__.py`
- [ ] 1.11 Create `agentx/application/graphs/builder/` directory with `__init__.py`
- [ ] 1.12 Create `agentx/application/graphs/routing/` directory with `__init__.py`
- [ ] 1.13 Create `agentx/application/graphs/mutation/` directory with `__init__.py`
- [ ] 1.14 Create `agentx/application/graphs/storage/` directory with `__init__.py`
- [ ] 1.15 Create `agentx/application/graphs/presets/` directory with `__init__.py`
- [ ] 1.16 Create `agentx/application/evaluation/` directory with `__init__.py`
- [ ] 1.17 Create `agentx/application/coordination/` directory with `__init__.py`
- [ ] 1.18 Create `agentx/application/tools/` directory with `__init__.py`
- [ ] 1.19 Create `agentx/application/use_cases/` directory with `__init__.py`
- [ ] 1.20 Create `agentx/application/models/` directory with `__init__.py`
- [ ] 1.21 Create `agentx/application/mappers/` directory with `__init__.py`
- [ ] 1.22 Create `agentx/infrastructure/` directory with `__init__.py`
- [ ] 1.23 Create `agentx/infrastructure/memory/` directory with `__init__.py`
- [ ] 1.24 Create `agentx/infrastructure/voice/` directory with `__init__.py`
- [ ] 1.25 Create `agentx/infrastructure/retrieval/` directory with `__init__.py`
- [ ] 1.26 Create `agentx/infrastructure/repositories/` directory with `__init__.py`
- [ ] 1.27 Create `agentx/infrastructure/external/` directory with `__init__.py`
- [ ] 1.28 Create `agentx/presentation/` directory with `__init__.py`
- [ ] 1.29 Create `agentx/presentation/api/` directory with `__init__.py`
- [ ] 1.30 Create `agentx/presentation/api/v1/` directory with `__init__.py`
- [ ] 1.31 Create `agentx/presentation/api/v1/agents/` directory with `__init__.py`
- [ ] 1.32 Create `agentx/presentation/api/v1/graphs/` directory with `__init__.py`
- [ ] 1.33 Create `agentx/presentation/api/v1/memory/` directory with `__init__.py`
- [ ] 1.34 Create `agentx/presentation/api/v1/voice/` directory with `__init__.py`
- [ ] 1.35 Create `agentx/presentation/api/v1/threads/` directory with `__init__.py`
- [ ] 1.36 Create `agentx/presentation/api/v1/websocket/` directory with `__init__.py`
- [ ] 1.37 Create `agentx/presentation/models/` directory with `__init__.py`
- [ ] 1.38 Create `agentx/presentation/middleware/` directory with `__init__.py`
- [ ] 1.39 Run `ruff check --fix` on new directories
- [ ] 1.40 Run `ruff format` on new directories

## 2. Domain Layer - Entities

- [ ] 2.1 Create `agentx/domain/entities/graph.py` with Graph dataclass (id, spec, metadata, score, created_at, version)
- [ ] 2.2 Create `agentx/domain/entities/mutation.py` with Mutation dataclass (type, target, params)
- [ ] 2.3 Create `agentx/domain/entities/execution.py` with Execution dataclass (session, trace, result)
- [ ] 2.4 Run `ruff check --fix` and `ruff format` on entity files
- [ ] 2.5 Run `pyrefly check --summarize-errors` on entity files

## 3. Domain Layer - Signatures

- [ ] 3.1 Create `agentx/domain/signatures/analysis_signature.py` with AnalysisSignature (query, context → goals, confidence)
- [ ] 3.2 Create `agentx/domain/signatures/reasoning_signature.py` with ReasoningSignature (context, question → answer, reasoning)
- [ ] 3.3 Create `agentx/domain/signatures/search_signature.py` with SearchSignature (query, context → answer, reasoning, citations)
- [ ] 3.4 Run `ruff check --fix` and `ruff format` on signature files
- [ ] 3.5 Run `pyrefly check --summarize-errors` on signature files

## 4. Core Layer - Configuration

- [ ] 4.1 Create `agentx/core/config.py` with Settings class (Pydantic Settings)
- [ ] 4.2 Add server configuration (host, port) to Settings
- [ ] 4.3 Add LLM configuration (provider, model) to Settings
- [ ] 4.4 Add voice configuration (kyutai URLs) to Settings
- [ ] 4.5 Add memory configuration (Mem0AI, Qdrant) to Settings
- [ ] 4.6 Create settings singleton instance
- [ ] 4.7 Run `ruff check --fix` and `ruff format` on config.py
- [ ] 4.8 Run `pyrefly check --summarize-errors` on config.py

## 5. Core Layer - Dependencies

- [ ] 5.1 Create `agentx/core/dependencies.py` with dependency getter functions
- [ ] 5.2 Implement `ensure_dspy_configured()` to configure global LM/RM with Ollama
- [ ] 5.3 Implement `get_mem0_client()` singleton getter
- [ ] 5.4 Implement `get_qdrant_client()` singleton getter
- [ ] 5.5 Implement agent registry getter
- [ ] 5.6 Run `ruff check --fix` and `ruff format` on dependencies.py
- [ ] 5.7 Run `pyrefly check --summarize-errors` on dependencies.py

## 6. Core Layer - Exceptions

- [ ] 6.1 Create `agentx/core/exceptions.py` with global exception classes
- [ ] 6.2 Define AgentException base class
- [ ] 6.3 Define GraphCompilationException
- [ ] 6.4 Define MemoryException
- [ ] 6.5 Run `ruff check --fix` and `ruff format` on exceptions.py

## 7. Application Layer - Stem Cell Agent

- [ ] 7.1 Create `agentx/application/agents/stem_cell.py` with StemCellAgent class
- [ ] 7.2 Implement StemCellAgent.__init__ with signature parameter and default pluripotent signature
- [ ] 7.3 Implement set_signature() method for signature changes
- [ ] 7.4 Implement reset_signature() method to restore pluripotent state
- [ ] 7.5 Implement add_tool() method for tool mounting
- [ ] 7.6 Implement forward() method with Mem0AI search before execution
- [ ] 7.7 Implement forward() method with Mem0AI storage after execution
- [ ] 7.8 Add graceful degradation when Mem0AI fails
- [ ] 7.9 Run `ruff check --fix` and `ruff format` on stem_cell.py
- [ ] 7.10 Run `pyrefly check --summarize-errors` on stem_cell.py

## 8. Application Layer - Specialized Agents

- [ ] 8.1 Create `agentx/application/agents/analyst.py` with AnalystAgent class
- [ ] 8.2 Implement AnalystAgent with analyst signature (query, memory_context, knowledge_context → context_summary, goals, is_sufficient, confidence)
- [ ] 8.3 Create `agentx/application/agents/researcher.py` with ResearcherAgent class
- [ ] 8.4 Implement ResearcherAgent with research signature (query, context → answer, reasoning, citations)
- [ ] 8.5 Create `agentx/application/agents/conversation.py` with ConversationAgent class
- [ ] 8.6 Implement ConversationAgent with conversation signature
- [ ] 8.7 Run `ruff check --fix` and `ruff format` on agent files
- [ ] 8.8 Run `pyrefly check --summarize-errors` on agent files

## 9. Application Layer - Graph Builder

- [ ] 9.1 Create `agentx/application/graphs/builder/graph_compiler.py` with GraphCompiler class
- [ ] 9.2 Implement compile() method to build StateGraph from agent registry and edge definitions
- [ ] 9.3 Create `agentx/application/graphs/builder/node_factory.py` with node creation functions
- [ ] 9.4 Implement create_dspy_node() to wrap agents for LangGraph
- [ ] 9.5 Run `ruff check --fix` and `ruff format` on builder files
- [ ] 9.6 Run `pyrefly check --summarize-errors` on builder files

## 10. Application Layer - Graph Routing

- [ ] 10.1 Create `agentx/application/graphs/routing/router.py` with Router class
- [ ] 10.2 Implement select_graph() method to query Qdrant for similar graphs
- [ ] 10.3 Create `agentx/application/graphs/routing/conditional.py` with conditional edge logic
- [ ] 10.4 Implement route_based_on_context() for dynamic routing
- [ ] 10.5 Run `ruff check --fix` and `ruff format` on routing files
- [ ] 10.6 Run `pyrefly check --summarize-errors` on routing files

## 11. Application Layer - Graph Mutation

- [ ] 11.1 Create `agentx/application/graphs/mutation/add_node.py` with add_node() function
- [ ] 11.2 Create `agentx/application/graphs/mutation/remove_edge.py` with remove_edge() function
- [ ] 11.3 Create `agentx/application/graphs/mutation/modify_condition.py` with modify_condition() function
- [ ] 11.4 Create `agentx/application/graphs/mutation/spawn_subgraph.py` with spawn_subgraph() function
- [ ] 11.5 Implement versioning for mutations (create new version, not in-place)
- [ ] 11.6 Run `ruff check --fix` and `ruff format` on mutation files
- [ ] 11.7 Run `pyrefly check --summarize-errors` on mutation files

## 12. Application Layer - Graph Storage

- [ ] 12.1 Create `agentx/application/graphs/storage/graph_store.py` with GraphStore class
- [ ] 12.2 Implement save_graph() to vectorize and store graph spec to Qdrant
- [ ] 12.3 Implement find_similar() to search Qdrant for similar graphs
- [ ] 12.4 Create `agentx/application/graphs/storage/variation_store.py` with VariationStore class
- [ ] 12.5 Implement save_variation() to store genetic variations
- [ ] 12.6 Run `ruff check --fix` and `ruff format` on storage files
- [ ] 12.7 Run `pyrefly check --summarize-errors` on storage files

## 13. Application Layer - Graph Presets

- [ ] 13.1 Create `agentx/application/graphs/presets/conversation_graph.py` with build_conversation_graph() function
- [ ] 13.2 Create `agentx/application/graphs/presets/research_graph.py` with build_research_graph() function
- [ ] 13.3 Implement preset graphs using builder pattern
- [ ] 13.4 Run `ruff check --fix` and `ruff format` on preset files
- [ ] 13.5 Run `pyrefly check --summarize-errors` on preset files

## 14. Application Layer - Evaluation

- [ ] 14.1 Create `agentx/application/evaluation/critic.py` with Critic class
- [ ] 14.2 Implement evaluate() method to score execution quality (0.0 to 1.0)
- [ ] 14.3 Create `agentx/application/evaluation/metrics.py` with quality metrics functions
- [ ] 14.4 Implement latency, accuracy, and tool success rate metrics
- [ ] 14.5 Create `agentx/application/evaluation/evaluator.py` with Evaluator class
- [ ] 14.6 Implement compare_variations() to compare graph variations
- [ ] 14.7 Run `ruff check --fix` and `ruff format` on evaluation files
- [ ] 14.8 Run `pyrefly check --summarize-errors` on evaluation files

## 15. Application Layer - Coordination

- [ ] 15.1 Create `agentx/application/coordination/coordinator.py` with Coordinator class
- [ ] 15.2 Implement decide() method to return 'continue', 'replan', or 'mutate' based on critic score
- [ ] 15.3 Implement decision thresholds (>0.8 continue, >0.5 replan, else mutate)
- [ ] 15.4 Run `ruff check --fix` and `ruff format` on coordinator.py
- [ ] 15.5 Run `pyrefly check --summarize-errors` on coordinator.py

## 16. Application Layer - Tools

- [ ] 16.1 Create `agentx/application/tools/web/` directory with `__init__.py`
- [ ] 16.2 Create `agentx/application/tools/web/search.py` with searxng_search() function
- [ ] 16.3 Wrap searxng_search with dspy.Tool and export as searxng_search_tool
- [ ] 16.4 Create `agentx/application/tools/memory/` directory with `__init__.py`
- [ ] 16.5 Create `agentx/application/tools/memory/retrieve.py` with memory retrieval functions
- [ ] 16.6 Run `ruff check --fix` and `ruff format` on tool files
- [ ] 16.7 Run `pyrefly check --summarize-errors` on tool files

## 17. Infrastructure Layer - Memory

- [ ] 17.1 Create `agentx/infrastructure/memory/mem0_client.py` with Mem0AI wrapper
- [ ] 17.2 Implement singleton Mem0AI client initialization
- [ ] 17.3 Create `agentx/infrastructure/memory/qdrant_rm.py` with QdrantRM and prefetch
- [ ] 17.4 Implement PrefetchQdrantRM with dense → ColBERT fallback
- [ ] 17.5 Create `agentx/infrastructure/memory/langgraph_store.py` with LangGraph checkpoint store
- [ ] 17.6 Create `agentx/infrastructure/memory/graph_collection.py` with Qdrant collection setup
- [ ] 17.7 Run `ruff check --fix` and `ruff format` on memory files
- [ ] 17.8 Run `pyrefly check --summarize-errors` on memory files

## 18. Infrastructure Layer - Voice (using existing voice_client SDK)

- [ ] 18.1 Add `voice-client-sdk` to requirements-core.txt (from libs/voice_client/)
- [ ] 18.2 Create `agentx/infrastructure/voice/voice_adapter.py` with VoiceSDKAdapter class
- [ ] 18.3 Implement VoiceSDKAdapter as thin wrapper around voice_client.VoiceClient
- [ ] 18.4 Create `agentx/infrastructure/voice/voice_gateway.py` with VoiceGatewayService
- [ ] 18.5 Implement VoiceGatewayService.handle_session() using SDK's VoiceClient.converse_stream()
- [ ] 18.6 Create `agentx/infrastructure/voice/text_stream_handler.py` with TextStreamHandler
- [ ] 18.7 Implement STT buffering and TTS sentence splitting for agent callbacks
- [ ] 18.8 Run `ruff check --fix` and `ruff format` on voice files
- [ ] 18.9 Run `pyrefly check --summarize-errors` on voice files

## 19. Infrastructure Layer - Retrieval

- [ ] 19.1 Create `agentx/infrastructure/retrieval/prefetch_rm.py` with PrefetchRM wrapper
- [ ] 19.2 Implement dense → ColBERT prefetch pattern
- [ ] 19.3 Create `agentx/infrastructure/retrieval/searxng_client.py` with SearXNG client
- [ ] 19.4 Run `ruff check --fix` and `ruff format` on retrieval files
- [ ] 19.5 Run `pyrefly check --summarize-errors` on retrieval files

## 20. Presentation Layer - Models

- [ ] 20.1 Create `agentx/presentation/models/requests.py` with request DTOs
- [ ] 20.2 Add AgentRequest, GraphRequest, MemoryRequest DTOs
- [ ] 20.3 Create `agentx/presentation/models/responses.py` with response DTOs
- [ ] 20.4 Add AgentResponse, GraphResponse, MemoryResponse DTOs
- [ ] 20.5 Run `ruff check --fix` and `ruff format` on model files
- [ ] 20.6 Run `pyrefly check --summarize-errors` on model files

## 21. Presentation Layer - API Routes

- [ ] 21.1 Create `agentx/presentation/api/v1/agents/routes.py` with agent endpoints
- [ ] 21.2 Implement POST /api/v1/agents/execute endpoint
- [ ] 21.3 Implement GET /api/v1/agents/{id} endpoint
- [ ] 21.4 Create `agentx/presentation/api/v1/graphs/routes.py` with graph endpoints
- [ ] 21.5 Implement POST /api/v1/graphs/compile endpoint
- [ ] 21.6 Implement POST /api/v1/graphs/execute endpoint
- [ ] 21.7 Create `agentx/presentation/api/v1/memory/routes.py` with memory endpoints
- [ ] 21.8 Create `agentx/presentation/api/v1/voice/routes.py` with voice endpoints
- [ ] 21.9 Create `agentx/presentation/api/v1/threads/routes.py` with thread endpoints
- [ ] 21.10 Run `ruff check --fix` and `ruff format` on route files
- [ ] 21.11 Run `pyrefly check --summarize-errors` on route files

## 22. Main Application Entry Point

- [ ] 22.1 Update `agentx/main.py` to import from new folder structure
- [ ] 22.2 Implement lifespan() context manager with startup hooks
- [ ] 22.3 Call ensure_dspy_configured() on startup
- [ ] 22.4 Initialize external clients on startup
- [ ] 22.5 Add cleanup logic on shutdown
- [ ] 22.6 Include all API routers in FastAPI app
- [ ] 22.7 Run `ruff check --fix` and `ruff format` on main.py
- [ ] 22.8 Run `pyrefly check --summarize-errors` on main.py

## 23. Core Middleware

- [ ] 23.1 Create `agentx/core/middleware/cors.py` with CORS middleware configuration
- [ ] 23.2 Create `agentx/core/middleware/logging.py` with request logging middleware
- [ ] 23.3 Create `agentx/core/middleware/error_handler.py` with global error handling
- [ ] 23.4 Run `ruff check --fix` and `ruff format` on middleware files
- [ ] 23.5 Run `pyrefly check --summarize-errors` on middleware files

## 24. Quality Check and Validation

- [ ] 24.1 Run `ruff check --fix` on entire agentx/ directory
- [ ] 24.2 Run `ruff format` on entire agentx/ directory
- [ ] 24.3 Run `pyrefly check --summarize-errors` on entire agentx/ directory
- [ ] 24.4 Verify all imports are absolute (no relative imports)
- [ ] 24.5 Verify no file exceeds 100 lines of executable code
- [ ] 24.6 Fix any remaining issues from quality tools

## 25. Documentation

- [ ] 25.1 Update CLAUDE.md with new folder structure documentation
- [ ] 25.2 Add folder structure diagram to CLAUDE.md
- [ ] 25.3 Document codebase expansion algorithm in CLAUDE.md
- [ ] 25.4 Document differentiation pattern in CLAUDE.md
- [ ] 25.5 Update import examples in CLAUDE.md to use absolute imports

## 26. Testing

- [ ] 26.1 Create `tests/unit/domain/entities/test_graph.py` for Graph entity tests
- [ ] 26.2 Create `tests/unit/application/agents/test_stem_cell.py` for StemCellAgent tests
- [ ] 26.3 Create `tests/unit/application/graphs/builder/test_graph_compiler.py` for GraphCompiler tests
- [ ] 26.4 Create tests for tool wrapping and registration
- [ ] 26.5 Create tests for memory integration (search before, store after)
- [ ] 26.6 Create tests for signature validation
- [ ] 26.7 Run pytest and verify all tests pass
