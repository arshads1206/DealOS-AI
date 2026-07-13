"""
DealOS AI — Company Extractor.

Uses GPT-4o to generate a structured company profile from retrieved
document chunks. Pure function design — no DB dependencies.

Extracts:
  Business Summary, Industry, Sector, Products, Business Segments,
  Countries, Major Customers, Major Competitors, Employee Count,
  Founded Year, Headquarters

This is intelligence aggregation — synthesizing scattered information
from multiple document sections into a cohesive company profile.
"""

import json

import structlog
from openai import AsyncOpenAI

from app.config import get_settings
from app.schemas.company_intelligence import ExtractedCompanyProfile

logger = structlog.get_logger(__name__)

COMPANY_EXTRACTION_PROMPT = """You are a business intelligence AI. Analyze the following document content and create a comprehensive company profile.

## Instructions
1. Synthesize information from across the document to build a complete profile.
2. Only include information that is supported by the text.
3. For the business summary, write 2-4 paragraphs covering what the company does, its market position, and key competitive advantages.
4. List products, segments, countries, customers, and competitors as arrays.
5. If information for a field is not available in the text, use null or empty arrays.

## Output Format
Return ONLY a JSON object with this exact structure:
{
  "business_summary": "Detailed business description...",
  "industry": "Technology",
  "sector": "Enterprise Software",
  "products": ["Product A", "Product B"],
  "business_segments": ["Enterprise", "Consumer", "Cloud Services"],
  "countries": ["United States", "Germany", "Japan"],
  "major_customers": ["Customer A", "Customer B"],
  "major_competitors": ["Competitor A", "Competitor B"],
  "employee_count": 50000,
  "founded_year": 1998,
  "headquarters": "San Francisco, CA, USA"
}

## Document Content
"""


class CompanyExtractor:
    """
    Generate structured company profiles from document text using GPT-4o.

    Pure function design: takes context text in, returns validated
    Pydantic objects out. No database dependencies.
    """

    def __init__(self) -> None:
        self._settings = get_settings()
        self._client: AsyncOpenAI | None = None

        if self._settings.openai_api_key:
            self._client = AsyncOpenAI(api_key=self._settings.openai_api_key)

    async def extract(self, context: str) -> ExtractedCompanyProfile | None:
        """
        Extract a structured company profile from context text.

        Args:
            context: Concatenated text from retrieved document chunks.

        Returns:
            ExtractedCompanyProfile with validated company data.
            Returns None if extraction fails or no API key.
        """
        if not self._client:
            logger.warning(
                "company_extractor_no_client",
                reason="No OpenAI API key configured",
            )
            return None

        if not context.strip():
            logger.warning("company_extractor_empty_context")
            return None

        logger.info(
            "company_extraction_start",
            context_length=len(context),
        )

        try:
            response = await self._client.chat.completions.create(
                model=self._settings.openai_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a business intelligence analyst. "
                                   "Always return valid JSON. Only include factual information.",
                    },
                    {
                        "role": "user",
                        "content": COMPANY_EXTRACTION_PROMPT + context,
                    },
                ],
                temperature=0.3,  # Moderate — allows synthesis while staying factual
                response_format={"type": "json_object"},
            )

            raw_output = response.choices[0].message.content
            if not raw_output:
                logger.warning("company_extractor_empty_response")
                return None

            parsed = json.loads(raw_output)
            result = ExtractedCompanyProfile.model_validate(parsed)

            logger.info(
                "company_extraction_complete",
                industry=result.industry,
                products_count=len(result.products),
                segments_count=len(result.business_segments),
                countries_count=len(result.countries),
            )

            return result

        except json.JSONDecodeError as e:
            logger.error("company_extractor_json_error", error=str(e))
            return None

        except Exception as e:
            logger.error("company_extractor_error", error=str(e))
            return None
