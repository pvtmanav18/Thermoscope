# graph.py

from langgraph.graph import StateGraph, START, END

from state import FireState

# -----------------------------
# Import Agents
# -----------------------------

from agents.firms_loader_agent import firms_loader_agent
from agents.weather_agent import weather_agent
from agents.classification_agent import classification_agent
from agents.spread_agent import fire_spread_agent
from agents.gis_context_agent import gis_context_agent
from agents.damage_agent import damage_agent
from agents.risk_agent import risk_agent
from agents.casualty_agent import casualty_agent
from agents.explanation_agent import explanation_agent

# -----------------------------
# Build LangGraph
# -----------------------------

builder = StateGraph(FireState)

# Register Nodes

builder.add_node("FIRMS Loader", firms_loader_agent)
builder.add_node("Weather Agent", weather_agent)
builder.add_node("Classification Agent", classification_agent)
builder.add_node("Fire Spread Agent", fire_spread_agent)
builder.add_node("GIS Context Agent", gis_context_agent)
builder.add_node("Damage Agent", damage_agent)
builder.add_node("Risk Agent", risk_agent)
builder.add_node("Casualty Agent", casualty_agent)
builder.add_node("Explanation Agent", explanation_agent)

# -----------------------------
# Graph Flow
# -----------------------------

builder.add_edge(START, "FIRMS Loader")

builder.add_edge("FIRMS Loader", "Weather Agent")
builder.add_edge("Weather Agent", "Classification Agent")
builder.add_edge("Classification Agent", "Fire Spread Agent")
builder.add_edge("Fire Spread Agent", "GIS Context Agent")
builder.add_edge("GIS Context Agent", "Damage Agent")
builder.add_edge("Damage Agent", "Risk Agent")
builder.add_edge("Risk Agent", "Casualty Agent")
builder.add_edge("Casualty Agent", "Explanation Agent")

builder.add_edge("Explanation Agent", END)

# -----------------------------
# Compile Graph
# -----------------------------

fire_graph = builder.compile()

print("🔥 NTRO Sentinel LangGraph Initialized Successfully")