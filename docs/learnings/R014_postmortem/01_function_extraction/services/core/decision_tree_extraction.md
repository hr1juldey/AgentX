# Function Postmortem: services/core/decision_tree.py

## Metadata
- **File**: services/core/decision_tree.py
- **Lines of Code**: 134
- **Purpose**: Base classes for building decision trees that branch agent execution
- **Dependencies**: typing, abc

---

## Analysis

**File Status**: PRODUCTION INFRASTRUCTURE

**Purpose**: Provides decision tree infrastructure for branching agent execution based on conditions.

---

## Classes Extracted

### DecisionNode (ABC)

**Purpose**: Abstract base class for decision tree nodes.

**Lines**: 11-22

**Key Code**:
```python
class DecisionNode(ABC):
    """Base class for decision tree nodes."""

    @abstractmethod
    def evaluate(self, context: Dict[str, Any]) -> bool:
        """Evaluate if this node's condition is true."""
        pass

    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Any:
        """Execute this node's action."""
        pass
```

**What Works**:
- ✅ Abstract base: Enforces evaluate() and execute() interface
- ✅ Context-driven: All operations take context dict
- ✅ Simple API: 2 methods (evaluate, execute)

---

### ConditionNode

**Purpose**: A node that evaluates a condition and branches to one of two children.

**Lines**: 25-46

**Key Code**:
```python
class ConditionNode(DecisionNode):
    """A node that evaluates a condition and branches to one of two children."""

    def __init__(
        self,
        condition: Callable[[Dict[str, Any]], bool],
        true_branch: DecisionNode,
        false_branch: DecisionNode,
        name: str = "condition",
    ):
        self.condition = condition
        self.true_branch = true_branch
        self.false_branch = false_branch
        self.name = name

    def evaluate(self, context: Dict[str, Any]) -> bool:
        return self.condition(context)

    def execute(self, context: Dict[str, Any]) -> Any:
        if self.evaluate(context):
            return self.true_branch.execute(context)
        return self.false_branch.execute(context)
```

**What Works**:
- ✅ Binary branching: true_branch vs false_branch
- ✅ Callable condition: Any function that takes context and returns bool
- ✅ Recursive execution: Delegates to child nodes
- ✅ Named nodes: name parameter for debugging

**Behavioral Notes**:
- condition is a Callable[[Dict[str, Any]], bool]
- execute() evaluates condition, then delegates to appropriate branch
- true_branch and false_branch are also DecisionNodes (recursive structure)

---

### ActionNode

**Purpose**: A leaf node that executes an action.

**Lines**: 49-60

**Key Code**:
```python
class ActionNode(DecisionNode):
    """A leaf node that executes an action."""

    def __init__(self, action: Callable[[Dict[str, Any]], Any], name: str = "action"):
        self.action = action
        self.name = name

    def evaluate(self, context: Dict[str, Any]) -> bool:
        return True

    def execute(self, context: Dict[str, Any]) -> Any:
        return self.action(context)
```

**What Works**:
- ✅ Leaf node: Always returns True from evaluate()
- ✅ Action execution: Executes action callable with context
- ✅ Any return type: Action can return anything

**Behavioral Notes**:
- evaluate() always returns True (leaf nodes don't branch)
- execute() runs action and returns its result
- Used as terminal nodes in the tree

---

### DecisionTree

**Purpose**: Decision tree executor for agent branching logic.

**Lines**: 63-71

**Key Code**:
```python
class DecisionTree:
    """Decision tree executor for agent branching logic."""

    def __init__(self, root: DecisionNode):
        self.root = root

    def execute(self, context: Dict[str, Any]) -> Any:
        """Execute the decision tree with the given context."""
        return self.root.execute(context)
```

**What Works**:
- ✅ Simple wrapper: Just holds root and executes it
- ✅ Context-driven: All execution uses context dict
- ✅ Recursive: root.execute() handles all branching

---

### DecisionTreeBuilder

**Purpose**: Fluent builder for complex decision trees.

**Lines**: 74-90

**Key Code**:
```python
class DecisionTreeBuilder:
    """Fluent builder for complex decision trees."""

    def __init__(self):
        self.nodes = []

    def when(
        self, condition: Callable[[Dict[str, Any]], bool]
    ) -> "DecisionBranchBuilder":
        """Start a conditional branch."""
        return DecisionBranchBuilder(self, condition)

    def build(self, default_action: Callable) -> DecisionTree:
        """Build the tree with a default fallback."""
        if self.nodes:
            return DecisionTree(root=self.nodes[0])
        return DecisionTree(root=ActionNode(default_action))
```

**What Works**:
- ✅ Fluent API: when().then().otherwise() pattern
- ✅ Default fallback: build() accepts default_action
- ✅ Empty tree handling: Returns ActionNode if no nodes

---

### DecisionBranchBuilder

**Purpose**: Builder for a single decision branch (when → then).

**Lines**: 93-106

**Key Code**:
```python
class DecisionBranchBuilder:
    """Builder for a single decision branch."""

    def __init__(
        self,
        tree_builder: DecisionTreeBuilder,
        condition: Callable[[Dict[str, Any]], bool],
    ):
        self.tree_builder = tree_builder
        self.condition = condition

    def then(self, action: Callable) -> "DecisionElseBuilder":
        """Set the true branch action."""
        return DecisionElseBuilder(self.tree_builder, self.condition, action)
```

**What Works**:
- ✅ then() returns DecisionElseBuilder for chaining
- ✅ Holds tree_builder reference to append nodes

---

### DecisionElseBuilder

**Purpose**: Builder for the else branch (otherwise).

**Lines**: 109-133

**Key Code**:
```python
class DecisionElseBuilder:
    """Builder for the else branch."""

    def otherwise(self, action: Callable) -> DecisionTreeBuilder:
        """Set the false branch action and return to tree builder."""
        false_branch = ActionNode(action, name="otherwise")
        true_branch = ActionNode(self.true_action, name="then")
        node = ConditionNode(
            self.condition,
            true_branch=true_branch,
            false_branch=false_branch,
            name="condition",
        )
        self.tree_builder.nodes.append(node)
        return self.tree_builder
```

**What Works**:
- ✅ otherwise() completes the branch and returns to builder
- ✅ Creates ConditionNode with ActionNode leaves
- ✅ Appends to tree_builder.nodes for chaining

**Behavioral Notes**:
- Builds tree from inside out: ActionNode → ConditionNode → append to builder
- Returns tree_builder for chaining multiple when().then().otherwise() blocks

---

## File Summary

**Total Classes**: 7
**Lines of Code**: 134

**Overall Assessment**: Clean decision tree infrastructure with fluent builder API. Provides composable branching logic for agent execution.

**Key Learnings for Real AgentX**:
1. ✅ Fluent builder API: when().then().otherwise() pattern is intuitive
2. ✅ Callable conditions: Any function that takes context and returns bool
3. ✅ Recursive structure: ConditionNode contains DecisionNode children
4. ✅ Leaf nodes: ActionNode executes actions (no branching)
5. ✅ Context-driven: All operations use context dict for data flow
6. ✅ Named nodes: name parameter helps with debugging
7. ✅ Default fallback: build() accepts default_action for safety

**Reuse for Real AgentX**: ✅ DIRECT - Use this decision tree infrastructure for any agent branching logic (routing, fallback, error handling).
