# PRD - Prototype Template

## Product Overview

**Name**: {{PROTOTYPE_NAME}}
**Level**: {{LEVEL}}
**Category**: {{CATEGORY}}
**Estimated Time**: {{HOURS}} hours

## User Utility

{{Describe the actual user utility - what problem does this solve?}}

## Requirements

### Functional Requirements

- {{FR-1}}: Description
- {{FR-2}}: Description

### Non-Functional Requirements

- **Performance**: API latency p95 <500ms
- **Usability**: Clean, intuitive UI
- **Reliability**: Graceful error handling

## Technical Specification

### Backend (FastAPI)

#### Endpoints
| Method | Path | Description |
|--------|------|-------------|
| GET | /api/v1/health | Health check |
| {{METHOD}} | {{PATH}} | {{DESCRIPTION}} |

#### Data Models
```python
# Example schema
class ExampleSchema(BaseModel):
    field: str
```

### Frontend (Next.js + shadcn/ui)

#### Pages
- `/` - Main page with {{DESCRIPTION}}

#### Components
- `Button`, `Input`, `Card` - shadcn/ui components

## Success Criteria

1. ✅ Backend API functional with all endpoints
2. ✅ Frontend UI displays data correctly
3. ✅ User can {{KEY_ACTION}}
4. ✅ Tests pass with ≥80% coverage
5. ✅ Performance meets requirements

## Dependencies

### Backend
- fastapi>=0.115.0
- sqlmodel>=0.0.22
- (Add prototype-specific dependencies)

### Frontend
- next@^15.1.0
- react@^19.0.0
- (Add prototype-specific dependencies)

## Out of Scope

{{What features are explicitly NOT included in this prototype}}
