"""Coordinator agent for ReAct hierarchy.

This agent analyzes queries and deploys specialized sub-agents
with limited tools (3-5 each) to prevent hallucination.
"""

import dspy

from agentx.agent.react_agents.base_agent import BaseReActAgent


class CoordinatorSignature(dspy.Signature):
    """Signature for coordinator decision-making.

    The coordinator decides which sub-agent should handle the query.
    """

    query = dspy.InputField(desc="User's query")
    conversation_history = dspy.InputField(desc="Previous messages", default="")
    available_agents = dspy.InputField(desc="List of available sub-agents")

    selected_agent = dspy.OutputField(
        desc="Which sub-agent: research, widget, synthesis, memory, direct"
    )
    reasoning = dspy.OutputField(desc="Why this agent")
    sub_task = dspy.OutputField(desc="Specific task for the sub-agent")


class CoordinatorAgent(BaseReActAgent):
    """Main coordinator that deploys specialized sub-agents.

    Each sub-agent has LIMITED tools (3-5 max) to prevent hallucination.
    The coordinator analyzes the query and routes to the appropriate sub-agent.
    """

    def __init__(
        self,
        research_agent,
        widget_agent,
        synthesis_agent,
        memory_agent,
    ):
        """Initialize coordinator with sub-agents.

        Args:
            research_agent: Research specialist (3 tools)
            widget_agent: Widget specialist (3 tools)
            synthesis_agent: Synthesis specialist (3 tools)
            memory_agent: Memory specialist (3 tools)
        """
        # Coordinator has no tools, just decision-making
        super().__init__(tools=[], max_tools=0)

        self.decide = dspy.Predict(CoordinatorSignature)

        # Sub-agents (each with limited tools)
        self.research_agent = research_agent
        self.widget_agent = widget_agent
        self.synthesis_agent = synthesis_agent
        self.memory_agent = memory_agent

    def forward(self, query: str, **kwargs) -> dspy.Prediction:
        """Decide which sub-agent handles this query.

        Args:
            query: User's query
            **kwargs: Additional context (conversation_history)

        Returns:
            dspy.Prediction: Result from delegated sub-agent
        """
        conversation_history = kwargs.get("conversation_history", "")

        # Decide which sub-agent to use
        decision = self.decide(
            query=query,
            conversation_history=conversation_history,
            available_agents="research, widget, synthesis, memory, direct",
        )

        # Route to appropriate sub-agent
        agent = decision.selected_agent.lower()  # type: ignore[attr-defined]

        if agent == "research":
            return self.research_agent(query=query)
        elif agent == "widget":
            return self.widget_agent(query=query)
        elif agent == "synthesis":
            return self.synthesis_agent(query=query)
        elif agent == "memory":
            return self.memory_agent(query=query)
        else:  # direct
            return dspy.Prediction(response=query)
