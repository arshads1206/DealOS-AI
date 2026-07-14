"""
DealOS AI — LangGraph Node Functions.

Each function is a graph node that reads from GraphState, performs work,
and returns a partial state update. Nodes are pure orchestrators — they
delegate ALL domain work to existing services.

Node responsibilities:
  planner_node        → Understand intent, decide which agents to invoke
  financial_node      → Fetch/trigger financial analysis, summarize
  risk_node           → Fetch/trigger risk analysis, summarize
  company_node        → Fetch/trigger company profile, summarize
  committee_node      → Synthesize final investment recommendation

CRITICAL: No node performs retrieval, extraction, or document parsing.
All intelligence work is delegated to existing services.

Retry strategy: LLM calls use tenacity with exponential backoff (3 attempts).
This handles transient OpenAI API errors without failing the entire graph.
"""

import json
import time
from uuid import UUID

import structlog
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.ai.agents.state import GraphState
from app.config import get_settings
from app.services.company_analysis_service import CompanyAnalysisService
from app.services.financial_analysis_service import FinancialAnalysisService
from app.services.risk_analysis_service import RiskAnalysisService

logger = structlog.get_logger(__name__)

_settings = get_settings()


def _get_openai_client() -> AsyncOpenAI | None:
    """Get a shared OpenAI client. Returns None if no API key."""
    if not _settings.openai_api_key:
        return None
    return AsyncOpenAI(api_key=_settings.openai_api_key)


# ── Retry-wrapped LLM call ──
# Retries on any Exception (covers rate limits, timeouts, transient errors)
# 3 attempts with exponential backoff: 1s, 2s, 4s

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    retry=retry_if_exception_type(Exception),
    reraise=True,
)
async def _llm_call(
    client: AsyncOpenAI,
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.2,
    response_format: dict | None = None,
) -> str:
    """
    Retry-wrapped LLM call with exponential backoff.

    Args:
        client: AsyncOpenAI client.
        system_prompt: System message.
        user_prompt: User message.
        temperature: Sampling temperature.
        response_format: Optional response format (e.g., json_object).

    Returns:
        The LLM's response content string.
    """
    kwargs = {
        "model": _settings.openai_model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": temperature,
    }
    if response_format:
        kwargs["response_format"] = response_format

    response = await client.chat.completions.create(**kwargs)
    return response.choices[0].message.content or ""


# ═══════════════════════════════════════════════════════════════════
# Planner Node
# ═══════════════════════════════════════════════════════════════════

PLANNER_PROMPT = """You are an investment analysis planner. Given a user's question about a company, decide which specialist agents should be invoked.

Available agents:
- "financial": For questions about revenue, profit, margins, cash flow, debt, ratios, KPIs, earnings, financial performance
- "risk": For questions about risks, threats, litigation, regulatory issues, concentration, ESG, cybersecurity, auditor changes, executive changes
- "company": For questions about business overview, products, segments, competitors, geography, customers, industry

Rules:
1. Only invoke agents whose expertise is relevant to the question.
2. For broad questions like "analyze this company" or "should we invest", invoke ALL agents.
3. For specific questions, invoke only the relevant agent(s).
4. Always return a JSON object with an "agents" array.

Conversation context (if any):
{history}

User question: {question}

Return ONLY a JSON object like: {{"agents": ["financial", "risk"]}}"""


async def planner_node(state: GraphState, session: AsyncSession) -> dict:
    """
    Analyze user intent and create an execution plan.

    Determines which specialist agents are needed based on the question.
    Skips unnecessary agents to save latency and token costs.
    """
    start = time.time()
    question = state.get("question", "")
    messages = state.get("messages", [])

    logger.info("planner_node_start", question_preview=question[:100])

    # Build conversation history context
    history_text = ""
    if messages:
        recent = messages[-6:]  # Last 3 turns (user+assistant pairs)
        history_text = "\n".join(
            f"{m['role']}: {m['content'][:200]}" for m in recent
        )

    client = _get_openai_client()
    if not client:
        # Fallback: invoke all agents
        logger.warning("planner_no_openai_client")
        return {
            "execution_plan": ["financial", "risk", "company"],
            "agent_traces": [
                {
                    "name": "planner",
                    "status": "completed",
                    "duration_ms": int((time.time() - start) * 1000),
                    "summary": "Fallback: invoking all agents (no OpenAI key)",
                }
            ],
        }

    try:
        prompt = PLANNER_PROMPT.format(
            history=history_text or "No prior conversation.",
            question=question,
        )

        raw = await _llm_call(
            client=client,
            system_prompt="You are an investment analysis routing AI. Return only JSON.",
            user_prompt=prompt,
            temperature=0.1,
            response_format={"type": "json_object"},
        )

        parsed = json.loads(raw or "{}")
        agents = parsed.get("agents", ["financial", "risk", "company"])

        # Validate agent names
        valid_agents = {"financial", "risk", "company"}
        agents = [a for a in agents if a in valid_agents]
        if not agents:
            agents = ["financial", "risk", "company"]

        duration_ms = int((time.time() - start) * 1000)

        logger.info("planner_node_complete", execution_plan=agents, duration_ms=duration_ms)

        return {
            "execution_plan": agents,
            "agent_traces": [
                {
                    "name": "planner",
                    "status": "completed",
                    "duration_ms": duration_ms,
                    "summary": f"Invoking agents: {', '.join(agents)}",
                }
            ],
        }

    except Exception as e:
        logger.error("planner_node_error", error=str(e))
        return {
            "execution_plan": ["financial", "risk", "company"],
            "errors": [f"Planner error: {str(e)}"],
            "agent_traces": [
                {
                    "name": "planner",
                    "status": "error",
                    "duration_ms": int((time.time() - start) * 1000),
                    "summary": f"Error: {str(e)}, falling back to all agents",
                }
            ],
        }


# ═══════════════════════════════════════════════════════════════════
# Financial Analyst Node
# ═══════════════════════════════════════════════════════════════════

FINANCIAL_SUMMARY_PROMPT = """You are a senior financial analyst. Given the following structured financial metrics for a company, write a concise investment-grade financial summary.

Focus on:
- Key financial performance (revenue, profitability, margins)
- Cash flow health (operating cash flow, free cash flow)
- Balance sheet strength (debt, cash, ratios)
- Notable trends or concerns

If the data is insufficient, explicitly state what is missing.
Do NOT fabricate numbers.

Question context: {question}

Financial data:
{data}

Write a clear, structured financial summary (3-5 paragraphs):"""


async def financial_node(state: GraphState, session: AsyncSession) -> dict:
    """
    Fetch financial metrics and produce an analyst summary.

    Reuses FinancialAnalysisService — never retrieves documents directly.
    If no stored metrics exist, triggers extraction lazily.
    Uses tenacity retry on LLM summarization calls.
    """
    start = time.time()
    company_id = UUID(state["company_id"])
    question = state.get("question", "")

    logger.info("financial_node_start", company_id=str(company_id))

    try:
        service = FinancialAnalysisService(session)

        # Try to get stored metrics first
        result = await service.get_metrics(company_id=company_id)

        # Lazy extraction: if no data, trigger analysis
        if result.status == "no_data":
            logger.info("financial_node_triggering_extraction", company_id=str(company_id))
            result = await service.run_analysis(company_id=company_id)

        # Format metrics for the LLM
        if result.metrics:
            metrics_text = "\n".join(
                f"- {m.metric_name}: {m.metric_value} {m.currency or ''} "
                f"({m.unit or ''}) | Period: {m.period} | Confidence: {m.confidence}"
                for m in result.metrics
            )
        else:
            metrics_text = "No financial metrics available for this company."

        # Generate analyst summary via LLM (with retry)
        client = _get_openai_client()
        if client and result.metrics:
            prompt = FINANCIAL_SUMMARY_PROMPT.format(
                question=question,
                data=metrics_text,
            )
            summary = await _llm_call(
                client=client,
                system_prompt="You are a senior financial analyst at an investment bank.",
                user_prompt=prompt,
                temperature=0.2,
            )
        else:
            summary = metrics_text

        duration_ms = int((time.time() - start) * 1000)
        logger.info("financial_node_complete", duration_ms=duration_ms, metrics_count=len(result.metrics))

        # With Annotated[list, operator.add] reducer, just return the new entries
        return {
            "financial_result": summary,
            "agent_traces": [
                {
                    "name": "financial",
                    "status": "completed",
                    "duration_ms": duration_ms,
                    "summary": f"Analyzed {len(result.metrics)} financial metrics",
                }
            ],
        }

    except Exception as e:
        duration_ms = int((time.time() - start) * 1000)
        logger.error("financial_node_error", error=str(e))
        return {
            "financial_result": f"Financial analysis encountered an error: {str(e)}",
            "errors": [f"Financial agent error: {str(e)}"],
            "agent_traces": [
                {
                    "name": "financial",
                    "status": "error",
                    "duration_ms": duration_ms,
                    "summary": f"Error: {str(e)}",
                }
            ],
        }


# ═══════════════════════════════════════════════════════════════════
# Risk Analyst Node
# ═══════════════════════════════════════════════════════════════════

RISK_SUMMARY_PROMPT = """You are a senior risk analyst conducting investment due diligence. Given the following risk findings for a company, write a concise risk assessment.

Focus on:
- Critical and high-severity risks that could impact the investment thesis
- Risk concentration patterns (multiple risks in one category)
- Evidence quality and confidence levels
- Recommended mitigation or further investigation areas

If the data is insufficient, explicitly state what is missing.
Do NOT fabricate risks.

Question context: {question}

Risk findings:
{data}

Severity summary:
{severity}

Write a clear, structured risk assessment (3-5 paragraphs):"""


async def risk_node(state: GraphState, session: AsyncSession) -> dict:
    """
    Fetch risk findings and produce an analyst summary.

    Reuses RiskAnalysisService — never retrieves documents directly.
    If no stored risks exist, triggers extraction lazily.
    Uses tenacity retry on LLM summarization calls.
    """
    start = time.time()
    company_id = UUID(state["company_id"])
    question = state.get("question", "")

    logger.info("risk_node_start", company_id=str(company_id))

    try:
        service = RiskAnalysisService(session)

        # Try to get stored risks first
        result = await service.get_risks(company_id=company_id)

        # Lazy extraction
        if result.status == "no_data":
            logger.info("risk_node_triggering_extraction", company_id=str(company_id))
            result = await service.run_analysis(company_id=company_id)

        # Format risks for the LLM
        if result.risks:
            risks_text = "\n".join(
                f"- [{r.severity.upper()}] {r.title}: {r.description[:200]}... "
                f"| Category: {r.risk_category} | Confidence: {r.confidence}"
                for r in result.risks
            )
            severity_text = (
                f"Critical: {result.severity_summary.critical}, "
                f"High: {result.severity_summary.high}, "
                f"Medium: {result.severity_summary.medium}, "
                f"Low: {result.severity_summary.low}, "
                f"Info: {result.severity_summary.info}"
            )
        else:
            risks_text = "No risk findings available for this company."
            severity_text = "N/A"

        # Generate analyst summary (with retry)
        client = _get_openai_client()
        if client and result.risks:
            prompt = RISK_SUMMARY_PROMPT.format(
                question=question,
                data=risks_text,
                severity=severity_text,
            )
            summary = await _llm_call(
                client=client,
                system_prompt="You are a senior risk analyst at an investment bank.",
                user_prompt=prompt,
                temperature=0.2,
            )
        else:
            summary = risks_text

        duration_ms = int((time.time() - start) * 1000)
        logger.info("risk_node_complete", duration_ms=duration_ms, risks_count=len(result.risks))

        return {
            "risk_result": summary,
            "agent_traces": [
                {
                    "name": "risk",
                    "status": "completed",
                    "duration_ms": duration_ms,
                    "summary": f"Assessed {len(result.risks)} risk findings",
                }
            ],
        }

    except Exception as e:
        duration_ms = int((time.time() - start) * 1000)
        logger.error("risk_node_error", error=str(e))
        return {
            "risk_result": f"Risk analysis encountered an error: {str(e)}",
            "errors": [f"Risk agent error: {str(e)}"],
            "agent_traces": [
                {
                    "name": "risk",
                    "status": "error",
                    "duration_ms": duration_ms,
                    "summary": f"Error: {str(e)}",
                }
            ],
        }


# ═══════════════════════════════════════════════════════════════════
# Company Analyst Node
# ═══════════════════════════════════════════════════════════════════

COMPANY_SUMMARY_PROMPT = """You are a senior business analyst. Given the following company profile, write a concise company overview suitable for investment committee review.

Focus on:
- What the company does (business summary)
- Market position and competitive landscape
- Geographic and segment diversification
- Key customers and dependencies

If the data is insufficient, explicitly state what is missing.

Question context: {question}

Company profile:
{data}

Write a clear, structured company overview (2-4 paragraphs):"""


async def company_node(state: GraphState, session: AsyncSession) -> dict:
    """
    Fetch company profile and produce an analyst summary.

    Reuses CompanyAnalysisService — never retrieves documents directly.
    If no stored profile exists, triggers extraction lazily.
    Uses tenacity retry on LLM summarization calls.
    """
    start = time.time()
    company_id = UUID(state["company_id"])
    question = state.get("question", "")

    logger.info("company_node_start", company_id=str(company_id))

    try:
        service = CompanyAnalysisService(session)

        # Try to get stored profile first
        result = await service.get_profile(company_id=company_id)

        # Lazy extraction
        if result.status == "no_data":
            logger.info("company_node_triggering_extraction", company_id=str(company_id))
            result = await service.run_analysis(company_id=company_id)

        # Format profile for the LLM
        profile_parts = []
        if result.business_summary:
            profile_parts.append(f"Business Summary: {result.business_summary}")
        if result.industry:
            profile_parts.append(f"Industry: {result.industry}")
        if result.sector:
            profile_parts.append(f"Sector: {result.sector}")
        if result.products:
            profile_parts.append(f"Products/Services: {', '.join(result.products)}")
        if result.business_segments:
            profile_parts.append(f"Business Segments: {', '.join(result.business_segments)}")
        if result.countries:
            profile_parts.append(f"Geographic Presence: {', '.join(result.countries)}")
        if result.major_customers:
            profile_parts.append(f"Major Customers: {', '.join(result.major_customers)}")
        if result.major_competitors:
            profile_parts.append(f"Major Competitors: {', '.join(result.major_competitors)}")

        profile_text = "\n".join(profile_parts) if profile_parts else "No company profile available."

        # Generate analyst summary (with retry)
        client = _get_openai_client()
        if client and profile_parts:
            prompt = COMPANY_SUMMARY_PROMPT.format(
                question=question,
                data=profile_text,
            )
            summary = await _llm_call(
                client=client,
                system_prompt="You are a senior business analyst at an investment bank.",
                user_prompt=prompt,
                temperature=0.3,
            )
        else:
            summary = profile_text

        duration_ms = int((time.time() - start) * 1000)
        logger.info("company_node_complete", duration_ms=duration_ms)

        return {
            "company_result": summary,
            "agent_traces": [
                {
                    "name": "company",
                    "status": "completed",
                    "duration_ms": duration_ms,
                    "summary": f"Profiled company: {result.name}",
                }
            ],
        }

    except Exception as e:
        duration_ms = int((time.time() - start) * 1000)
        logger.error("company_node_error", error=str(e))
        return {
            "company_result": f"Company analysis encountered an error: {str(e)}",
            "errors": [f"Company agent error: {str(e)}"],
            "agent_traces": [
                {
                    "name": "company",
                    "status": "error",
                    "duration_ms": duration_ms,
                    "summary": f"Error: {str(e)}",
                }
            ],
        }


# ═══════════════════════════════════════════════════════════════════
# Investment Committee Node
# ═══════════════════════════════════════════════════════════════════

COMMITTEE_PROMPT = """You are an Investment Committee at a top-tier private equity firm. You are reviewing specialist analyst reports and must produce a final investment recommendation.

## Input Reports

### Financial Analysis
{financial}

### Risk Assessment
{risk}

### Company Profile
{company}

## Conversation Context
{history}

## Current Question
{question}

## Instructions
1. Synthesize the specialist reports into a cohesive investment perspective.
2. Provide a clear recommendation (Buy / Hold / Pass / Needs More Data).
3. List supporting reasons with specific evidence from the reports.
4. Highlight key risks that could derail the thesis.
5. Assign a confidence score (0.0 to 1.0) based on data completeness and conviction.
6. If evidence is insufficient for any area, explicitly state: "INSUFFICIENT DATA: [what is missing]".
7. NEVER fabricate data, metrics, or risk findings not present in the reports.

Format your response as:

## Executive Summary
[2-3 sentence overview]

## Investment Recommendation
[Buy / Hold / Pass / Needs More Data]

## Supporting Evidence
[Bullet points with specific data from reports]

## Key Risks
[Bullet points with severity context]

## Confidence Score
[0.0 - 1.0 with brief justification]

## Data Gaps
[What additional analysis would strengthen the recommendation]"""


async def committee_node(state: GraphState, session: AsyncSession) -> dict:
    """
    Synthesize all specialist outputs into a final investment recommendation.

    This is the final node — it combines financial, risk, and company
    summaries into a structured investment committee output.
    Uses tenacity retry on LLM synthesis calls.
    """
    start = time.time()
    question = state.get("question", "")
    messages = state.get("messages", [])

    financial = state.get("financial_result", "No financial analysis was performed.")
    risk = state.get("risk_result", "No risk analysis was performed.")
    company = state.get("company_result", "No company analysis was performed.")

    logger.info("committee_node_start")

    # Build conversation context
    history_text = ""
    if messages:
        recent = messages[-6:]
        history_text = "\n".join(
            f"{m['role']}: {m['content'][:300]}" for m in recent
        )

    client = _get_openai_client()
    if not client:
        fallback = (
            f"## Financial Analysis\n{financial}\n\n"
            f"## Risk Assessment\n{risk}\n\n"
            f"## Company Profile\n{company}\n\n"
            f"Note: Investment Committee synthesis unavailable (no OpenAI key)."
        )
        return {
            "committee_result": fallback,
            "confidence": 0.0,
            "agent_traces": [
                {
                    "name": "committee",
                    "status": "completed",
                    "duration_ms": int((time.time() - start) * 1000),
                    "summary": "Fallback: concatenated reports (no OpenAI key)",
                }
            ],
        }

    try:
        prompt = COMMITTEE_PROMPT.format(
            financial=financial,
            risk=risk,
            company=company,
            history=history_text or "No prior conversation.",
            question=question,
        )

        result = await _llm_call(
            client=client,
            system_prompt=(
                "You are the Investment Committee of a top-tier PE firm. "
                "Be rigorous, evidence-based, and never hallucinate."
            ),
            user_prompt=prompt,
            temperature=0.3,
        )

        # Extract confidence score from the response
        confidence = _extract_confidence(result)

        duration_ms = int((time.time() - start) * 1000)
        logger.info("committee_node_complete", duration_ms=duration_ms, confidence=confidence)

        return {
            "committee_result": result,
            "confidence": confidence,
            "agent_traces": [
                {
                    "name": "committee",
                    "status": "completed",
                    "duration_ms": duration_ms,
                    "summary": f"Recommendation generated (confidence: {confidence})",
                }
            ],
        }

    except Exception as e:
        duration_ms = int((time.time() - start) * 1000)
        logger.error("committee_node_error", error=str(e))
        return {
            "committee_result": f"Investment Committee synthesis failed: {str(e)}",
            "confidence": 0.0,
            "errors": [f"Committee error: {str(e)}"],
            "agent_traces": [
                {
                    "name": "committee",
                    "status": "error",
                    "duration_ms": duration_ms,
                    "summary": f"Error: {str(e)}",
                }
            ],
        }


def _extract_confidence(text: str) -> float:
    """
    Extract the confidence score from the committee's response.

    Looks for patterns like "Confidence Score: 0.75" or "0.8/1.0".
    Falls back to 0.5 if no score is found.
    """
    import re

    # Try to find confidence score in common formats
    patterns = [
        r"confidence\s*(?:score)?[:\s]*(\d+\.?\d*)",
        r"(\d+\.?\d*)\s*/\s*1\.0",
        r"(\d+\.?\d*)\s*out\s*of\s*1",
    ]

    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            try:
                score = float(match.group(1))
                if 0 <= score <= 1:
                    return score
                elif 1 < score <= 100:
                    return score / 100  # Handle percentage format
            except ValueError:
                continue

    return 0.5  # Default confidence
