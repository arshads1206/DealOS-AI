"""
DealOS AI — LangGraph State Definition.

Defines the TypedDict that flows through every node in the multi-agent graph.

Design decisions:
- TypedDict (not dataclass): LangGraph requires TypedDict for state.
- Every field has a default: Nodes only write what they produce.
- Specialist results are strings: LLM-generated summaries, not raw DB models.
  The DB models are consumed internally by the node and converted to prose.
- `messages` stores conversation history for multi-turn memory.
"""

from typing import TypedDict


class GraphState(TypedDict, total=False):
    """
    State that flows through the LangGraph investment analyst pipeline.

    Each node reads what it needs and writes its output field.
    The state accumulates results as it traverses the graph.
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

    # ── Observability ──
    errors: list[str]          # Errors encountered during execution
    agent_traces: list[dict]   # [{name, status, duration_ms, summary}]
