"""
DealOS AI — Test Data Factories.

Uses the Factory pattern to create realistic test data.
Factories produce model instances with sensible defaults that can
be overridden per-test for specific scenarios.

Why factories instead of raw inserts?
- Readable: factory.create_user(role="admin") is self-documenting
- Maintainable: Schema changes only need updates in one place
- Realistic: Defaults produce plausible data, not "test" / "12345"
"""

import uuid
from datetime import datetime

from app.core.constants import (
    DocumentStatus,
    NotificationType,
    RiskSeverity,
    TaskStatus,
    UserRole,
)


class UserFactory:
    """Factory for creating test User data."""

    @staticmethod
    def build(
        email: str = "analyst@dealos.ai",
        full_name: str = "Jane Analyst",
        role: str = UserRole.ANALYST,
        status: str = "active",
        hashed_password: str = "$2b$12$placeholder_hash",
    ) -> dict:
        """Build a user data dictionary (not persisted)."""
        return {
            "email": email,
            "full_name": full_name,
            "role": role,
            "status": status,
            "hashed_password": hashed_password,
        }

    @staticmethod
    def build_admin(**kwargs) -> dict:
        """Build an admin user."""
        defaults = {"email": "admin@dealos.ai", "full_name": "Admin User", "role": UserRole.ADMIN}
        defaults.update(kwargs)
        return UserFactory.build(**defaults)


class CompanyFactory:
    """Factory for creating test Company data."""

    @staticmethod
    def build(
        name: str = "Acme Corp",
        ticker: str = "ACME",
        industry: str = "Technology",
        sector: str = "Software",
        description: str = "A leading enterprise software company.",
        country: str = "US",
        created_by: uuid.UUID | None = None,
    ) -> dict:
        return {
            "name": name,
            "ticker": ticker,
            "industry": industry,
            "sector": sector,
            "description": description,
            "country": country,
            "created_by": created_by or uuid.uuid4(),
        }


class DocumentFactory:
    """Factory for creating test Document data."""

    @staticmethod
    def build(
        filename: str | None = None,
        original_filename: str = "annual_report_2024.pdf",
        content_type: str = "application/pdf",
        storage_path: str = "dealos-documents/test/file.pdf",
        file_size: int = 1024000,
        status: str = DocumentStatus.UPLOADED,
        company_id: uuid.UUID | None = None,
        uploaded_by: uuid.UUID | None = None,
    ) -> dict:
        return {
            "filename": filename or f"{uuid.uuid4()}.pdf",
            "original_filename": original_filename,
            "content_type": content_type,
            "storage_path": storage_path,
            "file_size": file_size,
            "status": status,
            "company_id": company_id or uuid.uuid4(),
            "uploaded_by": uploaded_by or uuid.uuid4(),
        }


class FinancialMetricFactory:
    """Factory for creating test FinancialMetric data."""

    @staticmethod
    def build(
        metric_name: str = "revenue",
        metric_value: float = 1250.5,
        currency: str = "USD",
        unit: str = "millions",
        period: str = "FY 2024",
        period_type: str = "annual",
        confidence: float = 0.92,
        company_id: uuid.UUID | None = None,
        document_id: uuid.UUID | None = None,
    ) -> dict:
        return {
            "metric_name": metric_name,
            "metric_value": metric_value,
            "currency": currency,
            "unit": unit,
            "period": period,
            "period_type": period_type,
            "confidence": confidence,
            "company_id": company_id or uuid.uuid4(),
            "document_id": document_id or uuid.uuid4(),
        }


class RiskFindingFactory:
    """Factory for creating test RiskFinding data."""

    @staticmethod
    def build(
        risk_category: str = "financial",
        risk_subcategory: str = "debt_growth",
        title: str = "Significant Debt Increase",
        description: str = "Total debt increased by 45% year-over-year.",
        severity: str = RiskSeverity.HIGH,
        confidence: float = 0.88,
        evidence: str = "Long-term debt grew from $2.1B to $3.05B (page 47).",
        source_page: int = 47,
        reasoning: str = "Rapid debt accumulation may indicate overleveraging.",
        company_id: uuid.UUID | None = None,
        document_id: uuid.UUID | None = None,
    ) -> dict:
        return {
            "risk_category": risk_category,
            "risk_subcategory": risk_subcategory,
            "title": title,
            "description": description,
            "severity": severity,
            "confidence": confidence,
            "evidence": evidence,
            "source_page": source_page,
            "reasoning": reasoning,
            "company_id": company_id or uuid.uuid4(),
            "document_id": document_id or uuid.uuid4(),
        }
