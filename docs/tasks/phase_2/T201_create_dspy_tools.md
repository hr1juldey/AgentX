# T201: Create DSPy Tools

**Phase**: 2
**Estimated Time**: 40 minutes
**Dependencies**: T001, T200
**Blocked By**: None

---

## Context

**LLD References**:
- `lld/agent_runtime.md` - Tool definitions
- `lld/incremental_release_plan.md` - Phase 2: Basic tools

**Description**:
Creates basic DSPy tools for the main agent: calculator, search, and weather. Tools are wrapped with dspy.Tool for ReAct agent usage.

---

## Acceptance Criteria

**Passing Criteria**:
- agent/tools/ directory exists
- calculator tool implemented with safe evaluation
- search tool implemented (SearXNG integration)
- weather tool implemented (mock for Phase 2)
- All tools wrapped with dspy.Tool
- All tools can be imported

**Verification Commands**:
```bash
cd /home/riju279/Documents/Code/XRIG/AgentX/prototypes/R013_travel_planning_stream/backend

# Verify directory exists
test -d agentx/agent/tools && echo "tools directory exists"

# Verify tools can be imported
python3 -c "from agentx.agent.tools.main_tools import calculator, search, get_current_weather; print('Tools OK')"
```

---

## Implementation Steps

### Step 1: Create calculator tool

Create file `agentx/agent/tools/calculator.py`:

```python
"""Calculator tool for mathematical expressions."""

import ast
import operator
from typing import Union


class SafeCalculator:
    """Safe mathematical expression evaluator."""

    ALLOWED_OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.Mod: operator.mod,
    }

    ALLOWED_FUNCTIONS = {
        "abs": abs,
        "round": round,
        "min": min,
        "max": max,
        "sum": sum,
    }

    def __init__(self):
        self.operator_map = self.ALLOWED_OPERATORS
        self.function_map = self.ALLOWED_FUNCTIONS

    def evaluate(self, expression: str) -> Union[float, int, str]:
        """Evaluate a mathematical expression safely.

        Args:
            expression: Mathematical expression as string

        Returns:
            Result of evaluation or error message

        Example:
            >>> calc = SafeCalculator()
            >>> calc.evaluate("2 + 2 * 3")
            8
            >>> calc.evaluate("abs(-5)")
            5
        """
        try:
            tree = ast.parse(expression, mode="eval")
            result = self._eval_node(tree.body)
            return result
        except Exception as e:
            return f"Error: {str(e)}"

    def _eval_node(self, node):
        """Recursively evaluate AST node."""
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.BinOp):
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            op_type = type(node.op)
            if op_type in self.operator_map:
                return self.operator_map[op_type](left, right)
            raise ValueError(f"Operator not allowed: {op_type}")
        elif isinstance(node, ast.UnaryOp):
            operand = self._eval_node(node.operand)
            op_type = type(node.op)
            if op_type in self.operator_map:
                return self.operator_map[op_type](operand)
            raise ValueError(f"Unary operator not allowed: {op_type}")
        elif isinstance(node, ast.Call):
            func_name = node.func.id
            if func_name in self.function_map:
                args = [self._eval_node(arg) for arg in node.args]
                return self.function_map[func_name](*args)
            raise ValueError(f"Function not allowed: {func_name}")
        elif isinstance(node, ast.Expression):
            return self._eval_node(node.body)
        else:
            raise ValueError(f"Expression type not allowed: {type(node)}")


# Global calculator instance
_calculator = SafeCalculator()


def calculator(expression: str) -> str:
    """Evaluate a mathematical expression safely.

    Supported operations: +, -, *, /, **, %, unary -
    Supported functions: abs, round, min, max, sum

    Args:
        expression: Mathematical expression to evaluate

    Returns:
        Result as string, or error message if evaluation fails

    Examples:
        >>> calculator("2 + 2")
        'The result is: 4'
        >>> calculator("10 * (5 + 3)")
        'The result is: 80'
        >>> calculator("abs(-15)")
        'The result is: 15'
    """
    result = _calculator.evaluate(expression)
    if isinstance(result, str) and result.startswith("Error:"):
        return result
    return f"The result is: {result}"
```

### Step 2: Create search tool

Create file `agentx/agent/tools/search.py`:

```python
"""Search tool using SearXNG."""

import httpx
from typing import List, Dict, Any
import json


class SearXNGSearch:
    """SearXNG metasearch engine client."""

    def __init__(self, base_url: str = "http://192.168.1.4:8080"):
        self.base_url = base_url.rstrip("/")
        self.timeout = 10

    def search(
        self,
        query: str,
        num_results: int = 5,
        engines: str = None
    ) -> List[Dict[str, Any]]:
        """Perform a web search using SearXNG.

        Args:
            query: Search query string
            num_results: Number of results to return (default: 5)
            engines: Comma-separated list of engines (optional)

        Returns:
            List of search results with title, url, snippet

        Example:
            >>> search = SearXNGSearch()
            >>> results = search.search("Python programming", num_results=3)
            >>> len(results) <= 3
            True
        """
        params = {
            "q": query,
            "format": "json",
            "engines": engines or "",
        }

        try:
            response = httpx.get(
                f"{self.base_url}/search",
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()

            results = []
            for result in data.get("results", [])[:num_results]:
                results.append({
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "snippet": result.get("content", ""),
                })

            return results

        except httpx.HTTPError as e:
            return [{"error": f"Search failed: {str(e)}"}]
        except Exception as e:
            return [{"error": f"Unexpected error: {str(e)}"}]


# Global search instance
_search = SearXNGSearch()


def search(query: str, num_results: int = 5) -> str:
    """Search the web for information.

    Uses SearXNG metasearch engine to get results from multiple sources.

    Args:
        query: Search query
        num_results: Number of results to return (default: 5)

    Returns:
        Formatted search results as string

    Examples:
        >>> search("weather in Tokyo")
        'Found 3 results:\\n1. [Title] URL - Snippet\\n...'
        >>> search("Python async await", num_results=3)
        'Found 3 results:\\n...'
    """
    results = _search.search(query, num_results=num_results)

    if not results:
        return "No results found."

    if results and "error" in results[0]:
        return results[0]["error"]

    output = [f"Found {len(results)} results:\\n"]
    for i, result in enumerate(results, 1):
        title = result.get("title", "No title")
        url = result.get("url", "")
        snippet = result.get("snippet", "")
        output.append(f"{i}. {title}")
        output.append(f"   {url}")
        if snippet:
            output.append(f"   {snippet}")
        output.append("")

    return "\\n".join(output)
```

### Step 3: Create weather tool (mock)

Create file `agentx/agent/tools/weather.py`:

```python
"""Weather tool (mock implementation for Phase 2)."""

from typing import Dict, Any
import random


class MockWeatherService:
    """Mock weather service for Phase 2 testing."""

    def get_weather(self, location: str) -> Dict[str, Any]:
        """Get mock weather data for a location.

        Args:
            location: City or location name

        Returns:
            Mock weather data with temperature, conditions, etc.

        Note:
            This is a mock implementation. Phase 3+ will integrate
            with real weather API (OpenWeatherMap or similar).
        """
        temperatures = {
            "tokyo": 18,
            "new york": 12,
            "london": 15,
            "paris": 14,
            "sydney": 22,
        }

        base_temp = temperatures.get(location.lower(), 20)
        temp = base_temp + random.randint(-3, 3)

        conditions = ["Sunny", "Cloudy", "Partly Cloudy", "Rainy"]
        condition = random.choice(conditions)

        humidity = random.randint(40, 80)

        return {
            "location": location,
            "temperature_c": temp,
            "temperature_f": round(temp * 9 / 5 + 32, 1),
            "condition": condition,
            "humidity": humidity,
            "wind_kph": random.randint(5, 25),
        }


# Global weather service instance
_weather = MockWeatherService()


def get_current_weather(location: str) -> str:
    """Get current weather information for a location.

    Args:
        location: City or location name

    Returns:
        Weather information as formatted string

    Examples:
        >>> get_current_weather("Tokyo")
        'Weather in Tokyo: 18°C, Sunny, Humidity: 65%'
        >>> get_current_weather("London")
        'Weather in London: 15°C, Cloudy, Humidity: 72%'
    """
    data = _weather.get_weather(location)

    output = [
        f"Weather in {data['location']}:",
        f"Temperature: {data['temperature_c']}°C ({data['temperature_f']}°F)",
        f"Condition: {data['condition']}",
        f"Humidity: {data['humidity']}%",
        f"Wind: {data['wind_kph']} km/h",
    ]

    return ". ".join(output)
```

### Step 4: Create tools __init__.py

Create file `agentx/agent/tools/__init__.py`:

```python
"""DSPy tools for AGENTX agents."""

from agentx.agent.tools.calculator import calculator
from agentx.agent.tools.search import search
from agentx.agent.tools.weather import get_current_weather

__all__ = [
    "calculator",
    "search",
    "get_current_weather",
]
```

### Step 5: Create tool wrapper module

Create file `agentx/agent/tools/main_tools.py`:

```python
"""Main DSPy tools wrapped for ReAct agent."""

import dspy

from agentx.agent.tools import calculator, search, get_current_weather


def wrap_tools():
    """Wrap all tools as dspy.Tool instances.

    Returns:
        List of dspy.Tool objects for ReAct agent

    Example:
        >>> tools = wrap_tools()
        >>> len(toools) >= 3
        True
    """
    return [
        dspy.Tool(calculator, name="calculator"),
        dspy.Tool(search, name="search"),
        dspy.Tool(get_current_weather, name="get_current_weather"),
    ]
```

---

## Expected Failures & Countermeasures

### Failure: SearXNG not accessible

**Likelihood**: Medium
**Symptoms**: `httpx.ConnectError` or search returns error

**Countermeasures**:
1. Check SearXNG is running: `curl http://192.168.1.4:8080/`
2. Start SearXNG: `sudo systemctl start searxng-docker`
3. Or use mock search for testing

**Recovery Time**: 5 minutes

### Failure: Calculator evaluates unsafe code

**Likelihood**: Low
**Symptoms**: Calculator executes arbitrary Python code

**Countermeasures**:
1. SafeCalculator uses AST parsing (not eval)
2. Only whitelisted operators and functions
3. No access to __builtins__ or unsafe operations

**Recovery Time**: 0 minutes (prevented by design)

---

## Retroactive Measures

### Upstream Drift Recovery

**Scenario**: T001 directory structure changed
**Detection**: agentx/agent/tools/ directory missing
**Action**: Re-run T001 to ensure all directories exist

**Recovery Time**: 5 minutes

### Downstream Impact

**Scenario**: Tool function signatures change
**Prevention**: All tool signatures are LOCKED
**Mitigation**: Update dspy.Tool wrappers in main_tools.py
**Affected Tasks**: T202 (Main DSPy Agent), T203 (Agent Use Cases)

---

## Artifacts

**Files Created**:
- `agentx/agent/tools/calculator.py` (Calculator tool, LOCKED)
- `agentx/agent/tools/search.py` (Search tool, LOCKED)
- `agentx/agent/tools/weather.py` (Weather tool, LOCKED)
- `agentx/agent/tools/__init__.py` (Package marker)
- `agentx/agent/tools/main_tools.py` (Tool wrappers, not locked)

**Locked APIs**:
- All tool function names
- All tool function signatures
- Tool return value formats

---

## Quality Gates

**Quality Checks**:
- **Check**: All tool files exist
  - Command: `ls agentx/agent/tools/*.py`
  - Expected: 5 .py files
  - Required: Yes

- **Check**: Tools can be imported
  - Command: `python3 -c "from agentx.agent.tools import calculator, search, get_current_weather; print('OK')"`
  - Expected: `OK`
  - Required: Yes

- **Check**: Calculator works
  - Command: `python3 -c "from agentx.agent.tools.calculator import calculator; print(calculator('2+2'))"`
  - Expected: `The result is: 4`
  - Required: Yes

---

## Notes

1. Calculator uses AST parsing for safety (not eval/exec)
2. Search tool integrates with SearXNG at 192.168.1.4:8080
3. Weather tool is mock implementation (real API in Phase 3+)
4. All tools return formatted strings for LLM consumption
5. Tools are wrapped with dspy.Tool for ReAct agent

---

## Completion Checklist

- [ ] calculator.py created with safe evaluation
- [ ] search.py created with SearXNG integration
- [ ] weather.py created with mock implementation
- [ ] tools/__init__.py exports all tools
- [ ] main_tools.py wraps tools as dspy.Tool
- [ ] All tools can be imported
- [ ] Calculator test passes
- [ ] Ready for T202 (Main DSPy Agent)

---

**Task T201 is part of Phase 2: Main DSPy Agent**
**Locked APIs**: All tool function names and signatures
