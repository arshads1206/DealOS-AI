"""
DealOS AI — User Management Endpoints.

Admin-only REST API for user CRUD:
- GET /users — List all users (paginated)
- POST /users — Create a user (with role assignment)
- GET /users/{id} — Get user by ID
- PATCH /users/{id} — Update user
- DELETE /users/{id} — Deactivate user

All endpoints require ADMIN role.
"""

import uuid

from fastapi import APIRouter, Depends, Query

from app.api.middleware.auth import CurrentUser
from app.core.constants import UserRole
from app.core.permissions import Permission, PermissionChecker
from app.dependencies import DbSession
from app.schemas.common import PaginatedResponse, PaginationMeta
from app.schemas.user import UserCreate, UserResponse, UserUpdate

from app.services.user_service import UserService

router = APIRouter()


@router.get(
    "/",
    response_model=PaginatedResponse[UserResponse],
    summary="List all users (admin only)",
    responses={
        200: {"description": "Paginated user list"},
        403: {"description": "Insufficient permissions"},
    },
)
async def list_users(
    db: DbSession,
    current_user: CurrentUser,
    _: None = Depends(PermissionChecker(Permission.MANAGE_USERS)),
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
):
    """
    List all users with pagination.

    Requires the `manage_users` permission (admin only).
    Returns users sorted by creation date (newest first).
    """
    service = UserService(db)
    skip = (page - 1) * page_size
    users, total = await service.list_users(skip=skip, limit=page_size)

    total_pages = (total + page_size - 1) // page_size

    return PaginatedResponse(
        data=users,
        meta=PaginationMeta(
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        ),
    )


@router.post(
    "/",
    response_model=UserResponse,
    status_code=201,
    summary="Create a new user (admin only)",
    responses={
        201: {"description": "User created"},
        403: {"description": "Insufficient permissions"},
        409: {"description": "Email already exists"},
    },
)
async def create_user(
    data: UserCreate,
    db: DbSession,
    current_user: CurrentUser,
    _: None = Depends(PermissionChecker(Permission.MANAGE_USERS)),
):
    """
    Create a new user with a specific role.

    Unlike self-registration, admin user creation allows assigning
    any role (admin, analyst, reviewer, viewer).
    """
    service = UserService(db)
    return await service.create_user(
        data=data,
        created_by=uuid.UUID(current_user["user_id"]),
    )


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID (admin only)",
    responses={
        200: {"description": "User details"},
        403: {"description": "Insufficient permissions"},
        404: {"description": "User not found"},
    },
)
async def get_user(
    user_id: uuid.UUID,
    db: DbSession,
    current_user: CurrentUser,
    _: None = Depends(PermissionChecker(Permission.MANAGE_USERS)),
):
    """Get a specific user by their ID."""
    service = UserService(db)
    return await service.get_user(user_id)


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update user (admin only)",
    responses={
        200: {"description": "User updated"},
        403: {"description": "Insufficient permissions"},
        404: {"description": "User not found"},
        409: {"description": "Email already in use"},
    },
)
async def update_user(
    user_id: uuid.UUID,
    data: UserUpdate,
    db: DbSession,
    current_user: CurrentUser,
    _: None = Depends(PermissionChecker(Permission.MANAGE_USERS)),
):
    """
    Update a user's profile, role, or status.

    Only provided fields are updated (PATCH semantics).
    Role changes are audited with old and new values.
    """
    service = UserService(db)
    return await service.update_user(
        user_id=user_id,
        data=data,
        updated_by=uuid.UUID(current_user["user_id"]),
    )


@router.delete(
    "/{user_id}",
    response_model=UserResponse,
    summary="Deactivate user (admin only)",
    responses={
        200: {"description": "User deactivated"},
        403: {"description": "Insufficient permissions"},
        404: {"description": "User not found"},
        422: {"description": "Cannot deactivate self"},
    },
)
async def deactivate_user(
    user_id: uuid.UUID,
    db: DbSession,
    current_user: CurrentUser,
    _: None = Depends(PermissionChecker(Permission.MANAGE_USERS)),
):
    """
    Deactivate a user account.

    The user's data is preserved but they can no longer log in.
    Admins cannot deactivate their own account.
    """
    service = UserService(db)
    return await service.deactivate_user(
        user_id=user_id,
        deactivated_by=uuid.UUID(current_user["user_id"]),
    )
