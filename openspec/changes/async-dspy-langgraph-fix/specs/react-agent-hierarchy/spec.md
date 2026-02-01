# Spec: ReAct Agent Hierarchy (Overview)

**Domain**: agent-runtime
**Generated**: 2026-02-02
**Status**: Overview - References granular implementation specs

---

## 1. Purpose

**This is an OVERVIEW spec** that ties together the granular implementation specs for the ReAct agent hierarchy.

Define the ReAct agent hierarchy pattern where a main Coordinator Agent deploys specialized sub-agents with limited tools (3-5 tools each) to prevent hallucination and improve performance.

**Problem Statement**: A single ReAct agent with 20+ tools causes:
- Tool confusion (agent doesn't know which tool to use)
- Hallucination (agent invents tool behaviors)
- Poor performance (excessive reasoning steps)

**Success Criteria**:
- Each sub-agent has maximum 5 tools (preferably 3)
- Coordinator analyzes query and deploys appropriate sub-agent
- Sub-agents complete tasks with minimal iterations (max 3)
- All DSPy signatures are class-based (no inline strings)
- All forward() methods return dspy.Prediction (not dict)

---

## 2. Granular Implementation Specs

This overview spec references the following granular specs for implementation details:

| Spec | Purpose | Key Components |
|------|---------|----------------|
| [`coordinator-agent/spec.md`](../coordinator-agent/spec.md) | Coordinator Agent | CoordinatorSignature, sub-agent deployment |
| [`research-sub-agent/spec.md`](../research-sub-agent/spec.md) | Research Agent | 3 tools: search_web, scrape_page, build_citation |
| [`widget-sub-agent/spec.md`](../widget-sub-agent/spec.md) | Widget Agent | 3 tools: select_widgets, render_card, show_chart |
| [`synthesis-sub-agent/spec.md`](../synthesis-sub-agent/spec.md) | Synthesis Agent | 3 tools: summarize, format_text, check_quality |
| [`memory-sub-agent/spec.md`](../memory-sub-agent/spec.md) | Memory Agent | 3 tools: store_memory, search_memory, consolidate |

---

## 3. Architecture Overview

```
User Query
    ↓
[Coordinator Agent]
    ├─ Analyze query
    ├─ Determine which sub-agent to deploy
    └─ Route to appropriate sub-agent
    ↓
┌─────────────────┬─────────────────┬─────────────────┬─────────────────┐
│ Research Agent  │  Widget Agent   │ Synthesis Agent  │  Memory Agent   │
│ (3 tools)       │  (3 tools)      │ (3 tools)        │  (3 tools)      │
│ • search_web    │  • select_wid   │ • summarize      │  • store_mem    │
│ • scrape_page   │  • render_card  │ • format_text    │  • search_mem   │
│ • build_citation│  • show_chart   │ • check_quality  │  • consolidate  │
└─────────────────┴─────────────────┴─────────────────┴─────────────────┘
```

---

## 4. Requirements

### 4.1 Functional Requirements

| ID | Requirement | Implementation Spec |
|----|-------------|---------------------|
| FR-RAH-001 | Coordinator Agent MUST analyze query and deploy sub-agent | coordinator-agent |
| FR-RAH-002 | Each sub-agent MUST have maximum 5 tools (preferably 3) | All sub-agents |
| FR-RAH-003 | BaseReActAgent MUST enforce tool limit at initialization | All sub-agents |
| FR-RAH-004 | All DSPy signatures MUST be class-based with InputField/OutputField | All sub-agents |
| FR-RAH-005 | All forward() methods MUST return dspy.Prediction | All sub-agents |
| FR-RAH-006 | Sub-agents MUST use max_iters=3 (limited reasoning) | All sub-agents |
| FR-RAH-007 | Coordinator MUST provide reasoning for agent selection | coordinator-agent |

### 4.2 Non-Functional Requirements

| ID | Requirement | Target Metric | Implementation Spec |
|----|-------------|---------------|---------------------|
| NFR-RAH-001 | Sub-agent file size | < 80 lines | All sub-agents |
| NFR-RAH-002 | Tool selection latency | < 100ms | coordinator-agent |
| NFR-RAH-003 | Sub-agent execution time | < 5s (per agent) | All sub-agents |
| NFR-RAH-004 | Code quality (ruff, pyrefly) | Pass all checks | All sub-agents |

---

## 5. Business Rules

| Rule | Description | Implementation Spec |
|------|-------------|---------------------|
| BR-RAH-001 | Tool limit: MAX_TOOLS_PER_AGENT = 5 | All sub-agents |
| BR-RAH-002 | All signatures class-based | All sub-agents |
| BR-RAH-003 | All returns are dspy.Prediction | All sub-agents |
| BR-RAH-004 | Sub-agents use max_iters=3 | All sub-agents |
| BR-RAH-005 | Coordinator provides reasoning | coordinator-agent |

---

## 6. Acceptance Criteria

- [ ] Coordinator Agent deploys sub-agents based on query analysis
- [ ] Each sub-agent has maximum 5 tools (preferably 3)
- [ ] BaseReActAgent enforces tool limit at initialization
- [ ] All DSPy signatures are class-based with InputField/OutputField
- [ ] All forward() methods return dspy.Prediction
- [ ] Sub-agents complete tasks in max 3 iterations
- [ ] Ruff and pyrefly checks pass
- [ ] File size < 80 lines per agent

---

## 7. Test Scenarios

### 7.1 Coordinator Routing

| Query | Expected Agent | Reason |
|-------|---------------|--------|
| "Compare iPhone vs Pixel" | research | Needs web search |
| "Show me a chart of sales data" | widget | Needs widget generation |
| "Summarize these findings" | synthesis | Needs text processing |
| "Store this preference" | memory | Needs memory operation |
| "What is 2+2?" | direct | Simple, no tools needed |

### 7.2 Tool Limit Enforcement

| Scenario | Expected Behavior |
|----------|------------------|
| Create agent with 6 tools | ValueError raised |
| Create agent with 3 tools | Success |
| Create agent with 5 tools | Success |

### 7.3 DSPy Best Practices

| Check | Expected |
|-------|----------|
| All signatures class-based | ✅ Pass |
| No inline `"query -> output"` | ✅ Pass |
| All returns are dspy.Prediction | ✅ Pass |
| No `return {...}` dict returns | ✅ Pass |

---

## 8. Comparison: Single Agent vs Hierarchy

| Aspect | Single Agent (20+ tools) | Hierarchy (5 sub-agents, 3-5 tools each) |
|--------|--------------------------|----------------------------------------|
| **Tool confusion** | 🔴 High | ✅ Low (focused tools) |
| **Hallucination risk** | 🔴 High | ✅ Low (limited scope) |
| **Reasoning steps** | 10-20 steps | 2-3 steps per sub-agent |
| **Performance** | 🔴 Slow | ✅ Fast |
| **Maintainability** | 🔴 Difficult | ✅ Easy (focused files) |
| **Debugging** | 🔴 Hard | ✅ Easy (clear scope) |

---

## 9. DSPy Fraud Fixes

| DSPy Fraud | Fix | Implementation Spec |
|------------|-----|---------------------|
| Inline signatures (`"query -> output"`) | Class-based with InputField/OutputField | All sub-agents |
| Dict returns (`return {...}`) | dspy.Prediction returns | All sub-agents |
| 20+ tools → hallucination | 3-5 tools per sub-agent | All sub-agents |
| No max_iters limit | max_iters=3 enforced | All sub-agents |

---

## 10. Integration Points

| Spec | Integration Details |
|------|-------------------|
| [`query-complexity-assessment/spec.md`](../query-complexity-assessment/spec.md) | Query complexity influences coordinator decision |
| [`dynamic-routing/spec.md`](../dynamic-routing/spec.md) | Sub-agents wrapped as LangGraph nodes |
| [`adaptive-widget-selection/spec.md`](../adaptive-widget-selection/spec.md) | Widget agent generates widgets |

---

**Next**: See [`coordinator-agent/spec.md`](../coordinator-agent/spec.md) for Coordinator Agent implementation.
