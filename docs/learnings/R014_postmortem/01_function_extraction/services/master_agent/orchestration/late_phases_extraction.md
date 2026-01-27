# Function Postmortem: services/master_agent/orchestration/late_phases.py

## Metadata
- **File**: services/master_agent/orchestration/late_phases.py
- **Lines of Code**: 151
- **Purpose**: Phases 5-8: Designer, Widget Selector, Sequencer, Presenter
- **Dependencies**: PhaseExecutor, logging, data_tracking, logging helpers

---

## Analysis

**File Status**: PRODUCTION DSPy MODULE

**Purpose**: Implements late pipeline phases (5-8) focused on design enhancement, widget selection, sequencing, and final presentation.

---

## Classes Extracted

### LatePhases

**Purpose**: Late pipeline phases (5-8): Design and presentation.

**Lines**: 28-151

**Key Code**:
```python
class LatePhases:
    """Late pipeline phases (5-8): Design and presentation."""

    def __init__(self, executor: PhaseExecutor) -> None:
        self.executor = executor

    def run_designer_phase(
        self,
        designer: "DesignerAgent",
        contextualized_result: dict,
        analysis_result: dict,
    ) -> dict[str, Any]:
        """Phase 5: DESIGNER - Add POVs, color schemes."""
        logger.info("  [DESIGNER] Adding design context...")
        result = self.executor.execute_phase(
            "design_qa",
            lambda: designer(
                researched_data=contextualized_result,
                analysis=analysis_result,
            ),
        )
        log_design_result(result)
        return result

    def run_widget_selector_phase(
        self,
        widget_selector: "WidgetSelectorAgent",
        design_result: dict,
        device_context: str,
    ) -> dict[str, Any]:
        """Phase 6: WIDGET SELECTOR - Choose widgets."""
        logger.info("  [WIDGET SELECTOR] Choosing widgets...")
        result = self.executor.execute_phase(
            "widget_selection_qa",
            lambda: widget_selector(
                designed_data=design_result,
                device_context=device_context,
            ),
        )
        log_widget_selection(result)
        return result

    def run_sequencer_phase(
        self,
        sequencer: "SequencerAgent",
        widget_selection: dict,
        user_query: str,
    ) -> dict[str, Any]:
        """Phase 7: SEQUENCER - Plan delivery order."""
        logger.info("  [SEQUENCER] Planning delivery order...")
        result = self.executor.execute_phase(
            "sequence_qa",
            lambda: sequencer(
                widgets=widget_selection.get("widgets", []),
                user_query=user_query,
            ),
        )
        return result

    def run_presenter_phase(
        self,
        presenter: "PresenterAgent",
        widget_selection: dict,
        sequence_plan: dict,
        design_result: dict,
        researched_data: dict,
    ) -> dict[str, Any]:
        """Phase 8: PRESENTER - Final polish and QA."""
        logger.info("  [PRESENTER] Final polish...")
        track_presenter_input(researched_data)
        result = self.executor.execute_phase(
            "presentation_qa",
            lambda: presenter(
                widgets=widget_selection.get("widgets", []),
                sequence=sequence_plan.get("sequence", []),
                design=design_result,
                researched_data=researched_data,
            ),
        )
        return result
```

**What Works**:
- ✅ Consistent pattern with EarlyPhases (log → execute → log → return)
- ✅ Lambda wrapping for exception handling
- ✅ Safe dict access with .get() fallbacks
- ✅ Data accumulation (contextualized → designed → widgets → sequence)
- ✅ Research data passed through to presenter for hydrators

**Mistakes Found**: None

**Behavioral Notes**:
- Designer: Adds POVs and color schemes to research
- Widget Selector: Chooses widgets based on design and device
- Sequencer: Plans delivery order (consultant-style)
- Presenter: Final polish before hydration
- All phases use .get() for safe dict access

**Dependencies**:
- **Imports**: PhaseExecutor, logging, log_* helpers, track_presenter_input
- **Uses**: executor.execute_phase(), logging helpers, data tracking

**Reusability**: High - pattern for design/presentation pipeline

---

## File Summary

**Total Classes**: 1
**Lines of Code**: 151

**Overall Assessment**: Clean implementation of late phases. The data accumulation pattern and safe dict access are production-ready.

**Key Learnings for Real AgentX**:
1. ✅ Consistent phase pattern (matches EarlyPhases)
2. ✅ Lambda wrapping for exception handling
3. ✅ Safe dict access with .get() fallbacks
4. ✅ Data accumulation through phases
5. ✅ Research data passed to final phase for hydrators
6. ✅ Device context considered in widget selection

**Reuse for Real AgentX**: ✅ HIGH - Late phase pattern
