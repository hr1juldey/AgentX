# Phase 3 Tasks: UI DSPy Agent + Descriptors

**Phase**: 3
**Estimated Time**: 2-3 hours
**Dependencies**: Phase 0 (T001-T009), Phase 1 (T100-T104), Phase 2 (T200-T204)
**Status**: Ready for Execution

---

## Phase Overview

Phase 3 implements the generative UI layer with DSPy-powered widget selection and WebSocket streaming for real-time updates.

### What's Implemented

- **UI Descriptors**: 7 core Pydantic schemas (Markdown, Card, Form, Progress, Action, Confirmation, Voice)
- **UI DSPy Signatures**: Widget selection and configuration signatures
- **UI DSPy Agent**: Generates UI descriptors based on content
- **WebSocket Streaming**: Real-time message streaming to frontend
- **Testing**: Integration tests for UI layer

### What's Stubbed

- LangGraph state machines - Phase 4
- Form interrupt/resume - Phase 4
- Memory consolidation - Phase 5
- Plugin system - Phase 6

---

## Task List

### T300: Create UI Descriptor Schemas (40 minutes)

**File**: `T300_ui_descriptor_schemas.md`

**Creates**:
- `ui/descriptors/base.py` - BaseUIDescriptor, UIDescriptorType enum
- `ui/descriptors/markdown_block.py` - MarkdownBlockDescriptor
- `ui/descriptors/card.py` - CardDescriptor, CardAction
- `ui/descriptors/form.py` - FormDescriptor, FormField
- `ui/descriptors/progress.py` - ProgressDescriptor
- `ui/descriptors/action.py` - ActionDescriptor
- `ui/descriptors/confirmation.py` - ConfirmationDescriptor
- `ui/descriptors/voice.py` - VoiceDescriptor

---

### T301: Create UI DSPy Signatures (25 minutes)

**File**: `T301_ui_dspy_signatures.md`

**Creates**:
- `agent/dspy_signatures/ui_signatures.py`
  - SelectWidgetSignature - Choose widget type
  - ConfigureFormSignature - Generate form fields
  - ShowCardSignature - Create card widgets
  - RequestConfirmationSignature - Confirmation dialogs
  - UpdateProgressSignature - Progress updates

---

### T302: Create UI DSPy Agent (35 minutes)

**File**: `T302_ui_dspy_agent.md`

**Creates**:
- `agentx/agent/dspy_agents/ui_dspy_agent.py`
  - UIDSPyAgent - Generates UI descriptors
  - create_markdown_block() - Text blocks
  - create_card() - Information cards
  - create_form() - User input forms
  - create_progress() - Progress indicators
  - create_action() - Action buttons
  - create_confirmation() - Confirmation dialogs
  - select_widget_for_content() - DSPy widget selection

---

### T303: Create WebSocket Streaming (50 minutes)

**File**: `T303_websocket_streaming.md`

**Creates**:
- `ui/protocols/websocket.py` - WebSocket message types
  - WebSocketMessageType enum
  - WebSocketMessage, TokenMessage, ReasoningStepMessage
  - ToolCallMessage, DescriptorCreateMessage
- `infrastructure/external/websocket_manager.py` - Connection management
- `presentation/api/websocket.py` - WebSocket routes
  - `/ws/agent/stream` endpoint
  - Real-time streaming of reasoning, tools, UI updates

---

### T304: Create Phase 3 Integration Tests (40 minutes)

**File**: `T304_phase3_tests.md`

**Creates**:
- `tests/integration/phase3/test_ui_descriptors.py`
- `tests/integration/phase3/test_ui_agent.py`
- `tests/integration/phase3/test_websocket.py`

---

## Running Phase 3

### Prerequisites

1. **Phase 0 Complete**: T001-T009
2. **Phase 1 Complete**: T100-T104
3. **Phase 2 Complete**: T200-T204

### Execution Order

```bash
# T300: UI Descriptor Schemas
cd /home/riju279/Documents/Code/XRIG/AgentX/prototypes/R013_travel_planning_stream/backend
# Follow T300_ui_descriptor_schemas.md

# T301: UI DSPy Signatures
# Follow T301_ui_dspy_signatures.md

# T302: UI DSPy Agent
# Follow T302_ui_dspy_agent.md

# T303: WebSocket Streaming
# Follow T303_websocket_streaming.md

# T304: Phase 3 Tests
# Follow T304_phase3_tests.md
```

### Verification (End of Phase 3)

```bash
cd /home/riju279/Documents/Code/XRIG/AgentX/prototypes/R013_travel_planning_stream/backend

# Verify UI descriptors
python3 -c "from agentx.ui.descriptors import MarkdownBlockDescriptor, CardDescriptor, FormDescriptor; print('Descriptors OK')"

# Verify UI agent
python3 -c "from agentx.agent.dspy_agents import UIDSPyAgent; print('UI Agent OK')"

# Verify WebSocket
python3 -c "from agentx.ui.protocols.websocket import WebSocketMessageType; print('WebSocket OK')"

# Run tests
pytest tests/integration/phase3/ -v
```

---

## Phase 3 Deliverables

### UI Layer

**Descriptors** (9 files):
- ✅ `base.py` - Base descriptor and types
- ✅ `markdown_block.py` - Markdown blocks
- ✅ `card.py` - Information cards
- ✅ `form.py` - User input forms
- ✅ `progress.py` - Progress indicators
- ✅ `action.py` - Action buttons
- ✅ `confirmation.py` - Confirmation dialogs
- ✅ `voice.py` - Voice input
- ✅ `__init__.py` - Package exports

### Agent Layer

**Signatures** (1 file):
- ✅ `ui_signatures.py` - UI DSPy signatures

**Agents** (1 file):
- ✅ `ui_dspy_agent.py` - UI DSPy agent

### Protocols

**WebSocket** (1 file):
- ✅ `websocket.py` - Message types

### Infrastructure

**WebSocket Manager** (1 file):
- ✅ `websocket_manager.py` - Connection management

### Presentation

**Routes** (1 file):
- ✅ `websocket.py` - WebSocket endpoints

### Testing

**Integration Tests** (3 files):
- ✅ `test_ui_descriptors.py`
- ✅ `test_ui_agent.py`
- ✅ `test_websocket.py`

**Total**: 17 files created in Phase 3

---

## Key Features

### 7 Core UI Descriptors

1. **MarkdownBlock** - Rich text content
2. **Card** - Structured information with actions
3. **Form** - User input with validation
4. **Progress** - Long-running operation status
5. **Action** - Standalone buttons
6. **Confirmation** - Risky operation confirmation
7. **Voice** - Audio input from microphone

### WebSocket Message Types

- **TOKEN** - Streaming text tokens
- **REASONING_STEP** - Agent reasoning updates
- **TOOL_CALL** - Tool execution updates
- **DESCRIPTOR_CREATE** - Create UI widget
- **DESCRIPTOR_UPDATE** - Update existing widget
- **DESCRIPTOR_DISMISS** - Remove widget
- **ERROR** - Error messages

---

## Next Phase: Phase 4 - LangGraph State Machines

**Phase 4 Tasks** (T400-T403):
- T400: Create LangGraph State Schemas
- T401: Create Backend State Machine
- T402: Create Frontend State Machine
- T403: Create Phase 4 Tests

**Phase 4 Deliverables**:
- Backend LangGraph state (agent reasoning, tool execution)
- Frontend LangGraph state (UI visibility, component lifecycle)
- State transition logic
- Interrupt/resume functionality
- Integration tests for state machines

---

**Phase 3 Status**: ✅ READY FOR EXECUTION

**All task files created**: T300-T304

**Total Estimated Time**: 2-3 hours
