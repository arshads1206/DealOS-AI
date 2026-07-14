"""
DealOS AI — LangGraph State Machine.

Compiles the multi-agent investment analyst graph:

    Planner → [Financial | Risk | Company] (parallel) → Investment Committee

Key design decisions:
- Conditional edges: Planner decides which specialists run, others are skipped.
- Fan-out/fan-in: Specialist agents run in parallel, then converge at committee.
- Error isolation: Each node handles its own errors and writes to state.errors.
- Session-injected: DB session is passed via functools.partial at invocation time.

LangGraph version: 0.4.x (uses StateGraph with TypedDict state).
"""

from functools import partial
from typing import Any

import structlog
from langgraph.graph import END, StateGraph
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.agents.nodes import (
    committee_node,
    company_node,
    financial_node,
    planner_node,
    risk_node,
)
from app.ai.agents.state import GraphState

logger = structlog.get_logger(__name__)


def _route_after_planner(state: GraphState) -> list[str]:
    """
    Conditional edge: route to specialist nodes based on execution plan.

    Returns a list of next node names for parallel execution.
    If the plan is empty (edge case), go directly to committee.
    """
    plan = state.get("execution_plan", [])
    if not plan:
        return ["committee"]

    next_nodes = []
    if "financial" in plan:
        next_nodes.append("financial")
    if "risk" in plan:
        next_nodes.append("risk")
    if "company" in plan:
        next_nodes.append("company")

    return next_nodes if next_nodes else ["committee"]


def build_graph(session: AsyncSession) -> StateGraph:
    """
    Build and compile the LangGraph investment analyst graph.

    The DB session is bound to each node via functools.partial so that
    nodes can access existing services without global state.

    Graph topology:
        START → planner → {financial, risk, company} → committee → END

    Args:
        session: Async SQLAlchemy session for service instantiation.

    Returns:
        Compiled StateGraph ready for invocation.
    """
    # Bind the DB session to each node function
    bound_planner = partial(planner_node, session=session)
    bound_financial = partial(financial_node, session=session)
    bound_risk = partial(risk_node, session=session)
    bound_company = partial(company_node, session=session)
    bound_committee = partial(committee_node, session=session)

    # Build the graph
    graph = StateGraph(GraphState)

    # Add nodes
    graph.add_node("planner", bound_planner)
    graph.add_node("financial", bound_financial)
    graph.add_node("risk", bound_risk)
    graph.add_node("company", bound_company)
    graph.add_node("committee", bound_committee)

    # Set entry point
    graph.set_entry_point("planner")

    # Conditional routing from planner to specialists
    graph.add_conditional_edges(
        "planner",
        _route_after_planner,
        {
            "financial": "financial",
            "risk": "risk",
            "company": "company",
            "committee": "committee",
        },
    )

    # All specialists converge at committee
    graph.add_edge("financial", "committee")
    graph.add_edge("risk", "committee")
    graph.add_edge("company", "committee")

    # Committee is the final node
    graph.add_edge("committee", END)

    return graph.compile()


async def run_graph(
    question: str,
    company_id: str,
    session_id: str,
    session: AsyncSession,
    messages: list[dict] | None = None,
) -> GraphState:
    """
    Execute the full multi-agent graph.

    This is the primary entry point for the chat service.

    Args:
        question: User's investment question.
        company_id: Company UUID string.
        session_id: Chat session UUID string.
        session: Async SQLAlchemy session.
        messages: Conversation history for multi-turn context.

    Returns:
        Final GraphState with all agent results.
    """
    logger.info(
        "graph_execution_start",
        question_preview=question[:100],
        company_id=company_id,
    )

    compiled_graph = build_graph(session)

    initial_state: GraphState = {
        "question": question,
        "company_id": company_id,
        "session_id": session_id,
        "messages": messages or [],
        "errors": [],
        "agent_traces": [],
    }

    # Execute the graph
    final_state = await compiled_graph.ainvoke(initial_state)

    logger.info(
        "graph_execution_complete",
        agents_run=len(final_state.get("agent_traces", [])),
        errors=len(final_state.get("errors", [])),
        confidence=final_state.get("confidence", 0.0),
    )

    return final_state


async def stream_graph(
    question: str,
    company_id: str,
    session_id: str,
    session: AsyncSession,
    messages: list[dict] | None = None,
):
    """
    Execute the graph with streaming, yielding status updates as nodes complete.

    Yields (node_name, state_update) tuples as each node finishes.

    Args:
        question: User's investment question.
        company_id: Company UUID string.
        session_id: Chat session UUID string.
        session: Async SQLAlchemy session.
        messages: Conversation history for multi-turn context.

    Yields:
        Tuples of (node_name: str, partial_state: dict) for each completed node.
    """
    logger.info(
        "graph_stream_start",
        question_preview=question[:100],
        company_id=company_id,
    )

    compiled_graph = build_graph(session)

    initial_state: GraphState = {
        "question": question,
        "company_id": company_id,
        "session_id": session_id,
        "messages": messages or [],
        "errors": [],
        "agent_traces": [],
    }

    # Stream node-by-node updates
    async for event in compiled_graph.astream(initial_state, stream_mode="updates"):
        for node_name, state_update in event.items():
            logger.info("graph_stream_node_complete", node=node_name)
            yield node_name, state_update
