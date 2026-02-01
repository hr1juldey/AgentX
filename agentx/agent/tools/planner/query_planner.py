"""DSPy QueryPlannerModule for generating execution plans.

This module defines the DSPy signature and module for analyzing query
complexity and generating execution plans with 0 to N research tasks.
"""

import dspy

from agentx.domain.models.query_plan import ExecutionPlan, ResearchTask, TaskType


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
    """

    def __init__(self):
        """Initialize the query planner module."""
        super().__init__()
        self.generate_plan = dspy.Predict(PlanQuerySignature)

    def forward(self, query: str, conversation_context: str = "") -> dspy.Prediction:
        """Generate execution plan for the query.

        Args:
            query: User's query
            conversation_context: Previous conversation (optional)

        Returns:
            dspy.Prediction: Contains ExecutionPlan
        """
        # Generate plan using LLM
        result = self.generate_plan(
            query=query,
            conversation_context=conversation_context,
        )

        # Parse task descriptions from JSON
        import json

        tasks: list[ResearchTask] = []

        try:
            task_data_list = json.loads(result.task_descriptions)  # type: ignore[attr-defined]
            for task_data in task_data_list:
                task = ResearchTask(
                    task_id=task_data.get("task_id", f"task_{len(tasks)}"),
                    task_type=TaskType(task_data.get("task_type", "search")),
                    description=task_data.get("description", ""),
                    query=task_data.get("query", query),
                    dependencies=task_data.get("dependencies", []),
                )
                tasks.append(task)
        except (json.JSONDecodeError, ValueError):
            # Default: single search task if parsing fails
            if result.needs_research.lower() == "true":  # type: ignore[attr-defined]
                tasks = [
                    ResearchTask(
                        task_id="search_1",
                        task_type=TaskType.SEARCH,
                        description="Search for information",
                        query=query,
                        dependencies=[],
                    )
                ]

        # Parse duration
        duration: int | None = None
        try:
            duration = (
                int(result.estimated_duration)  # type: ignore[attr-defined]
                if result.estimated_duration  # type: ignore[attr-defined]
                else None
            )
        except ValueError:
            duration = None

        # Create execution plan
        execution_plan = ExecutionPlan(
            query=query,
            needs_research=result.needs_research.lower() == "true",  # type: ignore[attr-defined]
            research_tasks=tasks,
            estimated_duration=duration,
            reasoning=result.reasoning,  # type: ignore[attr-defined]
        )

        return dspy.Prediction(
            execution_plan=execution_plan,
        )
