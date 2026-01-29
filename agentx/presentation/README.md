# Presentation Layer

**Purpose**: FastAPI routes (outermost layer).

## Structure

- `api/v1/`: REST endpoints organized by feature

## Constraints

- **Can import from**: application layer only
- **No business logic**: All logic in use cases
- **Thin controllers**: Routes delegate to use cases

## Files

- `agent_routes.py`: /query, /session/{id}, /sessions endpoints + WebSocket
- `health.py`: /health health check endpoint
