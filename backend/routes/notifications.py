import uuid
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from middleware.auth_middleware import get_current_user
from models.user import User
from schemas.notification import MarkReadRequest, NotificationList, NotificationRead
from services import notification_service

router = APIRouter(prefix="/notifications", tags=["notifications"])

logger = logging.getLogger("sps.notifications_routes")


@router.get("", response_model=NotificationList)
async def list_notifications(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = Query(default=20, ge=1, le=100),
    unread_only: bool = Query(default=False),
) -> NotificationList:
    """Get notifications for the current user."""
    notifications = await notification_service.get_user_notifications(
        db, current_user.id, limit=limit, unread_only=unread_only
    )
    unread_count = await notification_service.get_unread_count(db, current_user.id)
    return NotificationList(
        notifications=[NotificationRead.model_validate(n) for n in notifications],
        unread_count=unread_count,
    )


@router.get("/unread-count")
async def get_unread_count(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    """Get the number of unread notifications for the current user."""
    count = await notification_service.get_unread_count(db, current_user.id)
    return {"unread_count": count}


@router.post("/mark-read")
async def mark_notifications_read(
    payload: MarkReadRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    """Mark specific notifications as read."""
    if payload.notification_ids:
        await notification_service.mark_as_read(db, current_user.id, payload.notification_ids)
    return {"status": "ok"}


@router.post("/mark-all-read")
async def mark_all_notifications_read(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    """Mark all notifications as read."""
    await notification_service.mark_all_as_read(db, current_user.id)
    return {"status": "ok"}