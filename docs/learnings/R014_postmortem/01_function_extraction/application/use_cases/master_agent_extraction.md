# Function Postmortem: application/use_cases/master_agent.py

## Metadata
- **File**: application/use_cases/master_agent.py
- **Lines of Code**: 113
- **Purpose**: Master Agent use cases (Clean Architecture facade)
- **Dependencies**: `config.settings`, `services.master_agent`, `services.pipeline.*`, `services.hydrators.*`

---

## Analysis

**File Status**: CLEAN ARCHITECTURE USE CASE LAYER

**Purpose**: Use case facades that wrap the existing Master Agent service. Encapsulates pipeline and hydrator setup complexity.

---

## Classes Extracted

### MasterAgentUseCase

**Purpose**: Use case for Master Agent widget generation operations

**Signature**:
```python
class MasterAgentUseCase:
```

**Lines**: 8-101

**Architecture**: Facade pattern over MasterAgent

**Note**: Phase 1 delegates to factory. Phase 3 will implement full use case logic.

---

### create_master_agent

**Purpose**: Create a Master Agent instance with callbacks

**Signature**:
```python
def create_master_agent(
    self,
    widget_callback,  # type: ignore
    qa_callback,  # type: ignore
):
```

**Lines**: 18-32

**Key Code**:
```python
def create_master_agent(
    self,
    widget_callback,  # type: ignore
    qa_callback,  # type: ignore
):
    """Create a Master Agent instance with callbacks.

    Phase 1: Delegates to existing factory.
    """
    from services.master_agent import create_master_agent

    return create_master_agent(
        widget_callback=widget_callback,
        qa_callback=qa_callback,
    )
```

**What Works**:
- ✅ Facade pattern (delegates to factory)
- ✅ Callback parameters for async handling
- ✅ type: ignore for callable parameters
- ✅ Lazy import

**Mistakes Found**:
- ⚠️ No type hints for callbacks (type: ignore used)
- **Recommendation**: Use `Callable[[dict], None]` for callbacks

**Reusability**: HIGH - Factory facade pattern

---

### setup_master_agent_with_pipeline

**Purpose**: Create and fully configure a Master Agent with pipeline and hydrators

**Signature**:
```python
def setup_master_agent_with_pipeline(
    self,
    widget_callback,  # type: ignore
    qa_callback,  # type: ignore
):
```

**Lines**: 34-100

**Complexity**: O(n) where n is number of pipeline agents + hydrators

**Key Code**:
```python
def setup_master_agent_with_pipeline(
    self,
    widget_callback,  # type: ignore
    qa_callback,  # type: ignore
):
    """Create and fully configure a Master Agent with pipeline and hydrators.

    This encapsulates the complexity of setting up all pipeline agents
    and hydrators, maintaining a clean architectural boundary.

    Returns a configured Master Agent ready for execution.
    """
    from config.settings import settings
    from services.hydrators.card_hydrator import CardHydrator
    from services.hydrators.chart_hydrator import ChartHydrator
    from services.hydrators.form_hydrator import FormHydrator
    from services.hydrators.gallery_hydrator import GalleryHydrator
    from services.hydrators.image_hydrator import ImageHydrator
    from services.hydrators.markdown_hydrator import MarkdownHydrator
    from services.master_agent import DeliveryPlan, create_master_agent
    from services.pipeline.analyst import AnalystAgent
    from services.pipeline.data_contextualizer import DataContextualizerAgent
    from services.pipeline.designer import DesignerAgent
    from services.pipeline.presenter import PresenterAgent
    from services.pipeline.researcher import ResearcherAgent
    from services.pipeline.sequencer import SequencerAgent
    from services.pipeline.widget_selector import WidgetSelectorAgent

    # Create master agent
    master_agent = create_master_agent(
        widget_callback=widget_callback,
        qa_callback=qa_callback,
    )

    # Initialize all pipeline agents
    analyst = AnalystAgent()
    researcher = ResearcherAgent(searxng_url=settings.searxng_url)

    data_contextualizer = DataContextualizerAgent()
    designer = DesignerAgent()
    widget_selector = WidgetSelectorAgent()
    sequencer = SequencerAgent()
    presenter = PresenterAgent()

    # Initialize all hydrators
    hydrators = [
        ChartHydrator(),
        MarkdownHydrator(),
        CardHydrator(),
        FormHydrator(),
        ImageHydrator(),
        GalleryHydrator(),
    ]

    # Configure master agent with pipeline
    master_agent.set_pipeline_agents(
        analyst=analyst,
        researcher=researcher,
        data_contextualizer=data_contextualizer,
        designer=designer,
        widget_selector=widget_selector,
        sequencer=sequencer,
        presenter=presenter,
        hydrators=hydrators,
    )

    return master_agent, DeliveryPlan
```

**What Works**:
- ✅ **Encapsulates Complexity**: Hides pipeline setup from API layer
- ✅ **All 7 Pipeline Agents**: analyst, researcher, data_contextualizer, designer, widget_selector, sequencer, presenter
- ✅ **All 6 Hydrators**: chart, markdown, card, form, image, gallery
- ✅ **Settings Integration**: Uses settings.searxng_url
- ✅ **Tuple Return**: Returns master_agent and DeliveryPlan
- ✅ **Lazy Imports**: All imports inside function
- ✅ **Clear Structure**: Grouped by pipeline agents, hydrators, configuration

**Mistakes Found**:
- ⚠️ Hardcoded hydrator list (6 hydrators)
- **Issue**: If new hydrator added, must update this list
- **Mitigation**: Could use hydrator registry pattern

**Behavioral Notes**:
- Creates master agent with callbacks
- Initializes all pipeline agents (7 total)
- Initializes all hydrators (6 total)
- Configures master agent with set_pipeline_agents()
- Returns tuple: (master_agent, DeliveryPlan)

**Dependencies**:
- **Imports**: 13 different service modules
- **Called by**: API routes for master agent endpoints
- **Returns**: Configured MasterAgent + DeliveryPlan

**Reusability**: HIGH - Complete pipeline setup pattern

---

## Functions Extracted

### get_master_agent_use_case

**Purpose**: Singleton getter for dependency injection

**Signature**:
```python
def get_master_agent_use_case() -> MasterAgentUseCase:
```

**Lines**: 107-112

**Key Code**:
```python
# Singleton getter for dependency injection
_master_agent_use_case: MasterAgentUseCase | None = None


def get_master_agent_use_case() -> MasterAgentUseCase:
    """Get singleton instance of MasterAgentUseCase."""
    global _master_agent_use_case
    if _master_agent_use_case is None:
        _master_agent_use_case = MasterAgentUseCase()
    return _master_agent_use_case
```

**What Works**:
- ✅ Singleton pattern
- ✅ Lazy initialization
- ✅ Global variable with type annotation
- ✅ Dependency injection friendly

**Mistakes Found**: None

**Reusability**: HIGH - Singleton getter pattern for DI

---

## File Summary

**Total Classes**: 1
**Total Functions**: 2 methods + 1 getter
**Lines of Code**: 113

**Violations**: None

**Success Patterns**:
- ✅ **Use Case Facades**: Wrap services with use case classes
- ✅ **Encapsulates Complexity**: setup_master_agent_with_pipeline() hides 13 imports
- ✅ **Complete Pipeline Setup**: All 7 agents + 6 hydrators
- ✅ **Singleton Getters**: Global + getter for DI
- ✅ **Lazy Imports**: All imports inside functions
- ✅ **Tuple Return**: Returns master_agent + DeliveryPlan

**Overall Assessment**: EXCELLENT - Clean Architecture use case with complete pipeline setup.

**Key Learnings for Real AgentX**:
1. ✅ **Encapsulate Setup**: Use use case to hide complex initialization
2. ✅ **Complete Pipeline**: Initialize all agents and hydrators in one place
3. ✅ **Lazy Imports**: Import 13+ modules inside function
4. ✅ **Tuple Return**: Return multiple related objects
5. ⚠️ **Hardcoded Lists**: Consider registry pattern for extensibility
6. ⚠️ **Callback Types**: Use Callable[[dict], None] instead of type: ignore

**Reuse for Real AgentX**: ✅ REQUIRED - Use this pipeline setup pattern.

---

## Architectural Note

**Complete Master Agent Pipeline** (7 agents + 6 hydrators):

**Pipeline Agents** (in order):
1. **AnalystAgent**: Analyzes user query
2. **ResearcherAgent**: Searches SearXNG
3. **DataContextualizerAgent**: Contextualizes data
4. **DesignerAgent**: Design decisions
5. **WidgetSelectorAgent**: Selects widgets
6. **SequencerAgent**: Orders widgets
7. **PresenterAgent**: Formats presentation

**Hydrators** (data → widgets):
1. **ChartHydrator**: Numerical data → charts
2. **MarkdownHydrator**: Text → markdown widgets
3. **CardHydrator**: Stats → card widgets
4. **FormHydrator**: Inputs → form widgets
5. **ImageHydrator**: Images → image widgets
6. **GalleryHydrator**: Collections → gallery widgets

This setup_master_agent_with_pipeline() function encapsulates ALL of this complexity.
