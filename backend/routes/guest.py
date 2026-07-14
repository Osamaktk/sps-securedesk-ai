"""Guest (token-based) ticket dashboard — no full user account required.

A signed JWT (created by `services.auth_service.create_guest_dashboard_token`)
is embedded in the acknowledgment email. Holders of a valid token can:
  - GET  /api/guest/dashboard  -> list ALL of their tickets
  - POST /api/guest/reply      -> add a reply to one of their tickets
  - POST /api/guest/tickets    -> submit a brand-new ticket

The token's `sub` claim is the (normalized) requester email, which scopes every
query so a guest can only ever see/modify tickets they actually requested.
Authenticated (agent/admin/etc.) flows are completely untouched.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.ticket import Ticket, TicketStatus
from models.timeline_event import TimelineEvent, TimelineEventType
from schemas.ticket import TicketCreate, TicketRead
from services import ticket_service
from services.auth_service import decode_guest_dashboard_token

router = APIRouter(prefix="/api/guest", tags=["guest"])


class GuestReplyRequest(BaseModel):
    token: str
    ticket_number: str = Field(min_length=1, max_length=20)
    content: str = Field(min_length=1, max_length=5000)


class GuestTicketRequest(TicketCreate):
    # Extends TicketCreate (which already requires subject/description/category/
    # requester_email etc.) but we ignore the caller-supplied requester_email and
    # force it from the verified token instead.
    token: str


def _resolve_email(token: str) -> str:
    """Decode the guest token and return the requester email, or 401."""
    try:
        return decode_guest_dashboard_token(token)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc


@router.get("/dashboard", response_model=list[TicketRead])
async def guest_dashboard(
    token: str,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """List every ticket requested by the email encoded in the guest token."""
    email = _resolve_email(token)

    result = await db.execute(
        select(Ticket)
        .where(Ticket.requester_email == email)
        .order_by(Ticket.created_at.desc())
    )
    tickets = list(result.scalars().all())
    return [TicketRead.model_validate(t) for t in tickets]


@router.post("/reply", status_code=status.HTTP_201_CREATED)
async def guest_reply(
    payload: GuestReplyRequest,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Add a public reply (from the requester) to one of their own tickets."""
    email = _resolve_email(payload.token)

    ticket = await ticket_service.get_ticket_by_number_and_email(
        db, payload.ticket_number, email
    )
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found or not owned by this guest",
        )

    # Locked tickets (closed/duplicate/resolved) cannot receive replies.
    if ticket.status in {TicketStatus.CLOSED, TicketStatus.DUPLICATE, TicketStatus.RESOLVED}:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "ticket_locked",
                "message": f"Ticket {ticket.ticket_number} is {ticket.status.value} and cannot be replied to.",
                "ticket_number": ticket.ticket_number,
                "status": ticket.status.value,
            },
        )

    event = TimelineEvent(
        ticket_id=ticket.id,
        event_type=TimelineEventType.INTERNAL_NOTE,
        actor_id=None,
        actor_email=email,
        content=payload.content,
        is_public=True,
        channel="email",
    )
    db.add(event)
    await db.commit()
    await db.refresh(event)

    return {
        "ticket_number": ticket.ticket_number,
        "event_id": str(event.id),
        "content": event.content,
    }


@router.post(
    "/tickets",
    response_model=TicketRead,
    status_code=status.HTTP_201_CREATED,
)
async def guest_create_ticket(
    payload: GuestTicketRequest,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Submit a new ticket on behalf of the guest (requester_email from token)."""
    email = _resolve_email(payload.token)

    # Build a TicketCreate with the verified email overriding any caller value.
    create_payload = TicketCreate(
        source=payload.source,
        subject=payload.subject,
        description=payload.description,
        category=payload.category,
        priority=payload.priority,
        risk_level=payload.risk_level,
        requester_email=email,
        ai_summary=payload.ai_summary,
    )

    # actor=None -> treated as an unauthenticated (guest/portal) submission.
    ticket = await ticket_service.create_ticket(
        db,
        create_payload,
        None,
        ip_address=request.client.host if request.client else None,
    )
    return TicketRead.model_validate(ticket)