# Spec: Checkpointers Integration

**Domain**: agent-runtime
**Generated**: 2026-02-02
**Status**: Draft

---

## 1. Purpose

Define the LangGraph checkpointer integration for graph memory (procedural routing).

**Success Criteria**:
- PostgresSaver configured for graph memory
- Graph compiled with checkpointer
- Time-travel debugging enabled
- Thread-based state isolation

---

## 2. Scope

### In Scope

- Checkpointer configuration
- Graph compilation with checkpointer
- Time-travel debugging utilities
- Thread ID management

### Out of Scope

- State accumulation (covered by state-accumulation spec)
- Store integration (covered by agent-memory-store spec)

---

## 3. Requirements

### 3.1 Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-CI-001 | Graph MUST be compiled with checkpointer | Must |
| FR-CI-002 | MUST support PostgresSaver backend | Must |
| FR-CI-003 | MUST enable time-travel debugging | Should |
| FR-CI-004 | MUST use thread_id for isolation | Must |

---

## 4. API Contract

```python
# infrastructure/memory/checkpointer_config.py
from langgraph.checkpoint.postgres import PostgresSaver

def get_checkpointer():
    """Get checkpointer for graph memory.

    Returns:
        PostgresSaver: Configured checkpointer
    """
    DB_URI = "postgresql://postgres:postgres@localhost:5442/postgres?sslmode=disable"
    return PostgresSaver.from_conn_string(DB_URI)

# agent/graph/dynamic_agent_graph.py
from langgraph.graph import StateGraph

builder = StateGraph(AgentState)

# ... add nodes and edges ...

# Compile with checkpointer (graph memory)
checkpointer = get_checkpointer()
dynamic_agent = builder.compile(
    checkpointer=checkpointer,  # ← Graph memory (procedural)
)

# Invocation with thread_id
config = {"configurable": {"thread_id": thread_id}}
result = await dynamic_agent.ainvoke(state, config=config)
```

---

## 5. Time-Travel Debugging

```python
# application/debugging/time_travel.py

def inspect_past_states(thread_id: str) -> list[dict]:
    """Get all past states for a thread.

    Args:
        thread_id: Thread identifier

    Returns:
        list[dict]: List of historical states
    """
    config = {"configurable": {"thread_id": thread_id}}

    # Get state history
    history = []
    for checkpoint in dynamic_agent.get_state_history(config):
        history.append({
            "step": checkpoint.step,
            "timestamp": checkpoint.timestamp,
            "values": checkpoint.values,
        })

    return history

def replay_from_checkpoint(thread_id: str, step: int):
    """Replay execution from a specific checkpoint.

    Args:
        thread_id: Thread identifier
        step: Checkpoint step to replay from
    """
    config = {"configurable": {"thread_id": thread_id}}

    # Get past state
    past_state = dynamic_agent.get_state(config, step)

    # Resume from past state
    result = await dynamic_agent.ainvoke(
        past_state.values,
        config=config,
    )
```

---

## 6. Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| BR-CI-001 | Thread isolation | thread_id required |
| BR-CI-002 | Time-trail enabled | get_state_history() works |
| BR-CI-003 | Checkpoint persistence | Postgres backend |

---

## 7. Acceptance Criteria

- [ ] PostgresSaver configured
- [ ] Graph compiled with checkpointer
- [ ] Thread ID used for isolation
- [ ] get_state_history() works
- [ ] Can replay from checkpoint
- [ ] Ruff and pyrefly checks pass

---

## 8. Test Scenarios

| Operation | Expected Result |
|-----------|-----------------|
| Invoke with thread_id | State persisted to Postgres |
| Get state history | List of checkpoints returned |
| Replay from step | Execution resumes from checkpoint |

---

**Next**: See `state-accumulation/spec.md` for accumulated state fields.
