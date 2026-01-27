# Application Layer - Use Cases Summary

**Directory**: `application/use_cases/`

**Purpose**: Use case facades for Clean Architecture

---

## Files Extracted

1. **widget_generation.py** (76 lines)
   - WidgetGenerationUseCase
   - generate_widget()
   - generate_intelligent()

2. **master_agent.py** (113 lines)
   - MasterAgentUseCase
   - create_master_agent()
   - setup_master_agent_with_pipeline()

3. **search.py** (103 lines)
   - SearchUseCase
   - MultiHopSearchWebSocketUseCase
   - search()
   - search_with_streaming()

---

## Key Patterns

### Use Case Facades
- Wrap existing services with use case classes
- Return domain entities, not DTOs
- Singleton getter for dependency injection
- Lazy imports (from inside functions)

### Master Agent Pipeline Setup
**setup_master_agent_with_pipeline()** encapsulates:
- 7 pipeline agents (analyst, researcher, data_contextualizer, designer, widget_selector, sequencer, presenter)
- 6 hydrators (chart, markdown, card, form, image, gallery)
- Complete configuration in one place

### WebSocket Streaming
- Progress callback: `Callable[[dict[str, Any]], None]`
- Configurable limits (max_hops from request or settings)
- Returns full SearchResultResponse (not just string)

---

## Violations Found

- Minor: Inconsistent conversion (model_dump vs .get)
- Minor: Callback type hints use `# type: ignore`

---

## Reusability for Real AgentX

**REQUIRED** - Use this use case pattern.

**Key Files to Copy**:
- `application/use_cases/master_agent.py` - Pipeline setup pattern
- `application/use_cases/search.py` - WebSocket streaming pattern

**Pattern**: Use case facades with singleton getters
