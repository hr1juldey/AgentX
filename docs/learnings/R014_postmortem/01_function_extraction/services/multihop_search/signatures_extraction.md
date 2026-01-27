# Function Postmortem: services/multihop_search/signatures.py

## Metadata
- **File**: services/multihop_search/signatures.py
- **Lines of Code**: 92
- **Purpose**: DSPy signatures for multi-hop search with runtime reflection
- **Dependencies**: `dspy`

---

## Analysis

**File Status**: PRODUCTION DSPy SIGNATURES

**Purpose**: Defines DSPy signatures for multi-hop search pipeline. Covers query generation, answering with citations, completeness checking, next query planning, and final synthesis.

---

## Classes Extracted

### DSPy Signatures

**`class GenerateSearchQuery(Signature)`**
- **Purpose**: Generate a search query based on current context
- **Input Fields**:
  - `question: str` - Original user question
  - `context: str` - Accumulated context from previous hops
  - `hop_number: int` - Current hop number
  - `total_hops: int` - Total number of hops
- **Output Fields**:
  - `search_query: str` - Optimized search query for this hop
  - `reasoning: str` - Reasoning behind this query

**`class AnswerWithSources(Signature)`**
- **Purpose**: Answer questions using provided documents with citations
- **Input Fields**:
  - `question: str` - Question to answer
  - `context: str` - Accumulated context from previous hops
- **Output Fields**:
  - `answer: str` - Comprehensive answer with inline citations [1], [2], etc.
  - `sources_summary: str` - Brief summary of sources used

**`class CheckCompleteness(Signature)`**
- **Purpose**: Check if we have enough information to answer the question
- **Input Fields**:
  - `question: str` - Original question
  - `current_answer: str` - Current best answer from all hops
  - `documents_summary: str` - Brief summary of documents found
- **Output Fields**:
  - `is_sufficient: bool` - True if we can answer the question well
  - `confidence: float` - Confidence score 0.0 to 1.0
  - `gap_description: str` - Brief description of what's missing (if not sufficient)

**`class GenerateNextQuery(Signature)`**
- **Purpose**: Generate the next search query based on what's missing
- **Input Fields**:
  - `question: str` - Original question
  - `gap_description: str` - What information is still missing
  - `previous_queries: list[str]` - Search queries already tried
- **Output Fields**:
  - `next_query: str` - Proposed search query for next hop
  - `strategy: str` - Strategy: REFINE_TOPIC (go deeper), DISCOVER_NEW (new angle), VALIDATE_EXPAND (verify)

**`class SynthesizeFinalAnswer(Signature)`**
- **Purpose**: Synthesize final answer from all hop results
- **Input Fields**:
  - `question: str` - Original question
  - `all_hop_answers: list[str]` - Answers from each hop
  - `all_context: list[str]` - Context from each hop
- **Output Fields**:
  - `final_answer: str` - Synthesized final answer
  - `summary: str` - Brief summary of findings
  - `confidence: str` - Confidence level: low, medium, or high

---

## File Summary

**Total Classes**: 5 (DSPy Signatures)
**Lines of Code**: 92

**Overall Assessment**: Comprehensive DSPy signatures covering the full multi-hop search pipeline. Clear separation of concerns (query generation, answering, completeness checking, planning, synthesis). Good use of structured outputs (bool, float, list) for control flow.

**Key Learnings for Real AgentX**:
1. ✅ **Runtime reflection**: CheckCompleteness enables adaptive stopping
2. ✅ **Strategy selection**: GenerateNextQuery outputs strategy (REFINE_TOPIC/DISCOVER_NEW/VALIDATE_EXPAND)
3. ✅ **Inline citations**: AnswerWithSources requires [1], [2] citation format
4. ✅ **Confidence scoring**: Both numeric (0.0-1.0) and categorical (low/medium/high) confidence
5. ✅ **Gap description**: Explicitly states what's missing, guides next query
6. ✅ **List inputs**: all_hop_answers, all_context enable synthesis from multiple hops
7. ✅ **Hop awareness**: hop_number, total_hops enable adaptive query refinement
8. ⚠️ **Complex signatures**: Multiple input/output fields may confuse LLMs

**Reuse for Real AgentX**: ✅ HIGH - Excellent pattern for multi-hop reasoning. Runtime reflection is reusable for any iterative search. Strategy selection (REFINE_TOPIC/DISCOVER_NEW/VALIDATE_EXPAND) is applicable to exploration tasks.
