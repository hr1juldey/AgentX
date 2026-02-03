"""DSPy QueryPlannerModule for generating execution plans.

This module defines the DSPy signature and module for analyzing query
complexity and generating execution plans with 0 to N research tasks.
"""

import dspy

from agentx.agent.tools.planner.query_planner_helpers import (
    build_guidance_context,
    parse_duration,
    parse_task_descriptions,
)
from agentx.domain.models.query_plan import ExecutionPlan


class PlanQuerySignature(dspy.Signature):
    """Signature for query planning analysis.

    The LLM analyzes the query and determines:
    1. Is research needed? (simple queries get 0 tasks)
    2. What research tasks are needed? (0 to N tasks)
    3. What's the estimated duration?

    Key insight: Simple queries (0 tasks) skip research entirely.
    """

    query = dspy.InputField(desc="User's query")
    conversation_context = dspy.InputField(
        desc="Previous conversation messages (if any)",
        default="",
    )

    needs_research = dspy.OutputField(
        desc="True if research is needed, False for direct answer",
    )
    task_count = dspy.OutputField(
        desc="Number of research tasks (0 for simple queries)",
    )
    task_descriptions = dspy.OutputField(
        desc="JSON string of task descriptions: [{'task_id', 'task_type', 'description', 'query', 'dependencies'}]",
    )
    estimated_duration = dspy.OutputField(
        desc="Estimated seconds to complete (integer or null)",
    )
    reasoning = dspy.OutputField(
        desc="Why this plan was chosen",
    )


class QueryPlannerModule(dspy.Module):
    """DSPy module for generating execution plans.

    This module analyzes query complexity and generates an execution plan
    with 0 to N research tasks based on the query's needs.

    Simple queries (What is 2+2?) → 0 tasks → direct answer
    Complex queries (Compare iPhone vs Pixel) → N tasks → research workers

    ENHANCED with memory-guided search planning:
    - Optional search_guidance parameter from SearchGuidanceModule
    - Guidance enhances task generation but PRESERVES 0-to-N pattern
    """

    def __init__(self):
        """Initialize the query planner module."""
        super().__init__()
        self.generate_plan = dspy.Predict(PlanQuerySignature)

    def forward(
        self,
        query: str,
        conversation_context: str = "",
        search_guidance: dict | None = None,
    ) -> dspy.Prediction:
        """Generate execution plan for the query.

        Args:
            query: User's query
            conversation_context: Previous conversation (optional)
            search_guidance: Optional memory-guided search parameters from
                SearchGuidanceModule (enhances planning but PRESERVES 0-to-N pattern)

        Returns:
            dspy.Prediction: Contains ExecutionPlan
        """
        # Build enhanced context from search guidance (if provided)
        guidance_context = build_guidance_context(search_guidance)

        # Combine conversation context with guidance
        enhanced_context = conversation_context
        if guidance_context:
            enhanced_context = (
                f"{conversation_context}\n[Memory Guidance: {guidance_context}]"
            )

        # Generate plan using LLM with enhanced context
        result = self.generate_plan(
            query=query,
            conversation_context=enhanced_context,
        )

        # Parse task descriptions from JSON
        needs_research = result.needs_research.lower() == "true"  # type: ignore[attr-defined]
        tasks = parse_task_descriptions(
            result.task_descriptions,  # type: ignore[attr-defined]
            query,
            needs_research,
        )

        # Parse duration
        duration = parse_duration(result.estimated_duration)  # type: ignore[attr-defined]

        # Create execution plan
        execution_plan = ExecutionPlan(
            query=query,
            needs_research=needs_research,
            research_tasks=tasks,
            estimated_duration=duration,
            reasoning=result.reasoning,  # type: ignore[attr-defined]
        )

        return dspy.Prediction(
            execution_plan=execution_plan,
        )
