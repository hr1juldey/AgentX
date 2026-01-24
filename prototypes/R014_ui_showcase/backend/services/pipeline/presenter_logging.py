# =============================================================================
# AGENTX PRESENTER Logging Utilities
# =============================================================================
# Helper functions for presenter logging
# =============================================================================

from services.pipeline.agent_logging import log_step_result, safe_get


def extract_flow_metrics(flow_result: dict) -> dict:
    """Extract flow metrics from result.

    Args:
        flow_result: Result from flow checker

    Returns:
        Dictionary with flow_analysis, pacing_analysis, total_issues
    """
    flow_analysis = safe_get(flow_result, "flow_analysis", "Coherent flow")
    pacing_analysis = safe_get(flow_result, "pacing_analysis", "Appropriate pacing")
    flow_issues = safe_get(flow_result, "flow_issues", [])
    pacing_issues = safe_get(flow_result, "pacing_issues", [])
    total_issues = len(flow_issues) + len(pacing_issues)
    return {
        "Flow": flow_analysis,
        "Pacing": pacing_analysis,
        "Issues": total_issues,
    }


def extract_polish_metrics(polish_result: dict, widgets: list) -> dict:
    """Extract polish metrics from result.

    Args:
        polish_result: Result from polisher
        widgets: Original widget list

    Returns:
        Dictionary with enhanced_count and transition_count
    """
    enhanced_count = (
        len(safe_get(polish_result, "enhanced_content", widgets)) if widgets else 0
    )
    transition_count = len(safe_get(polish_result, "transition_suggestions", []))
    return {
        "Enhanced": f"{enhanced_count} widgets",
        "Suggestions": transition_count,
    }


def extract_qa_metrics(qa_result: dict) -> dict:
    """Extract QA metrics from result.

    Args:
        qa_result: Result from QA finalizer

    Returns:
        Dictionary with quality, accessibility, format, all_passed
    """
    quality_check = safe_get(qa_result, "quality_check", "passed")
    accessibility_check = safe_get(qa_result, "accessibility_check", "passed")
    format_check = safe_get(qa_result, "format_check", "passed")
    all_passed = safe_get(qa_result, "all_passed", True)
    return {
        "Quality": quality_check,
        "Accessibility": accessibility_check,
        "Format": format_check,
        "All passed": all_passed,
    }


def log_flow_check_result(flow_result: dict, step_time: float) -> None:
    """Log flow check results.

    Args:
        flow_result: Result from flow checker
        step_time: Time taken for this step
    """
    metrics = extract_flow_metrics(flow_result)
    log_step_result("Flow check", metrics, step_time)


def log_polish_result(polish_result: dict, widgets: list, step_time: float) -> None:
    """Log polish results.

    Args:
        polish_result: Result from polisher
        widgets: Original widget list
        step_time: Time taken for this step
    """
    metrics = extract_polish_metrics(polish_result, widgets)
    log_step_result("Polished content", metrics, step_time)


def log_qa_result(qa_result: dict, step_time: float) -> None:
    """Log QA results.

    Args:
        qa_result: Result from QA finalizer
        step_time: Time taken for this step
    """
    metrics = extract_qa_metrics(qa_result)
    log_step_result("QA checks", metrics, step_time)
