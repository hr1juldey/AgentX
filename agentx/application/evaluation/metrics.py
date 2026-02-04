"""Quality metrics for graph evaluation."""


def latency_score(execution_start: float, execution_end: float) -> float:
    """Calculate latency score (0.0 to 1.0).

    Args:
        execution_start: Start timestamp
        execution_end: End timestamp

    Returns:
        Latency score

    Raises:
        NotImplementedError: If not yet implemented
    """
    raise NotImplementedError("latency_score() not yet implemented")


def accuracy_score(expected: str, actual: str) -> float:
    """Calculate accuracy score (0.0 to 1.0).

    Args:
        expected: Expected result
        actual: Actual result

    Returns:
        Accuracy score

    Raises:
        NotImplementedError: If not yet implemented
    """
    raise NotImplementedError("accuracy_score() not yet implemented")
