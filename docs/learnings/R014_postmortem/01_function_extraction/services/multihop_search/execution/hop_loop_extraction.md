# Function Postmortem: services/multihop_search/execution/hop_loop.py

## Metadata
- **File**: services/multihop_search/execution/hop_loop.py
- **Lines of Code**: 123
- **Purpose**: Executes a single iteration of the multi-hop search loop
- **Dependencies**: logging, dspy, services.multihop_search.execution (helpers, progress)

---

## Analysis

**File Status**: PRODUCTION EXECUTION MODULE

**Purpose**: SRP-compliant module that executes one hop iteration (search, answer, assess, plan).

---

## Classes Extracted

### HopLoopExecutor

**Purpose**: Executes a single iteration of the multi-hop search loop with full orchestration of search, answer, assessment, and planning.

**Lines**: 25-122

**Key Code**:
```python
class HopLoopExecutor:
    """Executes a single iteration of the multi-hop search loop.

    SRP: Execute one hop iteration only.
    """

    def __init__(
        self,
        search: "HopSearch",
        assessment: "HopAssessment",
        planning: "HopPlanning",
        answer_module: dspy.ChainOfThought,
        max_hops: int,
        stop_threshold: float,
        progress_callback: Any,
    ) -> None:
        """Initialize hop loop executor."""
        self.search = search
        self.assessment = assessment
        self.planning = planning
        self.answer_module = answer_module
        self.max_hops = max_hops
        self.stop_threshold = stop_threshold
        self.progress_tracker = HopProgressTracker(progress_callback, max_hops)

    async def execute_hop_iteration(
        self,
        question: str,
        hop_num: int,
        plan_result: dspy.Prediction | None,
        hop_answers: list[str],
        hop_contexts: list[str],
        hop_queries: list[str],
    ) -> tuple[str, str, dspy.Prediction | None, bool]:
        """Execute a single hop iteration.

        Returns:
            Tuple of (context, search_query, new_plan_result, should_stop)
        """
        # Generate search query
        search_query, strategy = self.search.generate_query(
            question, hop_num, plan_result
        )
        hop_queries.append(search_query)

        self.progress_tracker.send_hop_start(hop_num, strategy, search_query)

        # Execute search
        context, results, _ = await self.search.execute(search_query, strategy)
        hop_contexts.append(context)

        self.progress_tracker.send_documents_found(hop_num, len(results))

        # Generate answer using helper
        answer = generate_hop_answer(self.answer_module, question, context)
        hop_answers.append(answer)

        # Assess completeness
        self.progress_tracker.send_assessing(hop_num)

        should_stop, reasoning, assessment = await self.assessment.assess(
            question=question,
            hop_answers=hop_answers,
            results=results,
            stop_threshold=self.stop_threshold,
        )

        if should_stop:
            self.progress_tracker.send_complete(hop_num, reasoning)
            return context, search_query, plan_result, True

        # Plan next hop
        new_plan_result = await self.planning.plan_next(
            question=question,
            assessment=assessment,
            hop_queries=hop_queries,
            hop_num=hop_num,
        )

        return context, search_query, new_plan_result, False
```

**What Works**:
- ✅ SRP compliance: Only executes one hop iteration
- ✅ Progress tracking at every stage (hop_start, documents_found, assessing, complete)
- ✅ Early return on should_stop (no unnecessary planning)
- ✅ Delegates to specialized modules (search, assessment, planning)
- ✅ Accumulates hop_answers, hop_contexts, hop_queries in-place
- ✅ Returns should_stop flag for orchestrator to control loop

**Mistakes Found**: None - clean orchestration

**Behavioral Notes**:
- search.generate_query() returns (search_query, strategy) tuple
- search.execute() returns (context, results, _)
- assessment.assess() returns (should_stop, reasoning, assessment)
- planning.plan_next() returns new_plan_result
- Progress is sent before each operation for UI feedback

**Dependencies**:
- **Imports**: logging, dspy, services.multihop_search.execution.hop_helpers.generate_hop_answer, services.multihop_search.execution.progress.HopProgressTracker
- **Uses**: HopSearch, HopAssessment, HopPlanning, dspy.ChainOfThought, HopProgressTracker

**Reusability**: HIGH - This hop iteration pattern is reusable for any iterative retrieval system.

---

## File Summary

**Total Classes**: 1
**Lines of Code**: 123

**Overall Assessment**: Clean SRP-compliant execution module that orchestrates one hop iteration. Progress tracking at each stage is excellent for UX.

**Key Learnings for Real AgentX**:
1. ✅ SRP execution: Execute one iteration, return control to orchestrator
2. ✅ Progress milestones: hop_start, documents_found, assessing, complete
3. ✅ Early exit: Return should_stop immediately without unnecessary planning
4. ✅ In-place accumulation: Modify hop_answers, hop_contexts, hop_queries in place
5. ✅ Tuple returns: Return structured tuples for clear data flow
6. ✅ Delegation: Use specialized modules for search, assessment, planning

**Reuse for Real AgentX**: ✅ DIRECT - Use this hop iteration pattern for any multi-stage retrieval system.
