import uuid
import logging
from datetime import datetime, timezone
from typing import Sequence

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.notification import Notification
from models.ticket import Ticket
from models.user import User, UserRole

STAFF_ROLES = {UserRole.AGENT, UserRole.SECURITY_ADMIN, UserRole.MANAGER, UserRole.ADMINISTRATOR}

logger = logging.getLogger("sps.notification_service")


async def create_notifications_for_new_ticket(
    db: AsyncSession,
    ticket: Ticket,
    requester_email: str,
) -> list[Notification]:
    """Create notifications for all staff users when a new ticket is created."""
    # Find all users with staff roles (agent, security_admin, manager, administrator)
    staff_roles = [UserRole.AGENT, UserRole.SECURITY_ADMIN, UserRole.MANAGER, UserRole.ADMINISTRATOR]
    result = await db.execute(
        select(User).where(User.role.in_(staff_roles), User.is_active == True)  # noqa: E712
    )
    staff_users: Sequence[User] = result.scalars().all()

    notifications = []
    for staff_user in staff_users:
        notification = Notification(
            recipient_id=staff_user.id,
            ticket_id=ticket.id,
            notification_type="ticket_created",
            title=f"New Ticket: {ticket.ticket_number}",
            message=f"{requester_email} submitted a new ticket: {ticket.subject}",
        )
        db.add(notification)
        notifications.append(notification)

    if notifications:
        await db.flush()
        logger.info(f"Created {len(notifications)} notifications for ticket {ticket.ticket_number}")

    return notifications


async def get_user_notifications(
    db: AsyncSession,
    user_id: uuid.UUID,
    *,
    limit: int = 20,
    unread_only: bool = False,
) -> list[Notification]:
    """Get notifications for a user, newest first."""
    statement = (
        select(Notification)
        .where(Notification.recipient_id == user_id)
        .order_by(Notification.created_at.desc())
        .limit(limit)
    )
    if unread_only:
        statement = statement.where(Notification.is_read == False)  # noqa: E712

    result = await db.execute(statement)
    return list(result.scalars().all())


async def get_unread_count(db: AsyncSession, user_id: uuid.UUID) -> int:
    """Get the number of unread notifications for a user."""
    result = await db.execute(
        select(Notification).where(
            Notification.recipient_id == user_id,
            Notification.is_read == False,  # noqa: E712
        )
    )
    return len(result.scalars().all())


async def mark_as_read(
    db: AsyncSession,
    user_id: uuid.UUID,
    notification_ids: list[uuid.UUID],
) -> None:
    """Mark specific notifications as read for a user."""
    await db.execute(
        update(Notification)
        .where(
            Notification.id.in_(notification_ids),
            Notification.recipient_id == user_id,
        )
        .values(is_read=True)
    )
    await db.commit()


async def mark_all_as_read(
    db: AsyncSession,
    user_id: uuid.UUID,
) -> None:
    """Mark all notifications as read for a user."""
    await db.execute(
        update(Notification)
        .where(
            Notification.recipient_id == user_id,
            Notification.is_read == False,  # noqa: E712
        )
        .values(is_read=True)
    )
    await db.commit()


async def create_notification_for_reply(
    db: AsyncSession,
    ticket: Ticket,
    reply_actor: User | None,
    event_type: str,
    is_public: bool,
) -> list[Notification]:
    """
    Create notifications when a reply is added to a ticket.
    
    - For public replies: notify the ticket requester (if not the actor)
    - For internal notes: notify all staff users except the actor
    - For agent replies: notify the requester
    - For requester replies: notify all assigned/participating staff
    """
    # Skip notifications if actor is None (e.g., email_worker events)
    if reply_actor is None:
        return []
    
    notifications = []
    
    # Determine who should be notified
    recipients = set()
    
    if is_public:
        # Public replies notify the other party
        if reply_actor.role in STAFF_ROLES:
            # Agent/admin replied - notify requester
            if ticket.requester_id and ticket.requester_id != reply_actor.id:
                recipients.add(ticket.requester_id)
        else:
            # Requester replied - notify all staff
            # Find assigned agent if any
            if ticket.assigned_agent_id and ticket.assigned_agent_id != reply_actor.id:
                recipients.add(ticket.assigned_agent_id)
            # Notify all staff users
            result = await db.execute(
                select(User).where(
                    User.role.in_(STAFF_ROLES),
                    User.is_active == True,  # noqa: E712
                    User.id != reply_actor.id,
                )
            )
            for staff_user in result.scalars().all():
                recipients.add(staff_user.id)
    else:
        # Internal notes notify all staff except the actor
        result = await db.execute(
            select(User).where(
                User.role.in_(STAFF_ROLES),
                User.is_active == True,  # noqa: E712
                User.id != reply_actor.id,
            )
        )
        for staff_user in result.scalars().all():
            recipients.add(staff_user.id)
    
    # Create notifications
    for recipient_id in recipients:
        actor_name = reply_actor.full_name or reply_actor.email
        if is_public:
            title = f"New reply on {ticket.ticket_number}"
            message = f"{actor_name} replied to ticket: {ticket.subject}"
        else:
            title = f"New internal note on {ticket.ticket_number}"
            message = f"{actor_name} added an internal note to: {ticket.subject}"
        
        notification = Notification(
            recipient_id=recipient_id,
            ticket_id=ticket.id,
            notification_type="ticket_reply",
            title=title,
            message=message,
        )
        db.add(notification)
        notifications.append(notification)
    
    if notifications:
        await db.flush()
        logger.info(f"Created {len(notifications)} reply notifications for ticket {ticket.ticket_number}")
    
    return notifications
