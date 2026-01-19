# T501: Create RAG Agent

**Phase**: 5
**Estimated Time**: 40 minutes
**Dependencies**: T001, T200, T500
**Blocked By**: None

---

## Context

**LLD References**:
- `lld/agent_runtime.md` - RAG agent definition
- `lld/incremental_release_plan.md` - Phase 5: RAG agent

**Description**:
Creates RAG (Retrieval-Augmented Generation) agent that retrieves context from memory before answering queries.

---

## Acceptance Criteria

**Passing Criteria**:
- agent/dspy_agents/rag_agent.py exists
- Uses memory repository for context retrieval
- Has retrieve_context() method
- Has query_with_context() method
- Can be imported

**Verification Commands**:
```bash
cd /home/riju279/Documents/Code/XRIG/AgentX/prototypes/R013_travel_planning_stream/backend

# Verify file exists
test -f agentx/agent/dspy_agents/rag_agent.py && echo "RAG agent exists"

# Verify import works
python3 -c "from agentx.agent.dspy_agents.rag_agent import RAGAgent; print('Import OK')"
```

---

## Implementation Steps

### Step 1: Create RAG agent

Create file `agentx/agent/dspy_agents/rag_agent.py`:

```python
"""RAG (Retrieval-Augmented Generation) agent."""

import dspy
from typing import List, Dict, Any, Optional
from uuid import UUID

from agentx.agent.dspy_signatures import MainAgentSignature
from agentx.domain.repositories.memory_repository import MemoryRepository
from agentx.core.dependencies import get_memory_repository


class RAGAgent(dspy.Module):
    """RAG agent for context-aware queries.

    This agent retrieves relevant memories before answering queries.
    It follows the agentic RAG pattern from the LLD.

    Example:
        >>> agent = RAGAgent()
        >>> result = await agent.query(user_id="user_hash", query="What did I work on yesterday?")
    """

    def __init__(
        self,
        top_k: int = 5,
        similarity_threshold: float = 0.7
    ):
        """Initialize RAG agent.

        Args:
            top_k: Number of memories to retrieve
            similarity_threshold: Minimum similarity score
        """
        super().__init__()
        self.top_k = top_k
        self.similarity_threshold = similarity_threshold

        # Main agent for answering
        self.main_agent = dspy.Predict(MainAgentSignature)

        # Get memory repository
        self.memory_repository: MemoryRepository = get_memory_repository()

    async def retrieve_context(
        self,
        query: str,
        user_id: str
    ) -> str:
        """Retrieve relevant context from memory.

        Args:
            query: Search query
            user_id: User identifier (SHA-256 hash)

        Returns:
            Formatted context string
        """
        try:
            # Search memories
            results = await self.memory_repository.search_memories(
                query=query,
                user_id=user_id,
                limit=self.top_k
            )

            # Filter by similarity threshold
            relevant = [
                r for r in results
                if r.get("score", 0) >= self.similarity_threshold
            ]

            if not relevant:
                return ""

            # Format context
            context_parts = []
            for i, result in enumerate(relevant, 1):
                content = result.get("content", "")
                score = result.get("score", 0)
                context_parts.append(f"[Memory {i}] (relevance: {score:.2f}): {content}")

            return "\\n\\n".join(context_parts)

        except Exception as e:
            # Log error but don't fail
            return f"Error retrieving context: {str(e)}"

    async def query(
        self,
        user_id: str,
        query: str,
        conversation_history: str = ""
    ) -> Dict[str, Any]:
        """Query with RAG context.

        Args:
            user_id: User identifier (SHA-256 hash)
            query: User's query
            conversation_history: Previous conversation

        Returns:
            Dictionary with answer, context, confidence
        """
        # Step 1: Retrieve context
        retrieved_context = await self.retrieve_context(query, user_id)

        # Step 2: Generate answer with context
        prediction = self.main_agent(
            user_query=query,
            conversation_history=conversation_history,
            retrieved_context=retrieved_context
        )

        return {
            "final_answer": prediction.final_answer,
            "reasoning": prediction.reasoning,
            "retrieved_context": retrieved_context,
            "context_used": len(retrieved_context) > 0
        }

    def is_confident(self, prediction: Dict[str, Any]) -> bool:
        """Check if RAG answer is confident.

        Args:
            prediction: Prediction from query()

        Returns:
            True if context was used and answer is confident
        """
        return prediction.get("context_used", False)


def get_rag_agent() -> RAGAgent:
    """Get or create RAG agent instance.

    Returns:
        RAGAgent instance
    """
    return RAGAgent()
```

### Step 2: Update dspy_agents __init__.py

Update file `agentx/agent/dspy_agents/__init__.py`:

```python
"""DSPy agents for AGENTX."""

from agentx.agent.dspy_agents.main_react_agent import (
    MainDSPyReActAgent,
    AgentFactory,
    get_main_agent,
)
from agentx.agent.dspy_agents.ui_dspy_agent import (
    UIDSPyAgent,
    get_ui_agent,
)
from agentx.agent.dspy_agents.rag_agent import (
    RAGAgent,
    get_rag_agent,
)

__all__ = [
    "MainDSPyReActAgent",
    "AgentFactory",
    "get_main_agent",
    "UIDSPyAgent",
    "get_ui_agent",
    "RAGAgent",
    "get_rag_agent",
]
```

---

## Expected Failures & Countermeasures

### Failure: Memory repository not initialized

**Likelihood**: Medium
**Symptoms**: `AttributeError: 'NoneType' object has no attribute 'search_memories'`

**Countermeasures**:
1. Ensure T500 (Memory Repository) is complete
2. Check dependencies.py has get_memory_repository()
3. Verify Qdrant adapter is returned

**Recovery Time**: 5 minutes

---

## Retroactive Measures

### Upstream Drift Recovery

**Scenario**: T500 memory repository changed
**Detection**: Repository method signatures changed
**Action**: Update RAG agent to use new repository interface

**Recovery Time**: 10 minutes

### Downstream Impact

**Scenario**: RAGAgent class name changes
**Prevention**: Class name is LOCKED
**Mitigation**: Update all use sites
**Affected Tasks**: T502 (Memory Consolidation), T503 (Tests)

---

## Artifacts

**Files Created**:
- `agentx/agent/dspy_agents/rag_agent.py` (RAG agent, LOCKED)

**Files Modified**:
- `agentx/agent/dspy_agents/__init__.py` (Add exports)

**Locked APIs**:
- RAGAgent class name
- All method signatures
- get_rag_agent() function signature

---

## Quality Gates

**Quality Checks**:
- **Check**: RAG agent file exists
  - Command: `test -f agentx/agent/dspy_agents/rag_agent.py && echo "OK"`
  - Expected: `OK`
  - Required: Yes

- **Check**: Can be imported
  - Command: `python3 -c "from agentx.agent.dspy_agents.rag_agent import RAGAgent; print('OK')"`
  - Expected: `OK`
  - Required: Yes

---

## Notes

1. Agentic RAG pattern (LLM decides if context is needed)
2. Retrieves top-k memories by semantic similarity
3. Filters by similarity threshold
4. Includes memory metadata in context
5. Falls back gracefully if retrieval fails
6. Can be used standalone or composed with main agent

---

## Completion Checklist

- [ ] rag_agent.py created with RAGAgent class
- [ ] retrieve_context() method implemented
- [ ] query() method implemented with full RAG flow
- [ ] is_confident() helper method
- [ ] get_rag_agent() factory function
- [ ] __init__.py updated
- [ ] All imports work
- [ ] Ready for T502 (Memory Consolidation)

---

**Task T501 is part of Phase 5: Memory + RAG**
**Locked APIs**: RAGAgent class name, method signatures
