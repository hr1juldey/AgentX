# T104: Create Phase 1 Integration Tests

**Phase**: 1
**Estimated Time**: 40 minutes
**Dependencies**: T100, T101, T102, T103
**Blocked By**: None

---

## Context

**LLD References**:
- `LLD.md` - Phase 5: Testing Strategy
- `lld/incremental_release_plan.md` - Phase 1: Test infrastructure layer

**Description**:
Creates integration tests for Phase 1 infrastructure components. These tests verify repository and adapter implementations with real services where possible.

---

## Acceptance Criteria

**Passing Criteria**:
- Test file for entity creation and state transitions
- Test file for SQLite adapter
- Test file for in-memory UI repository
- Test file for Ollama adapter (mocked, not real service)
- All tests use pytest async pattern
- Tests pass with `pytest tests/integration/phase1/`

**Verification Commands**:
```bash
cd /home/riju279/Documents/Code/XRIG/AgentX/prototypes/R013_travel_planning_stream/backend

# Verify test files exist
test -f tests/integration/phase1/test_entities.py && echo "Entity tests exist"
test -f tests/integration/phase1/test_sqlite_adapter.py && echo "SQLite tests exist"
test -f tests/integration/phase1/test_ui_repository.py && echo "UI repo tests exist"
test -f tests/integration/phase1/test_ollama_adapter.py && echo "Ollama tests exist"

# Run tests
pytest tests/integration/phase1/ -v
```

---

## Implementation Steps

### Step 1: Create test directory structure

```bash
mkdir -p tests/integration/phase1
```

### Step 2: Create entity tests

Create file `tests/integration/phase1/test_entities.py`:

```python
"""Integration tests for domain entities."""

import pytest
from datetime import datetime
from uuid import uuid4

from agentx.domain.entities.agent_session import AgentSessionEntity, SessionState
from agentx.domain.entities.ui_component import UIComponentEntity, UIComponentState, UIComponentType
from agentx.domain.entities.memory import MemoryEntity, MemoryType
from agentx.domain.entities.user import UserEntity


class TestAgentSessionEntity:
    """Test AgentSession entity behavior."""

    def test_create_session_has_initializing_state(self):
        """Session should start in INITIALIZING state."""
        session = AgentSessionEntity.create("test_user_hash")
        assert session.state == SessionState.INITIALIZING
        assert session.user_id == "test_user_hash"
        assert session.is_active() == False

    def test_pause_transitions_to_paused(self):
        """Session can transition from ACTIVE to PAUSED."""
        session = AgentSessionEntity.create("test_user_hash")
        session.state = SessionState.ACTIVE
        session.pause()
        assert session.state == SessionState.PAUSED

    def test_pause_fails_from_non_active(self):
        """Cannot pause session that is not ACTIVE."""
        session = AgentSessionEntity.create("test_user_hash")
        with pytest.raises(ValueError, match="Cannot pause"):
            session.pause()

    def test_resume_transitions_to_active(self):
        """Session can transition from PAUSED to ACTIVE."""
        session = AgentSessionEntity.create("test_user_hash")
        session.state = SessionState.PAUSED
        session.resume()
        assert session.state == SessionState.ACTIVE

    def test_close_transitions_to_closed(self):
        """Session can transition to CLOSED from any state."""
        session = AgentSessionEntity.create("test_user_hash")
        session.state = SessionState.ACTIVE
        session.close()
        assert session.state == SessionState.CLOSED

    def test_close_idempotent(self):
        """Closing an already closed session is safe."""
        session = AgentSessionEntity.create("test_user_hash")
        session.close()
        session.close()  # Should not raise
        assert session.state == SessionState.CLOSED

    def test_update_activity_updates_timestamp(self):
        """Last activity timestamp can be updated."""
        session = AgentSessionEntity.create("test_user_hash")
        old_timestamp = session.last_activity_at
        session.update_activity()
        assert session.last_activity_at >= old_timestamp


class TestUIComponentEntity:
    """Test UIComponent entity behavior."""

    def test_create_component_has_creating_state(self):
        """Component should start in CREATING state."""
        component = UIComponentEntity.create(
            session_id=uuid4(),
            component_type=UIComponentType.CARD,
            descriptor={"title": "Test"}
        )
        assert component.state == UIComponentState.CREATING
        assert component.is_visible() == False

    def test_mark_created_transitions_state(self):
        """Component can transition to CREATED."""
        component = UIComponentEntity.create(
            session_id=uuid4(),
            component_type=UIComponentType.MARKDOWN_BLOCK,
            descriptor={"content": "Test"}
        )
        component.mark_created()
        assert component.state == UIComponentState.CREATED
        assert component.is_visible() == True

    def test_dismiss_removes_component(self):
        """Component can be dismissed."""
        component = UIComponentEntity.create(
            session_id=uuid4(),
            component_type=UIComponentType.PROGRESS,
            descriptor={"task": "Test"}
        )
        component.mark_created()
        component.dismiss()
        assert component.state == UIComponentState.DISMISSED
        assert component.is_visible() == False

    def test_update_descriptor_updates_state(self):
        """Component descriptor can be updated."""
        component = UIComponentEntity.create(
            session_id=uuid4(),
            component_type=UIComponentType.CARD,
            descriptor={"title": "Old"}
        )
        component.mark_created()
        component.update_descriptor({"title": "New"})
        assert component.state == UIComponentState.UPDATING

    def test_is_dismissible_prevents_dismiss(self):
        """CREATING and DISMISSED components are not dismissible."""
        component = UIComponentEntity.create(
            session_id=uuid4(),
            component_type=UIComponentType.ACTION,
            descriptor={"action": "test"}
        )
        assert component.is_dismissible() == False

        component.dismiss()
        assert component.is_dismissible() == False


class TestMemoryEntity:
    """Test Memory entity behavior."""

    def test_create_memory_has_defaults(self):
        """Memory should be created with default values."""
        memory = MemoryEntity.create(
            user_id="test_user_hash",
            content="Test memory content"
        )
        assert memory.content == "Test memory content"
        assert memory.memory_type == MemoryType.EPISODIC
        assert memory.is_valid == True
        assert memory.embedding is None

    def test_set_embedding_stores_vector(self):
        """Memory can store vector embedding."""
        memory = MemoryEntity.create(user_id="test_user", content="Test")
        embedding = [0.1, 0.2, 0.3]
        memory.set_embedding(embedding)
        assert memory.embedding == embedding

    def test_invalidate_marks_memory_invalid(self):
        """Memory can be invalidated."""
        memory = MemoryEntity.create(user_id="test_user", content="Test")
        memory.invalidate()
        assert memory.is_valid == False

    def test_access_updates_timestamp(self):
        """Last accessed timestamp can be updated."""
        memory = MemoryEntity.create(user_id="test_user", content="Test")
        old_timestamp = memory.last_accessed_at
        memory.access()
        assert memory.last_accessed_at >= old_timestamp

    def test_ttl_expiration(self):
        """Memory with TTL should expire."""
        memory = MemoryEntity.create(user_id="test_user", content="Test")
        memory.ttl_seconds = 1  # 1 second TTL
        memory.created_at = datetime(2020, 1, 1)  # Old timestamp
        assert memory.is_expired() == True

    def test_no_ttl_never_expires(self):
        """Memory without TTL should not expire."""
        memory = MemoryEntity.create(user_id="test_user", content="Test")
        assert memory.is_expired() == False


class TestUserEntity:
    """Test User entity behavior."""

    def test_create_user_hashes_id(self):
        """User ID should be SHA-256 hashed."""
        user = UserEntity.create("raw_user_id_123")
        assert user.user_id != "raw_user_id_123"  # Should be hashed
        assert len(user.user_id) == 64  # SHA-256 hex length

    def test_preferences_can_be_set(self):
        """User preferences can be stored."""
        user = UserEntity.create("test_user")
        user.set_preference("theme", "dark")
        assert user.get_preference("theme") == "dark"

    def test_get_preference_returns_default(self):
        """Missing preference returns default value."""
        user = UserEntity.create("test_user")
        assert user.get_preference("missing", "default") == "default"

    def test_update_last_seen_updates_timestamp(self):
        """Last seen timestamp can be updated."""
        user = UserEntity.create("test_user")
        old_timestamp = user.last_seen_at
        user.update_last_seen()
        assert user.last_seen_at >= old_timestamp
```


### Step 3: Create SQLite adapter tests

Create file `tests/integration/phase1/test_sqlite_adapter.py`:

```python
"""Integration tests for SQLite session adapter."""

import pytest
import tempfile
import os
from uuid import uuid4

from agentx.infrastructure.external.sqlite_session_adapter import SQLiteSessionAdapter
from agentx.domain.entities.agent_session import AgentSessionEntity, SessionState


@pytest.fixture
def temp_db_path():
    """Create temporary database file."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    # Cleanup
    if os.path.exists(path):
        os.remove(path)


@pytest.fixture
def sqlite_adapter(temp_db_path):
    """Create SQLite adapter with temp database."""
    return SQLiteSessionAdapter(db_path=temp_db_path)


@pytest.fixture
def test_session():
    """Create test session entity."""
    return AgentSessionEntity.create("test_user_hash")


class TestSQLiteSessionAdapter:
    """Test SQLite adapter operations."""

    @pytest.mark.asyncio
    async def test_create_then_get_returns_same_session(self, sqlite_adapter, test_session):
        """Created session should be retrievable."""
        created = await sqlite_adapter.create(test_session)
        retrieved = await sqlite_adapter.get_by_id(test_session.session_id)

        assert retrieved is not None
        assert retrieved.session_id == created.session_id
        assert retrieved.user_id == created.user_id
        assert retrieved.state == created.state

    @pytest.mark.asyncio
    async def test_get_by_id_returns_none_for_nonexistent(self, sqlite_adapter):
        """Non-existent session should return None."""
        result = await sqlite_adapter.get_by_id(uuid4())
        assert result is None

    @pytest.mark.asyncio
    async def test_update_persists_changes(self, sqlite_adapter, test_session):
        """Updated session should persist changes."""
        await sqlite_adapter.create(test_session)

        test_session.state = SessionState.ACTIVE
        updated = await sqlite_adapter.update(test_session)

        retrieved = await sqlite_adapter.get_by_id(test_session.session_id)
        assert retrieved.state == SessionState.ACTIVE

    @pytest.mark.asyncio
    async def test_delete_removes_session(self, sqlite_adapter, test_session):
        """Deleted session should be removed."""
        await sqlite_adapter.create(test_session)
        deleted = await sqlite_adapter.delete(test_session.session_id)

        assert deleted == True
        result = await sqlite_adapter.get_by_id(test_session.session_id)
        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_user_id_filters_correctly(self, sqlite_adapter):
        """Should return all sessions for a user."""
        user1_hash = "user1_hash"
        user2_hash = "user2_hash"

        session1 = AgentSessionEntity.create(user1_hash)
        session2 = AgentSessionEntity.create(user1_hash)
        session3 = AgentSessionEntity.create(user2_hash)

        await sqlite_adapter.create(session1)
        await sqlite_adapter.create(session2)
        await sqlite_adapter.create(session3)

        user1_sessions = await sqlite_adapter.get_by_user_id(user1_hash)
        user2_sessions = await sqlite_adapter.get_by_user_id(user2_hash)

        assert len(user1_sessions) == 2
        assert len(user2_sessions) == 1

    @pytest.mark.asyncio
    async def test_get_active_sessions_filters_by_state(self, sqlite_adapter):
        """Should return only active sessions."""
        user_hash = "test_user_hash"

        active_session = AgentSessionEntity.create(user_hash)
        active_session.state = SessionState.ACTIVE
        closed_session = AgentSessionEntity.create(user_hash)
        closed_session.state = SessionState.CLOSED

        await sqlite_adapter.create(active_session)
        await sqlite_adapter.create(closed_session)

        active = await sqlite_adapter.get_active_sessions(user_hash)

        assert len(active) == 1
        assert active[0].session_id == active_session.session_id

    @pytest.mark.asyncio
    async def test_exists_returns_true_for_existing(self, sqlite_adapter, test_session):
        """exists() should return True for existing sessions."""
        await sqlite_adapter.create(test_session)
        assert await sqlite_adapter.exists(test_session.session_id) == True

    @pytest.mark.asyncio
    async def test_exists_returns_false_for_nonexistent(self, sqlite_adapter):
        """exists() should return False for non-existent sessions."""
        assert await sqlite_adapter.exists(uuid4()) == False


class TestSQLiteSessionAdapterPersistence:
    """Test SQLite persistence across instances."""

    @pytest.mark.asyncio
    async def test_data_persists_across_adapter_instances(self, temp_db_path):
        """Data should persist when creating new adapter instance."""
        session = AgentSessionEntity.create("test_user")

        # Create with first adapter instance
        adapter1 = SQLiteSessionAdapter(db_path=temp_db_path)
        await adapter1.create(session)

        # Retrieve with second adapter instance
        adapter2 = SQLiteSessionAdapter(db_path=temp_db_path)
        retrieved = await adapter2.get_by_id(session.session_id)

        assert retrieved is not None
        assert retrieved.session_id == session.session_id
```


### Step 4: Create in-memory UI repository tests

Create file `tests/integration/phase1/test_ui_repository.py`:

```python
"""Integration tests for in-memory UI component repository."""

import pytest
from uuid import uuid4

from agentx.infrastructure.external.in_memory_ui_repository import InMemoryUIComponentRepository
from agentx.domain.entities.ui_component import UIComponentEntity, UIComponentType, UIComponentState


@pytest.fixture
def ui_repository():
    """Create in-memory UI repository."""
    return InMemoryUIComponentRepository()


@pytest.fixture
def test_session_id():
    """Create test session ID."""
    return uuid4()


@pytest.fixture
def test_component(test_session_id):
    """Create test UI component."""
    return UIComponentEntity.create(
        session_id=test_session_id,
        component_type=UIComponentType.CARD,
        descriptor={"title": "Test Card"}
    )


class TestInMemoryUIComponentRepository:
    """Test in-memory UI repository operations."""

    @pytest.mark.asyncio
    async def test_create_then_get_returns_same_component(self, ui_repository, test_component):
        """Created component should be retrievable."""
        created = await ui_repository.create(test_component)
        retrieved = await ui_repository.get_by_id(test_component.component_id)

        assert retrieved is not None
        assert retrieved.component_id == created.component_id
        assert retrieved.component_type == UIComponentType.CARD

    @pytest.mark.asyncio
    async def test_get_by_id_returns_none_for_nonexistent(self, ui_repository):
        """Non-existent component should return None."""
        result = await ui_repository.get_by_id(uuid4())
        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_session_id_filters_correctly(
        self, ui_repository, test_session_id
    ):
        """Should return all components for a session."""
        other_session_id = uuid4()

        comp1 = UIComponentEntity.create(test_session_id, UIComponentType.CARD, {"title": "1"})
        comp2 = UIComponentEntity.create(test_session_id, UIComponentType.MARKDOWN_BLOCK, {"content": "2"})
        comp3 = UIComponentEntity.create(other_session_id, UIComponentType.PROGRESS, {"task": "3"})

        await ui_repository.create(comp1)
        await ui_repository.create(comp2)
        await ui_repository.create(comp3)

        session_components = await ui_repository.get_by_session_id(test_session_id)
        assert len(session_components) == 2

    @pytest.mark.asyncio
    async def test_get_visible_components_filters_by_state(
        self, ui_repository, test_session_id
    ):
        """Should return only visible (CREATED, UPDATING) components."""
        visible_comp = UIComponentEntity.create(test_session_id, UIComponentType.CARD, {"title": "Visible"})
        visible_comp.mark_created()

        dismissed_comp = UIComponentEntity.create(test_session_id, UIComponentType.CARD, {"title": "Dismissed"})
        dismissed_comp.dismiss()

        await ui_repository.create(visible_comp)
        await ui_repository.create(dismissed_comp)

        visible = await ui_repository.get_visible_components(test_session_id)
        assert len(visible) == 1
        assert visible[0].component_id == visible_comp.component_id

    @pytest.mark.asyncio
    async def test_update_persists_changes(self, ui_repository, test_component):
        """Updated component should persist changes."""
        await ui_repository.create(test_component)
        test_component.mark_created()

        updated = await ui_repository.update(test_component)
        retrieved = await ui_repository.get_by_id(test_component.component_id)

        assert retrieved.state == UIComponentState.CREATED

    @pytest.mark.asyncio
    async def test_dismiss_marks_component_dismissed(self, ui_repository, test_component):
        """Dismissed component should be marked."""
        await ui_repository.create(test_component)
        test_component.mark_created()

        dismissed = await ui_repository.dismiss(test_component.component_id)
        assert dismissed == True

        retrieved = await ui_repository.get_by_id(test_component.component_id)
        assert retrieved.state == UIComponentState.DISMISSED

    @pytest.mark.asyncio
    async def test_dismiss_by_session_dismisses_all(self, ui_repository, test_session_id):
        """Should dismiss all dismissible components for session."""
        comp1 = UIComponentEntity.create(test_session_id, UIComponentType.CARD, {"title": "1"})
        comp1.mark_created()

        comp2 = UIComponentEntity.create(test_session_id, UIComponentType.CARD, {"title": "2"})
        comp2.mark_created()

        comp3 = UIComponentEntity.create(test_session_id, UIComponentType.FORM, {"fields": []})
        comp3.mark_created()

        await ui_repository.create(comp1)
        await ui_repository.create(comp2)
        await ui_repository.create(comp3)

        count = await ui_repository.dismiss_by_session(test_session_id)
        assert count == 3

    @pytest.mark.asyncio
    async def test_delete_removes_component(self, ui_repository, test_component):
        """Deleted component should be removed."""
        await ui_repository.create(test_component)
        deleted = await ui_repository.delete(test_component.component_id)

        assert deleted == True
        result = await ui_repository.get_by_id(test_component.component_id)
        assert result is None
```


### Step 5: Create Ollama adapter tests (mocked)

Create file `tests/integration/phase1/test_ollama_adapter.py`:

```python
"""Integration tests for Ollama LLM adapter (with mocking)."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from httpx import Response

from agentx.infrastructure.external.ollama_llm import OllamaLLMAdapter, ModelInfo


@pytest.fixture
def ollama_adapter():
    """Create Ollama adapter."""
    return OllamaLLMAdapter(
        base_url="http://localhost:11434",
        model="gemma3:4b",
        timeout_seconds=30
    )


class TestOllamaLLMAdapter:
    """Test Ollama adapter behavior."""

    def test_adapter_initialization(self, ollama_adapter):
        """Adapter should initialize with correct parameters."""
        assert ollama_adapter.base_url == "http://localhost:11434"
        assert ollama_adapter.model == "gemma3:4b"
        assert ollama_adapter.timeout == 30
        assert repr(ollama_adapter) == "OllamaLLMAdapter(base_url=http://localhost:11434, model=gemma3:4b)"

    @pytest.mark.asyncio
    async def test_health_check_success(self, ollama_adapter):
        """health_check() should return True when Ollama is accessible."""
        with patch.object(ollama_adapter.client, "get") as mock_get:
            mock_response = Mock()
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            result = await ollama_adapter.health_check()
            assert result == True

    @pytest.mark.asyncio
    async def test_health_check_failure(self, ollama_adapter):
        """health_check() should return False on connection error."""
        with patch.object(ollama_adapter.client, "get", side_effect=Exception("Connection refused")):
            result = await ollama_adapter.health_check()
            assert result == False

    @pytest.mark.asyncio
    async def test_generate_response(self, ollama_adapter):
        """generate_response() should return LLM response."""
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {
            "message": {
                "content": "42"
            }
        }

        with patch.object(ollama_adapter.client, "post", return_value=mock_response):
            result = await ollama_adapter.generate_response(
                prompt="What is 6*7?",
                context=[],
                temperature=0.7,
                max_tokens=100
            )
            assert result == "42"

    @pytest.mark.asyncio
    async def test_stream_response(self, ollama_adapter):
        """stream_response() should yield text chunks."""
        # Mock streaming response
        mock_chunks = [
            '{"message": {"content": "Hello"}}',
            '{"message": {"content": " world"}}',
            '{"message": {"content": "!"}}',
        ]

        async def mock_aiter_lines():
            for chunk in mock_chunks:
                yield chunk

        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.aiter_lines = mock_aiter_lines

        async def mock_stream_post(*args, **kwargs):
            class ContextManager:
                async def __aenter__(self):
                    return mock_response
                async def __aexit__(self, *args):
                    pass
            return ContextManager()

        with patch.object(ollama_adapter.client, "stream", side_effect=mock_stream_post):
            chunks = []
            async for chunk in ollama_adapter.stream_response(
                prompt="Say hello",
                context=[]
            ):
                chunks.append(chunk)

            assert chunks == ["Hello", " world", "!"]

    def test_model_info(self, ollama_adapter):
        """ModelInfo should represent model details."""
        info = ModelInfo(
            name="gemma3:4b",
            base_url="http://localhost:11434",
            context_size=2048,
            supports_streaming=True
        )
        assert info.name == "gemma3:4b"
        assert info.supports_streaming == True


class TestOllamaAdapterIntegration:
    """Integration tests (require actual Ollama server)."""

    @pytest.mark.skipif(
        True,  # Set to False to test with real Ollama
        reason="Requires Ollama server running"
    )
    @pytest.mark.asyncio
    async def test_real_ollama_health_check(self):
        """Test with real Ollama server."""
        adapter = OllamaLLMAdapter(
            base_url="http://localhost:11434",
            model="gemma3:4b"
        )
        result = await adapter.health_check()
        assert result == True

    @pytest.mark.skipif(
        True,  # Set to False to test with real Ollama
        reason="Requires Ollama server and model"
    )
    @pytest.mark.asyncio
    async def test_real_ollama_generate(self):
        """Test generation with real Ollama."""
        adapter = OllamaLLMAdapter(
            base_url="http://localhost:11434",
            model="gemma3:4b"
        )
        result = await adapter.generate_response(
            prompt="Say 'test response'",
            context=[]
        )
        assert isinstance(result, str)
        assert len(result) > 0
```


### Step 6: Update conftest.py with Phase 1 fixtures

Update file `tests/conftest.py` (created in T006, add Phase 1 fixtures):

```python
"""Pytest configuration and fixtures."""

import pytest
import tempfile
import os
from uuid import uuid4

from agentx.main import create_app
from agentx.core.config import Settings, set_settings
from agentx.infrastructure.external.sqlite_session_adapter import SQLiteSessionAdapter
from agentx.infrastructure.external.in_memory_ui_repository import InMemoryUIComponentRepository
from agentx.domain.entities.agent_session import AgentSessionEntity


@pytest.fixture
def app():
    """FastAPI app fixture for testing."""
    return create_app()


@pytest.fixture
def settings():
    """Settings fixture for testing."""
    test_settings = Settings(
        app_name="AGENTX-Test",
        environment="testing",
        port=8001,
        redis_host="localhost",
        redis_port=6379,
        qdrant_url="http://localhost:6333",
        sqlite_db_path=":memory:"  # In-memory for testing
    )
    set_settings(test_settings)
    return test_settings


@pytest.fixture
def temp_db_path():
    """Create temporary database file."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    # Cleanup
    if os.path.exists(path):
        os.remove(path)


@pytest.fixture
def test_session():
    """Create test agent session."""
    return AgentSessionEntity.create("test_user_hash")


@pytest.fixture
def test_session_id():
    """Create test session ID."""
    return uuid4()


@pytest.fixture
def sqlite_adapter(temp_db_path):
    """Create SQLite adapter with temp database."""
    return SQLiteSessionAdapter(db_path=temp_db_path)


@pytest.fixture
def ui_repository():
    """Create in-memory UI repository."""
    return InMemoryUIComponentRepository()
```

---

## Expected Failures & Countermeasures

### Failure: Import errors for entities/adapters

**Likelihood**: Low (if T100-T102 complete)
**Symptoms**: `ModuleNotFoundError` when running tests

**Countermeasures**:
1. Ensure T100 (Entities) is complete
2. Ensure T101 (Repository Implementations) is complete
3. Ensure T102 (Ollama Adapter) is complete
4. Check all imports use absolute paths

**Recovery Time**: 5 minutes

### Failure: SQLite file permission error

**Likelihood**: Low
**Symptoms**: `PermissionError` when creating temp database

**Countermeasures**:
1. Use `/tmp` directory for temp files
2. Check write permissions on test directory
3. Use `:memory:` SQLite database as fallback

**Recovery Time**: 2 minutes

### Failure: Pytest not installed

**Likelihood**: Medium
**Symptoms**: `command not found: pytest`

**Countermeasures**:
1. Install pytest: `uv pip install pytest pytest-asyncio`
2. Or use from requirements.txt (T009)
3. Verify pytest is in PATH

**Recovery Time**: 3 minutes

---

## Retroactive Measures

### Upstream Drift Recovery

**Scenario**: T100-T103 implementations changed
**Detection**: Tests fail with AttributeError, wrong method signatures
**Action**: Update test assertions to match new implementations
**Recovery Time**: 10 minutes

**Scenario**: Entity/adapters renamed
**Detection**: Import errors in test files
**Action**: Update imports in test files
**Recovery Time**: 5 minutes

### Downstream Impact

**Scenario**: Test fixtures renamed
**Prevention**: Fixture names are not locked (can change)
**Mitigation**: Update tests using renamed fixtures
**Affected Tasks**: All later test tasks (T204, T304, etc.)

---

## Artifacts

**Files Created**:
- `tests/integration/phase1/test_entities.py` (Entity tests, not locked)
- `tests/integration/phase1/test_sqlite_adapter.py` (SQLite tests, not locked)
- `tests/integration/phase1/test_ui_repository.py` (UI repo tests, not locked)
- `tests/integration/phase1/test_ollama_adapter.py` (Ollama tests, not locked)
- `tests/conftest.py` (Updated with Phase 1 fixtures)

**Locked APIs**:
- None (tests are not locked)

---

## Quality Gates

**Quality Checks**:
- **Check**: All test files exist
  - Command: `ls tests/integration/phase1/*.py`
  - Expected: 4 test files
  - Required: Yes

- **Check**: Tests can be imported
  - Command: `python3 -c "import tests.integration.phase1.test_entities; print('OK')"`
  - Expected: `OK`
  - Required: Yes

- **Check**: Tests run (may fail on real service dependencies)
  - Command: `pytest tests/integration/phase1/ -v --tb=short`
  - Expected: Tests run (some may be skipped or fail on missing services)
  - Required: Yes

---

## Notes

1. Entity tests verify business logic (state transitions)
2. SQLite adapter tests use temp database files
3. In-memory UI repository tests verify session-scoped behavior
4. Ollama adapter tests are mocked (no real service required)
5. Optional integration tests for real Ollama (marked with skipif)
6. All tests use pytest async pattern (asyncio_mode=auto)
7. Fixtures defined in conftest.py for reusability

---

## Completion Checklist

- [ ] test_entities.py created with all entity tests
- [ ] test_sqlite_adapter.py created with CRUD tests
- [ ] test_ui_repository.py created with repository tests
- [ ] test_ollama_adapter.py created with mocked tests
- [ ] conftest.py updated with Phase 1 fixtures
- [ ] All test files can be imported
- [ ] Tests run with pytest
- [ ] Phase 1 complete!

---

## Phase 1 Summary

**Tasks Completed**:
- T100: Create Domain Entities
- T101: Create Repository Implementations
- T102: Create Ollama LLM Adapter
- T103: Update Dependency Injection Container
- T104: Create Phase 1 Integration Tests

**Phase 1 Deliverables**:
- All domain entities with business logic
- Qdrant, Redis, SQLite, In-Memory repositories
- Ollama LLM adapter with streaming support
- Updated DI container with all Phase 1 adapters
- Integration tests for infrastructure layer

**Next Phase**: Phase 2 - Main DSPy Agent (2-3 hours)

---

**Task T104 is part of Phase 1: Domain + Infrastructure**
**Phase 1 Status**: ✅ COMPLETE (after this task is done)
