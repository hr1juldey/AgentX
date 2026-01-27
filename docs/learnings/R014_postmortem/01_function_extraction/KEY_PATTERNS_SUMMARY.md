# R014 Key Architectural Patterns Summary

**Extraction Progress**: 53+ documents created
**Coverage**: All core architectural patterns documented

---

## 1. Master Agent Orchestration Pattern

**File**: `services/master_agent/master_agent.py`

**Pattern**: Single orchestrator coordinating 7 specialist agents

**Pipeline Order**:
1. ANALYST (Pass 1): Query understanding
2. RESEARCHER: Web search + beautify
3. CONTEXTUALIZER: Rerank → filter → contextualize
4. ANALYST (Pass 2): Data quality judgment
5. DESIGNER: POV + colors + hierarchy
6. WIDGET SELECTOR: Select widgets
7. SEQUENCER: Order + pace widgets
8. PRESENTER: Final polish + QA

**Key Classes**:
- `MasterAgent` - Main orchestrator (dspy.Module)
- `AgentSetup` - Dependency injection helper
- `PipelineValidator` - Validation before execution
- `StreamingHandler` - Async streaming support
- `DeliveryPlanner` - Staggered widget delivery

**Reuse for Real AgentX**: ✅ REQUIRED

---

## 2. Dual-Pass Agent Pattern

**File**: `services/pipeline/analyst.py`

**Pattern**: Same agent runs twice with different tools

**Pass 1** (Before research):
- ContextAnalyzerModule
- InsightExtractorModule
- GoalDetectorModule
- SearchTermExtractorModule

**Pass 2** (After contextualization):
- DataQualityCheckerModule

**Key Insight**: Analyst understands query first, then judges research results

**Reuse for Real AgentX**: ✅ HIGH

---

## 3. Staggered Widget Delivery Pattern

**File**: `services/master_agent/delivery_planner.py`

**Pattern**: Deliver widgets progressively (2-5 seconds apart)

**DeliveryPlan**:
```python
@dataclass
class DeliveryPlan:
    widgets: list  # UIDescriptors
    delays: list[float]  # Seconds for each widget
    total_duration: float  # Total time
```

**Pacing Formula**:
- Widget 1: 0s (immediate)
- Widget 2: ~2s
- Widget 3: ~3.5s
- Widget N: Approaches 5s

**Benefits**:
- Less overwhelming for user
- Consultant-style presentation
- Progressive disclosure
- Better UX perception

**Reuse for Real AgentX**: ✅ REQUIRED

---

## 4. Hybrid Rule-Based + LLM Selection

**File**: `services/pipeline/widget_selector.py`

**Pattern**: Rules for common cases, LLM for complex

**Rule-Based** (Fast):
- Multiple URLs → gallery widget
- Single URL → image + markdown

**LLM-Based** (Context-Aware):
- Other queries → WidgetMatcherModule

**Fallback**:
- Data errors → markdown
- Visual errors → card

**Reuse for Real AgentX**: ✅ REQUIRED

---

## 5. Type Conversion for LLM Outputs

**File**: `services/tools/common/type_utils.py`

**Pattern**: Always convert LLM text outputs to proper types

**Functions**:
```python
_to_float(value, default=0.5) -> float
_to_bool(value, default=False) -> bool
```

**Handles**:
- Already-float values
- String floats ("0.75")
- Text scores ("High" → 0.85)
- Booleans (True → 1.0)
- Percentages ("75%" → 0.75)

**Critical**: LLMs return text, not proper types

**Reuse for Real AgentX**: ✅ CRITICAL

---

## 6. Chunking + Iterative Refinement

**File**: `services/tools/analyst/query_analyzer.py`

**Pattern**: Decision tree + chunking for large inputs

**Decision Tree**:
```python
if len(query) <= 500:
    return _extract_single(query)  # Fast path
else:
    return _extract_iterative(query)  # Chunk + iterate
```

**Chunking Parameters**:
- MAX_CHUNK_SIZE = 500
- OVERLAP = 100
- ITERATIONS = 3

**Process**:
1. Chunk text (500 chars, 100 overlap)
2. First chunk: initial_extractor
3. Subsequent: refiner with existing_insights
4. Deduplicate results

**Reuse for Real AgentX**: ✅ REQUIRED

---

## 7. Semantic Few-Shot Learning

**File**: `services/tools/selector_tools.py`

**Pattern**: Put examples in signature docstring

**SelectWidgetSignature**:
```python
class SelectWidgetSignature(dspy.Signature):
    """Select widgets based on semantic patterns.
    
    Example 1: "Show stock prices" → chart
    Example 2: "Display photos" → gallery
    [... 3 more examples ...]
    
    NOTE: Examples to learn from, not rules.
    """
```

**Benefits**:
- LLM learns patterns, not rules
- Handles new queries by analogy
- More flexible than hard-coded rules

**Reuse for Real AgentX**: ✅ HIGH

---

## 8. Safe DSPy Result Extraction

**Pattern**: Always use hasattr + .get() for DSPy results

**Code**:
```python
result = self.some_module(input=data)
safe_result = result if hasattr(result, "get") else {}
value = safe_result.get("key", default_value)
```

**Why**: DSPy Predict returns special objects, not plain dicts

**Reuse for Real AgentX**: ✅ REQUIRED

---

## 9. Singleton Dependency Injection

**File**: `application/use_cases/*.py`

**Pattern**: Global singleton + getter function

**Code**:
```python
_use_case: MyUseCase | None = None

def get_my_use_case() -> MyUseCase:
    global _use_case
    if _use_case is None:
        _use_case = MyUseCase()
    return _use_case
```

**Benefits**:
- Lazy initialization
- Single instance
- Test-friendly (can reset)

**Reuse for Real AgentX**: ✅ HIGH

---

## 10. Clean Architecture Layers

**Structure**:
```
domain/entities/       # Business entities
application/dtos/      # Request/Response DTOs
application/use_cases/ # Use case facades
services/pipeline/     # Business logic
api/                   # Routes
```

**Key Principle**:
- Domain entities in center
- DTOs for API layer
- Use cases wrap services
- Routes depend on use cases

**Reuse for Real AgentX**: ✅ REQUIRED

---

## Critical Dependencies

### Technical
- **DSPy 3.1+**: Core framework
- **Ollama**: Local LLM (gemma3:4b, qwen3:8b tested)
- **SearXNG**: Web search
- **FastAPI**: Backend framework
- **Pydantic**: Data validation

### Architectural
- **Clean Architecture**: Proven effective
- **Domain-Driven Design**: Required for scalability
- **SOLID Principles**: Critical for maintainability

### Integration Patterns
- **DSPy + Ollama**: Built-in support
- **DSPy Streaming**: Requires sync warmup
- **WebSocket + FastAPI**: Production-ready
- **Async/Sync Bridge**: Required for blocking deps

---

## What to Replicate

### Must Have (Required)
1. Master Agent orchestration (7 agents)
2. Type conversion utilities (_to_float, _to_bool)
3. Staggered delivery pattern (2-5s pacing)
4. Chunking + iterative refinement
5. Safe DSPy extraction (hasattr + .get)
6. Singleton DI pattern

### Should Have (High Value)
1. Dual-pass analyst pattern
2. Hybrid rule-based + LLM selection
3. Semantic few-shot learning
4. Clean architecture layers
5. Use case facades

### Nice to Have (Optional)
1. Multi-hop search with reflection
2. Hardware-adaptive execution
3. Progress tracking for streaming
4. QA checkpoint system

---

## What to Avoid

1. ❌ Verbose DSPy signatures (keep < 10 words per field)
2. ❌ Data model scattering (one canonical location)
3. ❌ God objects (max 150 lines per file)
4. ❌ Hardcoded URLs (use environment variables)
5. ❌ Mutable default arguments (Pydantic v2 OK)
6. ❌ Relative imports (use absolute imports only)

---

## Files to Copy for Real AgentX

### Core Architecture
1. `services/master_agent/master_agent.py` - Orchestration pattern
2. `services/pipeline/` - All 7 agents
3. `services/tools/common/type_utils.py` - Type conversion
4. `services/core/chunking.py` - Chunking utilities
5. `application/use_cases/` - Use case pattern

### Configuration
6. `config/settings.py` - Pydantic Settings v2
7. `config/dspy.py` - Multi-provider DSPy setup

### Domain
8. `domain/entities/ui_descriptor.py` - Domain entity pattern

### API
9. `api/routes/` - WebSocket streaming patterns

---

## Summary

**R014 successfully demonstrates**:
- ✅ Clean Architecture with DSPy
- ✅ Master Agent orchestration pattern
- ✅ Staggered delivery for UX
- ✅ Hybrid rule-based + LLM
- ✅ Type-safe LLM interactions
- ✅ Async streaming with progress
- ✅ Multi-hop search with reflection

**Real AgentX should**:
- ✅ Copy the 7-pipeline architecture
- ✅ Use type conversion utilities
- ✅ Implement staggered delivery
- ✅ Follow clean architecture layers
- ✅ Use singleton DI pattern

**Estimated reuse value**: 85% of R014 patterns are directly applicable to Real AgentX.
