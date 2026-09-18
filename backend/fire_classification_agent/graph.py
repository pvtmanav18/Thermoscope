# ==========================================
# graph.py
# LangGraph Workflow
# ==========================================

from langgraph.graph import StateGraph, START, END

from state import FireState
from backend.fire_classification_agent.agent.classification_agent import classification_node
from backend.fire_classification_agent.agent.intensity_agent import intensity_node


def build_graph():
    """
    Build the fire classification graph.
    """

    graph = StateGraph(FireState)

    # -------------------------
    # Nodes
    # -------------------------
    graph.add_node("classification", classification_node)
    graph.add_node("intensity", intensity_node)

    # -------------------------
    # Flow
    # -------------------------
    graph.add_edge(START, "classification")
    graph.add_edge("classification", "intensity")
    graph.add_edge("intensity", END)

    return graph.compile()