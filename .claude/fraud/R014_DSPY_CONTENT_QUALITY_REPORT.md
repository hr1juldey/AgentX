# R014 UI Showcase Backend: Content Quality Issues

**Analysis Date**: 2026-02-02
**Codebase**: `/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/`
**Reference**: DSPy tutorials at `/home/riju279/Downloads/dspy-main/dspy-main/docs/`

---

## Executive Summary

The R014 backend system **WORKS functionally** but produces **POOR CONTENT QUALITY** due to fundamental issues in how DSPy modules handle context maintenance, result synthesis, and topic preservation throughout the multi-stage pipeline.

**Main Symptom**: The system forgets the original topic and just writes the latest search results.

**Root Causes Identified**:
1. No topic consistency layer in the pipeline
2. Inline signatures that gemma3:4b cannot parse reliably
3. Multi-hop search drifts without topic anchoring
4. No cross-source synthesis of research results
5. Widget generation ignores expensive research data

---

## Problem 1: Topic Drift - No Central Context Maintainer

### Severity: **CRITICAL** 🔴

### The Problem

The original query/topic is passed through the pipeline but **never actively reinforced** or used as a filtering criterion. Results drift into tangential topics because nothing says "Remember, we're researching TOPIC X."

### Where It Fails

#### 1.1 Contextualizer Filter - Too Permissive

**File**: `services/tools/contextualizer/filter.py`

```python
class FilterModule(dspy.Module):
    """Filters search results based on relevance thresholds.

    Instructions say:
    "Be generous with scoring. If there is ANY connection to the query,
    score at least 0.3. Only give 0.0 for completely unrelated topics."
    """

    def __init__(self):
        # Inline signature - gemma3:4b can't parse field semantics
        self.check_relevance = dspy.Predict("query, result -> is_relevant, relevance_score")
```

**Why It Fails**:
- Query is passed but only checks "ANY connection" (line 21-22)
- No threshold for "directly addresses the main topic"
- Tangential results with 0.3-0.5 scores pass through
- gemma3:4b needs explicit "main topic anchor" to stay focused

#### 1.2 Reranker - No Topic Alignment

**File**: `services/tools/contextualizer/reranker.py`

```python
class RerankerModule(dspy.Module):
    """Reranks search results by quality and relevance."""

    def __init__(self):
        # Inline signature - no field descriptions
        self.rank_by_quality = dspy.Predict("query, results -> ranked_results")
```

**Why It Fails**:
- Scores relevance but doesn't filter by topic alignment
- A result about "Linux kernel history" might rank high for "Best Linux distro for gaming" because both mention Linux
- No "topic_coherence" scoring dimension

#### 1.3 Multi-Hop Planner - Drift Without Anchor

**File**: `services/multihop_search/reflection/planner.py`

```python
class GenerateNextQuery(dspy.Signature):
    """Generate the next search query based on current gaps."""

    question: str = dspy.InputField(desc="Original question")
    gap_description: str = dspy.InputField(desc="What information is still missing")
    previous_queries: list[str] = dspy.InputField(desc="Search queries already tried")

    next_query: str = dspy.OutputField(desc="Proposed search query for next hop")
    # Missing: No main_topic field or "stay focused" instruction
```

**Why It Fails**:
- Hop 2-5 drift because `gap_description` dominates over `question`
- Example: "Best Linux distro for gaming" → Hop 2: "Linux history" → Hop 3: "Kernel development"
- No enforcement: "You MUST address the original question, not interesting tangents"

### The Fix: Topic-Anchored Signatures

```python
class GenerateAnchoredQuery(dspy.Signature):
    """Generate a search query that stays focused on the main topic.

    CRITICAL INSTRUCTION:
    The search query MUST directly address the original question.
    Do NOT drift into tangential topics, even if they are interesting.

    Before generating next_query, ask yourself:
    1. Does this query directly answer the user's original question?
    2. Am I exploring a tangent just because it's interesting?

    If the gap_description is about a tangential topic, IGNORE IT and
    find a different gap that actually addresses the main question.
    """

    main_topic: str = dspy.InputField(
        desc="The original user question - this is your NORTH STAR, never lose sight of it"
    )
    gap_description: str = dspy.InputField(
        desc="What information is still missing to answer main_topic"
    )
    hop_number: int = dspy.InputField(desc="Current hop number (1-5)")

    next_query: str = dspy.OutputField(
        desc="Search query that addresses the gap WHILE staying focused on main_topic"
    )
    topic_alignment_check: str = dspy.OutputField(
        desc="Explain how this query stays focused on main_topic (or why it doesn't)"
    )
```

---

## Problem 2: Inline Signatures Break gemma3:4b

### Severity: **HIGH** 🟠

### The Problem

~40% of signatures use inline `"input -> output"` format that **weak LLMs cannot parse reliably** without explicit field descriptions.

### Inline Signatures (BROKEN for gemma3:4b)

**File**: `services/tools/contextualizer/contextualizer.py`
```python
# Line 28-29
self.add_context = dspy.Predict("query, result -> contextualized_result")
self.enrich_metadata = dspy.Predict("result, metadata -> enriched_result")
```

**File**: `services/tools/presenter/polisher.py`
```python
# Line 21-22
self.polish_content = dspy.Predict("content -> polished_content")
self.enhance_clarity = dspy.Predict("content -> enhanced_content")
```

**File**: `services/tools/analyst/query_analyzer.py`
```python
# Line 16-18
self.detect_type = dspy.Predict("query -> query_type")
self.extract_domain = dspy.Predict("query -> domain")
self.identify_urgency = dspy.Predict("query -> urgency")
```

### Why gemma3:4b Fails

Inline signatures lack:
1. **Field descriptions** - gemma3:4b doesn't know what `query_type` means
2. **Type hints** - Is it a string? Enum? List?
3. **Instructions** - No guidance on how to interpret the field
4. **Examples** - No few-shot examples to guide the model

### Class-Based Signatures (WORK Better)

**File**: `services/tools/contextualizer/signatures.py` (Good pattern!)

```python
class CheckRelevanceSignature(dspy.Signature):
    """Check if a search result is relevant to the user query.

    Be generous with scoring. If there is ANY connection to the query,
    score at least 0.3. Only give 0.0 for completely unrelated topics.
    """

    query: str = dspy.InputField(desc="User query")
    result: str = dspy.InputField(desc="Search result to check")

    is_relevant: bool = dspy.OutputField(desc="Whether the result is relevant")
    relevance_score: float = dspy.OutputField(
        desc="Relevance score from 0.0 (unrelated) to 1.0 (directly relevant)"
    )
    reasoning: str = dspy.OutputField(desc="Brief explanation of the score")
```

**Why This Works**:
- ✅ Clear docstring with instructions
- ✅ Each field has `desc=` explaining semantics
- ✅ Output types are explicit (`bool`, `float`, `str`)
- ✅ `reasoning` field lets gemma3:4b show its work

### Impact on Content Quality

| Module | Inline Signature | Result |
|--------|------------------|--------|
| PolisherModule | `"content -> polished_content"` | Generic "Here's improved content" regardless of quality |
| ContextualizerModule | `"query, result -> contextualized_result"` | Loses connection to original query |
| QueryAnalyzerModule | `"query -> query_type"` | Misclassifies complex queries |

---

## Problem 3: No Cross-Source Synthesis

### Severity: **CRITICAL** 🔴

### The Problem

After multihop search returns **9 reports** (3²), nothing synthesizes them into a unified narrative. The system just concatenates or uses the latest one.

### Where It Fails

#### 3.1 Multihop Reader - No Final Synthesis

**File**: `services/tools/researcher/multihop_reader.py`

```python
class MultiHopReaderModule(dspy.Module):
    """Reads and processes results from multiple search hops.

    Returns: Dictionary with micro-reports from each source-hop combination.
    """

    def forward(self, query: str, search_results: list[dict]) -> dict:
        # Generates 9 micro-reports (3 hops × 3 sources)
        micro_reports = []
        for hop in range(num_hops):
            for source in sources:
                report = self.generate_micro_report(...)
                micro_reports.append(report)

        # ❌ PROBLEM: Just returns a list, no synthesis!
        return {
            "micro_reports": micro_reports,  # 9 separate reports
            "total_reports": len(micro_reports),  # 9
            # Missing: unified_summary, key_findings, contradictions
        }
```

**What's Missing**:
1. **Identify common themes** across the 9 reports
2. **Resolve contradictions** between sources
3. **Create unified narrative** that answers the main query
4. **Link back to original question** (does this actually help?)

#### 3.2 Report Generator - Micro, Not Macro

**File**: `services/tools/researcher/report_generator.py`

```python
class ReportGeneratorModule(dspy.Module):
    """Generates structured reports from raw data."""

    def __init__(self):
        # Inline signature - no synthesis guidance
        self.generate = dspy.Predict("data -> report")

    def forward(self, raw_data: list[dict]) -> dict:
        reports = []
        for data in raw_data:
            # Generates 2-4 sentence micro-reports
            result = self.generate(data=data)
            reports.append(result.report)

        # ❌ Returns list, not synthesized answer
        return {"reports": reports}  # Just concatenation
```

### The Fix: Multi-Source Synthesis Module

```python
class SynthesizeMultiSourceReport(dspy.Signature):
    """Create a unified report from multiple research sources.

    CRITICAL TASK:
    You are synthesizing information from MULTIPLE sources to answer
    the user's ORIGINAL question. This is not just summarization -
    you must INTEGRATE and ANALYZE across sources.

    REQUIREMENTS:
    1. Identify 3-5 key findings that DIRECTLY address the main query
    2. Note any CONTRADICTIONS between sources (e.g., "Source A says X, but Source B says Y")
    3. Attribute information to specific sources
    4. Prioritize information that answers the original question
    5. Ignore tangential information, even if interesting

    OUTPUT STRUCTURE:
    - Start with a direct answer to the main query
    - Support with evidence from multiple sources
    - Note contradictions where they exist
    - End with a conclusion that ties back to the original question
    """

    main_query: str = dspy.InputField(
        desc="The user's original question - this is what you must answer"
    )
    research_reports: list[str] = dspy.InputField(
        desc="List of micro-reports from multihop search (may contain contradictions)"
    )

    unified_report: str = dspy.OutputField(
        desc="Synthesized report that directly answers main_query using information from all sources"
    )
    key_findings: str = dspy.OutputField(
        desc="3-5 key findings that directly address the main query, with source attribution"
    )
    contradictions_noted: str = dspy.OutputField(
        desc="Any contradictions between sources, or 'NONE' if all sources agree"
    )
    confidence_assessment: str = dspy.OutputField(
        desc="High/Medium/Low confidence based on source agreement and directness of answer"
    )
```

---

## Problem 4: Widget Generation Ignores Research

### Severity: **CRITICAL** 🔴

### The Problem

WidgetSpawner generates content **WITHOUT using the expensive multihop research results**. All that research work is thrown away.

### Where It Fails

#### 4.1 Widget Executor - No Research Data

**File**: `services/widget_spawner/executor.py`

```python
class WidgetSpawnerService:
    """Generates UI widgets using DSPy."""

    async def generate_widget(self, widget_spec: dict, context: dict) -> dict:
        # ...

        # ❌ PROBLEM: Only gets context string, no research data!
        result = generator(user_query=context["user_query"])

        # The research_results from multihop search are NOT passed!
        # Widgets generate hallucinations instead of using research.
```

#### 4.2 Signatures Missing Research Input

**File**: `services/widget_spawner/signatures.py`

```python
class GenerateMarkdownSignature(dspy.Signature):
    """Generate markdown content for a markdown block widget."""

    user_query: str = dspy.InputField(desc="User's query or request")
    # ❌ Missing: research_results: str = dspy.InputField()

    markdown_content: str = dspy.OutputField(desc="Generated markdown content")
    # ❌ Missing: sources_used: str = dspy.OutputField()
```

**What Happens**:
1. Multihop search spends 9 API calls gathering research
2. Research is stored in `context["search_results"]`
3. WidgetSpawner is called with only `user_query`
4. Widget generates generic hallucinations
5. **All that research work is wasted**

### The Fix: Widget Generation WITH Research

```python
class GenerateMarkdownWithResearch(dspy.Signature):
    """Generate markdown content using research results.

    CRITICAL CONSTRAINT:
    You MUST use the provided research_data. Do NOT hallucinate facts.
    If research_data doesn't contain the answer, say "Information not found in research."

    Your goal is to PRESENT the research findings, not to create new knowledge.
    """

    user_query: str = dspy.InputField(
        desc="User's question - what you need to address from the research"
    )
    research_data: str = dspy.InputField(
        desc="Research findings from multihop search - your ONLY source of truth"
    )
    widget_type: str = dspy.InputField(desc="Type of widget: markdown_block, card, etc.")

    markdown_content: str = dspy.OutputField(
        desc="Markdown content that answers user_query using ONLY research_data"
    )
    sources_used: str = dspy.OutputField(
        desc="Cite which sources from research_data were used (e.g., 'Source 1, Source 3')"
    )
    information_gap: str = dspy.OutputField(
        desc="Any information needed to answer the query that was NOT found in research_data, or 'NONE' if complete"
    )
```

---

## Problem 5: Pipeline Lacks Topic Consistency Check

### Severity: **HIGH** 🟠

### The Problem

The 10-phase pipeline passes data but never checks: "Are we still addressing the user's original question?"

### Where It Should Be Added

**File**: `services/master_agent/orchestration/pipeline_execution.py`

```python
# Current pipeline (simplified):
async def execute_pipeline(query: str):
    # Phase 1: Analyst
    insights = await analyst_agent.extract_insights(query)

    # Phase 2: Researcher
    search_results = await researcher_agent.multihop_search(insights)

    # Phase 3: Contextualizer
    context = await contextualizer_agent.add_context(search_results)

    # Phase 4+: Designer, WidgetSelector, Sequencer, Presenter
    # ... each phase works on results

    # ❌ MISSING: Topic consistency check between phases!
```

### The Fix: Topic Consistency Layer

```python
class TopicConsistencyCheck(dspy.Signature):
    """Check if the pipeline is still addressing the user's question.

    This is called BETWEEN pipeline phases to prevent topic drift.

    EVALUATION CRITERIA:
    1. Does the current output directly address the original question?
    2. Have we drifted into tangential topics?
    3. Should we filter/rerank by relevance to the main query?

    If topic_drift_detected is True, the pipeline must:
    - Filter outputs by main_topic relevance
    - Rerank by topic_alignment_score
    - Or trigger a new research cycle
    """

    main_question: str = dspy.InputField(
        desc="The user's original question - this never changes"
    )
    current_phase_output: str = dspy.InputField(
        desc="Output from the current pipeline phase to check"
    )
    phase_name: str = dspy.InputField(
        desc="Which phase produced this output (e.g., 'Researcher', 'Contextualizer')"
    )

    is_on_topic: bool = dspy.OutputField(
        desc="True if output directly addresses main_question"
    )
    topic_alignment_score: float = dspy.OutputField(
        desc="0.0-1.0 based on how closely output aligns with main_question"
    )
    drift_description: str = dspy.OutputField(
        desc="If off-topic, describe how we drifted. If on-topic, write 'ON TOPIC'"
    )
    recommended_action: str = dspy.OutputField(
        desc="Either 'CONTINUE', 'FILTER_BY_TOPIC', 'RERANK', or 'NEW_RESEARCH'"
    )
```

**Integration**:
```python
async def execute_pipeline(query: str):
    # Phase 1: Analyst
    insights = await analyst_agent.extract_insights(query)

    # ✅ ADD: Topic consistency check
    check = await topic_checker(main_question=query, current_phase_output=insights, phase_name="Analyst")
    if not check.is_on_topic:
        insights = await filter_by_topic(insights, query)

    # Phase 2: Researcher
    search_results = await researcher_agent.multihop_search(insights)

    # ✅ ADD: Topic consistency check
    check = await topic_checker(main_question=query, current_phase_output=search_results, phase_name="Researcher")
    if check.topic_alignment_score < 0.5:
        search_results = await rerank_by_topic(search_results, query)

    # ... continue with remaining phases
```

---

## Problem 6: ChainOfThought Reasoning Is Discarded

### Severity: **MEDIUM** 🟡

### The Problem

`dspy.ChainOfThought` generates reasoning but the pipeline **throws it away**. gemma3:4b needs to see its own reasoning to stay on track.

### Where It Fails

**File**: `services/multihop_search/agents/multihop_agent.py`

```python
class MultiHopAgent(dspy.Module):
    def __init__(self):
        # ChainOfThought generates reasoning field
        self.answer_with_sources = dspy.ChainOfThought("question, context -> answer, sources_summary")

    def forward(self, question: str, context: str) -> dspy.Prediction:
        result = self.answer_with_sources(question=question, context=context)

        # ❌ reasoning field is available but NEVER USED!
        # It could check: "Does the reasoning stay focused on the question?"

        return dspy.Prediction(
            answer=result.answer,
            sources_summary=result.sources_summary
            # Missing: reasoning=result.reasoning (for debugging, for next module)
        )
```

**Why It Matters**:

ChainOfThought reasoning could be used to:
1. **Debug** topic drift: "Oh, the reasoning shows it went off track at hop 3"
2. **Feed forward** to next module: "Here's what I found, stay focused on this"
3. **Quality check**: "The reasoning doesn't match the question, regenerate"

### The Fix: Preserve and Use Reasoning

```python
class MultiHopAgent(dspy.Module):
    def forward(self, question: str, context: str) -> dspy.Prediction:
        result = self.answer_with_sources(question=question, context=context)

        # ✅ Check if reasoning stayed on topic
        if "off topic" in result.reasoning.lower():
            # Trigger topic recovery
            result = self.answer_with_sources(question=question, context=f"STAY FOCUSED: {question}")

        return dspy.Prediction(
            answer=result.answer,
            sources_summary=result.sources_summary,
            reasoning=result.reasoning,  # ✅ Preserve for next module
            topic_coherence=check_topic_coherence(result.reasoning, question)  # ✅ Validate
        )
```

---

## Summary: Root Causes

| # | Problem | Impact | Fix Complexity |
|---|---------|--------|----------------|
| 1 | No topic consistency layer | Results drift off-topic | Medium |
| 2 | Inline signatures (40%) | gemma3:4b can't parse | Low |
| 3 | Multi-hop planner drifts | Tangential searches | Medium |
| 4 | No cross-source synthesis | 9 reports, not unified answer | High |
| 5 | Widgets ignore research | Wasted API calls | Medium |
| 6 | ChainOfThought discarded | Can't debug drift | Low |

---

## Recommended Fixes by Priority

### Phase 1: Critical (Do First - These are breaking content quality)

| Fix | File | Change | Est. Time |
|-----|------|--------|----------|
| 1.1 | `contextualizer/filter.py` | Add `main_topic` field, raise threshold to 0.5 | 2h |
| 1.2 | `multihop_search/reflection/planner.py` | Add `main_topic` with strict focus instruction | 3h |
| 1.3 | `tools/researcher/multihop_reader.py` | Add `SynthesizeMultiSourceReport` module | 4h |
| 1.4 | `widget_spawner/executor.py` | Pass `research_data` to all generators | 3h |
| 1.5 | `pipeline_execution.py` | Add topic consistency check between phases | 4h |

**Subtotal**: 16 hours

### Phase 2: High Priority (Improving quality)

| Fix | File | Change | Est. Time |
|-----|------|--------|----------|
| 2.1 | Replace 40 inline signatures with class-based | Multiple files | 8h |
| 2.2 | `contextualizer/reranker.py` | Add `topic_coherence` scoring dimension | 2h |
| 2.3 | `multihop_agent.py` | Preserve and use `reasoning` field | 2h |
| 2.4 | Add `TopicRelevanceFilter` module | New file | 3h |

**Subtotal**: 15 hours

### Phase 3: Medium Priority (Polish)

| Fix | File | Change | Est. Time |
|-----|------|--------|----------|
| 3.1 | Add better error handling for off-topic detection | Multiple | 4h |
| 3.2 | Add quality metrics for synthesis quality | New file | 3h |
| 3.3 | Improve prompt instructions for weak LLMs | Multiple | 4h |

**Subtotal**: 11 hours

**Total Estimated Effort**: 42 hours

---

## Anti-Patterns vs Real Problems

This analysis distinguishes between:

### Anti-Patterns (Code style issues)
- Inline signatures instead of class-based
- Returning `dict` instead of `dspy.Prediction`
- Thin wrapper modules

### Real Problems (Breaking content quality)
- **Topic drift** - No enforcement of staying focused
- **No synthesis** - 9 reports but no unified answer
- **Research ignored** - Widgets don't use expensive research
- **Weak LLM constraints** - gemma3:4b needs explicit guidance

**Key Insight**: Fixing anti-patterns alone won't solve the content quality issues. We need to fix the **architectural problems** that cause topic drift and research waste.

---

## DSPy Patterns That WOULD Work Better

### 1. Topic-Anchored Multi-Hop

```python
class TopicAnchoredMultiHop(dspy.Module):
    """Multi-hop search that maintains topic focus."""

    def __init__(self, num_hops=3):
        super().__init__()
        self.planner = dspy.Predict(GenerateAnchoredQuery)
        self.topic_checker = dspy.Predict(TopicConsistencyCheck)

    def forward(self, question: str) -> dspy.Prediction:
        all_results = []
        current_topic = question  # ✅ Maintain topic reference

        for hop in range(num_hops):
            # ✅ Pass topic anchor
            next_query = self.planner(
                main_topic=current_topic,  # Not just "question"
                gap_description=gaps[hop]
            )

            results = search(next_query.next_query)

            # ✅ Check for topic drift
            check = self.topic_checker(
                main_question=current_topic,
                current_phase_output=results
            )

            if check.topic_alignment_score < 0.5:
                # ✅ Filter or reroute
                results = filter_by_topic(results, current_topic)

            all_results.extend(results)

        # ✅ Synthesize across all hops
        final = self.synthesize(
            main_query=question,
            hop_results=all_results
        )

        return final
```

### 2. Research-Aware Widget Generation

```python
class ResearchAwareWidgetSpawner(dspy.Module):
    """Generates widgets using research results."""

    def __init__(self):
        super().__init__()
        self.markdown_gen = dspy.Predict(GenerateMarkdownWithResearch)
        self.card_gen = dspy.Predict(GenerateCardWithResearch)

    def spawn_widget(self, widget_type: str, user_query: str, research_data: str) -> dspy.Prediction:
        # ✅ Research is REQUIRED input
        if widget_type == "markdown_block":
            result = self.markdown_gen(
                user_query=user_query,
                research_data=research_data  # ✅ Use expensive research!
            )
            return dspy.Prediction(
                widget_content=result.markdown_content,
                sources=result.sources_used,
                has_research=True  # ✅ Track research usage
            )
```

### 3. Synthesis-First Pipeline

```python
class SynthesisFirstPipeline:
    """Pipeline that synthesizes before presenting."""

    async def execute(self, query: str):
        # Phase 1: Research
        research = await self.researcher.multihop_search(query)

        # ✅ NEW: Synthesize FIRST
        synthesis = await self.synthesizer.unify_sources(
            main_query=query,
            research_reports=research
        )

        # ✅ Check synthesis quality
        if synthesis.confidence_assessment == "Low":
            # Try research again with better focus
            research = await self.researcher.multihop_search(
                query=synthesis.refined_query
            )

        # Phase 2+: Now present/sequence using SYNTHESIS
        widgets = await self.widget_spawner.generate(
            user_query=query,
            research_data=synthesis.unified_report  # ✅ Use synthesis
        )

        return widgets
```

---

## Conclusion

The R014 backend's content quality issues stem from **architectural problems**, not just code style anti-patterns:

1. **No topic consistency enforcement** - Results drift because nothing says "stay focused"
2. **Inline signatures** - gemma3:4b can't parse without explicit descriptions
3. **No synthesis layer** - 9 research reports but no unified answer
4. **Research not used** - Widgets generate hallucinations instead of using research

**The system works** - it produces output. **But the content is poor** - it forgets the main topic and just writes the latest search results.

**The fix requires**:
1. Adding topic anchoring throughout the pipeline
2. Converting inline signatures to class-based with descriptions
3. Creating a synthesis module to unify research results
4. Wiring research data into widget generation
5. Adding topic consistency checks between pipeline phases

**Estimated effort**: 42 hours

---

**Report Generated**: 2026-02-02
**Focus**: Content quality issues with gemma3:4b weak LLM
**Reference**: DSPy tutorials at `/home/riju279/Downloads/dspy-main/dspy-main/docs/`
