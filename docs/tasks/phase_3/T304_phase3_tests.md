# T304: Create Phase 3 Integration Tests

**Phase**: 3
**Estimated Time**: 40 minutes
**Dependencies**: T300, T301, T302, T303
**Blocked By**: None

---

## Context

**LLD References**:
- `LLD.md` - Phase 5: Testing Strategy
- `lld/incremental_release_plan.md` - Phase 3: Test UI layer

**Description**:
Creates integration tests for Phase 3 UI layer. Tests verify UI descriptors, UI agent, and WebSocket functionality.

---

## Acceptance Criteria

**Passing Criteria**:
- Test file for UI descriptor validation
- Test file for UI DSPy agent
- Test file for WebSocket manager
- Test file for WebSocket messages
- All tests use pytest async pattern
- Tests pass with `pytest tests/integration/phase3/`

**Verification Commands**:
```bash
cd /home/riju279/Documents/Code/XRIG/AgentX/prototypes/R013_travel_planning_stream/backend

# Verify test files exist
test -f tests/integration/phase3/test_ui_descriptors.py && echo "Descriptor tests exist"
test -f tests/integration/phase3/test_ui_agent.py && echo "UI agent tests exist"
test -f tests/integration/phase3/test_websocket.py && echo "WebSocket tests exist"

# Run tests
pytest tests/integration/phase3/ -v
```

---

## Implementation Steps

### Step 1: Create UI descriptor tests

Create file `tests/integration/phase3/test_ui_descriptors.py`:

```python
"""Integration tests for UI descriptors."""

import pytest
from uuid import uuid4

from agentx.ui.descriptors import (
    MarkdownBlockDescriptor,
    CardDescriptor,
    CardAction,
    FormDescriptor,
    FormField,
    ProgressDescriptor,
    ActionDescriptor,
    ConfirmationDescriptor,
    VoiceDescriptor,
    UIDescriptorType,
)


class TestMarkdownBlockDescriptor:
    """Test MarkdownBlock descriptor."""

    def test_create_markdown_block(self):
        """Should create valid markdown block."""
        descriptor = MarkdownBlockDescriptor(
            descriptor_id="test-id",
            content="# Hello World"
        )
        assert descriptor.descriptor_type == UIDescriptorType.MARKDOWN_BLOCK
        assert descriptor.content == "# Hello World"
        assert descriptor.allow_copy == True

    def test_markdown_block_serialization(self):
        """Should serialize to JSON correctly."""
        descriptor = MarkdownBlockDescriptor(
            descriptor_id="test-id",
            content="Test content"
        )
        data = descriptor.dict()
        assert data["content"] == "Test content"
        assert data["descriptor_type"] == "markdown_block"


class TestCardDescriptor:
    """Test Card descriptor."""

    def test_create_card_basic(self):
        """Should create card with title and content."""
        descriptor = CardDescriptor(
            descriptor_id="test-id",
            title="Test Card",
            content="Card content"
        )
        assert descriptor.descriptor_type == UIDescriptorType.CARD
        assert descriptor.title == "Test Card"
        assert len(descriptor.actions) == 0

    def test_create_card_with_actions(self):
        """Should create card with action buttons."""
        actions = [
            CardAction(action_id="action1", label="Click Me"),
            CardAction(action_id="action2", label="Cancel", variant="secondary")
        ]
        descriptor = CardDescriptor(
            descriptor_id="test-id",
            title="Action Card",
            content="Choose an action",
            actions=actions
        )
        assert len(descriptor.actions) == 2
        assert descriptor.actions[0].label == "Click Me"


class TestFormDescriptor:
    """Test Form descriptor."""

    def test_create_form_basic(self):
        """Should create form with fields."""
        fields = [
            FormField(field_name="name", field_type="text", label="Name", required=True),
            FormField(field_name="email", field_type="email", label="Email", required=True)
        ]
        descriptor = FormDescriptor(
            descriptor_id="test-id",
            form_id="form-1",
            fields=fields
        )
        assert descriptor.descriptor_type == UIDescriptorType.FORM
        assert len(descriptor.fields) == 2
        assert descriptor.fields[0].required == True

    def test_form_validation_required_fields(self):
        """Should validate required fields."""
        fields = [
            FormField(field_name="name", field_type="text", label="Name", required=True)
        ]
        descriptor = FormDescriptor(
            descriptor_id="test-id",
            form_id="form-1",
            fields=fields
        )
        assert descriptor.fields[0].required == True


class TestProgressDescriptor:
    """Test Progress descriptor."""

    def test_create_progress_determinate(self):
        """Should create progress with percentage."""
        descriptor = ProgressDescriptor(
            descriptor_id="test-id",
            task_name="Processing",
            progress_percent=50
        )
        assert descriptor.descriptor_type == UIDescriptorType.PROGRESS
        assert descriptor.progress_percent == 50
        assert descriptor.indeterminate == False

    def test_create_progress_indeterminate(self):
        """Should create indeterminate progress."""
        descriptor = ProgressDescriptor(
            descriptor_id="test-id",
            task_name="Loading",
            progress_percent=0,
            indeterminate=True
        )
        assert descriptor.indeterminate == True

    def test_progress_percent_bounds(self):
        """Should enforce 0-100 bounds."""
        with pytest.raises(ValueError):
            ProgressDescriptor(
                descriptor_id="test-id",
                task_name="Test",
                progress_percent=150  # Invalid
            )


class TestActionDescriptor:
    """Test Action descriptor."""

    def test_create_action_button(self):
        """Should create action button."""
        descriptor = ActionDescriptor(
            descriptor_id="test-id",
            button_text="Click Me",
            action_id="action-1",
            variant="primary"
        )
        assert descriptor.descriptor_type == UIDescriptorType.ACTION
        assert descriptor.button_text == "Click Me"
        assert descriptor.disabled == False


class TestConfirmationDescriptor:
    """Test Confirmation descriptor."""

    def test_create_confirmation_dialog(self):
        """Should create confirmation dialog."""
        descriptor = ConfirmationDescriptor(
            descriptor_id="test-id",
            title="Confirm Action",
            message="Are you sure?",
            risk_level="high"
        )
        assert descriptor.descriptor_type == UIDescriptorType.CONFIRMATION
        assert descriptor.risk_level == "high"
        assert descriptor.dangerous == True


class TestVoiceDescriptor:
    """Test Voice descriptor."""

    def test_create_voice_input(self):
        """Should create voice input descriptor."""
        descriptor = VoiceDescriptor(
            descriptor_id="test-id",
            max_duration_seconds=30
        )
        assert descriptor.descriptor_type == UIDescriptorType.VOICE
        assert descriptor.max_duration_seconds == 30
        assert descriptor.auto_submit == False
```

### Step 2: Create UI agent tests

Create file `tests/integration/phase3/test_ui_agent.py`:

```python
"""Integration tests for UI DSPy agent."""

import pytest
from uuid import uuid4

from agentx.agent.dspy_agents import UIDSPyAgent
from agentx.ui.descriptors import (
    UIDescriptorType,
    MarkdownBlockDescriptor,
    CardDescriptor,
    FormDescriptor,
)


class TestUIDSPyAgent:
    """Test UI DSPy agent."""

    def test_agent_initialization(self):
        """Agent should initialize with DSPy predictors."""
        agent = UIDSPyAgent()
        assert agent.widget_selector is not None
        assert agent.card_generator is not None
        assert agent.confirmation_generator is not None

    def test_create_markdown_block(self):
        """Should create markdown block descriptor."""
        agent = UIDSPyAgent()
        descriptor = agent.create_markdown_block("# Test Content")

        assert isinstance(descriptor, MarkdownBlockDescriptor)
        assert descriptor.descriptor_type == UIDescriptorType.MARKDOWN_BLOCK
        assert descriptor.content == "# Test Content"

    def test_create_card(self):
        """Should create card descriptor."""
        agent = UIDSPyAgent()
        descriptor = agent.create_card(
            title="Test Card",
            content="Card content",
            actions=[{"action_id": "test", "label": "Click"}]
        )

        assert isinstance(descriptor, CardDescriptor)
        assert descriptor.title == "Test Card"
        assert len(descriptor.actions) == 1

    def test_create_form(self):
        """Should create form descriptor."""
        agent = UIDSPyAgent()
        fields = [
            {"field_name": "name", "field_type": "text", "label": "Name", "required": True}
        ]
        descriptor = agent.create_form(fields, title="User Info")

        assert isinstance(descriptor, FormDescriptor)
        assert descriptor.title == "User Info"
        assert len(descriptor.fields) == 1

    def test_create_progress(self):
        """Should create progress descriptor."""
        agent = UIDSPyAgent()
        descriptor = agent.create_progress(
            task_name="Loading",
            progress_percent=75
        )

        assert descriptor.descriptor_type == UIDescriptorType.PROGRESS
        assert descriptor.task_name == "Loading"
        assert descriptor.progress_percent == 75

    def test_create_action(self):
        """Should create action descriptor."""
        agent = UIDSPyAgent()
        descriptor = agent.create_action(
            button_text="Submit",
            action_id="submit-action"
        )

        assert descriptor.descriptor_type == UIDescriptorType.ACTION
        assert descriptor.button_text == "Submit"

    def test_create_confirmation(self):
        """Should create confirmation descriptor."""
        agent = UIDSPyAgent()
        descriptor = agent.create_confirmation(
            title="Delete File?",
            message="This cannot be undone",
            risk_level="high"
        )

        assert descriptor.descriptor_type == UIDescriptorType.CONFIRMATION
        assert descriptor.risk_level == "high"
        assert descriptor.dangerous == True

    @pytest.mark.skipif(
        True,  # Set to False to test with real DSPy
        reason="Requires Ollama service"
    )
    def test_select_widget_for_content(self):
        """Should select appropriate widget type."""
        agent = UIDSPyAgent()
        widget_type = agent.select_widget_for_content(
            content_type="text",
            context="Display simple text content"
        )

        assert isinstance(widget_type, str)
        assert widget_type in [
            "markdown_block",
            "card",
            "form",
            "progress",
            "action",
            "confirmation",
            "voice"
        ]


def test_get_ui_agent():
    """Test factory function."""
    from agentx.agent.dspy_agents import get_ui_agent

    agent = get_ui_agent()
    assert isinstance(agent, UIDSPyAgent)
```

### Step 3: Create WebSocket tests

Create file `tests/integration/phase3/test_websocket.py`:

```python
"""Integration tests for WebSocket functionality."""

import pytest
from fastapi.testclient import TestClient
from fastapi import WebSocket
from uuid import uuid4

from agentx.infrastructure.external.websocket_manager import (
    WebSocketManager,
    get_websocket_manager,
)
from agentx.ui.protocols.websocket import (
    WebSocketMessageType,
    WebSocketMessage,
    TokenMessage,
    DescriptorCreateMessage,
)


class TestWebSocketMessage:
    """Test WebSocket message types."""

    def test_base_message_creation(self):
        """Should create base WebSocket message."""
        message = WebSocketMessage(
            message_type=WebSocketMessageType.TOKEN,
            session_id="test-session"
        )
        assert message.message_type == WebSocketMessageType.TOKEN
        assert message.session_id == "test-session"
        assert isinstance(message.data, dict)

    def test_token_message_creation(self):
        """Should create token message."""
        message = TokenMessage(
            session_id="test-session",
            data={"token": "Hello", "is_complete": False}
        )
        assert message.message_type == WebSocketMessageType.TOKEN
        assert message.data["token"] == "Hello"

    def test_descriptor_create_message(self):
        """Should create descriptor create message."""
        descriptor_data = {
            "descriptor_id": "test-id",
            "descriptor_type": "markdown_block",
            "content": "Test"
        }
        message = DescriptorCreateMessage(
            session_id="test-session",
            data={"descriptor": descriptor_data}
        )
        assert message.message_type == WebSocketMessageType.DESCRIPTOR_CREATE
        assert message.data["descriptor"]["descriptor_id"] == "test-id"


class TestWebSocketManager:
    """Test WebSocket connection manager."""

    def test_manager_initialization(self):
        """Should initialize with empty connections."""
        manager = WebSocketManager()
        assert manager.get_total_connections() == 0
        assert manager.get_connection_count("test-session") == 0

    @pytest.mark.asyncio
    async def test_connect_and_disconnect(self):
        """Should track connections."""
        manager = WebSocketManager()
        session_id = "test-session"

        # Create mock WebSocket
        class MockWebSocket:
            def __init__(self):
                self.accepted = False
                self.sent_messages = []

            async def accept(self):
                self.accepted = True

            async def send_json(self, data):
                self.sent_messages.append(data)

        websocket = MockWebSocket()
        await manager.connect(websocket, session_id)

        assert manager.get_connection_count(session_id) == 1
        assert websocket.accepted == True

        manager.disconnect(websocket, session_id)
        assert manager.get_connection_count(session_id) == 0

    @pytest.mark.asyncio
    async def test_send_message_to_session(self):
        """Should send message to specific session."""
        manager = WebSocketManager()
        session_id = "test-session"

        class MockWebSocket:
            def __init__(self):
                self.accepted = False
                self.sent_messages = []

            async def accept(self):
                self.accepted = True

            async def send_json(self, data):
                self.sent_messages.append(data)

        websocket = MockWebSocket()
        await manager.connect(websocket, session_id)

        message = WebSocketMessage(
            message_type=WebSocketMessageType.INFO,
            session_id=session_id,
            data={"info": "test"}
        )

        await manager.send_message(message, session_id)

        assert len(websocket.sent_messages) == 1
        assert websocket.sent_messages[0]["message_type"] == "info"

    @pytest.mark.asyncio
    async def test_broadcast_to_multiple_sessions(self):
        """Should broadcast to multiple sessions."""
        manager = WebSocketManager()

        class MockWebSocket:
            def __init__(self):
                self.sent_messages = []

            async def accept(self):
                pass

            async def send_json(self, data):
                self.sent_messages.append(data)

        # Create connections for multiple sessions
        ws1 = MockWebSocket()
        ws2 = MockWebSocket()

        await manager.connect(ws1, "session-1")
        await manager.connect(ws2, "session-2")

        message = WebSocketMessage(
            message_type=WebSocketMessageType.INFO,
            session_id="broadcast-test",
            data={"info": "broadcast"}
        )

        await manager.broadcast(message, session_ids=["session-1", "session-2"])

        # Both sessions should receive message
        assert len(ws1.sent_messages) == 1
        assert len(ws2.sent_messages) == 1


def test_get_websocket_manager_singleton():
    """Test WebSocket manager singleton."""
    manager1 = get_websocket_manager()
    manager2 = get_websocket_manager()
    assert manager1 is manager2
```

### Step 4: Create test directory

```bash
mkdir -p tests/integration/phase3
```

---

## Expected Failures & Countermeasures

### Failure: Pydantic validation error in tests

**Likelihood**: Low
**Symptoms**: Test fails with ValidationError

**Countermeasures**:
1. Check all descriptor fields have valid values
2. Ensure enum values are correct
3. Verify required fields are provided
4. Check ge/le constraints (progress_percent 0-100)

**Recovery Time**: 5 minutes

---

## Retroactive Measures

### Upstream Drift Recovery

**Scenario**: T300-T303 implementations changed
**Detection**: Test assertions fail
**Action**: Update tests to match new implementations

**Recovery Time**: 15 minutes

### Downstream Impact

**Scenario**: Test file names change
**Prevention**: Test file names are not locked
**Mitigation**: Update pytest commands
**Affected Tasks**: All later test tasks

---

## Artifacts

**Files Created**:
- `tests/integration/phase3/test_ui_descriptors.py` (Descriptor tests, not locked)
- `tests/integration/phase3/test_ui_agent.py` (UI agent tests, not locked)
- `tests/integration/phase3/test_websocket.py` (WebSocket tests, not locked)

**Locked APIs**:
- None (tests are not locked)

---

## Quality Gates

**Quality Checks**:
- **Check**: All test files exist
  - Command: `ls tests/integration/phase3/*.py`
  - Expected: 3 test files
  - Required: Yes

- **Check**: Tests can be imported
  - Command: `python3 -c "import tests.integration.phase3.test_ui_descriptors; print('OK')"`
  - Expected: `OK`
  - Required: Yes

- **Check**: Tests run
  - Command: `pytest tests/integration/phase3/ -v --tb=short`
  - Expected: Tests run (DSPy tests skipped)
  - Required: Yes

---

## Notes

1. Descriptor tests verify Pydantic validation
2. UI agent tests verify descriptor creation
3. WebSocket tests use mock connections
4. DSPy-dependent tests marked with skipif
5. All tests use pytest async pattern

---

## Completion Checklist

- [ ] test_ui_descriptors.py created
- [ ] test_ui_agent.py created
- [ ] test_websocket.py created
- [ ] All tests can be imported
- [ ] Tests run with pytest
- [ ] Phase 3 complete!

---

## Phase 3 Summary

**Tasks Completed**:
- T300: Create UI Descriptor Schemas
- T301: Create UI DSPy Signatures
- T302: Create UI DSPy Agent
- T303: Create WebSocket Streaming
- T304: Create Phase 3 Integration Tests

**Phase 3 Deliverables**:
- 7 UI descriptor types (Markdown, Card, Form, Progress, Action, Confirmation, Voice)
- UI DSPy signatures for widget generation
- UI DSPy agent for creating descriptors
- WebSocket streaming endpoints
- Integration tests for UI layer

**Next Phase**: Phase 4 - LangGraph State Machines (2-3 hours)

---

**Task T304 is part of Phase 3: UI DSPy Agent + Descriptors**
**Phase 3 Status**: ✅ COMPLETE (after this task is done)
