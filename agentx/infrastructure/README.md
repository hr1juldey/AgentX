# Infrastructure Layer

**Purpose**: External adapters and integrations (database, HTTP, storage).

## Structure

- `database/`: Database adapters (Redis, SQLite)
- `external/`: External service clients (Ollama, Qdrant, Mem0, WebSocket)

## Constraints

- **Can import from**: domain layer only
- **Cannot import from**: agent, application, presentation layers
- **External deps only**: This layer contains all external API calls

## Files

- `redis_session_adapter.py`: Redis implementation of AgentSessionRepository
- `sqlite_session_adapter.py`: SQLite implementation of AgentSessionRepository
