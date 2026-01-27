# Application Layer - DTOs Summary

**Directory**: `application/dtos/`

**Purpose**: Data Transfer Objects for Clean Architecture

---

## Files Extracted

1. **requests.py** (84 lines)
   - GenerateWidgetRequest
   - IntelligentGenerateRequest
   - SearchRequest
   - CitationRequest
   - HopEventRequest

2. **responses.py** (38 lines)
   - HealthResponse
   - SearchResultResponse
   - UIDescriptorResponse (type alias)

---

## Key Patterns

### Request DTOs
- Literal type constraints for enums (widget types)
- Field validation with Field() (min_length, ge, le)
- Device context pattern for responsive UI
- WebSocket event pattern for streaming

### Response DTOs
- Domain entities can be used directly (UIDescriptorResponse = UIDescriptor)
- Flexible dict fields for extensibility (metadata, llm)
- Lists for collections (citations, hops, queries)

---

## Violations Found

None - Clean Architecture compliant.

---

## Reusability for Real AgentX

**REQUIRED** - Use this DTO pattern for API layer.

**Key Files to Copy**:
- `application/dtos/requests.py` - Request DTO template
- `application/dtos/responses.py` - Response DTO template

**Pattern**: Separate request/response DTOs in application/dtos/
