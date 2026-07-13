"""
DealOS AI — Risk Extractor.

Uses GPT-4o to detect and classify risk signals from retrieved
document chunks. Pure function design — no DB dependencies.

Risk categories aligned with institutional risk frameworks (Basel III, ISO 31000):
  Debt Growth, Customer Concentration, Supplier Concentration, Litigation,
  Regulatory, Auditor Changes, Executive Changes, ESG, Operational,
  Cybersecurity, Market

Each risk includes severity, confidence, evidence, and reasoning
for auditability (SOX compliance).
"""

import json

import structlog
from openai import AsyncOpenAI

from app.config import get_settings
from app.schemas.risk import ExtractedRisk, RiskExtractionResult

logger = structlog.get_logger(__name__)

RISK_EXTRACTION_PROMPT = """You are a risk analysis AI specializing in investment due diligence. Analyze the following document content and identify all risk signals.

## Instructions
1. Identify risks ONLY from evidence present in the text. Do NOT invent risks.
2. Classify each risk into one of the predefined categories.
3. Assign severity levels based on potential impact to investment thesis.
4. Include verbatim evidence text that supports each risk finding.
5. Provide analytical reasoning explaining why this constitutes a risk.
6. Assign confidence scores: 1.0 for explicitly stated risks, 0.6-0.9 for inferred risks.

## Risk Categories (use exactly these)
- debt_growth: Increasing leverage, debt covenant concerns, refinancing risk
- customer_concentration: Revenue dependency on few customers
- supplier_concentration: Supply chain dependency on few suppliers
- litigation: Lawsuits, legal proceedings, settlements
- regulatory: Regulatory changes, compliance issues, government investigations
- auditor_changes: Changes in audit firm, auditor opinions, restatements
- executive_changes: C-suite turnover, key person departures
- esg: Environmental, social, governance concerns
- operational: Business continuity, process failures, quality issues
- cybersecurity: Data breaches, IT vulnerabilities, privacy concerns
- market: Competitive threats, market disruption, demand shifts

## Severity Levels
- critical: Immediate threat to investment thesis or company viability
- high: Significant concern requiring active mitigation
- medium: Notable risk worth monitoring
- low: Minor concern with limited impact
- info: Informational finding, not a material risk

## Output Format
Return ONLY a JSON object with this exact structure:
{
  "risks": [
    {
      "risk_category": "litigation",
      "risk_subcategory": "patent_infringement",
      "title": "Pending Patent Infringement Lawsuit",
      "description": "The company faces a patent infringement lawsuit filed by XYZ Corp seeking $500M in damages.",
      "severity": "high",
      "confidence": 0.95,
      "evidence": "As disclosed in Note 15, XYZ Corp filed a patent infringement claim in the Southern District of New York seeking damages of approximately $500 million.",
      "reasoning": "A $500M liability would represent 15% of the company's market cap and could materially impact free cash flow if settled or lost.",
      "source_page": null
    }
  ]
}

## Document Content
"""


class RiskExtractor:
    """
    Detect and classify risk signals from document text using GPT-4o.

    Pure function design: takes context text in, returns validated
    Pydantic objects out. No database dependencies.
    """

    def __init__(self) -> None:
        self._settings = get_settings()
        self._client: AsyncOpenAI | None = None

        if self._settings.openai_api_key:
            self._client = AsyncOpenAI(api_key=self._settings.openai_api_key)

    async def extract(self, context: str) -> RiskExtractionResult:
        """
        Extract risk findings from context text.

        Args:
            context: Concatenated text from retrieved document chunks.

        Returns:
            RiskExtractionResult with validated risk findings.
            Returns empty result if extraction fails or no API key.
        """
        if not self._client:
            logger.warning(
                "risk_extractor_no_client",
                reason="No OpenAI API key configured",
            )
            return RiskExtractionResult()

        if not context.strip():
            logger.warning("risk_extractor_empty_context")
            return RiskExtractionResult()

        logger.info(
            "risk_extraction_start",
            context_length=len(context),
        )

        try:
            response = await self._client.chat.completions.create(
                model=self._settings.openai_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert risk analyst for investment due diligence. "
                                   "Always return valid JSON. Only report risks with evidence.",
                    },
                    {
                        "role": "user",
                        "content": RISK_EXTRACTION_PROMPT + context,
                    },
                ],
                temperature=0.2,  # Slightly higher than financial for nuanced analysis
                response_format={"type": "json_object"},
            )

            raw_output = response.choices[0].message.content
            if not raw_output:
                logger.warning("risk_extractor_empty_response")
                return RiskExtractionResult()

            parsed = json.loads(raw_output)
            result = RiskExtractionResult.model_validate(parsed)

            logger.info(
                "risk_extraction_complete",
                risks_detected=len(result.risks),
                severities=[r.severity for r in result.risks],
            )

            return result

        except json.JSONDecodeError as e:
            logger.error("risk_extractor_json_error", error=str(e))
            return RiskExtractionResult()

        except Exception as e:
            logger.error("risk_extractor_error", error=str(e))
            return RiskExtractionResult()
