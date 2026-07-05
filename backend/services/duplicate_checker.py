"""Duplicate ticket detection service using content similarity matching."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from difflib import SequenceMatcher
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.ticket import Ticket, TicketStatus


def similarity(a: str, b: str) -> float:
    """Compute string similarity ratio between two strings.

    Args:
        a: First string to compare.
        b: Second string to compare.

    Returns:
        A float between 0.0 (completely different) and 1.0 (identical).
    """
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


async def check_for_duplicate(
    db: AsyncSession,
    requester_email: str,
    subject: str,
    description: str,
) -> Optional[Ticket]:
    """Check if the same user already has an open ticket with similar content
    submitted within the last 4 hours.

    Args:
        db: Database session.
        requester_email: Email of the ticket requester.
        subject: Subject of the new ticket.
        description: Description of the new ticket.

    Returns:
        The existing duplicate Ticket if found, or None if no duplicate exists.
    """
    four_hours_ago = datetime.now(timezone.utc) - timedelta(hours=4)

    result = await db.execute(
        select(Ticket).where(
            Ticket.requester_email == requester_email,
            Ticket.status.in_([
                TicketStatus.OPEN,
                TicketStatus.IN_PROGRESS,
                TicketStatus.ESCALATED,
            ]),
            Ticket.created_at >= four_hours_ago,
        )
    )
    existing_tickets: list[Ticket] = list(result.scalars().all())

    for existing in existing_tickets:
        subj_sim = similarity(subject, existing.subject)
        desc_sim = similarity(description or "", existing.description or "")
        if subj_sim >= 0.70 or desc_sim >= 0.80:
            return existing

    return None