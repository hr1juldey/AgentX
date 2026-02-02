"""Tests for iterative_refine function."""

from agentx.agent.tools.common.chunking import ITERATIONS, iterative_refine


class TestIterativeRefine:
    """Tests for iterative_refine function."""

    def test_zero_iterations_returns_original(self) -> None:
        """Test that zero iterations returns original items."""
        items = [1, 2, 3]

        def processor(current: list[int], previous: list[int]) -> list[int]:
            return [x + 1 for x in current]

        result = iterative_refine(items, processor, iterations=0)
        assert result == items

    def test_processor_called_correct_times(self) -> None:
        """Test that processor is called the correct number of times."""
        items = [1]
        call_count = [0]

        def processor(current: list[int], previous: list[int]) -> list[int]:
            call_count[0] += 1
            return [x + 1 for x in current]

        result = iterative_refine(items, processor, iterations=3)
        assert call_count[0] == 3
        assert result == [4]  # 1 + 1 + 1 + 1

    def test_previous_parameter_populated(self) -> None:
        """Test that previous parameter is populated correctly."""
        items = [1]

        def processor(current: list[int], previous: list[int]) -> list[int]:
            if not previous:
                return [10]
            else:
                # Should see the previous iteration's result
                return previous + [20]

        result = iterative_refine(items, processor, iterations=3)
        # Iteration 1: previous=[], returns [10]
        # Iteration 2: previous=[10], returns [10, 20]
        # Iteration 3: previous=[10, 20], returns [10, 20, 20]
        assert result == [10, 20, 20]

    def test_default_iterations(self) -> None:
        """Test that default ITERATIONS constant is used."""
        items = [1]
        call_count = [0]

        def processor(current: list[int], previous: list[int]) -> list[int]:
            call_count[0] += 1
            return current

        iterative_refine(items, processor)
        assert call_count[0] == ITERATIONS
