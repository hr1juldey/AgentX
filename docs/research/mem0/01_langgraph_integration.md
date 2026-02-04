# Mem0AI LangGraph Integration

**Source:** https://docs.mem0.ai/integrations/langgraph
**Retrieved:** 2025-02-04

---

## Overview

Build a personalized Customer Support AI Agent using LangGraph for conversation flow and Mem0 for memory retention. This integration enables context-aware and efficient support experiences.

### Key Features

1. **Memory Integration**: Uses Mem0 to store and retrieve relevant information from past interactions
2. **Personalization**: Provides context-aware responses based on user history
3. **Flexible Architecture**: LangGraph structure allows for easy expansion of the conversation flow
4. **Continuous Learning**: Each interaction is stored, improving future responses

---

## Setup and Configuration

### Install Dependencies

```bash
pip install langgraph langchain-openai mem0ai python-dotenv
```

### Import Required Modules

```python
from typing import Annotated, TypedDict, List
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from mem0 import MemoryClient
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from dotenv import load_dotenv

load_dotenv()

# Configuration
OPENAI_API_KEY = 'sk-xxx'  # Replace with your actual OpenAI API key
MEM0_API_KEY = 'your-mem0-key'  # Replace with your actual Mem0 API key

# Initialize LangChain and Mem0
llm = ChatOpenAI(model="gpt-4")
mem0 = MemoryClient()
```

---

## Define State and Graph

```python
class State(TypedDict):
    messages: Annotated[List[HumanMessage | AIMessage], add_messages]
    mem0_user_id: str

graph = StateGraph(State)
```

---

## Create Chatbot Function

```python
def chatbot(state: State):
    messages = state["messages"]
    user_id = state["mem0_user_id"]

    try:
        # Retrieve relevant memories
        memories = mem0.search(messages[-1].content, user_id=user_id)

        # Handle dict response format
        memory_list = memories['results']
        context = "Relevant information from previous conversations:\n"
        for memory in memory_list:
            context += f"- {memory['memory']}\n"

        system_message = SystemMessage(content=f"""You are a helpful customer support assistant. Use the provided context to personalize your responses and remember user preferences and past interactions.
{context}""")

        full_messages = [system_message] + messages
        response = llm.invoke(full_messages)

        # Store the interaction in Mem0
        try:
            interaction = [
                {
                    "role": "user",
                    "content": messages[-1].content
                },
                {
                    "role": "assistant",
                    "content": response.content
                }
            ]
            result = mem0.add(interaction, user_id=user_id)
            print(f"Memory saved: {len(result.get('results', []))} memories added")
        except Exception as e:
            print(f"Error saving memory: {e}")

        return {"messages": [response]}

    except Exception as e:
        print(f"Error in chatbot: {e}")
        # Fallback response without memory context
        response = llm.invoke(messages)
        return {"messages": [response]}
```

---

## Set Up Graph Structure

```python
graph.add_node("chatbot", chatbot)
graph.add_edge(START, "chatbot")
graph.add_edge("chatbot", "chatbot")
compiled_graph = graph.compile()
```

---

## Create Conversation Runner

```python
def run_conversation(user_input: str, mem0_user_id: str):
    config = {"configurable": {"thread_id": mem0_user_id}}
    state = {
        "messages": [HumanMessage(content=user_input)],
        "mem0_user_id": mem0_user_id
    }

    for event in compiled_graph.stream(state, config):
        for value in event.values():
            if value.get("messages"):
                print("Customer Support:", value["messages"][-1].content)
    return
```

---

## Main Interaction Loop

```python
if __name__ == "__main__":
    print("Welcome to Customer Support! How can I assist you today?")
    mem0_user_id = "alice"  # You can generate or retrieve this based on your user management system

    while True:
        user_input = input("You: ")
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("Customer Support: Thank you for contacting us. Have a great day!")
            break
        run_conversation(user_input, mem0_user_id)
```

---

## Key Patterns for AGENTX

### 1. Memory Search Before Execution

```python
# In any agent node:
def agent_node(state: State):
    user_id = state["mem0_user_id"]
    query = state["messages"][-1].content

    # Retrieve relevant context
    memories = mem0.search(query, user_id=user_id)
    memory_context = format_memories(memories['results'])

    # Use context in agent execution
    result = agent.execute(query, context=memory_context)

    return result
```

### 2. Store Results After Execution

```python
def agent_node(state: State):
    # ... execute agent ...

    # Store interaction in Mem0
    interaction = [
        {"role": "user", "content": query},
        {"role": "assistant", "content": result}
    ]
    mem0.add(interaction, user_id=state["mem0_user_id"])

    return result
```

### 3. User ID Management

```python
# Use thread_id as mem0_user_id
config = {"configurable": {"thread_id": "user-session-123"}}
state = {"messages": [...], "mem0_user_id": "user-session-123"}
```

### 4. Error Handling

```python
try:
    memories = mem0.search(query, user_id=user_id)
except Exception as e:
    # Continue without memory context
    memories = {'results': []}
```

---

## MemoryClient API Reference

### search()

```python
memories = mem0.search(query, user_id="user123")
# Returns: {'results': [{'memory': '...', 'metadata': {...}}, ...]}
```

### add()

```python
interaction = [
    {"role": "user", "content": "query"},
    {"role": "assistant", "content": "response"}
]
result = mem0.add(interaction, user_id="user123")
# Returns: {'results': [{'memory': '...', 'metadata': {...}}]}
```

### get_all()

```python
all_memories = mem0.get_all(user_id="user123")
```

---

## Integration with DSPy Agents

```python
import dspy
from mem0 import MemoryClient

mem0 = MemoryClient()

class DSPyAgentWithMemory(dspy.Module):
    def __init__(self):
        super().__init__()
        self.prog = dspy.ChainOfThought("question->answer")

    def forward(self, question, user_id):
        # Retrieve context from Mem0
        memories = mem0.search(question, user_id=user_id)
        context = "\n".join([m['memory'] for m in memories['results']])

        # Execute with context
        result = self.prog(question=f"{question}\n\nContext: {context}")

        # Store in Mem0
        mem0.add([
            {"role": "user", "content": question},
            {"role": "assistant", "content": result.answer}
        ], user_id=user_id)

        return result
```

---

## Notes for AGENTX Implementation

1. **Every agent should have Mem0AI integration** - not just Conversation agent
2. **Use user_id/session_id for memory isolation**
3. **Search before execution, store after execution**
4. **Handle Mem0 failures gracefully** (continue without memory)
5. **LangGraph thread_id maps to Mem0 user_id**
