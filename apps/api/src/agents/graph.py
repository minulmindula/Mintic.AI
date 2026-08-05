from typing import Any

from langgraph.graph import END, START, StateGraph

from src.agents.nodes import analyst_node, bear_node, bull_node, risk_manager_node
from src.agents.state import DeliberationState


def create_deliberation_graph() -> Any:
    """
    Compiles the multi-agent deliberation StateGraph for trade evaluation.

    Execution Flow:
        START -> analyst -> [bull, bear] -> risk_manager -> END

    Returns:
        Compiled LangGraph executable instance.
    """
    workflow = StateGraph(DeliberationState)

    # Add nodes to graph
    workflow.add_node("analyst", analyst_node)
    workflow.add_node("bull", bull_node)
    workflow.add_node("bear", bear_node)
    workflow.add_node("risk_manager", risk_manager_node)

    # Wire execution edges
    workflow.add_edge(START, "analyst")
    workflow.add_edge("analyst", "bull")
    workflow.add_edge("analyst", "bear")
    workflow.add_edge("bull", "risk_manager")
    workflow.add_edge("bear", "risk_manager")
    workflow.add_edge("risk_manager", END)

    return workflow.compile()
