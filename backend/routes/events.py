import uuid as uuid_module
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from middleware.auth_middleware import get_optional_current_user
from models.user import User
from schemas.ticket import TimelineEventCreate, TimelineEventRead
from services.ticket_service import add_timeline_event, get_ticket_by_number

router = APIRouter(prefix="/tickets", tags=["events"])


def _client_ip(request: Request):
    return request.client.host if request.client else None


@router.post("/{ticket_id}/events", response_model=TimelineEventRead, status_code=status.HTTP_201_CREATED)
async def create_event(
    ticket_id: str,
    payload: TimelineEventCreate,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User | None, Depends(get_optional_current_user)],
):
    # Accept either a UUID or a ticket_number string (e.g. "SPS-2026-106")
    try:
        resolved_uuid = uuid_module.UUID(ticket_id)
    except ValueError:
        ticket = await get_ticket_by_number(db, ticket_id)
        if ticket is None:
            raise HTTPException(status_code=404, detail="Ticket not found")
        resolved_uuid = ticket.id

    return await add_timeline_event(db, resolved_uuid, payload, current_user, ip_address=_client_ip(request))
