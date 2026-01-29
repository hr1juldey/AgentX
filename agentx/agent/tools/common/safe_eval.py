"""Safe evaluation utilities for agent tools.

Provides safe calculator evaluation for mathematical expressions.
Uses a restricted eval environment for security.
"""

import ast
import operator
from typing import Any, Union


# Supported operators for safe evaluation
_OPERATORS: dict[str, Any] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.BitXor: operator.xor,
    ast.USub: operator.neg,
}


class SafeEvalError(Exception):
    """Error raised when safe evaluation fails."""

    pass


def safe_eval(expression: str) -> Union[int, float]:
    """Safely evaluate a mathematical expression.

    Only supports basic arithmetic operations (+, -, *, /, **, ^).
    Does NOT support function calls, attribute access, or imports.

    Args:
        expression: Mathematical expression to evaluate

    Returns:
        Result of evaluation (int or float)

    Raises:
        SafeEvalError: If expression is unsafe or evaluation fails
    """
    try:
        # Parse the expression into an AST
        node = ast.parse(expression, mode="eval")

        # Validate the AST - only allow literals and operations
        for child in ast.walk(node):
            if isinstance(child, ast.Name):
                raise SafeEvalError(f"Variable access not allowed: {child.id}")
            if isinstance(child, ast.Attribute):
                raise SafeEvalError("Attribute access not allowed")
            if isinstance(child, ast.Call):
                raise SafeEvalError("Function calls not allowed")
            if isinstance(child, ast.Subscript):
                raise SafeEvalError("Subscript access not allowed")

        # Compile and evaluate in a restricted environment
        code = compile(node, "<string>", "eval")
        return eval(code, {"__builtins__": {}}, _OPERATORS)

    except (SyntaxError, ValueError, TypeError) as e:
        raise SafeEvalError(f"Invalid expression: {e}") from e
    except Exception as e:
        raise SafeEvalError(f"Evaluation failed: {e}") from e


def safe_calculate(expression: str) -> str:
    """Evaluate a mathematical expression and return the result as a string.

    Wrapper around safe_eval for use in agent tools.

    Args:
        expression: Mathematical expression to evaluate

    Returns:
        Result as string (for LLM consumption)

    Example:
        >>> safe_calculate("2 + 2")
        '4'
        >>> safe_calculate("10 * 5")
        '50'
    """
    try:
        result = safe_eval(expression)
        return str(result)
    except SafeEvalError as e:
        return f"Error: {str(e)}"
