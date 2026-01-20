read# AGENTX Generative UI Research & Design Plan

**Version**: 1.0.0
**Date**: 2026-01-19
**Status**: Design Review Pending
**Linked to**: PRD v1.1.0, HLD v1.0, Research Docs v1.0

---

## Executive Summary

Research and design plan for implementing a **LangGraph-based Generative UI system** for AGENTX frontend. The architecture uses a SOLID-compliant master-slave pattern where the main DSPy ReAct Agent controls a UI DSPy Agent as a tool, which in turn manages a LangGraph UI state machine.

**Key Innovation**: UI decisions are made through multiple focused DSPy signatures, not a monolithic controller. This keeps each signature simple, testable, and maintainable.

---

## Table of Contents

1. [Objective & Constraints](#1-objective--constraints)
2. [Architecture Design](#2-architecture-design)
3. [DSPy Signatures for UI](#3-dspy-signatures-for-ui)
4. [UI Descriptor Contract](#4-ui-descriptor-contract)
5. [Widget Mapping & Aesthetics](#5-widget-mapping--aesthetics)
6. [Implementation Plan](#6-implementation-plan)
7. [Fallback Strategy](#7-fallback-strategy)
8. [Research Findings](#8-research-findings)

---

## 1. Objective & Constraints

### 1.1 Objective

Implement a **Generative UI system** where the backend decides what UI appears and the frontend only decides how it looks. The system must:

- Work with small local LLMs (weak reasoning, limited planning)
- Use tool-driven UI (no free-form text descriptions)
- Support streaming updates in real-time
- Maintain SOLID principles throughout
- Have clear fallback strategy if approach proves too complex

### 1.2 Key Constraints

| Constraint | Description | Rationale |
|------------|-------------|-----------|
| **DSPy for Agent Logic** | All reasoning, tools, memory, RAG stay in DSPy | Proven in R011, R013 |
| **LangGraph for UI Only** | Generative UI + UI state management exclusively | Separation of concerns |
| **Python-first** | All LangGraph logic in FastAPI backend | Cannot debug JS/TS at agent layer |
| **No LangGraph JS** | Frontend is pure renderer | Maintainability |
| **Small Local LLMs** | Assume weak reasoning | Work with gemma3:4b, llama3.2 |
| **Tool-Driven UI** | UI via tool calls only | Deterministic behavior |
| **Fallback Required** | Backup plan like Silero → Kyutai | Risk mitigation |

### 1.3 Non-Goals

- No auto-layout by LLM (deterministic only)
- No frontend business logic (pure renderer)
- No implicit UI inference (explicit descriptors only)
- No React component invention (fixed registry only)

---

## 2. Architecture Design

### 2.1 SOLID-Compliant Master-Slave Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Central DSPy ReAct Agent (Master)                    │
│                    (Existing - No Changes Needed)                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Tools (All Equal):                                                      │
│  ├─ calculator      ├─ searxng_search      ├─ weather                  │
│  ├─ company_mis     ├─ voice_stt_tts      ├─ ui_agent  ← Just a tool! │
│                                                                          │
│  • ReAct reasoning                                                       │
│  • Temporal RAG (Mem0AI + Qdrant)                                        │
│  • Memory consolidation                                                  │
│  • Orchestrates all tools including UI                                   │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             │ Tool Call: ui_agent
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                  UI DSPy Agent (Slave Tool)                              │
│           (New - Multiple DSPy Signatures for UI)                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  DSPy Signatures (Multiple, Purpose-Built):                              │
│  ├─ select_widget(question) -> widget_type                              │
│  ├─ configure_form(context) -> form_schema                              │
│  ├─ update_progress(task, value) -> progress_state                      │
│  ├─ show_card(title, content) -> card_descriptor                        │
│  ├─ request_confirmation(action) -> confirmation_dialog                 │
│  ├─ handle_form_input(data) -> validation_result                        │
│  └─ control_langgraph(state) -> ui_transition                           │
│                                                                          │
│  • Each signature handles one UI concern                                 │
│  • DSPy ReAct orchestrates signatures as needed                          │
│  • Small, focused prompts for each signature                            │
│  • All async, streamable                                                │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             │ Tool Call: control_langgraph_ui
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    LangGraph UI State Machine                            │
│              (Pure State Machine - No LLM Calls)                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  • UI state transitions                                                  │
│  • Widget lifecycle management                                           │
│  • Form interrupt/resume                                                 │
│  • Streaming UI updates                                                  │
│  • Component registry                                                    │
│                                                                          │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             │ UI Descriptors (Pydantic)
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        Pydantic Bridge Layer                             │
│                    (Async Streaming via WebSocket)                       │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          Next.js BFF                                     │
│              (Streaming Proxy + Descriptor Normalizer)                  │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          shadcn/ui                                       │
│                      (Pure Renderer - No Logic)                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 SOLID Principles Applied

| Principle | Application |
|-----------|-------------|
| **Single Responsibility** | Main agent = reasoning, UI agent = interface decisions, LangGraph = state |
| **Open/Closed** | Add new UI widgets without changing agents |
| **Liskov Substitution** | ui_agent tool is interchangeable with other tools |
| **Interface Segregation** | Clean, focused tool interfaces |
| **Dependency Inversion** | Main agent depends on tool abstraction, not UI implementation |

### 2.3 Performance Considerations

| Aspect | Current | Future |
|--------|---------|--------|
| **LLM Calls** | Sequential on single gemma3:4b | Parallel on DGX Spark |
| **Latency Impact** | +200-500ms for UI decisions | Negligible with parallel execution |
| **Trade-off** | Clean architecture worth slight slowdown | Way better performance with more compute |

---

## 3. DSPy Signatures for UI

### 3.1 Signature Overview

The UI DSPy Agent uses **7 focused signatures** instead of one monolithic tool:

| Signature | Input | Output | Purpose |
|-----------|-------|--------|---------|
| **SelectWidget** | question, context | widget_type | Choose appropriate widget |
| **ConfigureForm** | context | form_schema | Set up form fields |
| **UpdateProgress** | task, value | progress_state | Update progress indicator |
| **ShowCard** | title, content | card_descriptor | Display information card |
| **RequestConfirmation** | action | confirmation_dialog | Ask user approval |
| **HandleFormInput** | form_data | validation_result | Process form submission |
| **ControlLangGraph** | state, intent | ui_transition | Manage UI state |

### 3.2 Signature Definitions

```python
import dspy
from dspy import Signature, Field

class SelectWidget(Signature):
    """Select appropriate widget for user interaction."""
    question = Field(desc="User's question or intent")
    context = Field(desc="Available context (tool results, memories)")
    widget_type = Field(desc="One of: text, card, form, progress, action, confirmation")

class ConfigureForm(Signature):
    """Configure form fields based on context."""
    required_fields = Field(desc="Information needed from user")
    form_schema = Field(desc="Form field definitions")

class ShowCard(Signature):
    """Create information card."""
    title = Field(desc="Card title")
    content = Field(desc="Card content")
    card_descriptor = Field(desc="Card UI descriptor")

class RequestConfirmation(Signature):
    """Request user confirmation for action."""
    action = Field(desc="Action requiring confirmation")
    confirmation_dialog = Field(desc="Confirmation UI descriptor")

class UpdateProgress(Signature):
    """Update progress indicator."""
    task = Field(desc="Task being performed")
    value = Field(desc="Progress value (0-1)")
    progress_state = Field(desc="Progress UI descriptor")

class HandleFormInput(Signature):
    """Validate and process form input."""
    form_data = Field(desc="User's form input")
    validation_result = Field(desc="Validation result + next action")

class ControlLangGraph(Signature):
    """Control LangGraph UI state transitions."""
    current_state = Field(desc="Current UI state")
    user_intent = Field(desc="User's latest input")
    ui_transition = Field(desc="Next UI state and actions")

# UI Agent with ReAct
class UIAgent(dspy.ReAct):
    """Purpose-built agent for UI decisions."""
    def __init__(self):
        super().__init__(
            "question->ui_decision",
            tools=[
                SelectWidget(),
                ConfigureForm(),
                ShowCard(),
                RequestConfirmation(),
                UpdateProgress(),
                HandleFormInput(),
                ControlLangGraph(),
            ]
        )
```

### 3.3 Prompt Strategy

Each signature uses **small, focused prompts**:

```python
# Example: SelectWidget prompt
"""
Given the user's question and available context, select the most appropriate UI widget.

Available widgets:
- text: Simple text/markdown response
- card: Information display with title and optional actions
- form: User input required (multiple fields)
- progress: Long-running task in progress
- action: Single button (confirm, approve, etc.)
- confirmation: Yes/No dialog for critical actions

Guidelines:
- Use text for simple answers
- Use card for structured information (search results, weather, etc.)
- Use form when user needs to provide data
- Use progress for operations taking >2 seconds
- Use action for single-step approvals
- Use confirmation for destructive or irreversible actions

Context: {context}
Question: {question}
"""
```

---

## 4. UI Descriptor Contract

### 4.1 Base Descriptor

```python
from pydantic import BaseModel
from typing import Literal, Optional

class UIDescriptor(BaseModel):
    """Base UI descriptor."""
    id: str
    type: Literal["text", "card", "form", "progress", "action", "confirmation", "voice"]
    timestamp: float
    dismissible: bool = True
```

### 4.2 Widget Descriptors

#### Text/Markdown Block
```python
class TextDescriptor(UIDescriptor):
    """Text/markdown block."""
    type: Literal["text"] = "text"
    content: str
    format: Literal["markdown", "plain"] = "markdown"
```

#### Card
```python
class CardDescriptor(UIDescriptor):
    """Information card."""
    type: Literal["card"] = "card"
    title: str
    content: str
    icon: Optional[str] = None  # lucide-react icon name
    actions: list[dict] = []  # [{label, action, variant}]
```

#### Form
```python
class FormField(BaseModel):
    name: str
    type: Literal["text", "number", "select", "checkbox", "textarea"]
    label: str
    required: bool = False
    placeholder: Optional[str] = None
    options: Optional[list[str]] = None  # For select
    validation: Optional[str] = None  # Regex pattern

class FormDescriptor(UIDescriptor):
    """Form for user input."""
    type: Literal["form"] = "form"
    title: str
    description: Optional[str] = None
    fields: list[FormField]
    submit_action: str
    submit_label: str = "Submit"
```

#### Progress Indicator
```python
class ProgressDescriptor(UIDescriptor):
    """Progress indicator."""
    type: Literal["progress"] = "progress"
    label: str
    value: float  # 0-1
    indeterminate: bool = False
```

#### Action Button
```python
class ActionDescriptor(UIDescriptor):
    """Action button."""
    type: Literal["action"] = "action"
    label: str
    action: str
    variant: Literal["default", "primary", "destructive", "outline"] = "default"
```

#### Confirmation Dialog
```python
class ConfirmationDescriptor(UIDescriptor):
    """Confirmation dialog."""
    type: Literal["confirmation"] = "confirmation"
    title: str
    message: str
    confirm_action: str
    confirm_label: str = "Confirm"
    cancel_action: str
    cancel_label: str = "Cancel"
    variant: Literal["default", "destructive"] = "default"
```

#### Voice Widget
```python
class VoiceDescriptor(UIDescriptor):
    """Voice recording widget."""
    type: Literal["voice"] = "voice"
    state: Literal["idle", "listening", "processing", "speaking"]
    transcription: Optional[str] = None
    visualizer: bool = True  # Show audio waveform
```

---

## 5. Widget Mapping & Aesthetics

### 5.1 Design Philosophy

**"Sexy but Minimal"** - The UI should feel modern and polished while maintaining simplicity:

- **No clutter**: Only one primary interaction surface at a time
- **Smooth transitions**: Widgets appear/disappear with animations
- **Visual hierarchy**: Important elements stand out
- **Responsive**: Works on desktop and mobile
- **Dark mode**: First-class dark theme support

### 5.2 shadcn/ui Component Mapping

| Descriptor | shadcn/ui Component | Styling | Animation |
|------------|-------------------|---------|-----------|
| **text** | `Typography` + `Prose` | Prose styling for markdown | Fade in (200ms) |
| **card** | `Card` + `CardHeader` + `CardContent` | Border, subtle shadow | Slide up + fade (300ms) |
| **form** | `Form` + `Input`/`Select`/`Checkbox` | Labeled fields, validation states | Scale in (250ms) |
| **progress** | `Progress` | Striped, animated | Expand (200ms) |
| **action** | `Button` | Variants mapped | Bounce on hover (150ms) |
| **confirmation** | `AlertDialog` | Backdrop blur | Scale + fade (200ms) |
| **voice** | Custom waveform viz | Canvas-based | Pulse recording |

### 5.3 Color Palette (shadcn/ui CSS Variables)

```css
:root {
  /* Primary - Brand accent */
  --primary: 222.2 47.4% 11.2%;
  --primary-foreground: 210 40% 98%;

  /* Secondary - Muted elements */
  --secondary: 210 40% 96%;
  --secondary-foreground: 222.2 47.4% 11.2%;

  /* Destructive - Dangerous actions */
  --destructive: 0 84% 60%;
  --destructive-foreground: 0 0% 98%;

  /* Muted - Backgrounds */
  --muted: 210 40% 96%;
  --muted-foreground: 215 16% 47%;

  /* Accent - Highlights */
  --accent: 210 40% 96%;
  --accent-foreground: 222.2 47.4% 11.2%;

  /* Borders */
  --border: 214.3 31.8% 91.4%;
  --input: 214.3 31.8% 91.4%;
  --ring: 222.2 84% 5%;

  /* Backgrounds */
  --background: 0 0% 100%;
  --foreground: 222.2 84% 5%;

  /* Card */
  --card: 0 0% 100%;
  --card-foreground: 222.2 84% 5%;
}

.dark {
  /* Dark mode defaults */
  --background: 222.2 84% 5%;
  --foreground: 210 40% 98%;
  --card: 222.2 84% 5%;
  --card-foreground: 210 40% 98%;
  --border: 217.2 32.6% 17.5%;
}
```

### 5.4 Typography

```css
/* Inter font family */
--font-sans: "Inter", var(--font-fallback), system-ui;

/* Type scale */
text-xs: 0.75rem (12px)
text-sm: 0.875rem (14px)
text-base: 1rem (16px)
text-lg: 1.125rem (18px)
text-xl: 1.25rem (20px)
text-2xl: 1.5rem (24px)
text-3xl: 1.875rem (30px)
```

### 5.5 Animation Timing

```typescript
// Framer motion variants
export const widgetVariants = {
  initial: { opacity: 0, y: 10 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -10 },
  transition: { duration: 0.2, ease: "easeInOut" }
};

// Stagger children for lists
const staggerContainer = {
  animate: {
    transition: {
      staggerChildren: 0.05
    }
  }
};
```

### 5.6 Layout Model

**Central Action Button**:
- Fixed position bottom-right (FAB style)
- Always visible
- Press to expand interaction UI

**ChatGPT-Style Sidebar**:
- Collapsed by default
- Shows conversation history
- Expands on hamburger click

**Widget Display Area**:
- Center stage, above fold
- One widget at a time
- Auto-dismiss when complete

---

## 6. Implementation Plan

### 6.1 Backend Implementation (FastAPI)

**File Structure**:
```
backend/
├── core/
│   ├── agents/
│   │   ├── main_agent.py          # Existing DSPy ReAct
│   │   ├── ui_agent.py            # New: UI DSPy Agent
│   │   └── base.py                # Base classes
│   ├── ui/
│   │   ├── langgraph_machine.py   # LangGraph UI state machine
│   │   ├── descriptors.py         # Pydantic UI schemas
│   │   ├── signatures.py          # DSPy signatures
│   │   └── widgets.py             # Widget type definitions
│   ├── tools/
│   │   ├── ui_agent_tool.py       # Tool wrapper for ui_agent
│   │   └── ...existing tools...
│   └── streaming/
│       └── ui_stream.py           # Async streaming handler
```

**Dependencies** (add to `requirements-core.txt`):
```txt
# LangChain & LangGraph for Generative UI
langchain>=0.3.0
langgraph>=0.2.0
langchain-core>=0.3.0
langchain-openai>=0.2.0  # For Ollama compatibility
```

### 6.2 BFF Implementation (Next.js)

**File Structure**:
```
frontend/
├── app/
│   └── api/
│       └── agent/
│           └── route.ts           # Streaming proxy
├── lib/
│   ├── agent/
│   │   ├── ui-registry.ts         # Widget → shadcn/ui mapping
│   │   └── descriptor-validator.ts # Zod validation
│   └── streaming/
│       └── ui-client.ts           # WebSocket client
└── components/
    └── agent/
        ├── AgentRenderer.tsx      # Main renderer
        ├── widgets/
        │   ├── TextWidget.tsx
        │   ├── CardWidget.tsx
        │   ├── FormWidget.tsx
        │   ├── ProgressWidget.tsx
        │   ├── ActionWidget.tsx
        │   ├── ConfirmationWidget.tsx
        │   └── VoiceWidget.tsx
        └── WidgetRegistry.tsx     # Component factory
```

**Dependencies** (add to `package.json`):
```json
{
  "dependencies": {
    "ai": "^3.0.0",           // Vercel AI SDK
    "zod": "^3.22.0",         // Schema validation
    "framer-motion": "^11.0.0" // Animations
  }
}
```

### 6.3 Timeline

| Week | Tasks | Deliverable |
|------|-------|-------------|
| **1** | Backend: ui_agent, descriptors, langgraph_machine | UI descriptors emitted |
| **2** | BFF: streaming proxy, widget registry | Frontend renders widgets |
| **3** | Test with small LLM, measure accuracy | Go/no-go decision |
| **4** | Polish or fallback to simpler approach | Production-ready |

---

## 7. Fallback Strategy

### 7.1 Failure Modes

| Failure Mode | Detection | Impact | Mitigation |
|--------------|-----------|--------|------------|
| **LangGraph too complex** | Implementation >2 weeks | Delay UI features | Switch to simpler |
| **Small LLM can't select widgets** | <50% accuracy | Poor UX | Pre-built rules |
| **Performance degradation** | Response >3s | Misses SLO | Remove UI layer |
| **Streaming conflicts** | UI blocks text | Bad UX | Separate channels |

### 7.2 Fallback Option A: DSPy-Only Enhanced

If LangGraph is too complex:

```python
# Main agent emits UI descriptors directly
class MainAgent(dspy.ReAct):
    def execute(self, question):
        result = self.reason(question)

        # Simple UI emission based on result type
        if result.needs_confirmation:
            self.emit_ui({"type": "confirmation", "title": result.action})
        elif result.is_form:
            self.emit_ui({"type": "form", "fields": result.form_fields})

        return result
```

**Pros**: Single LLM call, simpler debugging
**Cons**: Less sophisticated state management

### 7.3 Fallback Option B: Pre-Built Widget Library

If LLM widget selection fails:

```python
# Rule-based widget selection
WIDGET_RULES = {
    "calculator_result": "card",
    "search_results": "card",
    "confirmation": "confirmation",
    "form_input": "form",
    "long_task": "progress",
}

def select_widget(tool_name, result):
    widget_type = WIDGET_RULES.get(tool_name, "text")
    return {"type": widget_type, "data": result}
```

**Pros**: Deterministic, fast
**Cons**: Less flexible, can't adapt to context

### 7.4 Migration Path

```
Week 1-2: Implement LangGraph approach
Week 3:   Test with small LLM
          ↓
          If <70% widget selection accuracy
          ↓
Week 4:   Switch to Fallback A or B
```

---

## 8. Research Findings

### 8.1 LangChain Generative UI Patterns

From research of [LangSmith Generative UI React Documentation](https://docs.langchain.com/langsmith/generative-ui-react):

- **UI Descriptors**: `AnyUIMessage` structure with `id`, `display`, `data`, `metadata`
- **Tool-Based Emission**: Agents emit UI via structured tools, not free-form text
- **Streaming Events**: Separate event types for messages, UI updates, tool calls
- **Component Updates**: Same ID for updates, `merge` flag for incremental changes
- **Human-in-the-Loop**: Forms and confirmations via interrupt/resume

### 8.2 LangGraph JS Examples

From research of [langgraphjs-gen-ui-examples](https://github.com/langchain-ai/langgraphjs-gen-ui-examples):

- **Component Registry**: Factory pattern for UI component generation
- **Event-Driven**: Stream state updates through WebSockets
- **State Management**: Single source of truth in backend
- **Security**: Validate all UI descriptors, avoid runtime code generation

**JS Anti-Patterns to Avoid**:
- Direct DOM manipulation
- Client-side state management for agent decisions
- Component code generation
- Implicit UI inference

### 8.3 AGENTX Architecture

From review of PRD, HLD, and prototypes:

- **Frontend**: Next.js 14 + shadcn/ui + WebSocket streaming
- **Backend**: FastAPI + DSPy ReAct (proven in R011, R013)
- **Tools**: Calculator, SearXNG search, Weather, Company MIS
- **Voice**: Kyutai STT/TTS (planned)
- **Memory**: Mem0AI + Qdrant temporal RAG
- **Streaming**: Already implemented (text + audio in R013)

---

## 9. Dependencies

### 9.1 Backend (requirements-core.txt)

```txt
# LangChain & LangGraph for Generative UI
langchain>=0.3.0
langgraph>=0.2.0
langchain-core>=0.3.0
langchain-openai>=0.2.0  # For Ollama compatibility
```

### 9.2 Frontend (package.json)

```json
{
  "dependencies": {
    "ai": "^3.0.0",
    "zod": "^3.22.0",
    "framer-motion": "^11.0.0"
  }
}
```

---

## 10. Success Criteria

1. **Research Complete**: ✅ All patterns studied and understood
2. **Architecture Designed**: ✅ SOLID master-slave with multiple DSPy signatures
3. **Fallback Strategy**: ✅ Two fallback options with migration path
4. **Implementation Ready**: ✅ File structure, dependencies, timeline defined

---

## Appendix: Design Review Questions

For the design review, please consider:

1. **Widget Coverage**: Are all required widgets represented?
2. **Aesthetic Direction**: Does "sexy but minimal" align with vision?
3. **Animation Timing**: Are 200-300ms transitions appropriate?
4. **Color Palette**: Does the shadcn/ui default work, or custom needed?
5. **Layout Model**: Is FAB + sidebar + center stage right?
6. **Fallback Trigger**: Is <70% accuracy the right threshold?
7. **Performance**: Is +200-500ms latency acceptable for UI decisions?
8. **Dependencies**: Are LangChain/LangGraph versions appropriate?

---

**This plan is part of AGENTX engineering documentation. See [HLD.md](HLD.md) for complete architecture.**
