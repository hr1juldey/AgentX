# Domain Layer

**Purpose**: Contains business logic and domain models (innermost layer).

## Structure

- `entities/`: Core business entities (@dataclass)
- `value_objects/`: Immutable value objects
- `repositories/`: Repository interfaces (ABC)
- `services/`: Domain services

## Constraints

- **No external dependencies**: This layer must not import from infrastructure, agent, or presentation layers.
- **Pure business logic**: All business rules live here.
- **Framework-agnostic**: No FastAPI, DSPy, or external framework code.

## Files

- `agent_session.py`: Agent session entity with lifecycle management
- `ui_component.py`: UI component entity for server-driven UI
- `enums.py`: All domain enumerations (SessionState, UIComponentType, etc.)
