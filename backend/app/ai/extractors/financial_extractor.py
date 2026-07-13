"""
DealOS AI — Financial Extractor.

Uses GPT-4o to extract structured financial KPIs from retrieved
document chunks. Pure function design — takes text in, returns
validated Pydantic objects out. No DB dependencies.

Extraction targets (all optional — not every document contains every metric):
  Revenue, Gross Profit, Gross Margin, Operating Income, Operating Margin,
  EBITDA, Net Income, Operating Cash Flow, Free Cash Flow, ROE, ROCE,
  Total Debt, Cash & Equivalents, CAPEX, Current Ratio, Debt-to-Equity,
  Segment Revenue, Geographic Revenue, Fiscal Year, Quarter

The prompt instructs GPT-4o to return a JSON object matching the
ExtractionResult schema. Partial extraction is expected and handled.
"""

import json

import structlog
from openai import AsyncOpenAI

from app.config import get_settings
from app.schemas.financial import ExtractionResult, ExtractedMetric

logger = structlog.get_logger(__name__)

FINANCIAL_EXTRACTION_PROMPT = """You are a financial analyst AI. Extract structured financial metrics from the following document content.

## Instructions
1. Extract ONLY metrics that are explicitly stated or directly calculable from the text.
2. Do NOT fabricate, estimate, or infer values not present in the text.
3. Standardize metric names using the predefined list below.
4. Include the exact source text for each metric.
5. Assign confidence scores: 1.0 for explicitly stated values, 0.7-0.9 for calculated values, 0.5-0.7 for inferred values.
6. Identify the fiscal period and reporting currency.

## Metric Names (use exactly these)
- revenue
- gross_profit
- gross_margin
- operating_income
- operating_margin
- ebitda
- net_income
- operating_cash_flow
- free_cash_flow
- roe (return on equity)
- roce (return on capital employed)
- total_debt
- cash_and_equivalents
- capex (capital expenditure)
- current_ratio
- debt_to_equity
- segment_revenue
- geographic_revenue

## Units
- Use "millions" for most absolute dollar values
- Use "billions" if the values are in billions
- Use "percentage" for margins, returns, and ratios expressed as percentages
- Use "ratio" for pure ratios (current ratio, debt-to-equity)

## Output Format
Return ONLY a JSON object with this exact structure:
{
  "metrics": [
    {
      "metric_name": "revenue",
      "metric_value": 45200.0,
      "currency": "USD",
      "unit": "millions",
      "period": "FY 2023",
      "period_type": "annual",
      "confidence": 0.95,
      "source_text": "Total revenue for fiscal year 2023 was $45.2 billion",
      "source_page": null
    }
  ],
  "fiscal_year": "FY 2023",
  "reporting_currency": "USD"
}

## Document Content
"""


class FinancialExtractor:
    """
    Extract structured financial metrics from document text using GPT-4o.

    Pure function design: takes context text in, returns validated
    Pydantic objects out. No database dependencies.
    """

    def __init__(self) -> None:
        self._settings = get_settings()
        self._client: AsyncOpenAI | None = None

        if self._settings.openai_api_key:
            self._client = AsyncOpenAI(api_key=self._settings.openai_api_key)

    async def extract(self, context: str) -> ExtractionResult:
        """
        Extract financial metrics from context text.

        Args:
            context: Concatenated text from retrieved document chunks.

        Returns:
            ExtractionResult with validated financial metrics.
            Returns empty result if extraction fails or no API key.
        """
        if not self._client:
            logger.warning(
                "financial_extractor_no_client",
                reason="No OpenAI API key configured",
            )
            return ExtractionResult()

        if not context.strip():
            logger.warning("financial_extractor_empty_context")
            return ExtractionResult()

        logger.info(
            "financial_extraction_start",
            context_length=len(context),
        )

        try:
            response = await self._client.chat.completions.create(
                model=self._settings.openai_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a precise financial data extraction AI. "
                                   "Always return valid JSON. Never fabricate data.",
                    },
                    {
                        "role": "user",
                        "content": FINANCIAL_EXTRACTION_PROMPT + context,
                    },
                ],
                temperature=0.1,  # Low temperature for factual extraction
                response_format={"type": "json_object"},
            )

            raw_output = response.choices[0].message.content
            if not raw_output:
                logger.warning("financial_extractor_empty_response")
                return ExtractionResult()

            # Parse and validate via Pydantic
            parsed = json.loads(raw_output)
            result = ExtractionResult.model_validate(parsed)

            logger.info(
                "financial_extraction_complete",
                metrics_extracted=len(result.metrics),
                fiscal_year=result.fiscal_year,
                currency=result.reporting_currency,
            )

            return result

        except json.JSONDecodeError as e:
            logger.error("financial_extractor_json_error", error=str(e))
            return ExtractionResult()

        except Exception as e:
            logger.error("financial_extractor_error", error=str(e))
            return ExtractionResult()
