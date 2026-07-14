"""
DealOS AI — LangGraph Multi-Agent Orchestration.

Multi-agent investment analyst pipeline:
    Planner → [Financial | Risk | Company] → Investment Committee

Uses LangGraph StateGraph with TypedDict state, conditional routing,
and parallel specialist execution. All agents delegate to existing
services — no retrieval or extraction logic is duplicated.
"""

from app.ai.agents.graph import run_graph, stream_graph
from app.ai.agents.state import GraphState

__all__ = [
    "GraphState",
    "run_graph",
    "stream_graph",
]
