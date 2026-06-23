import logging
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from middleware.auth_middleware import get_current_user, require_roles
from models.user import User, UserRole
from schemas.user import UserCreateAdmin, UserRead, UserUpdate
from services.auth_service import hash_password

router = APIRouter(prefix="/users", tags=["users"])

logger = logging.getLogger("sps.users_routes")

ADMIN_ROLES = {UserRole.ADMINISTRATOR}


@router.get("", response_model=list[UserRead])
async def list_users(
    current_user: Annotated[User, Depends(require_roles(ADMIN_ROLES))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[User]:
    """List all users (admin only)."""
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    return list(result.scalars().all())


@router.get("/roles", response_model=list[dict])
async def list_roles(
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[dict]:
    """Return all available roles and their metadata."""
    return [
        {"name": "Intern", "value": "intern", "access": "Requester self-service"},
        {"name": "Employee", "value": "employee", "access": "Requester self-service"},
        {"name": "Agent", "value": "agent", "access": "Ticket queue and updates"},
        {"name": "Security Admin", "value": "security_admin", "access": "Approvals and security review"},
        {"name": "Manager", "value": "manager", "access": "Reports and approvals"},
        {"name": "Administrator", "value": "administrator", "access": "Full backend access"},
    ]


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreateAdmin,
    current_user: Annotated[User, Depends(require_roles(ADMIN_ROLES))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Create a new user (admin only)."""
    existing = await db.scalar(select(User).where(User.email == payload.email))
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists",
        )

    user = User(
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
        role=payload.role,
        is_active=payload.is_active,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: uuid.UUID,
    current_user: Annotated[User, Depends(require_roles(ADMIN_ROLES))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Get a single user by ID (admin only)."""
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: uuid.UUID,
    payload: UserUpdate,
    current_user: Annotated[User, Depends(require_roles(ADMIN_ROLES))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Update a user's name, role, or active status (admin only)."""
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Prevent the last admin from deactivating themselves
    if user.id == current_user.id and payload.is_active is False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot deactivate your own account",
        )

    if payload.full_name is not None:
        user.full_name = payload.full_name
    if payload.role is not None:
        user.role = payload.role
    if payload.is_active is not None:
        user.is_active = payload.is_active

    await db.commit()
    await db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: uuid.UUID,
    current_user: Annotated[User, Depends(require_roles(ADMIN_ROLES))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Delete a user (admin only). Cannot delete yourself."""
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete your own account",
        )

    await db.delete(user)
    await db.commit()