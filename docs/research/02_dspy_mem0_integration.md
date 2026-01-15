# DSPy + Mem0AI Integration Guide

## Overview

This guide covers building a memory-enabled AI agent using DSPy's ReAct framework combined with Mem0's persistent memory capabilities.

## Architecture

### DSPy Framework
DSPy provides a programmatic interface for LLM interactions:
- **Signatures** - Declarative input/output specifications
- **Modules** - Prompting strategies (Predict, ChainOfThought, ReAct)
- **Optimizers** - Automatic prompt tuning (MIPROv2, BootstrapFewShot)
- **Tools** - Function calling and external integrations

### Mem0 Memory System
Mem0 adds persistent memory to AI agents:
- **Episodic Memory** - Conversation history and events
- **Semantic Memory** - Extracted knowledge and facts
- **Procedural Memory** - Behavioral patterns and preferences
- **Long-term Storage** - Qdrant-backed vector database

## Setup

### Installation

```bash
pip install "dspy>=3.1.0" "mem0ai>=1.0.2"
```

### Configuration

```python
import dspy
from mem0 import Memory
import os

# Configure Ollama
lm = dspy.LM(
    model="ollama/llama3.2",
    api_base="http://localhost:11434",
    api_key=""  # Ollama doesn't require API key
)
dspy.configure(lm=lm)

# Configure Mem0
config = {
    "llm": {
        "provider": "ollama",
        "config": {
            "model": "llama3.2",
            "ollama_base_url": "http://localhost:11434"
        }
    },
    "embedder": {
        "provider": "ollama",
        "config": {
            "model": "nomic-embed-text",
            "ollama_base_url": "http://localhost:11434"
        }
    },
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": "localhost",
            "port": 6333,
            "collection_name": "agentx_memory"
        }
    }
}

memory = Memory.from_config(config)
```

## Core Components

### 1. Memory-Aware Tools

```python
from typing import Optional
from datetime import datetime

class MemoryTools:
    """Tools for interacting with Mem0 memory system."""

    def __init__(self, memory: Memory):
        self.memory = memory

    def store_memory(
        self,
        content: str,
        user_id: str = "default_user",
        metadata: Optional[dict] = None
    ) -> str:
        """Store information in memory."""
        try:
            result = self.memory.add(
                content,
                user_id=user_id,
                metadata=metadata or {}
            )
            return f"Stored: {content}"
        except Exception as e:
            return f"Error storing: {str(e)}"

    def search_memories(
        self,
        query: str,
        user_id: str = "default_user",
        limit: int = 5
    ) -> str:
        """Search for relevant memories."""
        try:
            results = self.memory.search(
                query,
                user_id=user_id,
                limit=limit
            )

            if not results or "results" not in results:
                return "No relevant memories found."

            memories = results.get("results", [])
            output = "Relevant memories:\n"
            for i, mem in enumerate(memories, 1):
                output += f"{i}. {mem.get('memory', 'N/A')}\n"
            return output
        except Exception as e:
            return f"Error searching: {str(e)}"

    def get_all_memories(self, user_id: str = "default_user") -> str:
        """Get all memories for a user."""
        try:
            results = self.memory.get_all(user_id=user_id)

            if not results or "results" not in results:
                return "No memories found."

            memories = results.get("results", [])
            output = f"All memories ({len(memories)} total):\n"
            for i, mem in enumerate(memories, 1):
                output += f"{i}. {mem.get('memory', 'N/A')}\n"
            return output
        except Exception as e:
            return f"Error retrieving: {str(e)}"

    def update_memory(
        self,
        memory_id: str,
        new_content: str
    ) -> str:
        """Update an existing memory."""
        try:
            self.memory.update(memory_id, new_content)
            return f"Updated: {new_content}"
        except Exception as e:
            return f"Error updating: {str(e)}"

    def delete_memory(self, memory_id: str) -> str:
        """Delete a specific memory."""
        try:
            self.memory.delete(memory_id)
            return "Memory deleted successfully."
        except Exception as e:
            return f"Error deleting: {str(e)}"
```

### 2. ReAct Agent with Memory

```python
class MemoryQA(dspy.Signature):
    """Memory-enabled question answering."""
    user_input: str = dspy.InputField()
    context: str = dspy.InputField(desc="Retrieved memories")
    response: str = dspy.OutputField()

class MemoryReActAgent(dspy.Module):
    """ReAct agent enhanced with Mem0 memory."""

    def __init__(self, memory: Memory):
        super().__init__()
        self.memory_tools = MemoryTools(memory)

        # Define available tools
        self.tools = [
            self.memory_tools.store_memory,
            self.memory_tools.search_memories,
            self.memory_tools.get_all_memories,
            self.get_current_time,
            self.set_reminder,
            self.get_preferences,
            self.update_preferences,
        ]

        # Initialize ReAct
        self.react = dspy.ReAct(
            signature=MemoryQA,
            tools=self.tools,
            max_iters=6
        )

    def forward(self, user_input: str, user_id: str = "default_user"):
        """Process user input with memory-aware reasoning."""
        # First, search for relevant memories
        context = self.memory_tools.search_memories(
            query=user_input,
            user_id=user_id,
            limit=3
        )

        # Process with ReAct
        result = self.react(
            user_input=user_input,
            context=context
        )

        return result

    # Helper methods
    def get_current_time(self) -> str:
        """Get current date and time."""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def set_reminder(
        self,
        reminder_text: str,
        date_time: str = None,
        user_id: str = "default_user"
    ) -> str:
        """Set a reminder for the user."""
        reminder = f"REMINDER: {date_time or 'ASAP'} - {reminder_text}"
        return self.memory_tools.store_memory(reminder, user_id)

    def get_preferences(
        self,
        category: str = "general",
        user_id: str = "default_user"
    ) -> str:
        """Get user preferences for a category."""
        query = f"user preferences {category}"
        return self.memory_tools.search_memories(query, user_id)

    def update_preferences(
        self,
        category: str,
        preference: str,
        user_id: str = "default_user"
    ) -> str:
        """Update user preferences."""
        text = f"User preference for {category}: {preference}"
        return self.memory_tools.store_memory(text, user_id)
```

## Usage Example

```python
# Initialize
memory = Memory.from_config(config)
agent = MemoryReActAgent(memory)

# Simulate conversation
conversations = [
    "Hi, I'm Alice and I love Italian food, especially pasta carbonara.",
    "I prefer to exercise in the morning around 7 AM.",
    "What do you remember about my food preferences?",
    "Set a reminder for me to go grocery shopping tomorrow.",
    "What are my exercise preferences?",
]

for user_input in conversations:
    print(f"\n📝 User: {user_input}")

    try:
        response = agent(user_input=user_input, user_id="alice")
        print(f"🤖 Agent: {response.response}")
    except Exception as e:
        print(f"❌ Error: {e}")
```

## Advanced Features

### Memory Categories

```python
def categorize_memory(content: str) -> str:
    """Categorize memory type."""
    categories = {
        "preference": ["prefer", "like", "love", "favorite"],
        "fact": ["is", "are", "was", "were"],
        "reminder": ["remind", "remember to", "don't forget"],
        "event": ["happened", "occurred", "did", "went"],
    }

    content_lower = content.lower()
    for category, keywords in categories.items():
        if any(kw in content_lower for kw in keywords):
            return category

    return "general"

# Use in storage
metadata = {
    "category": categorize_memory(content),
    "timestamp": datetime.now().isoformat(),
}
memory.add(content, metadata=metadata)
```

### Temporal Memory Retrieval

```python
from datetime import datetime, timedelta

def get_recent_memories(
    memory: Memory,
    user_id: str,
    days: int = 7
) -> list:
    """Get memories from last N days."""
    cutoff = datetime.now() - timedelta(days=days)

    all_memories = memory.get_all(user_id)
    recent = []

    for mem in all_memories.get("results", []):
        mem_time = mem.get("metadata", {}).get("timestamp")
        if mem_time:
            mem_datetime = datetime.fromisoformat(mem_time)
            if mem_datetime >= cutoff:
                recent.append(mem)

    return recent
```

### Memory Consolidation

```python
def consolidate_memories(
    memory: Memory,
    user_id: str,
    category: str
) -> str:
    """Consolidate multiple memories into summary."""
    # Get all memories in category
    all_mems = memory.get_all(user_id)
    category_mems = [
        m for m in all_mems.get("results", [])
        if m.get("metadata", {}).get("category") == category
    ]

    if not category_mems:
        return f"No {category} memories to consolidate."

    # Use LLM to summarize
    import dspy

    summarize = dspy.Predict(
        "memories -> summary"
    )

    memories_text = "\n".join([
        m["memory"] for m in category_mems
    ])

    summary = summarize(memories=memories_text)

    # Store consolidated memory
    memory.add(
        f"Consolidated {category}: {summary.summary}",
        metadata={
            "category": "consolidated",
            "source_category": category,
            "count": len(category_mems)
        }
    )

    # Delete old memories
    for mem in category_mems:
        memory.delete(mem["id"])

    return f"Consolidated {len(category_mems)} memories."
```

## DSPy Optimization

### Using MIPROv2 Optimizer

```python
from dspy import MIPROv2
import dspy

# Create training data
trainset = [
    {
        "user_input": "What's my favorite food?",
        "context": "User prefers Italian food, especially pasta carbonara.",
        "response": "Your favorite food is Italian cuisine, particularly pasta carbonara."
    },
    # ... more examples
]

# Define evaluation metric
def memory_accuracy(example, pred, trace=None):
    """Check if response uses memory correctly."""
    return any(
        keyword in pred.response.lower()
        for keyword in example["context"].lower().split()
    )

# Setup optimizer
optimizer = MIPROv2(
    metric=memory_accuracy,
    num_trials=5,
    max_labeled_demos=3,
    max_unlabeled_demos=3
)

# Optimize
optimized_agent = optimizer.compile(
    MemoryReActAgent(memory),
    trainset=trainset
)
```

## Best Practices

### 1. Memory Hygiene
```python
# Don't store everything
def should_store(content: str) -> bool:
    """Decide if content is worth storing."""
    # Skip trivial messages
    trivial = ["ok", "thanks", "bye", "hello"]
    if content.lower().strip() in trivial:
        return False

    # Skip very short messages
    if len(content.split()) < 3:
        return False

    return True
```

### 2. Context Window Management
```python
# Limit retrieved memories to prevent context overflow
MAX_RETRIEVED_MEMORIES = 5

def search_memories_limited(query: str, user_id: str) -> str:
    """Search with result limit."""
    results = memory.search(
        query,
        user_id=user_id,
        limit=MAX_RETRIEVED_MEMORIES
    )

    # Format results
    memories = results.get("results", [])
    return "\n".join([
        f"- {m['memory']}" for m in memories
    ])
```

### 3. User Memory Isolation
```python
# Always scope by user_id
def get_agent_for_user(user_id: str) -> MemoryReActAgent:
    """Get isolated agent for specific user."""
    user_memory = Memory.from_config(config)
    return MemoryReActAgent(user_memory)
```

## References

- [DSPy Mem0 Tutorial](https://dspy.ai/tutorials/mem0_react_agent/)
- [Mem0 Documentation](https://docs.mem0.ai/)
- [DSPy GitHub](https://github.com/stanfordnlp/dspy)
- [Mem0 GitHub](https://github.com/mem0ai/mem0)
