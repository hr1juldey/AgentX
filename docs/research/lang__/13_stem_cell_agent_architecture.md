# Stem Cell Agent Architecture: DSPy Module Differentiation Patterns

**Research Date:** 2026-02-04
**Topic:** Biological stem cell concepts mapped to DSPy agent architecture

---

## Executive Summary

Just as biological stem cells are **pluripotent** (can become any cell type but expert at nothing), a **Stem Cell Agent** in DSPy is a minimal, undifferentiated module that can be specialized into any agent type through **overexpression** (adding modules) and **underexpression** (removing modules).

**Key Insight:** In DSPy, "gene expression" = module composition. The stem cell agent contains ONLY the essential machinery:
1. Input handling
2. Basic reasoning (`dspy.ChainOfThought` or `dspy.Predict`)
3. Memory hooks (Mem0AI + ColBERT prefetch)
4. Tool loading mount points

**Differentiation** happens by composing modules differently - not by modifying the stem cell itself.

---

## Part 1: Biological Analogy Mapping

### Pluripotent Stem Cell Properties

| Biological Property | DSPy Equivalent |
|--------------------|-----------------|
| **Totipotent** (can form entire organism) | Not applicable - too complex |
| **Pluripotent** (can become ANY cell type) | `StemCellAgent` - minimal, undifferentiated |
| **Multipotent** (limited to tissue lineage) | Specialized agents (e.g., `ResearcherAgent`, `AnalystAgent`) |
| **Unipotent** (single cell type) | Single-purpose modules (e.g., `MarkdownHydrator`) |

| Biological Process | DSPy Equivalent |
|--------------------|-----------------|
| **Differentiation** (becoming specialized) | Module composition (overexpression/underexpression) |
| **Gene overexpression** (more of a protein) | Adding DSPy modules/signatures |
| **Gene underexpression** (less of a protein) | Removing/ignoring modules |
| **Gene deletion** (removing a gene) | `pass` or not calling a module |
| **Signaling pathway** (Wnt, BMP, Notch) | LangGraph edges + data flow |
| **Extracellular matrix** (cell environment) | Memory systems (Mem0AI + Qdrant) |
| **Morphogens** (concentration gradients) | Context/state passed between modules |

---

## Part 2: The Stem Cell Agent (Pluripotent Base)

### Minimal Stem Cell Agent Definition

```python
import dspy
from typing import Optional, Any, Callable

class StemCellAgent(dspy.Module):
    """
    Pluripotent Stem Cell Agent - Minimal, Undifferentiated.

    Can differentiate into ANY agent type through module composition.
    Contains ONLY essential machinery (no domain specialization).

    Stem Cell Properties:
    - Input/Output handling
    - Basic reasoning (minimal ChainOfThought)
    - Signature loading (custom or default)
    - Memory hooks (Mem0AI + global DSPy RM)
    - Tool mount points (empty by default)
    - NO domain logic
    - NO specialization
    - NO fixed behavior
    """

    def __init__(
        self,
        user_id: Optional[str] = "default",
        signature: Optional[dspy.Signature] = None,
        enable_tools: bool = False,
    ):
        super().__init__()
        self.user_id = user_id
        self.enable_tools = enable_tools

        # ============================================================
        # SIGNATURE LOADING (The "DNA" of the stem cell)
        # ============================================================

        # Use custom signature if provided, otherwise use default
        if signature is None:
            # Default pluripotent signature (minimal)
            self.signature = dspy.Signature(
                "context, question -> answer, reasoning",
                instructions="Answer the question based on the provided context."
            )
        else:
            self.signature = signature

        # Create reasoning module from signature
        self.reasoning = dspy.ChainOfThought(self.signature)

        # ============================================================
        # ESSENTIAL MACHINERY (The "Nucleus" of the stem cell)
        # ============================================================

        # Tool mount point (empty by default = no tools)
        self.tools: list[dspy.Tool] = []

        # ============================================================
        # MEMORY SYSTEM HOOKS (The "Extracellular Matrix")
        # ============================================================

        # Mem0AI: Conversational memory (simple, fast)
        # Note: This is per-agent (not globally configured)
        self.mem0_client: Optional[Any] = None  # Injected via setter

        # DSPy RM: Uses globally configured retriever via dspy.settings.configure()
        # The stem cell uses whatever RM is configured globally
        # No per-agent RM injection - DSPy handles this centrally

    def forward(
        self,
        question: str,
        context: str = "",
        **kwargs
    ) -> dspy.Prediction:
        """
        Stem cell execution - Minimal undifferentiated behavior.

        This is the "pluripotent" state - can become anything.
        Specialization happens via composition (inheritance or wrapping).

        Note: Uses globally configured DSPy LM and RM via dspy.settings.
        """
        # Stage 1: Retrieve from Mem0AI memory (per-agent, not global)
        memory_context = ""
        if self.mem0_client:
            memories = self.mem0_client.search(
                question, user_id=self.user_id
            )
            memory_context = "\n".join([
                m['memory'] for m in memories.get('results', [])
            ])

        # Stage 2: Retrieve from knowledge (uses globally configured DSPy RM)
        # The RM is configured globally via dspy.configure(rm=...)
        # No per-agent RM needed - DSPy handles this centrally
        knowledge_context = ""
        try:
            # Use whatever RM is globally configured (dense, ColBERT, prefetch, etc.)
            retrieved = dspy.Retrieve(k=5)(question)
            knowledge_context = "\n".join(retrieved.passages)
        except Exception:
            # No RM configured or retrieval failed - continue without knowledge
            knowledge_context = ""

        # Stage 3: Combine context
        full_context = f"{context}\n{memory_context}\n{knowledge_context}".strip()

        # Stage 4: Basic reasoning (uses globally configured LM)
        result = self.reasoning(
            context=full_context,
            question=question
        )

        # Stage 5: Store interaction in Mem0AI
        if self.mem0_client:
            self.mem0_client.add([
                {"role": "user", "content": question},
                {"role": "assistant", "content": result.answer}
            ], user_id=self.user_id)

        return result

    # ============================================================
    # MEMORY INJECTION (Setter for Mem0AI only)
    # ============================================================

    def set_mem0_client(self, mem0_client: Any):
        """Inject Mem0AI client for conversational memory.

        Note: DSPy LM and RM are configured globally via dspy.configure().
        Only Mem0AI needs per-agent injection for user-scoped memory.
        """
        self.mem0_client = mem0_client

    def add_tool(self, tool: dspy.Tool):
        """Add a tool to the stem cell's tool mount point."""
        if not self.enable_tools:
            self.enable_tools = True
        self.tools.append(tool)

    def set_signature(self, signature: dspy.Signature):
        """Replace the stem cell's signature (differentiation).

        This allows runtime signature changes for different behaviors.
        """
        self.signature = signature
        self.reasoning = dspy.ChainOfThought(self.signature)
```

### Key Properties of the Stem Cell Agent

| Property | Description |
|----------|-------------|
| **Minimal** | Only essential machinery (no domain logic) |
| **Undifferentiated** | No fixed behavior, can become anything |
| **Signature-driven** | Custom or default signature defines behavior |
| **Composable** | Can be wrapped/extended for specialization |
| **Memory-aware** | Mem0AI (per-agent) + DSPy RM (global) |
| **Tool-ready** | Mount points for tools (empty by default) |
| **Idempotent** | Multiple instances don't share state (each agent = separate "nucleus") |

### DSPy Configuration (Global vs Per-Agent)

| Component | Scope | Configuration Method |
|-----------|-------|---------------------|
| **LM (Language Model)** | Global | `dspy.configure(lm=dspy.LM(...))` |
| **RM (Retrieval)** | Global | `dspy.configure(rm=QdrantRM(...))` |
| **Mem0AI** | Per-Agent | `agent.set_mem0_client(mem0)` |
| **Signatures** | Per-Agent | Passed to `__init__` or `set_signature()` |
| **Tools** | Per-Agent | `agent.add_tool(tool)` |

**Key Insight:** DSPy LM and RM are configured ONCE globally. The stem cell agent uses whatever is configured. Only Mem0AI needs per-agent injection because it stores user-scoped conversational memory.

---

## Part 3: Differentiation Patterns (Overexpression/Underexpression)

### Pattern 1: Overexpression (Adding Modules = Cell Specialization)

**Biological analogy:** Overexpressing transcription factors (e.g., MyoD for muscle, Neurogenin for neurons) to drive differentiation.

**DSPy analogy:** Adding DSPy modules/signatures to specialize the agent.

```python
# STEM CELL → MUSCLE CELL (Researcher Agent)
# Overexpression: Add ReAct + Web Search Tools + Custom Signature

class ResearcherAgent(StemCellAgent):
    """
    Differentiated Stem Cell → Muscle Cell
    Specialization: Web search + multi-hop reasoning
    Overexpression: ReAct reasoning + search tools + custom signature
    """

    def __init__(self, searxng_url: str = "http://localhost:8080"):
        # Define muscle-specific signature
        research_signature = dspy.Signature(
            "query, context -> answer, reasoning, citations: list[str]",
            instructions="""Research the query using available tools.
            Provide comprehensive answer with citations.
            Use multi-hop reasoning if needed."""
        )

        # Initialize stem cell with custom signature
        super().__init__(signature=research_signature, enable_tools=True)

        # ============================================================
        # OVEREXPRESSION: Add specialized modules (MyoD equivalent)
        # ============================================================

        # Overexpress: ReAct reasoning (instead of basic ChainOfThought)
        self.react = dspy.ReAct(
            "query, context -> answer, reasoning",
            tools=[],  # Will be populated from self.tools
            max_iters=10
        )

        # Overexpress: Search tools (specialized function)
        def web_search(query: str) -> str:
            """Tool: Search web using SearXNG."""
            import requests
            response = requests.get(
                f"{searxng_url}/search",
                params={"q": query, "format": "json"}
            )
            results = response.json()
            return "\n".join([
                f"{r['title']}: {r.get('snippet', '')}"
                for r in results.get('results', [])[:5]
            ])

        self.add_tool(dspy.Tool(web_search, name="web_search"))

    def forward(self, question: str, context: str = "", **kwargs):
        """Execute with ReAct (overexpressed reasoning)."""

        # Use stem cell's memory retrieval (Mem0AI + global RM)
        memory_context = ""
        if self.mem0_client:
            memories = self.mem0_client.search(question, user_id=self.user_id)
            memory_context = "\n".join([
                m['memory'] for m in memories.get('results', [])
            ])

        knowledge_context = ""
        try:
            retrieved = dspy.Retrieve(k=10)(question)
            knowledge_context = "\n".join(retrieved.passages)
        except Exception:
            pass

        full_context = f"{context}\n{memory_context}\n{knowledge_context}".strip()

        # Use overexpressed ReAct with tools
        self.react.tools = self.tools
        result = self.react(query=question, context=full_context)

        # Store in Mem0AI
        if self.mem0_client:
            self.mem0_client.add([
                {"role": "user", "content": question},
                {"role": "assistant", "content": result.answer}
            ], user_id=self.user_id)

        return result
```

### Pattern 2: Signature Differentiation (Cell Type Specification)

**Biological analogy:** Expressing cell-type-specific transcription factors (e.g., Neurogenin for neurons, MyoD for muscle).

**DSPy analogy:** Customizing the signature to change agent behavior.

```python
# STEM CELL → NEURON (Analyst Agent)
# Signature differentiation: Custom signature for analysis + judgment
# Note: Neurons NEED deep memory (retrieval) for complex reasoning

class AnalystAgent(StemCellAgent):
    """
    Differentiated Stem Cell → Neuron
    Specialization: Query analysis + data judgment + deep knowledge
    Differentiation: Custom signature + specialized modules

    Neurons are thinking cells - they NEED access to:
    - Mem0AI (conversational memory)
    - Deep knowledge (globally configured DSPy RM with ColBERT)
    """

    def __init__(self):
        # Define neuron-specific signature
        analyst_signature = dspy.Signature(
            "query, device_context, memory_context, knowledge_context -> "
            "context_summary, goals, is_sufficient, gap_description, confidence",
            instructions="""Analyze the query and judge if we have sufficient information.
            Use memory_context from past conversations and knowledge_context from retrieval.
            Output structured analysis with goals and confidence assessment."""
        )

        # Initialize stem cell with custom signature
        super().__init__(signature=analyst_signature, enable_tools=True)

        # ============================================================
        # OVEREXPRESSION: Specialized analysis modules
        # ============================================================

        # Overexpress: Context analysis (uses neuron signature)
        self.context_analyzer = dspy.Predict(
            "query -> context_summary, goals: list[str]"
        )

        # Overexpress: Data quality judgment
        self.data_judgment = dspy.ChainOfThought(
            "query, data -> is_sufficient: bool, gap_description, confidence: float"
        )

    def forward(self, question: str, device_context: str = "desktop"):
        """Execute analyst workflow with deep memory."""

        # Step 1: Get memory from Mem0AI (per-agent)
        memory_context = ""
        if self.mem0_client:
            memories = self.mem0_client.search(question, user_id=self.user_id)
            memory_context = "\n".join([
                m['memory'] for m in memories.get('results', [])
            ])

        # Step 2: Get deep knowledge from globally configured RM
        # Uses DSPy's global RM (could be ColBERT with prefetch)
        knowledge_context = ""
        try:
            retrieved = dspy.Retrieve(k=10)(question)
            knowledge_context = "\n".join(retrieved.passages)
        except Exception:
            pass  # No RM configured

        # Step 3: Analyze context using stem cell's reasoning (with custom signature)
        result = self.reasoning(
            query=question,
            device_context=device_context,
            memory_context=memory_context,
            knowledge_context=knowledge_context
        )

        return result
```

### Pattern 3: Sequential Composition (Cell Signaling Pathways)

**Biological analogy:** Signal transduction pathways (Wnt → β-catenin → transcription).

**DSPy analogy:** Chaining modules in sequence.

```python
# STEM CELL → MULTI-STAGE PIPELINE (Designer Agent)
# Sequential: Input → Analysis → Design → Selection

class DesignerAgent(StemCellAgent):
    """
    Differentiated Stem Cell → Specialized Pipeline
    Specialization: UI design generation
    Pattern: Sequential module composition (signaling pathway)
    """

    def __init__(self):
        super().__init__(enable_retrieval=False)

        # ============================================================
        # SEQUENTIAL COMPOSITION: Signaling pathway
        # ============================================================

        # Stage 1: Input → Goal extraction
        self.goal_extractor = dspy.Predict("query -> goals")

        # Stage 2: Goals → UI design pattern
        self.pattern_matcher = dspy.Predict(
            "goals, device_context -> ui_pattern, rationale"
        )

        # Stage 3: Pattern → Widget selection
        self.widget_selector = dspy.Predict(
            "ui_pattern, goals -> widgets: list[str]"
        )

        # Stage 4: Widgets → Final descriptor
        self.descriptor_generator = dspy.ChainOfThought(
            "widgets, goals, device_context -> ui_descriptor"
        )

    def forward(self, question: str, device_context: str = "desktop"):
        """Execute sequential pipeline."""

        # Stage 1: Extract goals
        goals = self.goal_extractor(query=question).goals

        # Stage 2: Match pattern
        pattern = self.pattern_matcher(
            goals=goals,
            device_context=device_context
        )

        # Stage 3: Select widgets
        widgets = self.widget_selector(
            ui_pattern=pattern.ui_pattern,
            goals=goals
        ).widgets

        # Stage 4: Generate descriptor
        descriptor = self.descriptor_generator(
            widgets=widgets,
            goals=goals,
            device_context=device_context
        )

        return descriptor
```

### Pattern 4: Parallel Composition (Cell Cell-Cell Communication)

**Biological analogy:** Cell-cell communication via signaling molecules.

**DSPy analogy:** Parallel module execution.

```python
# STEM CELL → PARALLEL EXECUTION (Contextualizer Agent)
# Parallel: Multiple analysis tracks simultaneously

class DataContextualizerAgent(StemCellAgent):
    """
    Differentiated Stem Cell → Parallel Processing
    Specialization: Multi-track data analysis
    Pattern: Parallel module composition (cell-cell communication)
    """

    def __init__(self):
        super().__init__()

        # ============================================================
        # PARALLEL COMPOSITION: Multiple signaling pathways
        # ============================================================

        # Track 1: Content analysis
        self.content_analyzer = dspy.Predict(
            "data -> content_summary, key_points"
        )

        # Track 2: Quality assessment
        self.quality_assessor = dspy.ChainOfThought(
            "data -> quality_score, issues: list[str]"
        )

        # Track 3: Entity extraction
        self.entity_extractor = dspy.Predict(
            "data -> entities: list[dict]"
        )

    def forward(self, data: dict):
        """Execute parallel tracks."""

        import asyncio

        # Parallel execution (all tracks run simultaneously)
        results = asyncio.run(self._parallel_execute(data))

        # Merge results (cell-cell communication)
        return dspy.Prediction(
            content_summary=results['content'].content_summary,
            key_points=results['content'].key_points,
            quality_score=results['quality'].quality_score,
            issues=results['quality'].issues,
            entities=results['entities'].entities
        )

    async def _parallel_execute(self, data: dict):
        """Execute all tracks in parallel."""
        import asyncio

        # Run all three tracks concurrently
        results = await asyncio.gather(
            asyncio.to_thread(self.content_analyzer, data=data),
            asyncio.to_thread(self.quality_assessor, data=data),
            asyncio.to_thread(self.entity_extractor, data=data),
        )

        return {
            'content': results[0],
            'quality': results[1],
            'entities': results[2]
        }
```

---

## Part 4: Differentiation Examples (Cell Types)

### Example 1: Muscle Cell (Researcher Agent)

**Specialization:** Web search + multi-hop reasoning

**Overexpression:**
- `dspy.ReAct` (complex reasoning)
- `web_search` tool
- `multi_hop_search` module

**Underexpression:**
- None (uses all stem cell capabilities)

```python
class ResearcherAgent(StemCellAgent):
    """Muscle cell: Contractile, motile, specialized for movement (search)."""

    def __init__(self, searxng_url: str):
        super().__init__(enable_tools=True)

        # OVEREXPRESSION: ReAct reasoning
        self.react = dspy.ReAct(
            "query -> answer",
            tools=[
                dspy.Tool(self._web_search, name="web_search"),
                dspy.Tool(self._lookup_page, name="lookup_page"),
            ],
            max_iters=20
        )

        # OVEREXPRESSION: Multi-hop search
        self.multi_hop = MultiHopSearchAgent(searxng_url=searxng_url)

    def _web_search(self, query: str) -> str:
        """Tool: Search SearXNG."""
        # ... implementation ...

    def _lookup_page(self, url: str) -> str:
        """Tool: Fetch page content."""
        # ... implementation ...
```

### Example 2: Neuron (Analyst Agent)

**Specialization:** Query analysis + data judgment

**Custom Signature:**
- Input: `query, device_context, memory_context, knowledge_context`
- Output: `context_summary, goals, is_sufficient, gap_description, confidence`

**Overexpression:**
- `context_analyzer`
- `data_judgment`

**Memory:**
- Mem0AI + Global RM (neurons need deep knowledge for reasoning)

```python
class AnalystAgent(StemCellAgent):
    """Neuron: Excitable signaling, specialized for analysis."""

    def __init__(self):
        # Define neuron-specific signature
        analyst_signature = dspy.Signature(
            "query, device_context, memory_context, knowledge_context -> "
            "context_summary, goals: list[str], is_sufficient: bool, "
            "gap_description, confidence: float",
            instructions="Analyze query and judge data sufficiency."
        )

        super().__init__(signature=analyst_signature, enable_tools=True)

        # OVEREXPRESSION: Analysis modules
        self.context_analyzer = dspy.Predict("query -> context_summary, goals")
        self.data_judgment = dspy.ChainOfThought(
            "query, data -> is_sufficient, gap_description"
        )
```

### Example 3: Fibroblast (Designer Agent)

**Specialization:** UI design generation

**Custom Signature:**
- Input: `query, device_context, memory_context`
- Output: `ui_pattern, rationale, widgets: list[str]`

**Overexpression:**
- `goal_extractor`
- `pattern_matcher`
- `widget_selector`

**Memory:**
- Mem0AI + Global RM (design patterns come from knowledge)

```python
class DesignerAgent(StemCellAgent):
    """Fibroblast: ECM synthesis, specialized for structure (UI)."""

    def __init__(self):
        # Define fibroblast-specific signature
        design_signature = dspy.Signature(
            "query, device_context, memory_context, knowledge_context -> "
            "ui_pattern, rationale, widgets: list[str]",
            instructions="Design UI pattern based on query and context."
        )

        super().__init__(signature=design_signature, enable_tools=True)

        # OVEREXPRESSION: Design pipeline
        self.goal_extractor = dspy.Predict("query -> goals: list[str]")
        self.pattern_matcher = dspy.Predict(
            "goals, device_context -> ui_pattern, rationale"
        )
        self.widget_selector = dspy.Predict(
            "ui_pattern, goals -> widgets: list[str]"
        )
```

### Example 4: Hepatocyte (Presenter Agent)

**Specialization:** Final output formatting

**Custom Signature:**
- Input: `content, format_type`
- Output: `formatted_output, streaming_chunks: list[str]`

**Overexpression:**
- `format_selector`
- `streaming_handler`

**Memory:**
- Mem0AI only (no RM needed - already has all data)

```python
class PresenterAgent(StemCellAgent):
    """Hepatocyte: Metabolic synthesis, specialized for output."""

    def __init__(self):
        # Define hepatocyte-specific signature
        presenter_signature = dspy.Signature(
            "content, format_type -> formatted_output, "
            "streaming_chunks: list[str]",
            instructions="Format content for presentation."
        )

        super().__init__(signature=presenter_signature)

        # OVEREXPRESSION: Formatting modules
        self.format_selector = dspy.Predict(
            "content -> format_type, rationale"
        )
        self.streaming_handler = StreamingHandler()

    def forward(self, content: str, format_type: str = "markdown"):
        """Format and stream output.

        Note: Skips knowledge retrieval because data is already provided.
        Only uses Mem0AI to remember this presentation.
        """
        # Format the content
        result = self.reasoning(content=content, format_type=format_type)
        return result
```

---

## Part 5: Memory Architecture (Extracellular Matrix)

### Key Principle: Global DSPy RM + Per-Agent Mem0AI

**Biological fact:** Cells share the extracellular environment (blood, interstitial fluid) but have their own nuclei.

**DSPy principle:**
- **DSPy RM (Retrieval)** = Shared environment (global configuration)
- **Mem0AI** = Per-agent nucleus (isolated per user)

### DSPy Configuration (Global vs Per-Agent)

```python
# =============================================================================
# GLOBAL CONFIGURATION (Done once at startup)
# =============================================================================

import dspy
from dspy.retrieve.qdrant import QdrantRM

# Configure LM globally (all agents use this)
lm = dspy.LM("ollama_chat/gemma3:4b", api_base="http://localhost:11434")

# Configure RM globally with prefetch pattern (dense → ColBERT)
# All agents share this knowledge base
dense_rm = QdrantRM(
    "agentx_knowledge",
    vector_name="dense",
    k=100  # Top 100 candidates
)

colbert_rm = QdrantRM(
    "agentx_knowledge",
    vector_name="colbert",
    k=5   # Top 5 from rerank
)

# Use prefetch wrapper for optimal retrieval
from agentx.infrastructure.retrieval import PrefetchRM
prefetch_rm = PrefetchRM(
    dense_rm=dense_rm,
    colbert_rm=colbert_rm,
    dense_k=100,
    colbert_k=5
)

# Configure globally (ONE TIME)
dspy.configure(lm=lm, rm=prefetch_rm)

# =============================================================================
# PER-AGENT CONFIGURATION (Mem0AI only)
# =============================================================================

from mem0 import MemoryClient

# Each agent gets its own Mem0AI namespace (user-scoped)
agent_alice = StemCellAgent(user_id="alice")
agent_bob = StemCellAgent(user_id="bob")

# Inject Mem0AI clients (per-user memory)
mem0_client = MemoryClient()
agent_alice.set_mem0_client(mem0_client)
agent_bob.set_mem0_client(mem0_client)

# Both agents use the SAME global RM (shared knowledge)
# But have SEPARATE Mem0AI memory (isolated conversations)
```

### Memory System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    AGENTX Memory System                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────────┐    ┌──────────────────────┐          │
│  │   Mem0AI Memory     │    │   DSPy Retrieval      │          │
│  │   (Per-Agent)       │    │   (Global Shared)     │          │
│  │                     │    │                      │          │
│  │ Namespace per user: │    │ Collection:           │          │
│  │ - alice             │    │ agentx_knowledge      │          │
│  │ - bob               │    │                      │          │
│  │ - charlie           │    │ Named vectors:        │          │
│  │                     │    │ - dense (fast)        │          │
│  │ Purpose:            │    │ - colbert (accurate)  │          │
│  │ - Conversational    │    │                      │          │
│  │   memory            │    │ Purpose:             │          │
│  │ - User preferences  │    │ - RAG documents       │          │
│  │ - Personal facts    │    │ - Web search cache    │          │
│  │                     │    │ - Knowledge base      │          │
│  │ ISOLATED per user   │    │ SHARED by all agents   │          │
│  └─────────────────────┘    └──────────────────────┘          │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Why This Architecture?

| Component | Scope | Reason |
|-----------|-------|--------|
| **DSPy LM** | Global | One LLM instance serves all agents |
| **DSPy RM** | Global | Knowledge base is shared (all agents need same facts) |
| **Mem0AI** | Per-Agent | Conversational memory must be isolated (privacy, context) |

**Analogy:**
- **DSPy RM** = Bloodstream (shared, carries nutrients/knowledge to all cells)
- **Mem0AI** = Nucleus (unique to each cell, holds individual DNA/memories)

---

## Part 6: LangGraph Integration (Developmental Biology)

### Stem Cell + LangGraph = Developmental Process

LangGraph provides the **developmental environment** (like the womb) where stem cells differentiate.

```python
from langgraph.graph import StateGraph, START, END
from typing import TypedDict

class AgentState(TypedDict):
    """Developmental state for stem cell differentiation."""
    question: str
    device_context: str
    agent_type: str  # "researcher", "analyst", "designer", etc.
    result: dict
    user_id: str

# =============================================================================
# IMPORTANT: DSPy LM and RM are configured globally at app startup
# =============================================================================
# dspy.configure(lm=lm, rm=prefetch_rm)  # Done once
# =============================================================================

# Create developmental environment
graph = StateGraph(AgentState)

# Stem cell factory (undifferentiated)
def create_stem_cell(state: AgentState):
    """Create undifferentiated stem cell based on request."""
    stem = StemCellAgent(
        user_id=state.get("user_id", "default")
    )
    # Only Mem0AI needs injection (DSPy LM/RM are global)
    stem.set_mem0_client(get_mem0_client())
    return {"stem_cell": stem}

# Differentiation function
def differentiate_agent(state: AgentState):
    """Differentiate stem cell into specialized agent."""
    stem = state["stem_cell"]
    agent_type = state["agent_type"]

    if agent_type == "researcher":
        # Differentiate → Muscle cell (with custom signature)
        return ResearcherAgent(
            stem_cell=stem,
            searxng_url="http://localhost:8080"
        )
    elif agent_type == "analyst":
        # Differentiate → Neuron (with custom signature)
        return AnalystAgent(stem_cell=stem)
    elif agent_type == "designer":
        # Differentiate → Fibroblast (with custom signature)
        return DesignerAgent(stem_cell=stem)
    else:
        # Stay pluripotent
        return stem

# Execute differentiated agent
def execute_agent(state: AgentState):
    """Execute the differentiated agent."""
    agent = state["agent"]
    # All agents use the globally configured DSPy LM and RM
    # Mem0AI provides per-user memory
    result = agent(
        question=state["question"],
        device_context=state.get("device_context", "desktop")
    )
    return {"result": result}

# Build developmental graph
graph.add_node("create_stem_cell", create_stem_cell)
graph.add_node("differentiate", differentiate_agent)
graph.add_node("execute", execute_agent)

graph.add_edge(START, "create_stem_cell")
graph.add_edge("create_stem_cell", "differentiate")
graph.add_edge("differentiate", "execute")
graph.add_edge("execute", END)

app = graph.compile()
```

---

## Part 7: Quick Reference (Differentiation Matrix)

| Cell Type | Agent | Overexpression | Signature | Memory Access |
|-----------|-------|---------------|-----------|---------------|
| **Stem Cell** | `StemCellAgent` | None (base) | Default pluripotent | Mem0AI + Global RM |
| **Muscle** | `ResearcherAgent` | ReAct + tools | Custom search signature | Mem0AI + Global RM |
| **Neuron** | `AnalystAgent` | Analysis modules | Custom analysis signature | Mem0AI + Global RM |
| **Fibroblast** | `DesignerAgent` | Design pipeline | Custom design signature | Mem0AI + Global RM |
| **Hepatocyte** | `PresenterAgent` | Formatting | Custom format signature | Mem0AI only (no RM needed) |
| **Erythrocyte** | `SequencerAgent` | Ordering logic | Custom sequence signature | Mem0AI + Global RM |
| **Osteocyte** | `WidgetSelectorAgent` | Classification | Custom classify signature | Mem0AI + Global RM |

**Key Clarification:**
- **Mem0AI**: Per-agent conversational memory (injected via `set_mem0_client()`)
- **Global RM**: DSPy's globally configured retriever (configured once via `dspy.configure(rm=...)`)
- **All agents use the global RM** - the differentiation is in their SIGNATURE and MODULES, not in memory access
- **Only PresenterAgent** might skip RM because it's a final formatting stage (already has all the data)

---

## Part 8: Implementation Checklist

### Global Configuration (App Startup)

- [ ] Configure DSPy LM globally: `dspy.configure(lm=...)`
- [ ] Configure DSPy RM globally with prefetch pattern
- [ ] Create Qdrant collections: `agentx_knowledge` (dense + colbert vectors)
- [ ] Verify global RM is accessible to all agents

### Creating a Stem Cell Agent

- [ ] Define minimal `StemCellAgent` with signature loading
- [ ] Add Mem0AI hook (per-agent, inject via setter)
- [ ] Add tool mount points (empty by default)
- [ ] Use global DSPy RM (no per-agent RM injection)
- [ ] Add `set_signature()` method for runtime differentiation

### Differentiating into Specialized Agents

- [ ] Define custom signature for the agent type
- [ ] Identify required DSPy modules (overexpression)
- [ ] Create subclass that passes signature to `super().__init__()`
- [ ] Override `forward()` to use specialized modules
- [ ] Add domain-specific tools via `add_tool()`

### Memory System Setup

- [ ] Configure Mem0AI with user-scoped namespaces
- [ ] Inject Mem0AI client via `set_mem0_client()` per agent
- [ ] Use global DSPy RM for all agents (shared knowledge)
- [ ] Ensure Mem0AI memory isolation (per user_id)

---

## Part 9: Key Insights

### 1. Minimal Stem Cell = Maximum Flexibility

The stem cell agent should have NO domain logic. Only:
- Signature loading (custom or default pluripotent signature)
- Input/output handling
- Basic reasoning via `dspy.ChainOfThought(signature)`
- Mem0AI hook (per-user memory)
- Tool mount points (empty by default)
- Uses global DSPy LM and RM (no per-agent injection)

### 2. Signature = DNA (The Core Differentiation Mechanism)

**Differentiation happens primarily through SIGNATURE changes:**
- Default signature = Pluripotent (can do anything, expert at nothing)
- Custom signature = Differentiated cell type (specialized behavior)
- `set_signature()` = Runtime differentiation

The signature defines:
- Input fields (what the agent receives)
- Output fields (what the agent produces)
- Instructions (how the agent behaves)

### 3. Global DSPy LM/RM = Bloodstream (Shared Environment)

**DSPy LM and RM are configured ONCE globally:**
- All agents share the same LLM instance
- All agents share the same knowledge base (RM with prefetch)
- No per-agent RM injection needed
- Differentiation is in SIGNATURE and MODULES, not in memory access

### 4. Mem0AI = Nucleus (Per-Agent Memory)

**Only Mem0AI needs per-agent injection:**
- User-scoped conversational memory
- Isolated per user_id (privacy)
- Injected via `set_mem0_client()`

### 5. Overexpression/Underexpression = Gene Regulation

In DSPy:
- **Overexpression** = Add modules/signatures/tools (cell specialization)
- **Underexpression** = Skip using certain capabilities (not common)
- **Signature change** = Most common differentiation method

### 6. LangGraph = Developmental Environment

LangGraph manages the differentiation process:
- State transitions = Cell fate decisions
- Edges = Signaling pathways
- Checkpoints = Developmental milestones
- Conditional routing = Morphogen gradients

### 7. All Agents Need Deep Memory (Except Final Formatting)

**Neurons (Analyst) NEED retrieval:**
- Complex reasoning requires knowledge access
- Don't disable RM for thinking agents

**Only Presenter (Hepatocyte) might skip RM:**
- Final formatting stage already has all data
- Still uses Mem0AI to remember the presentation

---

## Sources

- DSPy Tutorials: `/home/riju279/Downloads/dspy-main/dspy-main/docs/docs/tutorials/`
- R014 Backend: `/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/`
- ColBERT Integration: `docs/research/lang__/12_colbertv2_qdrant_dspy_integration.md`
- Mem0 Integration: `docs/research/mem0/01_langgraph_integration.md`

---

**Next Steps:**
- Implement `StemCellAgent` base class
- Create differentiation factory for LangGraph
- Set up per-agent memory collections
- Define agent type → cell type mapping
