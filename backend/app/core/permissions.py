"""
DealOS AI — Role-Based Access Control (RBAC).

Maps roles to permissions and provides FastAPI dependencies for
enforcement at the endpoint level.

Design decisions:
1. Permission-based, not role-based checking: Endpoints check "can_upload_documents"
   not "is_analyst". This decouples endpoints from specific roles, making it easy
   to add new roles without modifying endpoints.

2. Permissions are a frozenset (immutable): Prevents accidental runtime modification.

3. Implemented as FastAPI dependencies: Composable, testable, and declarative.
   An endpoint declares its required permission in the function signature.

Permission matrix:
    ┌─────────────────────┬───────┬─────────┬──────────┬────────┐
    │ Permission          │ Admin │ Analyst │ Reviewer │ Viewer │
    ├─────────────────────┼───────┼─────────┼──────────┼────────┤
    │ manage_users        │   ✓   │         │          │        │
    │ manage_system       │   ✓   │         │          │        │
    │ create_company      │   ✓   │    ✓    │          │        │
    │ upload_documents    │   ✓   │    ✓    │          │        │
    │ run_analysis        │   ✓   │    ✓    │          │        │
    │ delete_resources    │   ✓   │         │          │        │
    │ generate_reports    │   ✓   │    ✓    │    ✓     │        │
    │ chat_with_ai        │   ✓   │    ✓    │    ✓     │        │
    │ view_documents      │   ✓   │    ✓    │    ✓     │   ✓    │
    │ view_reports        │   ✓   │    ✓    │    ✓     │   ✓    │
    │ view_dashboard      │   ✓   │    ✓    │    ✓     │   ✓    │
    │ view_audit_logs     │   ✓   │         │          │        │
    └─────────────────────┴───────┴─────────┴──────────┴────────┘
"""

from enum import StrEnum
from typing import Annotated

from fastapi import Depends

from app.core.constants import UserRole
from app.core.exceptions import AuthorizationError


class Permission(StrEnum):
    """Enumerated permissions for fine-grained access control."""

    MANAGE_USERS = "manage_users"
    MANAGE_SYSTEM = "manage_system"
    CREATE_COMPANY = "create_company"
    UPLOAD_DOCUMENTS = "upload_documents"
    RUN_ANALYSIS = "run_analysis"
    DELETE_RESOURCES = "delete_resources"
    GENERATE_REPORTS = "generate_reports"
    CHAT_WITH_AI = "chat_with_ai"
    VIEW_DOCUMENTS = "view_documents"
    VIEW_REPORTS = "view_reports"
    VIEW_DASHBOARD = "view_dashboard"
    VIEW_AUDIT_LOGS = "view_audit_logs"


# ── Role → Permission Mapping ──
# frozenset for immutability — prevents accidental modification at runtime.

ROLE_PERMISSIONS: dict[str, frozenset[str]] = {
    UserRole.ADMIN: frozenset({
        Permission.MANAGE_USERS,
        Permission.MANAGE_SYSTEM,
        Permission.CREATE_COMPANY,
        Permission.UPLOAD_DOCUMENTS,
        Permission.RUN_ANALYSIS,
        Permission.DELETE_RESOURCES,
        Permission.GENERATE_REPORTS,
        Permission.CHAT_WITH_AI,
        Permission.VIEW_DOCUMENTS,
        Permission.VIEW_REPORTS,
        Permission.VIEW_DASHBOARD,
        Permission.VIEW_AUDIT_LOGS,
    }),
    UserRole.ANALYST: frozenset({
        Permission.CREATE_COMPANY,
        Permission.UPLOAD_DOCUMENTS,
        Permission.RUN_ANALYSIS,
        Permission.GENERATE_REPORTS,
        Permission.CHAT_WITH_AI,
        Permission.VIEW_DOCUMENTS,
        Permission.VIEW_REPORTS,
        Permission.VIEW_DASHBOARD,
    }),
    UserRole.REVIEWER: frozenset({
        Permission.GENERATE_REPORTS,
        Permission.CHAT_WITH_AI,
        Permission.VIEW_DOCUMENTS,
        Permission.VIEW_REPORTS,
        Permission.VIEW_DASHBOARD,
    }),
    UserRole.VIEWER: frozenset({
        Permission.VIEW_DOCUMENTS,
        Permission.VIEW_REPORTS,
        Permission.VIEW_DASHBOARD,
    }),
}


def has_permission(role: str, permission: str) -> bool:
    """Check if a role has a specific permission."""
    role_perms = ROLE_PERMISSIONS.get(role, frozenset())
    return permission in role_perms


def get_permissions(role: str) -> frozenset[str]:
    """Get all permissions for a given role."""
    return ROLE_PERMISSIONS.get(role, frozenset())


class PermissionChecker:
    """
    FastAPI dependency that enforces a required permission.

    Usage:
        @router.post("/companies")
        async def create_company(
            current_user: CurrentUser,
            _: None = Depends(PermissionChecker(Permission.CREATE_COMPANY)),
        ):
            ...

    The checker reads the current user's role from the request state
    (set by the auth middleware) and verifies the required permission.
    """

    def __init__(self, required_permission: Permission) -> None:
        self.required_permission = required_permission

    def __call__(self, current_user: dict) -> None:
        """
        Verify the current user has the required permission.

        Args:
            current_user: User data dict from auth middleware (injected via Depends).

        Raises:
            AuthorizationError: If the user's role lacks the required permission.
        """
        role = current_user.get("role", "")

        if not has_permission(role, self.required_permission):
            raise AuthorizationError(
                message=f"Permission '{self.required_permission}' required",
                error_code="INSUFFICIENT_PERMISSIONS",
                details={
                    "required": self.required_permission,
                    "user_role": role,
                },
            )


class RoleChecker:
    """
    FastAPI dependency that enforces minimum role level.

    Simpler alternative to PermissionChecker when you want to restrict
    by role directly (e.g., admin-only endpoints).

    Usage:
        @router.delete("/users/{user_id}")
        async def delete_user(
            _: None = Depends(RoleChecker([UserRole.ADMIN])),
        ):
            ...
    """

    def __init__(self, allowed_roles: list[str]) -> None:
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: dict) -> None:
        role = current_user.get("role", "")

        if role not in self.allowed_roles:
            raise AuthorizationError(
                message="Insufficient role for this action",
                error_code="INSUFFICIENT_ROLE",
                details={
                    "required_roles": self.allowed_roles,
                    "user_role": role,
                },
            )
