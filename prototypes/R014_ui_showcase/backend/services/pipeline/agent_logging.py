# =============================================================================
# AGENTX Pipeline Agent Logging Utilities
# =============================================================================
# Unified logging infrastructure for all pipeline agents
# =============================================================================

import logging
from typing import Any, List

logger = logging.getLogger(__name__)


def safe_get(result: Any, key: str, default: Any = None) -> Any:
    """Safely get a value from a dict-like object.

    Args:
        result: Object that may be a dict (or coroutine)
        key: Key to look up
        default: Default value if key not found

    Returns:
        Value from result or default
    """
    if hasattr(result, "get"):
        return result.get(key, default)
    return default


def safe_get_list(result: Any, key: str) -> List[Any]:
    """Safely get a list from a dict-like object.

    Args:
        result: Object that may be a dict (or coroutine)
        key: Key to look up

    Returns:
        List from result or empty list
    """
    if hasattr(result, "get"):
        return result.get(key, [])
    return []


def log_step_start(agent_name: str, step_name: str, detail: str = "") -> None:
    """Log the start of a pipeline step.

    Args:
        agent_name: Name of the agent (e.g., "CONTEXTUALIZER")
        step_name: Name of the step (e.g., "Reranking")
        detail: Optional detail message (e.g., "5 documents")
    """
    if detail:
        logger.info(f"  [{agent_name}] {step_name} {detail}...")
    else:
        logger.info(f"  [{agent_name}] {step_name}...")


def log_step_result(
    step_name: str,
    metrics: dict[str, Any],
    step_time: float,
) -> None:
    """Log the result of a pipeline step with timing.

    Args:
        step_name: Name of the step for the log message
        metrics: Dictionary of metrics to log
        step_time: Time taken for this step in seconds
    """
    metric_str = ", ".join(f"{k}: {v}" for k, v in metrics.items())
    logger.info(f"    → {step_name}: {metric_str} ({step_time:.2f}s)")
