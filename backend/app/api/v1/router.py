"""
DealOS AI — API v1 Router.

Aggregates all v1 endpoint routers under a single prefix.
Versioned API design enables backward-compatible evolution.

Why /api/v1/?
- Explicit versioning prevents breaking changes for API consumers
- Standard practice at financial institutions (Bloomberg, Refinitiv APIs)
- Enables parallel v2 development without disrupting production
"""

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1")


# ── Health Check ──
# Lives at /api/v1/health (not root) so it's behind the version prefix
# for consistency, while the root health check is in main.py

@router.get("/health", tags=["System"])
async def health_check():
    """API v1 health check endpoint."""
    return {
        "status": "healthy",
        "version": "v1",
        "service": "dealos-ai",
    }


# ── Route Registration ──
# Uncommented as each phase adds its router:
#
# from app.api.v1 import auth, users, companies, documents, analysis
# from app.api.v1 import reports, chat, dashboard, search, admin
#
# router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
# router.include_router(users.router, prefix="/users", tags=["Users"])
# router.include_router(companies.router, prefix="/companies", tags=["Companies"])
# router.include_router(documents.router, prefix="/documents", tags=["Documents"])
# router.include_router(analysis.router, prefix="/analysis", tags=["Analysis"])
# router.include_router(reports.router, prefix="/reports", tags=["Reports"])
# router.include_router(chat.router, prefix="/chat", tags=["Chat"])
# router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
# router.include_router(search.router, prefix="/search", tags=["Search"])
# router.include_router(admin.router, prefix="/admin", tags=["Admin"])
