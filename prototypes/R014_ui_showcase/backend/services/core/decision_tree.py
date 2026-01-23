# =============================================================================
# AGENTX Decision Tree Infrastructure
# =============================================================================
# Base classes for building decision trees that branch agent execution
# =============================================================================

from typing import Any, Callable, Dict
from abc import ABC, abstractmethod


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


class ActionNode(DecisionNode):
    """A leaf node that executes an action."""

    def __init__(self, action: Callable[[Dict[str, Any]], Any], name: str = "action"):
        self.action = action
        self.name = name

    def evaluate(self, context: Dict[str, Any]) -> bool:
        return True

    def execute(self, context: Dict[str, Any]) -> Any:
        return self.action(context)


class DecisionTree:
    """Decision tree executor for agent branching logic."""

    def __init__(self, root: DecisionNode):
        self.root = root

    def execute(self, context: Dict[str, Any]) -> Any:
        """Execute the decision tree with the given context."""
        return self.root.execute(context)


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


class DecisionElseBuilder:
    """Builder for the else branch."""

    def __init__(
        self,
        tree_builder: DecisionTreeBuilder,
        condition: Callable[[Dict[str, Any]], bool],
        true_action: Callable[[Dict[str, Any]], Any],
    ):
        self.tree_builder = tree_builder
        self.condition = condition
        self.true_action = true_action

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
