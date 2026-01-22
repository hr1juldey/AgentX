# =============================================================================
# AGENTX Multi-Hop Search - DSPy Agents
# =============================================================================
# SRP-compliant modules: Assessor, Planner, MultiHopSearchAgent
# =============================================================================

from __future__ import annotations

import logging
import time
from typing import Any, Callable

import dspy

from services.multihop_search.schemas import HopEvent
from services.multihop_search.search_client import get_search_client, SearchResultItem
from services.multihop_search.signatures import (
    AnswerWithSources,
    CheckCompleteness,
    GenerateNextQuery,
    SynthesizeFinalAnswer,
)
from services.multihop_search.time_estimator import get_time_estimator

logger = logging.getLogger(__name__)


class CompletenessAssessor(dspy.Module):
    """SRP: Only assesses whether current information is sufficient.

    Does NOT plan next hops - that's HopPlanner's job.
    """

    def __init__(self) -> None:
        super().__init__()
        self.check = dspy.ChainOfThought(CheckCompleteness)

    def forward(
        self,
        question: str,
        current_answer: str,
        documents_summary: str,
    ) -> dspy.Prediction:
        """Check if we have enough information.

        Args:
            question: Original question
            current_answer: Current best answer from all hops
            documents_summary: Brief summary of documents found

        Returns:
            Prediction with is_sufficient, confidence, gap_description
        """
        return self.check(  # type: ignore[bad-return]
            question=question,
            current_answer=current_answer,
            documents_summary=documents_summary,
        )


class HopPlanner(dspy.Module):
    """SRP: Only plans the next search hop.

    Takes gap_description and outputs next_query + strategy.
    """

    def __init__(self) -> None:
        super().__init__()
        self.plan = dspy.ChainOfThought(GenerateNextQuery)

    def forward(
        self,
        question: str,
        gap_description: str,
        previous_queries: list[str],
    ) -> dspy.Prediction:
        """Generate next search query and strategy.

        Args:
            question: Original question
            gap_description: What information is still missing
            previous_queries: Search queries already tried

        Returns:
            Prediction with next_query and strategy
        """
        return self.plan(  # type: ignore[bad-return]
            question=question,
            gap_description=gap_description,
            previous_queries=previous_queries,
        )


class MultiHopSearchAgent(dspy.Module):
    """Multi-hop search agent orchestrating SRP-compliant modules.

    Uses CompletenessAssessor to check if we have enough info,
    and HopPlanner to decide what to search next.
    """

    def __init__(
        self,
        max_hops: int = 5,
        docs_per_hop: int = 5,
        progress_callback: Callable[[HopEvent], Any] | None = None,
        stop_threshold: float = 0.85,
    ) -> None:
        """Initialize multi-hop search agent.

        Args:
            max_hops: Maximum number of search hops (safety limit)
            docs_per_hop: Number of documents to retrieve per hop
            progress_callback: Optional callback for progress events
            stop_threshold: Confidence threshold for early stopping
        """
        super().__init__()
        self.max_hops = max_hops
        self.docs_per_hop = docs_per_hop
        self.progress_callback = progress_callback
        self.stop_threshold = stop_threshold

        # Core modules
        self.answer_with_sources = dspy.ChainOfThought(AnswerWithSources)
        self.synthesize_final = dspy.ChainOfThought(SynthesizeFinalAnswer)

        # Reflection modules (SRP-compliant)
        self.assessor = CompletenessAssessor()
        self.planner = HopPlanner()

        # Services
        self.search_client = get_search_client(
            base_url="http://192.168.1.4:8080",
        )
        self.time_estimator = get_time_estimator()

    def _send_progress(
        self,
        event_type: str,
        hop_number: int,
        message: str,
        progress: float,
        eta_seconds: float | None = None,
        documents_found: int = 0,
        query_used: str | None = None,
        reflection_reasoning: str | None = None,
    ) -> None:
        """Send progress update via callback.

        Args:
            event_type: Type of event
            hop_number: Current hop number
            message: Human-readable message
            progress: Progress 0.0 to 1.0
            eta_seconds: Estimated time remaining
            documents_found: Number of documents found
            query_used: Search query used
            reflection_reasoning: Runtime reflection output
        """
        if self.progress_callback is None:
            return

        event = HopEvent(
            event_type=event_type,
            hop_number=hop_number,
            total_hops=self.max_hops,
            message=message,
            progress=progress,
            eta_seconds=eta_seconds,
            documents_found=documents_found,
            query_used=query_used,
            reflection_reasoning=reflection_reasoning,
        )

        try:
            self.progress_callback(event)
        except Exception as e:
            logger.error(f"Failed to send progress: {e}")

    def _summarize_documents(self, documents: list[SearchResultItem]) -> str:
        """Create brief summary for assessment.

        Args:
            documents: List of search results

        Returns:
            Brief summary string
        """
        if not documents:
            return "No documents found."

        summaries: list[str] = []
        for i, doc in enumerate(documents[:5]):
            title = doc.title or "Untitled"
            content = (
                doc.content[:150] + "..." if len(doc.content) > 150 else doc.content
            )
            summaries.append(f"{i + 1}. {title}: {content}")

        return "\n".join(summaries)

    async def forward(self, question: str) -> dspy.Prediction:
        """Execute multi-hop search with runtime reflection.

        Args:
            question: User's question

        Returns:
            Prediction with answer, citations, hops, metadata
        """
        hop_answers: list[str] = []
        hop_contexts: list[str] = []
        hop_queries: list[str] = []

        overall_start = time.time()
        hop_num = 0
        context = ""
        strategy = "INITIAL"

        # Initialize plan_result for type checker
        plan_result: dspy.Prediction | None = None

        while hop_num < self.max_hops:
            hop_num += 1
            hop_start = time.time()

            # Generate search query for this hop
            if hop_num == 1:
                search_query = question
                strategy = "INITIAL"
            elif plan_result is not None:
                # Use planned query from previous iteration
                search_query = plan_result.next_query
                strategy = plan_result.strategy
            else:
                # Fallback: refine the original query
                search_query = f"{question} details"
                strategy = "REFINE_TOPIC"

            hop_queries.append(search_query)

            # Hop start event
            self._send_progress(
                event_type="hop_start",
                hop_number=hop_num,
                message=f"Hop {hop_num}: {strategy}",
                progress=(hop_num - 1) / self.max_hops,
                query_used=search_query,
            )

            # Search
            results = await self.search_client.search(
                query=search_query,
                max_results=self.docs_per_hop,
            )

            # Build context from results
            context_parts: list[str] = []
            for i, result in enumerate(results):  # type: ignore[bad-argument-type]
                context_parts.append(f"[{i + 1}] {result.title}\n{result.content}")
            context = "\n\n".join(context_parts)

            # Update progress
            self._send_progress(
                event_type="hop_progress",
                hop_number=hop_num,
                message=f"Found {len(results)} documents",  # type: ignore[bad-argument-type]
                progress=(hop_num - 0.7) / self.max_hops,
                documents_found=len(results),  # type: ignore[bad-argument-type]
            )

            # Generate answer for this hop
            hop_result = self.answer_with_sources(  # type: ignore[bad-return]
                question=question,
                context=context,
            )
            hop_answers.append(hop_result.answer)  # type: ignore[missing-attribute]
            hop_contexts.append(context)

            # Record timing
            hop_elapsed = time.time() - hop_start
            self.time_estimator.record_hop_time(strategy, hop_elapsed)

            # Assess completeness
            self._send_progress(
                event_type="hop_progress",
                hop_number=hop_num,
                message="Assessing completeness...",
                progress=(hop_num - 0.4) / self.max_hops,
            )

            current_answer = "\n\n".join(hop_answers)
            documents_summary = self._summarize_documents(results)  # type: ignore[bad-argument-type]

            assessment = self.assessor(  # type: ignore[bad-return]
                question=question,
                current_answer=current_answer,
                documents_summary=documents_summary,
            )

            # Check stop conditions
            is_sufficient_val = assessment.is_sufficient  # type: ignore[missing-attribute]
            confidence_val = assessment.confidence  # type: ignore[missing-attribute]
            if is_sufficient_val or confidence_val >= self.stop_threshold:
                reasoning = f"Complete (confidence: {confidence_val:.0%})"
                self._send_progress(
                    event_type="hop_complete",
                    hop_number=hop_num,
                    message=reasoning,
                    progress=1.0,
                    reflection_reasoning=reasoning,
                )
                logger.info(f"Stopping at hop {hop_num}: sufficient info")
                break

            # Plan next hop
            self._send_progress(
                event_type="hop_progress",
                hop_number=hop_num,
                message="Planning next hop...",
                progress=(hop_num - 0.2) / self.max_hops,
            )

            plan_result = self.planner(  # type: ignore[bad-assignment]
                question=question,
                gap_description=assessment.gap_description,  # type: ignore[missing-attribute]
                previous_queries=hop_queries,
            )

            reasoning = (
                f"Gap: {assessment.gap_description}\n"  # type: ignore[missing-attribute]
                f"Strategy: {plan_result.strategy}\n"  # type: ignore[missing-attribute]
                f"Next: {plan_result.next_query}"  # type: ignore[missing-attribute]
            )

            plan_strategy = plan_result.strategy  # type: ignore[missing-attribute]
            eta = self.time_estimator.estimate_total_time(1, [plan_strategy])
            self._send_progress(
                event_type="hop_complete",
                hop_number=hop_num,
                message=f"Continuing: {plan_result.strategy}",  # type: ignore[missing-attribute]
                progress=hop_num / self.max_hops,
                eta_seconds=eta,
                reflection_reasoning=reasoning,
            )

            logger.info(
                f"Hop {hop_num}: confidence={assessment.confidence:.2f}, "  # type: ignore[missing-attribute]
                f"strategy={plan_result.strategy}"  # type: ignore[missing-attribute]
            )

        # Synthesize final answer
        self._send_progress(
            event_type="hop_progress",
            hop_number=hop_num,
            message="Synthesizing final answer...",
            progress=0.95,
        )

        final_result = self.synthesize_final(  # type: ignore[bad-return]
            question=question,
            all_hop_answers=hop_answers,
            all_context=hop_contexts,
        )

        total_elapsed = time.time() - overall_start

        self._send_progress(
            event_type="search_complete",
            hop_number=hop_num,
            message="Search complete",
            progress=1.0,
            eta_seconds=0,
        )

        # Build citations from sources
        citations: list[dict[str, Any]] = []
        for hop_result in hop_answers:
            if hasattr(hop_result, "sources_summary"):
                citations.append({"summary": hop_result.sources_summary})

        return dspy.Prediction(
            answer=final_result.final_answer,  # type: ignore[missing-attribute]
            summary=final_result.summary,  # type: ignore[missing-attribute]
            confidence=final_result.confidence,  # type: ignore[missing-attribute]
            citations=citations,
            hops=[
                {
                    "hop_number": i + 1,
                    "query": hop_queries[i],
                    "answer": hop_answers[i],
                }
                for i in range(len(hop_answers))
            ],
            metadata={
                "total_time": total_elapsed,
                "num_hops": hop_num,
                "queries_used": hop_queries,
            },
        )
