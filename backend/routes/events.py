import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from middleware.auth_middleware import get_optional_current_user
from models.user import User
from schemas.ticket import TimelineEventCreate, TimelineEventRead
from services.ticket_service import add_timeline_event

router = APIRouter(prefix="/tickets", tags=["events"])


def _client_ip(request: Request) -> str | None:
    return request.client.host if request.client else None


@router.post("/{ticket_id}/events", response_model=TimelineEventRead, status_code=status.HTTP_201_CREATED)
async def create_event(
    ticket_id: uuid.UUID,
    payload: TimelineEventCreate,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User | None, Depends(get_optional_current_user)],
):
    return await add_timeline_event(db, ticket_id, payload, current_user, ip_address=_client_ip(request))
