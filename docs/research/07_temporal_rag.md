# Temporal RAG Systems Guide

## Overview

Temporal RAG addresses the critical limitation of traditional RAG systems: time-blindness. Standard vector similarity doesn't understand when information was created, whether it's still valid, or how events relate temporally.

## The Problem

### Why Standard RAG Fails with Time

```
User timeline:
January:  "I love Adidas shoes"
July:     "My Adidas broke, I now prefer Puma"
September: "What shoes should I buy?"

Standard RAG result:
- Retrieves: "I love Adidas shoes" (January)
- Ignores: "I now prefer Puma" (July)
- Outcome: Wrong recommendation
```

### Key Challenges

1. **Temporal decay** - Old information becomes less relevant
2. **Fact invalidation** - New facts override old ones
3. **Event sequencing** - Understanding "what happened before X"
4. **Duration tracking** - Long-term states vs point events
5. **Memory consolidation** - Summarizing over time periods

## Solutions

### 1. Temporal Metadata Enrichment

```python
from datetime import datetime
from typing import Dict, Any

def add_temporal_metadata(
    content: str,
    user_id: str
) -> Dict[str, Any]:
    """Add temporal information to memory."""

    now = datetime.now()

    return {
        "text": content,
        "user_id": user_id,

        # Temporal information
        "created_at": now.isoformat(),
        "modified_at": now.isoformat(),
        "valid_from": now.isoformat(),
        "valid_until": None,  # None means still valid

        # Temporal classification
        "temporal_type": classify_temporal_type(content),

        # Relationships
        "supersedes": find_superseded_memories(content, user_id),
        "related_events": find_related_events(content, user_id),
    }


def classify_temporal_type(content: str) -> str:
    """Classify the temporal nature of content."""
    keywords = {
        "preference": ["prefer", "like", "love", "favorite"],
        "state": ["currently", "now", "right now"],
        "event": ["happened", "occurred", "did", "went"],
        "plan": ["will", "going to", "planning to"],
    }

    content_lower = content.lower()

    for temp_type, terms in keywords.items():
        if any(term in content_lower for term in terms):
            return temp_type

    return "fact"


def find_superseded_memories(content: str, user_id: str) -> list:
    """Find memories that this content invalidates."""
    # Extract entities and topics
    entities = extract_entities(content)

    # Search for conflicting memories
    conflicts = []
    for entity in entities:
        results = memory.search(
            f"{entity} preference",
            user_id=user_id
        )
        conflicts.extend(results.get("results", []))

    return [c["id"] for c in conflicts]
```

### 2. Time-Aware Retrieval

```python
from datetime import datetime, timedelta
from qdrant_client.models import Filter, FieldCondition

def temporal_search(
    query: str,
    user_id: str,
    time_filter: str = "recent"  # recent, all, historical
) -> list:
    """Search with temporal filtering."""

    query_embedding = list(embedding_model.query_embed(query))[0]

    # Build time-based filter
    if time_filter == "recent":
        # Last 30 days
        cutoff = datetime.now() - timedelta(days=30)
        time_condition = FieldCondition(
            key="created_at",
            range=models.DateTimeRange(gte=cutoff)
        )
    elif time_filter == "historical":
        # Older than 30 days
        cutoff = datetime.now() - timedelta(days=30)
        time_condition = FieldCondition(
            key="created_at",
            range=models.DateTimeRange(lt=cutoff)
        )
    else:  # "all"
        time_condition = None

    # Search with filter
    results = qdrant_client.query_points(
        collection_name="agentx_memory",
        query=query_embedding,
        query_filter=Filter(must=[time_condition]) if time_condition else None,
        limit=10,
        with_payload=True
    )

    # Post-process for fact invalidation
    processed = invalidate_outdated_facts(results.results)

    return processed


def invalidate_outdated_facts(results: list) -> list:
    """Remove or mark outdated facts."""

    # Group by entity/topic
    groups = {}
    for result in results:
        entity = extract_entity(result.payload["text"])
        if entity not in groups:
            groups[entity] = []
        groups[entity].append(result)

    # Keep only latest for each entity
    final = []
    for entity, memories in groups.items():
        # Sort by timestamp
        memories.sort(
            key=lambda m: m.payload["created_at"],
            reverse=True
        )

        # Add latest, mark others as superseded
        final.append(memories[0])
        for memory in memories[1:]:
            memory.payload["superseded_by"] = memories[0].id
            # Optionally include for transparency
            final.append(memory)

    return final
```

### 3. Temporal Knowledge Graphs

```python
# memory/temporal_graph.py
from typing import Dict, List
from datetime import datetime

class TemporalMemoryGraph:
    """Knowledge graph with temporal relationships."""

    def __init__(self):
        self.nodes: Dict[str, Dict] = {}
        self.edges: List[Dict] = []

    def add_event(
        self,
        event_id: str,
        timestamp: datetime,
        entities: List[str],
        attributes: Dict
    ):
        """Add temporal event to graph."""
        self.nodes[event_id] = {
            "timestamp": timestamp,
            "entities": entities,
            "attributes": attributes
        }

        # Create temporal edges
        for other_id, other_node in self.nodes.items():
            if other_id == event_id:
                continue

            # Determine relationship
            if timestamp > other_node["timestamp"]:
                relationship = "after"
            else:
                relationship = "before"

            # Add edge if entities overlap
            if set(entities) & set(other_node["entities"]):
                self.edges.append({
                    "from": event_id,
                    "to": other_id,
                    "relationship": relationship,
                    "entities": list(set(entities) & set(other_node["entities"]))
                })

    def get_timeline(
        self,
        entity: str,
        start: datetime,
        end: datetime
    ) -> List[Dict]:
        """Get timeline for entity."""
        events = []

        for event_id, node in self.nodes.items():
            if (entity in node["entities"] and
                start <= node["timestamp"] <= end):
                events.append({
                    "id": event_id,
                    "timestamp": node["timestamp"],
                    "attributes": node["attributes"]
                })

        return sorted(events, key=lambda e: e["timestamp"])

    def get_chain(self, start_event: str, end_event: str) -> List[str]:
        """Get event chain between two events."""
        # Find path through temporal edges
        visited = set()
        path = []
        current = start_event

        while current != end_event and current not in visited:
            visited.add(current)
            path.append(current)

            # Find next event in chain
            for edge in self.edges:
                if edge["from"] == current:
                    if edge["to"] == end_event:
                        path.append(end_event)
                        return path
                    elif edge["to"] not in visited:
                        current = edge["to"]
                        break

        return path
```

### 4. Duration-Aware Memory

```python
# memory/duration_memory.py
from datetime import datetime
from typing import Optional

class DurationMemory:
    """Track states with durations."""

    def __init__(self):
        self.active_states: Dict[str, Dict] = {}

    def start_state(
        self,
        state_id: str,
        state_type: str,
        attributes: Dict,
        user_id: str
    ):
        """Start tracking a state."""
        self.active_states[state_id] = {
            "type": state_type,
            "start_time": datetime.now(),
            "attributes": attributes,
            "user_id": user_id
        }

    def end_state(self, state_id: str) -> Optional[Dict]:
        """End a state and calculate duration."""
        if state_id not in self.active_states:
            return None

        state = self.active_states[state_id]
        end_time = datetime.now()

        duration = {
            "type": state["type"],
            "start_time": state["start_time"],
            "end_time": end_time,
            "duration": (end_time - state["start_time"]).total_seconds(),
            "attributes": state["attributes"],
            "user_id": state["user_id"]
        }

        # Store as consolidated memory
        memory.add(
            f"Duration: {state['type']} for {duration['duration']}s",
            user_id=state["user_id"],
            metadata={
                "type": "duration",
                "start": state["start_time"].isoformat(),
                "end": end_time.isoformat(),
                "duration_seconds": duration["duration"]
            }
        )

        del self.active_states[state_id]
        return duration

    def get_active_states(self, user_id: str) -> List[Dict]:
        """Get all active states for user."""
        return [
            {**state, "id": state_id}
            for state_id, state in self.active_states.items()
            if state["user_id"] == user_id
        ]


# Usage
duration_memory = DurationMemory()

# Start tracking
duration_memory.start_state(
    "exercise_session",
    "exercise",
    {"activity": "running", "location": "gym"},
    user_id="alice"
)

# Later, end it
duration = duration_memory.end_state("exercise_session")
# Returns: {"type": "exercise", "duration": 1800, ...}
```

### 5. Advanced: Hindsight-Inspired Architecture

```python
# memory/hindsight.py
from enum import Enum

class MemoryNetwork(Enum):
    """Four logical networks from Hindsight architecture."""
    WORLD = "objective_facts"
    BANK = "agent_experiences"
    OPINION = "beliefs_with_confidence"
    OBSERVATION = "entity_summaries"

class HindsightMemory:
    """Hindsight-inspired memory architecture."""

    def __init__(self):
        self.networks = {
            network.value: {}
            for network in MemoryNetwork
        }

    def add(
        self,
        content: str,
        network: MemoryNetwork,
        confidence: float = 1.0,
        user_id: str = "default"
    ):
        """Add memory to specific network."""
        memory_id = f"{user_id}_{len(self.networks[network.value])}"

        self.networks[network.value][memory_id] = {
            "content": content,
            "confidence": confidence,
            "created_at": datetime.now(),
            "user_id": user_id
        }

        # Update related observations
        if network == MemoryNetwork.WORLD:
            self._update_observations(content, user_id)

    def _update_observations(self, fact: str, user_id: str):
        """Update entity observations."""
        entities = extract_entities(fact)

        for entity in entities:
            entity_key = f"{user_id}_{entity}"

            # Get existing observations
            existing = self.networks[MemoryNetwork.OBSERVATION.value].get(
                entity_key,
                {"content": "", "examples": []}
            )

            # Add new example
            existing["examples"].append({
                "fact": fact,
                "timestamp": datetime.now()
            })

            # Consolidate observation
            existing["content"] = self._consolidate_observations(
                entity,
                existing["examples"]
            )

            self.networks[MemoryNetwork.OBSERVATION.value][entity_key] = existing

    def _consolidate_observations(self, entity: str, examples: list) -> str:
        """Create entity summary from examples."""
        # Use LLM to summarize
        summary_prompt = f"""
Summarize observations about {entity}:
{chr(10).join([f"- {e['fact']}" for e in examples[-5:]])}

Create a neutral, preference-free summary.
"""

        import dspy
        summarizer = dspy.Predict("examples -> summary")
        result = summarizer(examples=summary_prompt)

        return result.summary

    def retrieve(
        self,
        query: str,
        networks: List[MemoryNetwork] = None,
        user_id: str = "default"
    ) -> Dict[str, list]:
        """Retrieve from specified networks."""
        if networks is None:
            networks = list(MemoryNetwork)

        results = {}
        for network in networks:
            network_data = self.networks[network.value]

            # Filter by user and search
            user_memories = {
                k: v for k, v in network_data.items()
                if v["user_id"] == user_id
            }

            # Semantic search
            results[network.value] = semantic_search(
                query,
                user_memories
            )

        return results
```

## Query Patterns

### Temporal Queries

```python
# "What happened before X?"
def query_before(event: str, user_id: str) -> list:
    """Get events before specified event."""
    event_data = memory.get(event, user_id)

    cutoff = event_data["created_at"]

    results = temporal_search(
        f"Context for {event}",
        user_id,
        time_filter="all"
    )

    return [
        r for r in results
        if r.payload["created_at"] < cutoff
    ]


# "How long have I been doing X?"
def query_duration(activity: str, user_id: str) -> float:
    """Calculate duration of activity."""
    start_events = temporal_graph.get_timeline(
        activity,
        start=datetime.min,
        end=datetime.now()
    )

    if not start_events:
        return 0

    # Find ongoing state or sum durations
    active = duration_memory.get_active_states(user_id)

    for state in active:
        if state["type"] == activity:
            # Currently active
            return (datetime.now() - state["start_time"]).total_seconds()

    # Sum historical durations
    total = sum(
        e.get("duration", 0)
        for e in start_events
        if "duration" in e
    )

    return total


# "What's my current preference for X?"
def query_current_preference(entity: str, user_id: str) -> str:
    """Get most recent preference for entity."""
    results = temporal_search(
        f"{entity} preference",
        user_id,
        time_filter="recent"
    )

    if not results:
        return "No preference found"

    # Return most recent, unsuperseded
    for result in results:
        if "superseded_by" not in result.payload:
            return result.payload["text"]

    return results[0].payload["text"]
```

## Best Practices

### 1. Temporal Indexing

```python
# Add temporal indexes to Qdrant
qdrant_client.create_collection(
    collection_name="agentx_memory",
    vectors_config=...,
    optimizers_config=models.OptimizersConfig(
        indexing_threshold=20000
    ),
    payload_schema={
        "created_at": models.PayloadSchemaType.DATETIME,
        "valid_from": models.PayloadSchemaType.DATETIME,
        "valid_until": models.PayloadSchemaType.DATETIME,
    }
)
```

### 2. Memory Consolidation

```python
# Run periodic consolidation
async def consolidate_old_memories():
    """Consolidate memories older than 90 days."""
    cutoff = datetime.now() - timedelta(days=90)

    old_memories = qdrant_client.scroll(
        collection_name="agentx_memory",
        scroll_filter=Filter(
            must=[
                FieldCondition(
                    key="created_at",
                    range=models.DateTimeRange(lt=cutoff)
                )
            ]
        ),
        limit=1000
    )

    # Group by topic/entity
    topics = {}
    for record in old_memories[0]:
        topic = extract_topic(record.payload["text"])
        if topic not in topics:
            topics[topic] = []
        topics[topic].append(record)

    # Summarize each topic
    for topic, memories in topics.items():
        summary = summarize_memories(memories)

        # Store consolidated memory
        memory.add(
            f"Consolidated {topic}: {summary}",
            metadata={
                "type": "consolidated",
                "source_count": len(memories),
                "date_range": (
                    min(m.payload["created_at"] for m in memories),
                    max(m.payload["created_at"] for m in memories)
                )
            }
        )

        # Mark old memories as consolidated
        for mem in memories:
            qdrant_client.set_payload(
                collection_name="agentx_memory",
                payload={"consolidated_into": summary.id},
                points=[mem.id]
            )
```

### 3. Temporal Query Optimization

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def cached_temporal_search(
    query_hash: str,
    time_filter: str,
    user_id: str
) -> list:
    """Cache temporal searches."""
    return temporal_search(
        query_hash,
        user_id,
        time_filter
    )


def get_cache_key(query: str, time_filter: str) -> str:
    """Generate cache key."""
    import hashlib
    content = f"{query}:{time_filter}"
    return hashlib.md5(content.encode()).hexdigest()
```

## References

- [Hindsight Architecture](https://www.opensourceforu.com/2025/12/agentic-memory-hindsight-beats-rag-in-long-term-ai-reasoning/)
- [Temporal Semantic Memory](https://arxiv.org/html/2601.07468v1)
- [Beyond Naive RAG](https://www.linkedin.com/pulse/beyond-naive-rag-from-vector-soup-hindsight-memory-temporal-verma-ssjpc)
- [Temporal Event Horizon Problem](https://www.blankline.org/research/beyond-retrieval-augmented-generation-how-we-solved-the-temporal-event-horizon-problem)
