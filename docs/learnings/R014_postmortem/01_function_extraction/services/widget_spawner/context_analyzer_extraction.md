# context_analyzer.py - Function Extraction

## File: services/widget_spawner/context_analyzer.py

### Primary Purpose
Analyzes user queries to understand content type, user intent, and context using DSPy ReAct.

### Key Functions

#### `detect_content_type(query: str) -> str`
**Purpose**: Detect content type from keywords.

**Returns**: One of:
- `"data-heavy"`: data, trends, sales, chart, graph, statistics, analytics, metrics
- `"text-heavy"`: explain, guide, article, summary, blog, description
- `"visual-heavy"`: image, photo, gallery, picture, visual
- `"mixed"`: default

---

#### `infer_user_goal(query: str) -> str`
**Purpose**: Infer user intent from query.

**Returns**: One of:
- `"comparison"`: compare, vs, versus, difference, better, between
- `"exploration"`: show, display, what, list, all
- `"decision"`: should, recommend, best, choose, decision
- `"monitor"`: monitor, track, status, progress
- `"general"`: default

---

#### `check_device_capabilities(device_context_str: str) -> str`
**Purpose**: Check device capabilities for responsive design.

**Returns**: One of `"mobile"`, `"tablet"`, `"desktop"` (default if parsing fails)

---

### DSPy Classes

#### `AnalyzeContextSignature(dspy.Signature)`
**Purpose**: DSPy signature for context analysis.

**Inputs**:
- `user_query`: User's natural language request
- `device_context`: Device type, screen size

**Outputs**:
- `content_analysis`: Content type, complexity, structure
- `user_intent`: Goal (explore/compare/decide/monitor)
- `presentation_constraints`: Layout limits, accessibility needs

---

#### `ContextAnalyzerAgent(dspy.Module)`
**Purpose**: Context analyzer using ReAct for automatic tool selection.

**Tools**:
- `detect_content_type`
- `infer_user_goal`
- `check_device_capabilities`

**Max iterations**: 3

**ReAct benefit**: Automatically decides which tools to call based on query.

---

### Architectural Patterns

1. **Keyword-based heuristics**: Simple pattern matching for classification
2. **ReAct for composition**: LLM decides which tools to use
3. **Device-aware**: Considers mobile/tablet/desktop differences
4. **Three-layer analysis**: Content type + user intent + device context

---

### Dependencies

**Internal**:
- None (standalone analyzer)

**External**:
- `dspy`: DSPy framework
- `json`: JSON parsing
- `logging`: Standard logging

---

### Lessons Learned

1. **ReAct for automatic tool selection**: Don't hardcode which tools to call
2. **Keyword heuristics work**: Simple pattern matching is often enough
3. **Device context matters**: Mobile needs different UI than desktop
4. **Three-layer analysis**: Content + intent + device = complete context
5. **JSON parsing safety**: Handle JSONDecodeError gracefully
