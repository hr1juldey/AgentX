# Spec: STT Preprocessing

**Domain**: agent-runtime
**Generated**: 2026-02-01
**Status**: Draft

---

## 1. Purpose

Define the STT preprocessing system that transforms noisy, episodic speech-to-text input into clean, well-formed queries suitable for the query planner.

**Problem Statement**: Humans speak differently than they write. Speech is episodic, has false starts, fillers ("um", "uh"), informal grammar, and spelling errors. Without preprocessing, these noisy inputs produce poor query plans.

**Success Criteria**:
- STT input preprocessed into clean queries
- Fillers and false starts removed
- Informal grammar normalized
- Query planner receives well-formed input regardless of source

---

## 2. Scope

### In Scope

- STT input preprocessing (speech-to-text output)
- Filler removal ("um", "uh", "like", "you know")
- False start handling
- Informal grammar normalization
- Spelling correction
- Episodic utterance consolidation (partial → full query)

### Out of Scope

- STT engine itself (kyutai integration - see C010 voice client)
- Query planning (see query-complexity-assessment spec)
- Dynamic routing (see dynamic-routing spec)

---

## 3. Requirements

### 3.1 Functional Requirements

| ID | Requirement | Priority | Source |
|----|-------------|----------|--------|
| FR-STT-001 | Detect input path (TEXT vs STT) | Must | Input awareness |
| FR-STT-002 | Preprocess STT input before query planner | Must | Clean input |
| FR-STT-003 | Remove fillers ("um", "uh", "like") | Must | Noise reduction |
| FR-STT-004 | Handle false starts ("I wanted... I need...") | Must | Coherence |
| FR-STT-005 | Normalize informal grammar | Should | Standard form |
| FR-STT-006 | Correct common spelling errors | Should | Accuracy |
| FR-STT-007 | Consolidate episodic utterances | Should | Full query |
| FR-STT-008 | Preprocessing < 500ms | Should | Performance |

### 3.2 Non-Functional Requirements

| ID | Requirement | Priority | Target Metric |
|----|-------------|----------|---------------|
| NFR-STT-001 | Preprocessing latency | Must | < 500ms |
| NFR-STT-002 | Accuracy | Should | >95% clean output |
| NFR-STT-003 | Backwards compatible | Must | TEXT input unchanged |

---

## 4. Data Model

### 4.1 Preprocessed Query

```python
# domain/models/stt_preprocessing.py
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

class InputPath(str, Enum):
    """Where the query came from."""
    TEXT = "text"      # Clean, well-formed input
    STT = "stt"        # Noisy, episodic, needs preprocessing

class UtteranceSegment(BaseModel):
    """A segment of speech before consolidation."""
    text: str = Field(description="Raw STT text for this segment")
    timestamp: float = Field(description="Segment timestamp (seconds from start)")
    is_partial: bool = Field(default=True, description="True if this is a partial utterance")

class PreprocessedQuery(BaseModel):
    """Result of STT preprocessing."""
    input_path: InputPath = Field(description="Source of original query")
    original_text: str = Field(description="Original raw input")
    preprocessed_text: str = Field(description="Clean, well-formed query")
    was_preprocessed: bool = Field(description="Whether preprocessing was applied")
    transformations: List[str] = Field(default_factory=list, description="Transformations applied")

    # For episodic utterances
    segments: List[UtteranceSegment] = Field(default_factory=list, description="Original segments if consolidated")
    final_segment_count: int = Field(default=1, description="Number of segments consolidated")

class PreprocessingMetrics(BaseModel):
    """Metrics for preprocessing quality."""
    original_length: int = Field(description="Character count of original")
    preprocessed_length: int = Field(description="Character count after preprocessing")
    fillers_removed: int = Field(description="Number of filler words removed")
    false_starts_handled: int = Field(description="Number of false starts corrected")
    segments_consolidated: int = Field(description="Number of segments merged")
    processing_time_ms: float = Field(description="Processing time in milliseconds")
```

---

## 5. API Contract

### 5.1 DSPy Preprocessing Module

```python
# agent/tools/preprocessing/stt_preprocessor.py
import dspy
from dspy import InputField, OutputField, Signature

class PreprocessSTTSignature(dspy.Signature):
    """Preprocess noisy STT input into clean query."""
    raw_stt_text = InputField(desc="Raw speech-to-text output (noisy, episodic)")
    conversation_context = InputField(desc="Previous utterances for consolidation", default="")

    preprocessed_query = OutputField(desc="Clean, well-formed query")
    transformations = OutputField(desc="List of transformations applied (e.g., 'fillers_removed', 'grammar_fixed')")

class STTPreprocessorModule(dspy.Module):
    """Preprocess STT input using LLM."""

    def __init__(self):
        super().__init__()
        self.preprocess = dspy.Predict(PreprocessSTTSignature)

    def forward(self, raw_stt_text: str, conversation_context: str = "") -> dspy.Prediction:
        """Preprocess STT text."""
        return self.preprocess(
            raw_stt_text=raw_stt_text,
            conversation_context=conversation_context
        )

    async def aforward(self, raw_stt_text: str, conversation_context: str = "") -> dspy.Prediction:
        """Async preprocessing."""
        return await self.preprocess.acall(
            raw_stt_text=raw_stt_text,
            conversation_context=conversation_context
        )

class RuleBasedPreprocessor:
    """Fast rule-based preprocessing (no LLM)."""

    FILLERS = {
        "um", "uh", "like", "you know", "actually", "basically",
        "sort of", "kind of", "I mean", "right", "mhm"
    }

    FALSE_START_PATTERNS = [
        r"I wanted to ask\b",
        r"So I was\b",
        r"I guess\b",
        r"Maybe\b",
    ]

    def __init__(self):
        import re
        self.re = re

    def preprocess(self, raw_text: str) -> tuple[str, list[str]]:
        """Apply rule-based preprocessing."""

        text = raw_text
        transformations = []

        # 1. Remove filler words (with surrounding punctuation)
        for filler in self.FILLERS:
            pattern = rf"(?<=[.!?]|\s){self.re.escape(filler)}(?=[.!?]|\s)"
            if self.re.search(pattern, text, self.re.IGNORECASE):
                text = self.re.sub(pattern, "", text, flags=self.re.IGNORECASE)
                transformations.append("fillers_removed")

        # 2. Clean up extra whitespace
        text = " ".join(text.split())
        transformations.append("whitespace_normalized")

        # 3. Remove repeated punctuation (??? → ?)
        text = self.re.sub(r"([.!?])\1+", r"\1", text)
        transformations.append("punctuation_normalized")

        # 4. Fix common speech patterns
        text = self.re.sub(r"\bgonna\b", "going to", text, flags=self.re.IGNORECASE)
        text = self.re.sub(r"\bwanna\b", "want to", text, flags=self.re.IGNORECASE)
        text = self.re.sub(r"\bgotta\b", "got to", text, flags=self.re.IGNORECASE)
        transformations.append("contractions_expanded")

        # 5. Capitalize first letter
        text = text[0].upper() + text[1:] if text else ""
        transformations.append("capitalization_fixed")

        # 6. Ensure ending punctuation
        if text and not text[-1] in ".!?":
            text = text + "."
            transformations.append("punctuation_added")

        return text, transformations
```

### 5.2 Preprocessing Node

```python
# agent/nodes/stt_preprocessor.py
from agent.tools.preprocessing.stt_preprocessor import STTPreprocessorModule, RuleBasedPreprocessor
import time

class PreprocessorConfig:
    """Configuration for preprocessing strategy."""
    USE_LLM_FOR_LONG_INPUTS = True  # Use LLM for inputs > 200 chars
    USE_RULES_FOR_SHORT_INPUTS = True  # Use rules for inputs <= 200 chars

async def stt_preprocessor_node(state: AgentState) -> dict:
    """Preprocess STT input before query planning.

    This node runs BEFORE the query planner if input_path is STT.
    For TEXT input, it passes through unchanged.
    """

    input_path = state.get("input_path", InputPath.TEXT)
    raw_query = state["query"]

    # Text input passes through
    if input_path == InputPath.TEXT:
        return {
            "preprocessed_query": raw_query,
            "preprocessing_metrics": None,
        }

    # STT input needs preprocessing
    start_time = time.perf_counter()

    preprocessor = STTPreprocessorModule()
    rule_preprocessor = RuleBasedPreprocessor()

    # Choose strategy based on input length
    if len(raw_query) > 200 and PreprocessorConfig.USE_LLM_FOR_LONG_INPUTS:
        # Use LLM for complex/long inputs
        result = await preprocessor.aforward(raw_query)
        preprocessed = result.preprocessed_query
        transformations = result.transformations.split(", ") if result.transformations else []
    elif PreprocessorConfig.USE_RULES_FOR_SHORT_INPUTS:
        # Use rules for simple/short inputs (fast)
        preprocessed, transformations = rule_preprocessor.preprocess(raw_query)
    else:
        # Fallback: just clean whitespace
        preprocessed = " ".join(raw_query.split())
        transformations = ["whitespace_normalized"]

    processing_time_ms = (time.perf_counter() - start_time) * 1000

    # Create metrics
    metrics = PreprocessingMetrics(
        original_length=len(raw_query),
        preprocessed_length=len(preprocessed),
        fillers_removed=transformations.count("fillers_removed"),
        false_starts_handled=transformations.count("false_starts_fixed"),
        processing_time_ms=processing_time_ms,
    )

    return {
        "preprocessed_query": preprocessed,
        "preprocessing_metrics": metrics,
        "execution_path": ["stt_preprocessor"],
    }

# Add to graph BEFORE query planner
builder.add_conditional_edges(
    START,
    lambda state: "stt_preprocessor" if state.get("input_path") == InputPath.STT else "query_planner",
    {
        "stt_preprocessor": "stt_preprocessor",
        "query_planner": "query_planner",
    }
)
builder.add_edge("stt_preprocessor", "query_planner")
```

---

## 6. Business Rules

| Rule | Description | Enforcement | Source |
|------|-------------|-------------|--------|
| BR-STT-001 | TEXT input passes through unchanged | Node check | Performance |
| BR-STT-002 | STT input always preprocessed | Node check | Quality |
| BR-STT-003 | Short inputs (< 200 chars) use rules | Strategy choice | Speed |
| BR-STT-004 | Long inputs (> 200 chars) use LLM | Strategy choice | Quality |
| BR-STT-005 | Preprocessing < 500ms | Performance check | UX |

---

## 7. Acceptance Criteria

- [ ] TEXT input passes through unchanged
- [ ] STT input preprocessed into clean query
- [ ] Fillers removed ("um", "uh", "like")
- [ ] False starts handled
- [ ] Grammar normalized
- [ ] Preprocessing < 500ms
- [ ] Ruff and pyrefly checks pass

---

## 8. Test Scenarios

### 8.1 Filler Removal

| Input | Output |
|-------|--------|
| "um what is the capital of france" | "What is the capital of France?" |
| "like tell me about iphone" | "Tell me about iPhone." |
| "uh I wanted to ask about python" | "I wanted to ask about Python." |

### 8.2 False Start Handling

| Input | Output |
|-------|--------|
| "I wanted to ask about... I need to know about Italy" | "I need to know about Italy." |
| "So I was thinking... maybe we could compare cars" | "Maybe we could compare cars." |

### 8.3 Grammar Normalization

| Input | Output |
|-------|--------|
| "whats two plus two" | "What is two plus two?" |
| "how do I get to the airport from here" | "How do I get to the airport from here?" |
| "gotta know about latest movies" | "Got to know about latest movies." |

---

## 9. Integration with Query Planner

```python
# The query planner receives preprocessed text
class QueryPlannerModule(dspy.Module):
    async def aforward(
        self,
        query: str,  # Already preprocessed if from STT
        input_path: InputPath,
        available_knowledge: str = "",
    ) -> dspy.Prediction:
        """Generate execution plan.

        Note: query is already preprocessed by stt_preprocessor_node
        if input_path is STT.
        """

        # Search episodic memory for cached research
        cached_research = {}
        if self.memory_store:
            memories = await self.memory_store.search_research_memories(
                query=query,  # Clean query
                user_id=user_id,
                limit=5,
            )
            cached_research = {m.memory_id: m.summary for m in memories}

        # Generate plan
        return await self.plan.acall(
            query=query,
            input_path=input_path.value,
            cached_research=str(cached_research),
            available_knowledge=available_knowledge,
        )
```

---

## 10. References

- **Kyutai Voice Server**: `openspec/changes/c010-voice-client/` - STT/TTS integration
- **DSPy Async**: `/home/riju279/Downloads/dspy-main/dspy-main/docs/docs/tutorials/async/index.md`
- **Query Planner**: `query-complexity-assessment/spec.md` - Uses preprocessed query

---

**Next**: See `transient-ux/spec.md` for UX patterns during long-running tasks.
