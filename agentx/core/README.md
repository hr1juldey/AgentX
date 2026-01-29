# Core Layer

**Purpose**: Configuration and dependency injection.

## Structure

- `config.py`: Pydantic Settings for environment-based configuration
- `dependencies.py`: DI singletons with getter functions
- `middleware/`: CORS, logging, auth middleware

## Configuration

Uses Pydantic Settings with environment variable support:
- Database settings (Redis URL, SQLite path, Qdrant URL)
- LLM settings (provider, model, API base)
- Server settings (host, port, workers)
- Voice settings (sample rates)

## Dependency Injection

Global singletons with lazy-loading:
- `get_redis_session_adapter()`
- `get_sqlite_session_adapter()`
- `get_agent_session_repository()`

Call `reset_dependencies()` for testing.

## Files

- `config.py`: Settings class and get_settings() function
- `dependencies.py`: All dependency getter functions
