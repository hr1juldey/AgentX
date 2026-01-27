# Function Postmortem: services/master_agent/orchestration/early_phases.py

## Metadata
- **File**: services/master_agent/orchestration/early_phases.py
- **Lines of Code**: 148
- **Purpose**: Phases 1-4: Analyst, Researcher, Contextualizer, Analyst Judgment
- **Dependencies**: PhaseExecutor, logging, data_tracking, logging helpers

---

## Analysis

**File Status**: PRODUCTION DSPy MODULE

**Purpose**: Implements early pipeline phases (1-4) focused on data gathering, research, contextualization, and quality judgment.

---

## Classes Extracted

### EarlyPhases

**Purpose**: Early pipeline phases (1-4): Data gathering and analysis.

**Lines**: 28-148

**Key Code**:
```python
class EarlyPhases:
    """Early pipeline phases (1-4): Data gathering and analysis."""

    def __init__(self, executor: PhaseExecutor) -> None:
        self.executor = executor

    def run_analyst_phase(
        self,
        analyst: "AnalystAgent",
        user_query: str,
        device_context: str,
    ) -> dict[str, Any]:
        """Phase 1: ANALYST - Understand query and context."""
        logger.info("  [ANALYST] Understanding query context...")
        result = self.executor.execute_phase(
            "analysis_qa",
            lambda: analyst(user_query=user_query, device_context=device_context),
        )
        log_analysis_result(result)
        return result

    def run_researcher_phase(
        self,
        researcher: "ResearcherAgent",
        analysis_result: dict,
    ) -> dict[str, Any]:
        """Phase 2: RESEARCHER - Fetch live data."""
        search_terms = analysis_result.get("search_terms", [])
        if search_terms:
            logger.info(f"  [RESEARCHER] Search terms: {search_terms[:5]}")
        else:
            search_query = (
                analysis_result.get("goal") or analysis_result.get("query") or ""
            )
            logger.info(f"  [RESEARCHER] No search terms, using: '{search_query[:80]}...'")
        result = self.executor.execute_phase(
            "research_qa",
            lambda: researcher(analysis=analysis_result),
        )
        log_research_result(result)
        return result

    def run_contextualizer_phase(
        self,
        data_contextualizer: "DataContextualizerAgent",
        research_result: dict,
    ) -> dict[str, Any]:
        """Phase 3: DATA CONTEXTUALIZER - Rerank, filter, contextualize."""
        doc_count = len(research_result.get("documents", []))
        logger.info(f"  [CONTEXTUALIZER] Processing {doc_count} documents...")
        result = self.executor.execute_phase(
            "contextualization_qa",
            lambda: data_contextualizer(research_data=research_result),
        )
        track_contextualizer_output(result)
        return result

    def run_analyst_judgment_phase(
        self,
        analyst: "AnalystAgent",
        user_query: str,
        device_context: str,
        contextualized_result: dict,
    ) -> dict[str, Any]:
        """Phase 4: ANALYST (Pass 2) - Judge data quality."""
        logger.info("  [ANALYST] Judging data quality...")
        result = self.executor.execute_phase(
            "judgment_qa",
            lambda: analyst(
                user_query=user_query,
                device_context=device_context,
                contextualized_data=contextualized_result,
                pass_number=2,
            ),
        )
        log_judgment_result(result)
        return result
```

**What Works**:
- ✅ Consistent pattern: log → execute → log → return
- ✅ Lambda wrapping enables exception handling by executor
- ✅ QA checkpoint names match expected names
- ✅ Logging helper functions for structured output
- ✅ Data tracking for debugging
- ✅ Analyst runs twice with different parameters

**Mistakes Found**: None

**Behavioral Notes**:
- Each phase wrapped in execute_phase() for QA
- Search terms fallback to goal/query if missing
- Analyst pass 2 includes contextualized_data and pass_number
- Document count logged before contextualization
- All results logged after execution

**Dependencies**:
- **Imports**: PhaseExecutor, logging, log_* helpers, track_contextualizer_output
- **Uses**: executor.execute_phase(), logging helpers, data tracking

**Reusability**: High - pattern for any multi-phase data pipeline

---

## File Summary

**Total Classes**: 1
**Lines of Code**: 148

**Overall Assessment**: Clean, consistent phase execution pattern. The lambda wrapping enables elegant exception handling and QA tracking.

**Key Learnings for Real AgentX**:
1. ✅ Consistent phase pattern: log → execute → log → return
2. ✅ Lambda wrapping for exception handling
3. ✅ Agent can run multiple times with different parameters
4. ✅ Helper functions for logging (keeps code clean)
5. ✅ Data tracking for debugging
6. ✅ Fallback logic for missing fields (search_terms)

**Reuse for Real AgentX**: ✅ HIGH - Phase execution pattern
