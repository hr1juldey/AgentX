# Application Layer

**Purpose**: Use cases orchestration and DTOs.

## Structure

- `use_cases/`: Single-purpose classes with `execute()` method
- `commands/`: Command DTOs (requests)
- `queries/`: Query DTOs (requests)
- `dtos/`: Pydantic models for API layer
- `mappers/`: Entity ↔ DTO conversion (static methods)
- `services/`: Application services

## Constraints

- **Can import from**: domain, infrastructure layers
- **Orchestrates workflows**: Use cases coordinate between domain and infrastructure
- **API contracts**: DTOs define the API surface

## Files

- `execute_agent_query.py`: Main use case for query processing
- `agent_dtos.py`: ExecuteAgentQueryRequest/Response, ToolCallDTO, UIComponentDTO
- `ui_dtos.py`: UI component DTOs (Markdown, Card, Form, etc.)
- `agent_session_mapper.py`: Mapper for AgentSessionEntity
- `ui_component_mapper.py`: Mapper for UIComponentEntity and descriptors
