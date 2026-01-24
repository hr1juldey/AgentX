# =============================================================================
# AGENTX SEQUENCER Logging Utilities
# =============================================================================
# Helper functions for sequencer logging
# =============================================================================

from services.pipeline.agent_logging import log_step_result, safe_get


def extract_narrative_flow_data(flow_result: dict) -> tuple:
    """Extract narrative flow data from result.

    Args:
        flow_result: Result from flow planner

    Returns:
        Tuple of (narrative_arc, is_valid)
    """
    narrative_arc = safe_get(
        flow_result, "narrative_arc", "hook → context → insight → action"
    )
    is_valid = safe_get(flow_result, "is_valid", True)
    return narrative_arc, is_valid


def extract_pacing_data(pacing_result: dict) -> float:
    """Extract pacing data from result.

    Args:
        pacing_result: Result from pacing calculator

    Returns:
        Total duration as float
    """
    return safe_get(pacing_result, "total_duration", 0)


def log_narrative_flow_result(flow_result: dict) -> tuple:
    """Log narrative flow result and extract key data.

    Args:
        flow_result: Result from flow planner

    Returns:
        Tuple of (narrative_arc, is_valid)
    """
    narrative_arc, is_valid = extract_narrative_flow_data(flow_result)
    from services.pipeline.agent_logging import logger

    logger.info(f"    → Narrative arc: {narrative_arc}")
    return narrative_arc, is_valid


def log_pacing_result(pacing_result: dict, sequence: list) -> float:
    """Log pacing result and extract total duration.

    Args:
        pacing_result: Result from pacing calculator
        sequence: Sequence list

    Returns:
        Total duration as float
    """
    total_duration = extract_pacing_data(pacing_result)
    metrics = {
        "Total duration": f"{total_duration:.1f}s",
        "delivery": "staggered",
        "sequence length": len(sequence),
    }
    log_step_result("Pacing calculated", metrics, 0)
    return total_duration
