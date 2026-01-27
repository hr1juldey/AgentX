# Function Extraction: services/pipeline/presenter.py

## File Overview
**Path**: `/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/services/pipeline/presenter.py`
**Purpose**: PRESENTER Agent - Polishes presentation and performs final QA
**Lines**: 121
**Phase**: Phase 8 - Final Polish + QA

---

## Classes and Functions

### `PresenterAgent` (Class)

**Purpose**: DSPy Module that polishes widgets, checks flow, and performs QA.

**Signature**:
```python
class PresenterAgent(dspy.Module):
    def __init__(self):
        # Initializes 3 presentation tools + 2 helpers

    def forward(
        self,
        widgets: list,
        sequence: list,
        design: Optional[dict] = None,
        researched_data: Optional[dict] = None,
    ) -> dict:

    def get_progress_status(self, phase: str = "polishing") -> dict:
```

**Lines**: 30-120

**Key Code Snippet**:
```python
def forward(
    self,
    widgets: list,
    sequence: list,
    design: Optional[dict] = None,
    researched_data: Optional[dict] = None,
) -> dict:
    design_data = design or {}
    sequence_list = (
        sequence.get("sequence", []) if isinstance(sequence, dict) else sequence
    )

    # Check narrative flow and pacing
    step_start = time.time()
    logger.info("  [PRESENTER] Checking narrative flow...")
    flow_result_raw = self.flow_checker(sequence=sequence_list, widgets=widgets)
    flow_result: dict = (
        flow_result_raw if hasattr(flow_result_raw, "get") else {}
    )
    step_time = time.time() - step_start
    log_flow_check_result(flow_result, step_time)

    # Polish widget content
    step_start = time.time()
    logger.info("  [PRESENTER] Polishing content...")
    polish_result_raw = self.polisher(widgets=widgets, sequence=sequence_list)
    polish_result: dict = (
        polish_result_raw if hasattr(polish_result_raw, "get") else {}
    )
    step_time = time.time() - step_start
    log_polish_result(polish_result, widgets, step_time)

    # Final QA checks
    step_start = time.time()
    logger.info("  [PRESENTER] Running QA checks...")
    qa_result_raw = self.qa_finalizer(widgets=widgets, sequence=sequence_list)
    qa_result: dict = (
        qa_result_raw if hasattr(qa_result_raw, "get") else {}
    )
    step_time = time.time() - step_start
    log_qa_result(qa_result, step_time)

    # Build presentation_ready dict
    return self._result_builder.build_presentation_ready(
        widgets=widgets,
        sequence_list=sequence_list,
        design_data=design_data,
        flow_result=flow_result,
        polish_result=polish_result,
        qa_result=qa_result,
        researched_data=researched_data or {},
    )
```

**What Works**:
1. **Step timing**: Uses `time.time()` to measure each pipeline stage
2. **Type flexibility**: Handles both dict and list sequence inputs
3. **Three-stage pipeline**: flow check → polish → QA
4. **Builder pattern**: Delegates final output construction to PresenterResultBuilder

**Mistakes Found**:
None - clean three-stage orchestration

**Behavioral Notes**:
- Each stage is timed for performance monitoring
- Flow checker validates narrative coherence
- Polisher enhances widget content
- QA finalizer ensures quality standards

**Dependencies**:
- `services.pipeline.presenter_logging` - log_flow_check_result, log_polish_result, log_qa_result
- `services.pipeline.presenter_modules` - PresenterResultBuilder, PresenterProgressTracker
- `services.tools.presenter` - FlowCheckerModule, PolisherModule, QAFinalizeModule

**Reusability**: High - Generic presentation preparation

---

### `get_progress_status()` (Method)

**Purpose**: Get progress status for UI updates during polishing.

**Signature**:
```python
def get_progress_status(self, phase: str = "polishing") -> dict:
```

**Lines**: 111-120

**Reusability**: Medium - Specific to UI progress tracking

---

## Helper Classes and Functions

### `PresenterResultBuilder.build_presentation_ready()`

**Purpose**: Build presentation_ready dict from all pipeline results.

**Signature**:
```python
@staticmethod
def build_presentation_ready(
    widgets: list,
    sequence_list: list,
    design_data: dict,
    flow_result: dict,
    polish_result: dict,
    qa_result: dict,
    researched_data: dict,
) -> Dict[str, Any]:
```

**Lines**: presenter_modules/result_builder.py 31-98

**Key Code Snippet**:
```python
@staticmethod
def _ensure_list(value) -> List[str]:
    """Ensure value is a list of strings."""
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return value
    return []

def build_presentation_ready(
    widgets: list,
    sequence_list: list,
    design_data: dict,
    flow_result: dict,
    polish_result: dict,
    qa_result: dict,
    researched_data: dict,
) -> Dict[str, Any]:
    presentation_ready = {
        "widgets": polish_result.get("polished_content", widgets),
        "enhanced_widgets": polish_result.get("enhanced_content", widgets),
        "transition_suggestions": polish_result.get("transition_suggestions", []),
        "delivery_sequence": sequence_list,
        "flow_analysis": {
            "narrative_flow": flow_result.get("flow_analysis", "Coherent flow"),
            "flow_issues": flow_result.get("flow_issues", []),
            "pacing_analysis": flow_result.get("pacing_analysis", "Appropriate pacing"),
            "pacing_issues": flow_result.get("pacing_issues", []),
        },
        "qa_report": {
            "quality_check": qa_result.get("quality_check", "passed"),
            "accessibility_check": qa_result.get("accessibility_check", "passed"),
            "format_check": qa_result.get("format_check", "passed"),
            "sequence_check": qa_result.get("sequence_check", "passed"),
            "all_passed": qa_result.get("all_passed", True),
            "issues": qa_result.get("issues", []),
        },
        "ready_to_send": qa_result.get("ready_to_send", True),
        "design_context": {
            "color_scheme": design_data.get("color_scheme", {}),
            "visual_hierarchy": design_data.get("visual_hierarchy", []),
        },
        "query": researched_data.get("query", ""),
        "researched_data": researched_data,
        "beautiful_data": researched_data.get("beautiful_data", {}),
    }

    # Add warnings if issues detected
    issues: List[str] = []
    issues.extend(_ensure_list(flow_result.get("flow_issues", [])))
    issues.extend(_ensure_list(flow_result.get("pacing_issues", [])))
    issues.extend(_ensure_list(qa_result.get("issues", [])))

    if issues:
        presentation_ready["warnings"] = issues
        presentation_ready["requires_review"] = True

    return presentation_ready
```

**What Works**:
1. **_ensure_list() helper**: Handles string/list/other type conversion
2. **Comprehensive output**: Combines all pipeline stages into single dict
3. **Warning aggregation**: Collects issues from all stages
4. **Conditional flags**: Sets `requires_review` only when issues exist

**Reusability**: High - Generic result builder pattern

---

## Key Patterns

1. **Step Timing Pattern**:
```python
step_start = time.time()
# ... do work ...
step_time = time.time() - step_start
log_result(result, step_time)
```

2. **Type Flexibility Pattern**:
```python
sequence_list = (
    sequence.get("sequence", []) if isinstance(sequence, dict) else sequence
)
```

3. **Warning Aggregation Pattern**:
```python
issues = []
issues.extend(_ensure_list(flow_result.get("flow_issues", [])))
if issues:
    presentation_ready["warnings"] = issues
    presentation_ready["requires_review"] = True
```

---

## Lessons Learned

1. **Time your pipeline stages**: Step timing helps identify bottlenecks
2. **Handle multiple input types**: Sequence can be dict or list - handle both
3. **Aggregate warnings**: Collect issues from all stages for user awareness
4. **Use builder pattern**: Keeps orchestration method clean and focused
