"""
DealOS AI — LangGraph State Definition.

Defines the TypedDict that flows through every node in the multi-agent graph.

Design decisions:
- TypedDict (not dataclass): LangGraph requires TypedDict for state.
- Every field has a default: Nodes only write what they produce.
- Specialist results are strings: LLM-generated summaries, not raw DB models.
  The DB models are consumed internally by the node and converted to prose.
- `messages` stores conversation history for multi-turn memory.
- `Annotated` with `operator.add`: List fields (errors, agent_traces) use
  reducer annotations so parallel fan-out nodes ACCUMULATE rather than
  overwrite each other's entries. This is critical for LangGraph parallel
  execution where financial, risk, and company nodes run concurrently.
"""

import operator
from typing import Annotated, TypedDict


class GraphState(TypedDict, total=False):
    """
    State that flows through the LangGraph investment analyst pipeline.

    Each node reads what it needs and writes its output field.
    The state accumulates results as it traverses the graph.

    Fields with `Annotated[..., operator.add]` use LangGraph's reducer
    pattern: when parallel nodes both write to the same list field,
    their entries are concatenated instead of overwritten.
    """

    # ── Input ──
    question: str              # User's investment question
    company_id: str            # Company UUID (string for serialization)
    session_id: str            # Chat session UUID

    # ── Planner Output ──
    execution_plan: list[str]  # Agents to invoke: ["financial", "risk", "company"]

    # ── Specialist Outputs (LLM-generated summaries) ──
    financial_result: str      # Financial analyst's summary
    risk_result: str           # Risk analyst's summary
    company_result: str        # Company analyst's summary

    # ── Committee Output ──
    committee_result: str      # Final investment recommendation
    confidence: float          # Confidence score (0-1)

    # ── Conversation Memory ──
    messages: list[dict]       # [{role, content}] for multi-turn context

    # ── Observability (reducer: accumulate across parallel nodes) ──
    errors: Annotated[list[str], operator.add]
    agent_traces: Annotated[list[dict], operator.add]
